namespace Bridge.Shared.Decisions;

/// <summary>
/// The presentation budgets that keep a typed decision readable.
///
/// <para>
/// These are not style preferences: they are the difference between a decision a person can act
/// on and a wall of text that looks like an answer. SendOS encodes the same numbers in
/// <c>apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Decision/PresentationBudget.cs</c>
/// and enforces them with <c>PresentationBudgetEnforcer</c>; the values here are the ones its
/// comments document (headline ≤ 12 words, meaning ≤ 2 sentences, consequence ≤ 1 sentence,
/// ≤ 4 next moves, one question ≤ 3 options).
/// </para>
/// <para>
/// Budgeting at the boundary (rather than hoping the prompt obeyed) is what makes the guarantee
/// testable: a validator over typed fields needs no model call and no network.
/// </para>
/// </summary>
public sealed record PresentationBudget
{
    /// <summary>Default budgets, matching the SendOS contract.</summary>
    public static PresentationBudget Default { get; } = new();

    public int MaxHeadlineWords { get; init; } = 12;

    public int MaxMeaningSentences { get; init; } = 2;

    public int MaxConsequenceSentences { get; init; } = 1;

    public int MaxRecommendationSentences { get; init; } = 1;

    public int MaxNextMoves { get; init; } = 4;

    public int MaxClarificationOptions { get; init; } = 3;

    public int MinClarificationOptions { get; init; } = 1;
}
