using System.Globalization;

namespace Bridge.Shared.Configuration;

/// <summary>
/// Everything the labs need to talk to an OpenAI-compatible chat-completions endpoint.
///
/// <para>
/// The point of this type is the <b>provider seam</b>: the rest of the lab never reads an
/// environment variable and never hard-codes a host. Swapping DeepSeek for OpenAI, a local
/// vLLM server, or a fake transport is a configuration change, not a code change.
/// </para>
/// <para>
/// Read order for learners: <see cref="FromEnvironment"/> (what is configurable and what
/// the defaults are) → <see cref="Bridge.Shared.Providers.ChatCompletionsClient"/> (the wire
/// call) → this repo's week-1 lab. SendOS equivalent: the provider registry and per-provider
/// adapters in <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Infrastructure/ExternalServices/</c>.
/// </para>
/// </summary>
public sealed record BridgeSettings
{
    /// <summary>Bearer credential for the provider. Never logged, never written to disk.</summary>
    public required string ApiKey { get; init; }

    /// <summary>Base URL including the API version segment, e.g. <c>https://api.deepseek.com/v1</c>.</summary>
    public required Uri BaseUri { get; init; }

    /// <summary>The model id sent on the wire.</summary>
    public required string Model { get; init; }

    /// <summary>Per-run spend ceiling used by the CLI to stop before spending more. Null = unconstrained.</summary>
    public decimal? MaxCostUsd { get; init; }

    /// <summary>Per-request timeout applied by the HTTP client.</summary>
    public TimeSpan Timeout { get; init; } = TimeSpan.FromSeconds(120);

    /// <summary>Environment variable names consulted, in order, for the API key.</summary>
    public static readonly string[] ApiKeyVariables =
    [
        "BRIDGE_API_KEY",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
    ];

    /// <summary>
    /// Builds settings from the environment.
    ///
    /// <para>
    /// Precedence and defaults are deliberate and documented rather than clever:
    /// <list type="bullet">
    ///   <item><c>BRIDGE_BASE_URL</c> — default <c>https://api.deepseek.com/v1</c> (cheapest
    ///   model for high-volume labs, per the repo plan).</item>
    ///   <item><c>BRIDGE_MODEL</c> — default <c>deepseek-chat</c>.</item>
    ///   <item><c>BRIDGE_MAX_COST_USD</c> — default <c>0.50</c>, matching the plan's per-run cap.</item>
    ///   <item>API key — the first non-empty of <see cref="ApiKeyVariables"/>.</item>
    /// </list>
    /// </para>
    /// </summary>
    /// <exception cref="BridgeConfigurationException">
    /// No API key was found. The message names every variable that was checked, so a learner
    /// does not have to guess which one to set.
    /// </exception>
    public static BridgeSettings FromEnvironment()
    {
        var apiKey = FirstNonEmpty(ApiKeyVariables)
                     ?? throw new BridgeConfigurationException(
                         "No API key found. Set BRIDGE_API_KEY (or OPENAI_API_KEY / DEEPSEEK_API_KEY) " +
                         "for a live run, or pass --mock / --selftest to stay offline.");

        var baseUrl = Get("BRIDGE_BASE_URL") ?? "https://api.deepseek.com/v1";
        var model = Get("BRIDGE_MODEL") ?? "deepseek-chat";
        var maxCost = Get("BRIDGE_MAX_COST_USD") is { } raw
                      && decimal.TryParse(raw, NumberStyles.Number, CultureInfo.InvariantCulture, out var parsed)
            ? parsed
            : 0.50m;
        var timeoutSeconds = Get("BRIDGE_TIMEOUT_SECONDS") is { } t
                             && int.TryParse(t, NumberStyles.Integer, CultureInfo.InvariantCulture, out var secs)
            ? secs
            : 120;

        return new BridgeSettings
        {
            ApiKey = apiKey,
            BaseUri = new Uri(baseUrl.TrimEnd('/') + "/"),
            Model = model,
            MaxCostUsd = maxCost,
            Timeout = TimeSpan.FromSeconds(timeoutSeconds),
        };
    }

    /// <summary>Settings used by <c>--mock</c> and <c>--selftest</c>: a fake key and host, never dialled.</summary>
    public static BridgeSettings ForOfflineFake(string model = "mock-model") => new()
    {
        ApiKey = "offline-not-a-real-key",
        BaseUri = new Uri("https://offline.invalid/v1/"),
        Model = model,
        MaxCostUsd = null,
        Timeout = TimeSpan.FromSeconds(5),
    };

    /// <summary>
    /// The chat-completions endpoint for <see cref="BaseUri"/>. Kept in one place because
    /// every provider-compatible host appends the same path and a duplicated string is how a
    /// base URL with a trailing slash becomes a 404.
    /// </summary>
    public Uri ChatCompletionsUri => new(BaseUri, "chat/completions");

    /// <summary>Reads an environment variable, trimming it, and treats whitespace-only as absent.</summary>
    public static string? Get(string name)
    {
        var value = Environment.GetEnvironmentVariable(name);
        return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
    }

    private static string? FirstNonEmpty(IEnumerable<string> names)
    {
        foreach (var name in names)
        {
            if (Get(name) is { } value)
            {
                return value;
            }
        }

        return null;
    }

    /// <summary>Redacts the key so a debug print of settings is safe to paste into a chat.</summary>
    public string DescribeSafe() =>
        $"model={Model} base={BaseUri} key={Mask(ApiKey)} timeout={Timeout.TotalSeconds:0}s " +
        $"maxCostUsd={(MaxCostUsd?.ToString(CultureInfo.InvariantCulture) ?? "unbounded")}";

    private static string Mask(string secret) =>
        secret.Length <= 8 ? "***" : $"{secret[..4]}…{secret[^4..]}";
}

/// <summary>Raised when the environment cannot produce usable settings. Carries a fix, not just a symptom.</summary>
public sealed class BridgeConfigurationException(string message) : Exception(message);
