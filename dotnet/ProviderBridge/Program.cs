using System.Diagnostics;
using System.Text;
using Bridge.Shared;
using Bridge.Shared.Configuration;
using Bridge.Shared.Providers;
using Bridge.Shared.Testing;

namespace ProviderBridge;

/// <summary>
/// Week-1 bridge lab: call a chat-completions endpoint over raw <see cref="HttpClient"/>, stream
/// the response over SSE, and retry transient failures with backoff.
///
/// <para>
/// <b>What this app is for:</b> the Python week-1 lab writes the provider seam in
/// <c>agentlab/providers/openai_compat.py</c>. This app writes the same seam in C# so that when
/// you open SendOS's <c>Send.Model.Adapter</c> you recognise every responsibility:
/// build the payload, parse the response, capture usage, parse SSE frames, classify errors.
/// The two things SendOS adds that this lab does not — budget-aware routing and
/// schema-validated structured completion — are weeks 3 and 8 topics.
/// </para>
/// <para>
/// <b>Run it:</b>
/// <code>
/// dotnet run --project dotnet/ProviderBridge -- --selftest       # offline, no key, proves the mechanisms
/// dotnet run --project dotnet/ProviderBridge -- --mock           # offline demo with scripted responses
/// dotnet run --project dotnet/ProviderBridge -- --stream --prompt "Explain SSE in one sentence"
/// </code>
/// A live run needs <c>BRIDGE_API_KEY</c> (or <c>OPENAI_API_KEY</c> / <c>DEEPSEEK_API_KEY</c>).
/// </para>
/// </summary>
internal static class Program
{
    private static async Task<int> Main(string[] args)
    {
        var options = CliOptions.Parse(args);

        if (options.ShowHelp)
        {
            CliOptions.PrintUsage();
            return 0;
        }

        if (options.SelfTest)
        {
            return await SelfTest.RunAsync().ConfigureAwait(false);
        }

        if (options.Mock)
        {
            return await RunMockAsync(options).ConfigureAwait(false);
        }

        BridgeSettings settings;
        try
        {
            settings = BridgeSettings.FromEnvironment();
        }
        catch (BridgeConfigurationException ex)
        {
            ConsoleUi.Bad(ex.Message);
            ConsoleUi.Info("Falling back to --mock so the lab still runs offline.");
            return await RunMockAsync(options).ConfigureAwait(false);
        }

        return await RunLiveAsync(settings, options).ConfigureAwait(false);
    }

    // ── Mock mode ────────────────────────────────────────────────────────────────────────────
    // A scripted transport replaces the network. The script deliberately includes one 429 so the
    // retry path is visible without needing a provider to misbehave on cue.
    private static async Task<int> RunMockAsync(CliOptions options)
    {
        ConsoleUi.Title("ProviderBridge — offline mock mode");
        ConsoleUi.Dim("No network is used. Responses come from ScriptedHttpMessageHandler.");
        Console.WriteLine();

        var settings = BridgeSettings.ForOfflineFake();
        var retry = new RetryPolicy(maxAttempts: 3, baseDelay: TimeSpan.FromMilliseconds(40));
        var handler = new ScriptedHttpMessageHandler();
        handler.EnqueueStatus(
            System.Net.HttpStatusCode.TooManyRequests,
            """{"error":{"message":"rate limited","code":"rate_limit_exceeded"}}""");
        if (options.Stream)
        {
            handler.EnqueueSse(MockSseStream());
        }
        else
        {
            handler.EnqueueJson(MockCompletionJson());
        }

        using var client = new ChatCompletionsClient(settings, handler, retry);
        ConsoleUi.Section($"endpoint: {settings.DescribeSafe()}");
        ConsoleUi.Info("first response is a scripted 429; the second succeeds");
        Console.WriteLine();

        return options.Stream
            ? await RunStreamingAsync(client, settings, options).ConfigureAwait(false)
            : await RunCompletionAsync(client, settings, options).ConfigureAwait(false);
    }

    // ── Live mode ────────────────────────────────────────────────────────────────────────────
    private static async Task<int> RunLiveAsync(BridgeSettings settings, CliOptions options)
    {
        ConsoleUi.Title("ProviderBridge — live run");
        ConsoleUi.Section($"endpoint: {settings.DescribeSafe()}");
        if (settings.ApiKey.Length <= 8)
        {
            ConsoleUi.Warn("The API key is very short; check that the environment variable holds the full key.");
        }

        using var client = new ChatCompletionsClient(settings);
        return options.Stream
            ? await RunStreamingAsync(client, settings, options).ConfigureAwait(false)
            : await RunCompletionAsync(client, settings, options).ConfigureAwait(false);
    }

    private static async Task<int> RunCompletionAsync(
        ChatCompletionsClient client,
        BridgeSettings settings,
        CliOptions options)
    {
        var messages = new List<ChatMessage>
        {
            ChatMessage.System("You are a concise engineering assistant. Answer in at most three sentences."),
            ChatMessage.User(options.Prompt),
        };

        ConsoleUi.Section("request");
        ConsoleUi.Info($"model   : {settings.Model}");
        ConsoleUi.Info($"messages: {messages.Count} (system + user)");
        ConsoleUi.Dim($"prompt  : {Truncate(options.Prompt, 100)}");
        Console.WriteLine();

        var stopwatch = Stopwatch.StartNew();
        try
        {
            var response = await client
                .CompleteAsync(messages, options.Temperature, options.MaxTokens)
                .ConfigureAwait(false);
            stopwatch.Stop();

            ConsoleUi.Section("response");
            Console.WriteLine(ConsoleUi.Wrap(response.FirstText()));
            Console.WriteLine();
            ConsoleUi.Info($"finish_reason: {response.FinishReason() ?? "(none)"}");
            PrintUsageAndCost(settings, response.Usage, stopwatch.ElapsedMilliseconds);
            PrintRetries(client);
            return 0;
        }
        catch (ChatCompletionException ex)
        {
            stopwatch.Stop();
            ConsoleUi.Bad(ex.Message);
            ConsoleUi.Info($"transient: {ex.IsTransient}; providerCode: {ex.ProviderCode ?? "(none)"}");
            PrintRetries(client);
            return 2;
        }
    }

    private static async Task<int> RunStreamingAsync(
        ChatCompletionsClient client,
        BridgeSettings settings,
        CliOptions options)
    {
        var messages = new List<ChatMessage>
        {
            ChatMessage.System("You are a concise engineering assistant. Answer in at most three sentences."),
            ChatMessage.User(options.Prompt),
        };

        ConsoleUi.Section("streaming request");
        ConsoleUi.Info($"model: {settings.Model}; SSE parsing enabled");
        Console.WriteLine();

        var stopwatch = Stopwatch.StartNew();
        long firstTokenMs = -1;
        var text = new StringBuilder();

        try
        {
            await foreach (var delta in client.StreamAsync(messages, options.Temperature, options.MaxTokens))
            {
                if (firstTokenMs < 0)
                {
                    firstTokenMs = stopwatch.ElapsedMilliseconds;
                }

                text.Append(delta);
                Console.Write(delta); // deltas are printed as they arrive — this is the point of streaming
            }

            stopwatch.Stop();
            Console.WriteLine();
            Console.WriteLine();

            ConsoleUi.Section("stream summary");
            ConsoleUi.Info($"time to first token: {firstTokenMs} ms");
            ConsoleUi.Info($"total time         : {stopwatch.ElapsedMilliseconds} ms");
            ConsoleUi.Info($"finish_reason      : {client.LastFinishReason ?? "(none)"}");
            ConsoleUi.Info($"characters         : {text.Length}");
            PrintUsageAndCost(settings, client.LastStreamUsage, stopwatch.ElapsedMilliseconds);
            if (client.StreamUsageMissing)
            {
                ConsoleUi.Warn("The provider did not report usage for the stream; cost cannot be measured exactly.");
            }

            PrintRetries(client);
            return 0;
        }
        catch (ChatCompletionException ex)
        {
            stopwatch.Stop();
            Console.WriteLine();
            ConsoleUi.Bad(ex.Message);
            ConsoleUi.Info($"transient: {ex.IsTransient}; providerCode: {ex.ProviderCode ?? "(none)"}");
            PrintRetries(client);
            return 2;
        }
    }

    private static void PrintUsageAndCost(BridgeSettings settings, TokenUsage? usage, long latencyMs)
    {
        if (usage is null)
        {
            ConsoleUi.Info($"latency: {latencyMs} ms; usage: (not reported)");
            return;
        }

        var cost = CostTable.Estimate(settings.Model, usage);
        ConsoleUi.Info(
            $"tokens: prompt={usage.PromptTokens} completion={usage.CompletionTokens} total={usage.TotalTokens}");
        ConsoleUi.Info($"latency: {latencyMs} ms; estimated cost: {CostTable.Format(cost)}");

        if (settings.MaxCostUsd is { } cap && cost > cap)
        {
            ConsoleUi.Warn($"cost {CostTable.Format(cost)} exceeds the configured cap {CostTable.Format(cap)}.");
        }
    }

    private static void PrintRetries(ChatCompletionsClient client)
    {
        if (client.RetryAttempts.Count <= 1)
        {
            ConsoleUi.Dim("attempts: 1 (no retry)");
            return;
        }

        ConsoleUi.Section("retry timeline");
        foreach (var attempt in client.RetryAttempts)
        {
            var status = attempt.StatusCode is { } code ? ((int)code).ToString() : "(transport)";
            ConsoleUi.Info(
                $"attempt {attempt.Attempt}: status={status} -> {attempt.Outcome}, backoff={attempt.Delay.TotalMilliseconds:0} ms");
        }
    }

    // ── Scripted responses ───────────────────────────────────────────────────────────────────

    private static string MockCompletionJson() => """
    {
      "id": "chatcmpl-mock-1",
      "model": "mock-model",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Streaming is a response shape, not a feature: the server flushes tokens as SSE frames so the client can render before the answer is complete."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": { "prompt_tokens": 38, "completion_tokens": 27, "total_tokens": 65 }
    }
    """;

    /// <summary>
    /// Builds a realistic SSE body. Note the final usage-only chunk: OpenAI-compatible providers
    /// send usage after the last text delta, which is why a streaming client cannot report cost
    /// until the stream ends.
    /// </summary>
    private static string MockSseStream()
    {
        var pieces = new[]
        {
            "Streaming ",
            "is a ",
            "response ",
            "shape, ",
            "not a ",
            "feature: ",
            "the server ",
            "flushes ",
            "tokens ",
            "as they are produced.",
        };

        var builder = new StringBuilder();
        builder.Append(
            "data: {\"id\":\"chatcmpl-mock-stream\",\"model\":\"mock-model\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\"}}]}\n\n");
        foreach (var piece in pieces)
        {
            builder.Append("data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":")
                .Append(System.Text.Json.JsonSerializer.Serialize(piece))
                .Append("}}]}\n\n");
        }

        builder.Append("data: {\"choices\":[{\"index\":0,\"delta\":{},\"finish_reason\":\"stop\"}]}\n\n");
        builder.Append(
            "data: {\"choices\":[],\"usage\":{\"prompt_tokens\":42,\"completion_tokens\":18,\"total_tokens\":60}}\n\n");
        builder.Append("data: [DONE]\n\n");
        return builder.ToString();
    }

    private static string Truncate(string value, int max) =>
        value.Length <= max ? value : value[..max] + "…";
}

/// <summary>
/// Parsed command-line options. Hand-rolled rather than pulled from a package: the lab must build
/// with no external NuGet, and a 40-line parser is easier to read than a dependency.
/// </summary>
internal sealed record CliOptions
{
    public bool Stream { get; init; }

    public bool Mock { get; init; }

    public bool SelfTest { get; init; }

    public bool ShowHelp { get; init; }

    public string Prompt { get; init; } =
        "In one sentence, why does streaming exist?";

    public double? Temperature { get; init; }

    public int? MaxTokens { get; init; }

    public static CliOptions Parse(string[] args)
    {
        var options = new CliOptions();
        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--stream":
                    options = options with { Stream = true };
                    break;
                case "--mock":
                    options = options with { Mock = true };
                    break;
                case "--selftest":
                    options = options with { SelfTest = true };
                    break;
                case "--help" or "-h" or "/?":
                    options = options with { ShowHelp = true };
                    break;
                case "--prompt":
                    if (i + 1 < args.Length)
                    {
                        options = options with { Prompt = args[++i] };
                    }

                    break;
                case "--temperature":
                    if (i + 1 < args.Length && double.TryParse(args[++i], out var temperature))
                    {
                        options = options with { Temperature = temperature };
                    }

                    break;
                case "--max-tokens":
                    if (i + 1 < args.Length && int.TryParse(args[++i], out var maxTokens))
                    {
                        options = options with { MaxTokens = maxTokens };
                    }

                    break;
                default:
                    ConsoleUi.Warn($"Unknown argument '{args[i]}' ignored (see --help).");
                    break;
            }
        }

        return options;
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        ProviderBridge — raw chat-completions, SSE streaming, retry/backoff.

        Usage:
          dotnet run --project dotnet/ProviderBridge -- [options]

        Options:
          --selftest          Run the offline mechanism checks (no key, no network). Exit code 0 = pass.
          --mock              Use scripted responses (no key, no network).
          --stream            Stream the response over SSE instead of one JSON body.
          --prompt <text>     User message (default: a one-line question).
          --temperature <n>   Sampling temperature.
          --max-tokens <n>    Output token ceiling.
          --help              Print this help.

        Environment (live mode only):
          BRIDGE_API_KEY      Bearer key. Fallbacks: OPENAI_API_KEY, DEEPSEEK_API_KEY.
          BRIDGE_BASE_URL     Default https://api.deepseek.com/v1
          BRIDGE_MODEL        Default deepseek-chat
          BRIDGE_MAX_COST_USD Default 0.50 (a warning is printed above this)
          BRIDGE_TIMEOUT_SECONDS  Default 120
          NO_COLOR=1          Disable ANSI colour.
        """);
    }
}
