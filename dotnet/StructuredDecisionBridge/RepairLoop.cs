using System.Diagnostics;
using Bridge.Shared.Decisions;
using Bridge.Shared.Providers;

namespace StructuredDecisionBridge;

/// <summary>
/// One attempt to obtain a valid decision, with what it cost to find out it was not.
/// </summary>
/// <param name="Number">1-based attempt number (1 = first call, 2+ = repairs).</param>
/// <param name="Result">The parse outcome; on success this is the only attempt with a decision.</param>
/// <param name="Raw">The raw model text, kept for the audit trail and for showing the failure.</param>
/// <param name="PromptChars">Characters in the conversation when the call was made (cost signal).</param>
/// <param name="LatencyMs">Wall-clock time of the provider call.</param>
public sealed record RepairAttempt(
    int Number,
    ParseResult Result,
    string Raw,
    int PromptChars,
    long LatencyMs);

/// <summary>The outcome of a repair loop: a validated decision, or an honest failure with its history.</summary>
public sealed record RepairOutcome(
    bool Success,
    DecisionInteraction? Decision,
    IReadOnlyList<RepairAttempt> Attempts,
    PresentationBudget Budget)
{
    /// <summary>Repairs performed after the first attempt.</summary>
    public int RepairsUsed => Math.Max(0, Attempts.Count - 1);

    /// <summary>
    /// Estimated cost of the whole loop, in USD, from character counts.
    /// <para>
    /// Explicitly an estimate: real usage is only available on the live path, and the repair
    /// loop's prompt grows with every failure — which is the economic fact the lab wants visible.
    /// </para>
    /// </summary>
    public decimal EstimatedCostUsd(string model)
    {
        var promptTokens = Attempts.Sum(a => (a.PromptChars + 3) / 4);
        var completionTokens = Attempts.Sum(a => (a.Raw.Length + 3) / 4);
        return CostTable.Estimate(model, new TokenUsage
        {
            PromptTokens = promptTokens,
            CompletionTokens = completionTokens,
            TotalTokens = promptTokens + completionTokens,
        });
    }

    /// <summary>Human-readable reason for the terminal failure, when there is one.</summary>
    public string? FailureSummary =>
        Success
            ? null
            : Attempts.Count == 0
                ? "no attempts were made"
                : $"gave up after {Attempts.Count} attempts; last rejection was at stage {Attempts[^1].Result.Issues[0].Stage}.";
}

/// <summary>
/// Bounded repair loop: call the model, parse, and on rejection feed the violations back once
/// more, up to a ceiling.
///
/// <para>
/// <b>Why bounded, and why feed errors back:</b> a schema failure is usually a prompt/model
/// mismatch that a single corrective message fixes — the model genuinely did not know the
/// contract. But repair has diminishing returns and rising cost (each attempt carries the whole
/// failing response plus the instruction, so the prompt grows), and an unbounded loop is a money
/// fire. Three repairs is a common production ceiling; the lab makes the ceiling configurable so
/// you can measure the difference.
/// </para>
/// <para>
/// <b>Why the loop never returns a partial decision:</b> the contract with the caller is "a
/// validated decision or nothing". Returning the best-effort object would move the failure
/// downstream, where it becomes a wrong action instead of a visible error. SendOS makes the
/// identical choice in <c>StructuredCompletionHandler</c> (<c>StructuredOutput = null</c> on any
/// failure) and in the runtime's <c>Limitation</c> response type: an honest "I could not do this"
/// is a first-class outcome.
/// </para>
/// </summary>
public static class RepairLoop
{
    public const int DefaultMaxRepairs = 3;
    public const int MaxRepairCeiling = 5;

    /// <summary>
    /// Runs the loop.
    /// </summary>
    /// <param name="provider">The model seam. Mocked in tests, live in the demo.</param>
    /// <param name="goal">The business goal in natural language.</param>
    /// <param name="maxRepairs">Repair attempts after the first call (0..5).</param>
    /// <param name="budget">Presentation budgets; defaults to <see cref="PresentationBudget.Default"/>.</param>
    /// <param name="onAttempt">Optional observer so a CLI can print progress as it happens.</param>
    public static async Task<RepairOutcome> RunAsync(
        IDecisionProvider provider,
        string goal,
        int maxRepairs = DefaultMaxRepairs,
        PresentationBudget? budget = null,
        Action<RepairAttempt>? onAttempt = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(goal);
        maxRepairs = Math.Clamp(maxRepairs, 0, MaxRepairCeiling);
        var effectiveBudget = budget ?? PresentationBudget.Default;

        var messages = new List<ChatMessage>
        {
            ChatMessage.System(DecisionPrompts.System),
            ChatMessage.User(DecisionPrompts.UserGoal(goal)),
        };

        var attempts = new List<RepairAttempt>();
        var promptChars = messages.Sum(m => m.Content.Length);

        for (var attempt = 1; attempt <= 1 + maxRepairs; attempt++)
        {
            var stopwatch = Stopwatch.StartNew();
            var raw = await provider
                .CompleteAsync(messages, cancellationToken)
                .ConfigureAwait(false);
            stopwatch.Stop();

            var result = DecisionParser.Parse(raw, effectiveBudget);
            var record = new RepairAttempt(attempt, result, raw, promptChars, stopwatch.ElapsedMilliseconds);
            attempts.Add(record);
            onAttempt?.Invoke(record);

            if (result.IsOk)
            {
                return new RepairOutcome(true, result.Decision, attempts, effectiveBudget);
            }

            // Repair message construction: show the model its own output, then the violations.
            // The previous assistant turn is included because a corrective instruction that says
            // "you did it wrong" without "what you said" makes the model re-invent a different
            // answer instead of editing this one.
            messages.Add(ChatMessage.Assistant(raw));
            messages.Add(ChatMessage.User(result.ToRepairInstruction()));

            // Prompt characters grow with each repair; this is the cost curve the console prints.
            promptChars = messages.Sum(m => m.Content.Length);
        }

        return new RepairOutcome(false, null, attempts, effectiveBudget);
    }
}
