using Bridge.Shared.Configuration;
using Bridge.Shared.Decisions;
using Bridge.Shared.Providers;

namespace StructuredDecisionBridge;

/// <summary>
/// The seam the repair loop talks to: "given messages, return raw model text".
///
/// <para>
/// It returns <b>text</b>, not a decision, on purpose. The whole week-3 lesson is that the model
/// does not produce your type — it produces bytes that must pass a gate before becoming your
/// type. A provider interface that returned <c>DecisionInteraction</c> would hide the gate that
/// is the point of the lab.
/// </para>
/// <para>
/// Two implementations: <see cref="MockDecisionProvider"/> (scripted, offline, deterministic) and
/// <see cref="LiveDecisionProvider"/> (a real provider via the week-1 client). The repair loop
/// cannot tell them apart, which is exactly why it can be tested without a key.
/// </para>
/// </summary>
public interface IDecisionProvider
{
    /// <summary>Short human-readable description for the console.</summary>
    string Name { get; }

    /// <summary>Returns raw model text for the conversation. Never validates; the parser does that.</summary>
    Task<string> CompleteAsync(IReadOnlyList<ChatMessage> messages, CancellationToken cancellationToken = default);

    /// <summary>Provider-reported usage for the last call, when available.</summary>
    TokenUsage? LastUsage { get; }
}

/// <summary>
/// A scripted provider: returns canned responses in order, then repeats the last one.
///
/// <para>
/// The default script walks the exact failure sequence a real model produces when first asked for
/// a decision: it answers with a chart (an artifact the family cannot represent), then a
/// structurally broken decision, then a decision that is structurally fine but over the
/// presentation budgets, and only then a valid decision. Watching the repair loop converge over
/// those four stages is more instructive than a single success.
/// </para>
/// </summary>
public sealed class MockDecisionProvider : IDecisionProvider
{
    private readonly Queue<string> _script;
    private int _calls;

    public MockDecisionProvider(IEnumerable<string>? script = null)
    {
        _script = new Queue<string>(script ?? DefaultScript());
    }

    public string Name => "mock (scripted responses)";

    public int Calls => _calls;

    public TokenUsage? LastUsage => null; // scripted responses have no real usage

    public Task<string> CompleteAsync(
        IReadOnlyList<ChatMessage> messages,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        _calls++;

        var response = _script.Count > 1 ? _script.Dequeue() : _script.Peek();
        return Task.FromResult(response);
    }

    /// <summary>The default four-stage failure sequence. Kept as data so tests can reuse or extend it.</summary>
    public static IEnumerable<string> DefaultScript() =>
    [
        DecisionSamples.ExcludedArtifact,
        DecisionSamples.SchemaBroken,
        DecisionSamples.BudgetBroken,
        DecisionSamples.ValidDecisionState,
    ];
}

/// <summary>
/// A real provider behind the week-1 client, asking for JSON output.
///
/// <para>
/// <c>jsonMode: true</c> is a request, not a guarantee: on hosts that support it the model is
/// nudged to emit syntactically valid JSON; on hosts that do not, the flag may be ignored. Either
/// way the reply still has to pass the parser — which is why the labs never trust the flag.
/// </para>
/// </summary>
public sealed class LiveDecisionProvider : IDecisionProvider, IDisposable
{
    private readonly ChatCompletionsClient _client;

    public LiveDecisionProvider(BridgeSettings settings, ChatCompletionsClient? client = null)
    {
        _client = client ?? new ChatCompletionsClient(settings);
        Settings = settings;
    }

    public BridgeSettings Settings { get; }

    public string Name => $"live ({Settings.Model} @ {Settings.BaseUri.Host})";

    public TokenUsage? LastUsage { get; private set; }

    public async Task<string> CompleteAsync(
        IReadOnlyList<ChatMessage> messages,
        CancellationToken cancellationToken = default)
    {
        var response = await _client
            .CompleteAsync(messages, temperature: 0, jsonMode: true, cancellationToken: cancellationToken)
            .ConfigureAwait(false);
        LastUsage = response.Usage;
        return response.FirstText();
    }

    public void Dispose() => _client.Dispose();
}
