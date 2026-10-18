namespace Bridge.Shared.Providers;

/// <summary>
/// A token-count estimate used only where a provider did not report usage.
///
/// <para>
/// <b>Be precise about what this is:</b> a heuristic, not a measurement. The common English rule
/// of thumb is ~4 characters per token; it is wrong for code, non-English text and JSON, and it
/// is wrong in a direction that matters (it underestimates structured output). Anything that
/// makes a spend decision from an estimate is guessing; anything that reports "estimated" and
/// labels it is honest.
/// </para>
/// <para>
/// SendOS does the same thing in <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/
/// Handlers/CompletionHandler.cs</c> (<c>EstimatePromptTokens</c>) for pre-flight budget checks,
/// and deliberately never substitutes the estimate for the provider's reported usage.
/// </para>
/// </summary>
public static class TokenEstimator
{
    /// <summary>Rough tokens for a string (~4 chars/token, rounded up).</summary>
    public static int Estimate(string? text) =>
        string.IsNullOrEmpty(text) ? 0 : (text.Length + 3) / 4;

    /// <summary>Rough prompt tokens across messages (content only; role/overhead ignored).</summary>
    public static int Estimate(IEnumerable<ChatMessage> messages) =>
        messages.Sum(message => Estimate(message.Content));
}
