using System.Net;
using System.Text;
using System.Text.Json;
using Bridge.Shared.Configuration;
using Bridge.Shared.Json;

namespace Bridge.Shared.Providers;

/// <summary>
/// A deliberately small chat-completions client: one class, one wire protocol, no framework.
///
/// <para>
/// <b>What it teaches by being small:</b>
/// </para>
/// <list type="number">
///   <item><description>
///   The <b>provider seam</b> is a single method taking messages and returning a typed response.
///   Swapping providers is a base URL and model id, which is exactly the seam SendOS puts in
///   <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Interfaces/IProviderAdapter.cs</c>.
///   </description></item>
///   <item><description>
///   <b>Streaming is a different response shape</b>, not a flag on a callback: the body is
///   <c>text/event-stream</c> and must be parsed incrementally, with usage arriving in the final
///   chunk only when requested.
///   </description></item>
///   <item><description>
///   <b>Errors are data.</b> A provider error returns a status code and a body worth reading;
///   turning it into a bare exception at the transport layer destroys the detail a retry or a
///   user message needs.
///   </description></item>
/// </list>
/// <para>
/// SendOS equivalent: <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Infrastructure/ExternalServices/
/// {OpenAiProviderAdapter,AnthropicProviderAdapter,BedrockProviderAdapter}.cs</c> — same
/// responsibilities (payload build, response parse, usage capture), plus budget routing and
/// schema-validated structured completion which are deliberately out of scope for week 1.
/// </para>
/// </summary>
public sealed class ChatCompletionsClient : IDisposable
{
    private readonly HttpClient _http;
    private readonly BridgeSettings _settings;
    private readonly RetryHandler _retry;

    /// <summary>
    /// Creates a client.
    /// </summary>
    /// <param name="settings">Endpoint, key and model. Never logged by this type.</param>
    /// <param name="handler">
    /// Optional transport override. The labs pass a scripted handler for offline runs
    /// (<see cref="Testing.ScriptedHttpMessageHandler"/>) — the same trick that lets SendOS
    /// test provider adapters without network.
    /// </param>
    /// <param name="retry">Retry policy; defaults to three attempts with jittered backoff.</param>
    public ChatCompletionsClient(
        BridgeSettings settings,
        HttpMessageHandler? handler = null,
        RetryPolicy? retry = null)
    {
        ArgumentNullException.ThrowIfNull(settings);
        _settings = settings;

        var pipeline = new RetryHandler(retry ?? RetryPolicy.Default, handler ?? new HttpClientHandler());
        _retry = pipeline;
        _http = new HttpClient(pipeline, disposeHandler: true)
        {
            Timeout = settings.Timeout,
        };
        _http.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", settings.ApiKey);
        _http.DefaultRequestHeaders.Accept.Add(
            new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));
    }

    /// <summary>Settings in use, with the key redacted.</summary>
    public string Describe() => _settings.DescribeSafe();

    /// <summary>Retries performed by the transport, exposed so a lab can print what happened.</summary>
    public IReadOnlyList<RetryAttempt> RetryAttempts => _retry.Attempts;

    /// <summary>
    /// Runs a non-streamed completion and returns the typed response.
    /// </summary>
    /// <exception cref="ChatCompletionException">
    /// The provider returned a non-success status. The exception carries status, body and a
    /// transient classification so a caller can decide whether retrying is meaningful.
    /// </exception>
    public async Task<ChatCompletionResponse> CompleteAsync(
        IReadOnlyList<ChatMessage> messages,
        double? temperature = null,
        int? maxTokens = null,
        bool jsonMode = false,
        CancellationToken cancellationToken = default)
    {
        var body = new ChatCompletionRequest
        {
            Model = _settings.Model,
            Messages = messages,
            Temperature = temperature,
            MaxTokens = maxTokens,
            ResponseFormat = jsonMode ? ResponseFormat.JsonObject : null,
        };

        using var request = new HttpRequestMessage(HttpMethod.Post, _settings.ChatCompletionsUri)
        {
            Content = JsonContent(body),
        };

        using var response = await _http
            .SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cancellationToken)
            .ConfigureAwait(false);

        var text = await response.Content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false);
        if (!response.IsSuccessStatusCode)
        {
            throw ChatCompletionException.FromResponse(response.StatusCode, text);
        }

        return JsonSerializer.Deserialize<ChatCompletionResponse>(text, BridgeJson.Options)
               ?? throw new ChatCompletionException(
                   response.StatusCode,
                   "The provider returned an empty JSON body where a completion was expected.",
                   isTransient: false,
                   providerCode: null);
    }

    /// <summary>
    /// Streams a completion, yielding text deltas as they arrive.
    ///
    /// <para>
    /// The final usage is exposed on <see cref="LastStreamUsage"/> after enumeration completes
    /// (only when the provider honoured <c>stream_options.include_usage</c>). This mirrors the
    /// real trade-off: streaming gives lower time-to-first-token but complicates accounting,
    /// because usage arrives after the last visible token.
    /// </para>
    /// </summary>
    public async IAsyncEnumerable<string> StreamAsync(
        IReadOnlyList<ChatMessage> messages,
        double? temperature = null,
        int? maxTokens = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        LastStreamUsage = null;
        LastFinishReason = null;

        var body = new ChatCompletionRequest
        {
            Model = _settings.Model,
            Messages = messages,
            Stream = true,
            Temperature = temperature,
            MaxTokens = maxTokens,
            StreamOptions = new StreamOptions { IncludeUsage = true },
        };

        using var request = new HttpRequestMessage(HttpMethod.Post, _settings.ChatCompletionsUri)
        {
            Content = JsonContent(body),
        };

        using var response = await _http
            .SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cancellationToken)
            .ConfigureAwait(false);

        if (!response.IsSuccessStatusCode)
        {
            var errorBody = await response.Content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false);
            throw ChatCompletionException.FromResponse(response.StatusCode, errorBody);
        }

        var contentType = response.Content.Headers.ContentType?.MediaType ?? "(none)";
        if (!string.Equals(contentType, "text/event-stream", StringComparison.OrdinalIgnoreCase))
        {
            // Some compatible hosts ignore stream:true and return JSON. Surface that as an
            // explicit error rather than silently parsing zero events and printing nothing.
            var fallback = await response.Content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false);
            throw new ChatCompletionException(
                response.StatusCode,
                $"Expected text/event-stream but the provider returned '{contentType}'. Body: {Truncate(fallback, 400)}",
                isTransient: false,
                providerCode: "not-a-stream");
        }

        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken).ConfigureAwait(false);
        using var reader = new StreamReader(stream, Encoding.UTF8);
        var parser = new SseParser();
        var buffer = new char[4096];

        while (true)
        {
            var read = await reader.ReadAsync(buffer.AsMemory(), cancellationToken).ConfigureAwait(false);
            if (read == 0)
            {
                break;
            }

            // Feed the whole chunk; the parser keeps the remainder of a partial frame.
            foreach (var sse in parser.Feed(new string(buffer, 0, read)))
            {
                foreach (var delta in HandleSseEvent(sse))
                {
                    yield return delta;
                }
            }
        }

        foreach (var sse in parser.Flush())
        {
            foreach (var delta in HandleSseEvent(sse))
            {
                yield return delta;
            }
        }

        if (LastStreamUsage is null)
        {
            // Documented, not an error: include_usage is a request, not a guarantee.
            StreamUsageMissing = true;
        }
    }

    /// <summary>Usage reported by the stream, or null when the provider sent none.</summary>
    public TokenUsage? LastStreamUsage { get; private set; }

    /// <summary>Finish reason reported by the stream, e.g. <c>stop</c> or <c>length</c>.</summary>
    public string? LastFinishReason { get; private set; }

    /// <summary>True when the stream finished without reporting usage (cost becomes an estimate).</summary>
    public bool StreamUsageMissing { get; private set; }

    private IEnumerable<string> HandleSseEvent(SseEvent sse)
    {
        if (sse.Data == "[DONE]")
        {
            yield break;
        }

        if (string.IsNullOrWhiteSpace(sse.Data))
        {
            yield break;
        }

        ChatCompletionChunk? chunk;
        try
        {
            chunk = JsonSerializer.Deserialize<ChatCompletionChunk>(sse.Data, BridgeJson.Options);
        }
        catch (JsonException ex)
        {
            // A malformed frame is data corruption; it must be visible, not swallowed into a
            // truncated answer. The choice here is to fail loudly (a lab) — production clients
            // usually count and skip, which is a policy decision worth noticing.
            throw new ChatCompletionException(
                HttpStatusCode.OK,
                $"Stream frame was not valid JSON ({ex.Message}). Frame: {Truncate(sse.Data, 200)}",
                isTransient: true,
                providerCode: "bad-frame");
        }

        if (chunk is null)
        {
            yield break;
        }

        if (chunk.Usage is { } usage)
        {
            LastStreamUsage = usage;
        }

        foreach (var choice in chunk.Choices)
        {
            if (choice.FinishReason is { } finish)
            {
                LastFinishReason = finish;
            }

            var content = choice.Delta?.Content;
            if (!string.IsNullOrEmpty(content))
            {
                yield return content;
            }
        }
    }

    private static StringContent JsonContent<T>(T value) =>
        new(JsonSerializer.Serialize(value, BridgeJson.Options), Encoding.UTF8, "application/json");

    private static string Truncate(string value, int max) =>
        value.Length <= max ? value : value[..max] + "…";

    public void Dispose() => _http.Dispose();
}

/// <summary>
/// A provider error worth reading.
///
/// <para>
/// The <see cref="IsTransient"/> flag is the single most useful field: it is what a caller
/// switches on to decide "retry" versus "fix the request". Deriving it from the status code
/// here means every call site does not need its own list.
/// </para>
/// </summary>
public sealed class ChatCompletionException : Exception
{
    public ChatCompletionException(
        HttpStatusCode status,
        string message,
        bool isTransient,
        string? providerCode)
        : base(message)
    {
        Status = status;
        IsTransient = isTransient;
        ProviderCode = providerCode;
    }

    public HttpStatusCode Status { get; }

    public bool IsTransient { get; }

    /// <summary>The provider's own error code when one could be read (e.g. <c>rate_limit_exceeded</c>).</summary>
    public string? ProviderCode { get; }

    /// <summary>
    /// Builds an exception from a status and body, extracting the provider's error envelope when
    /// the body uses the common <c>{"error":{"message":…,"code":…}}</c> shape.
    /// </summary>
    public static ChatCompletionException FromResponse(HttpStatusCode status, string body)
    {
        var (message, code) = TryReadError(body);
        var transient = status is
            HttpStatusCode.RequestTimeout or
            HttpStatusCode.TooManyRequests or
            HttpStatusCode.InternalServerError or
            HttpStatusCode.BadGateway or
            HttpStatusCode.ServiceUnavailable or
            HttpStatusCode.GatewayTimeout;

        return new ChatCompletionException(
            status,
            $"HTTP {(int)status} {status}: {message ?? Truncate(body, 500)}",
            transient,
            code);
    }

    private static (string? Message, string? Code) TryReadError(string body)
    {
        try
        {
            using var document = JsonDocument.Parse(body);
            if (document.RootElement.ValueKind == JsonValueKind.Object
                && document.RootElement.TryGetProperty("error", out var error))
            {
                var message = error.TryGetProperty("message", out var m) ? m.GetString() : null;
                var code = error.TryGetProperty("code", out var c) ? c.GetString() : null;
                return (message, code);
            }
        }
        catch (JsonException)
        {
            // Body is not JSON; the caller falls back to a truncated raw body.
        }

        return (null, null);
    }

    private static string Truncate(string value, int max) =>
        value.Length <= max ? value : value[..max] + "…";
}
