using System.Text.Json.Serialization;

namespace Bridge.Shared.Decisions;

/// <summary>
/// The closed family of decision responses — the C# bridge's mirror of SendOS's
/// <c>apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs</c>.
///
/// <para>
/// <b>Why a closed family instead of free text:</b> a paragraph cannot be governed. A typed
/// decision can be validated (does a clarification carry exactly one question?), budgeted
/// (is the headline under 12 words?), approved (does an action proposal name the action?),
/// traced (does it carry a trace reference?) and rendered by a surface that knows the shape
/// it is drawing. Free text supports none of that without re-parsing prose, which is the
/// failure mode this family removes.
/// </para>
/// <para>
/// <b>What is deliberately absent:</b> SendOS excludes <c>Chart</c>, <c>Dashboard</c>,
/// <c>VisualisationSpec</c>, <c>ReportCanvas</c> and <c>AnalyticsWorkspace</c> from its family
/// so a chart request <i>cannot</i> be represented and must be elevated to a decision. In this
/// bridge the exclusion is the same technique at a smaller scale: the union has no subtype for
/// those artifacts, so no code path can produce one.
/// </para>
/// <para>
/// <b>Wire shape:</b> a discriminated union encoded with a <c>responseType</c> string
/// discriminator. System.Text.Json polymorphism writes it first and binds it on read; the
/// validator then checks the fields the type system cannot (counts, lengths, presence).
/// </para>
/// </summary>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "responseType")]
[JsonDerivedType(typeof(ClarificationPrompt), "clarificationPrompt")]
[JsonDerivedType(typeof(DirectAnswer), "directAnswer")]
[JsonDerivedType(typeof(DecisionState), "decisionState")]
[JsonDerivedType(typeof(AnalysisConclusion), "analysisConclusion")]
[JsonDerivedType(typeof(DecisionRecommendation), "decisionRecommendation")]
[JsonDerivedType(typeof(ActionProposal), "actionProposal")]
[JsonDerivedType(typeof(Limitation), "limitation")]
public abstract record DecisionInteraction
{
    /// <summary>Stable id for this interaction. Required: the audit trail joins on it.</summary>
    public string InteractionId { get; init; } = string.Empty;

    /// <summary>One-line answer. Budgeted to ≤ 12 words by <see cref="PresentationBudget"/>.</summary>
    public string Headline { get; init; } = string.Empty;

    /// <summary>What the person can do next. Empty is legal; more than four is not.</summary>
    public IReadOnlyList<NextMove> NextMoves { get; init; } = [];

    /// <summary>Correlation key into the append-only trace. Required.</summary>
    public string TraceReference { get; init; } = string.Empty;

    /// <summary>The discriminator as a typed value. Never serialised (the wire field carries it).</summary>
    [JsonIgnore]
    public abstract ResponseType Type { get; }
}

/// <summary>The closed discriminator set.</summary>
public enum ResponseType
{
    ClarificationPrompt,
    DirectAnswer,
    DecisionState,
    AnalysisConclusion,
    DecisionRecommendation,
    ActionProposal,
    Limitation,
}

/// <summary>A suggested follow-up. Identity and label only — the surface renders it, not the runtime.</summary>
public sealed record NextMove
{
    public string Id { get; init; } = string.Empty;

    public string Label { get; init; } = string.Empty;
}

/// <summary>
/// One focused question with at most three options, emitted when the goal is too ambiguous to act on.
/// <para>The alternative — guessing — is how an agent confidently answers a different question.</para>
/// </summary>
public sealed record ClarificationPrompt : DecisionInteraction
{
    public string Question { get; init; } = string.Empty;

    public IReadOnlyList<string> Options { get; init; } = [];

    public override ResponseType Type => ResponseType.ClarificationPrompt;
}

/// <summary>A factual answer to a request an authoritative read could answer.</summary>
public sealed record DirectAnswer : DecisionInteraction
{
    public string Answer { get; init; } = string.Empty;

    public override ResponseType Type => ResponseType.DirectAnswer;
}

/// <summary>What the current situation means, its consequence, and a compact evidence summary.</summary>
public sealed record DecisionState : DecisionInteraction
{
    /// <summary>≤ 2 sentences under <see cref="PresentationBudget.Default"/>.</summary>
    public string Meaning { get; init; } = string.Empty;

    /// <summary>≤ 1 sentence.</summary>
    public string Consequence { get; init; } = string.Empty;

    public string EvidenceSummary { get; init; } = string.Empty;

    public override ResponseType Type => ResponseType.DecisionState;
}

/// <summary>A concluded analysis: what the evidence means, with its evidence summary.</summary>
public sealed record AnalysisConclusion : DecisionInteraction
{
    public string Meaning { get; init; } = string.Empty;

    public string EvidenceSummary { get; init; } = string.Empty;

    public override ResponseType Type => ResponseType.AnalysisConclusion;
}

/// <summary>A recommendation with consequence, confidence and known uncertainty.</summary>
public sealed record DecisionRecommendation : DecisionInteraction
{
    public string Recommendation { get; init; } = string.Empty;

    public string Consequence { get; init; } = string.Empty;

    /// <summary>0..1. A recommendation without a confidence is an assertion, not advice.</summary>
    public double Confidence { get; init; }

    public string Uncertainty { get; init; } = string.Empty;

    public string EvidenceSummary { get; init; } = string.Empty;

    public override ResponseType Type => ResponseType.DecisionRecommendation;
}

/// <summary>
/// A proposed governed action requiring approval before execution.
///
/// <para>
/// The reference is the binding token: approval is granted for <i>this</i> action, and an
/// execution that presents a different reference must be refused. In SendOS that check lives in
/// <c>ApprovalCheckpoint.Evaluate</c>; here the validator makes the reference mandatory so the
/// binding is even representable.
/// </para>
/// </summary>
public sealed record ActionProposal : DecisionInteraction
{
    public string Recommendation { get; init; } = string.Empty;

    public string ProposedActionReference { get; init; } = string.Empty;

    public bool RequiresApproval { get; init; } = true;

    /// <summary>Who must approve, when the policy names a role. Null means any authorised approver.</summary>
    public string? ApproverRole { get; init; }

    public override ResponseType Type => ResponseType.ActionProposal;
}

/// <summary>An honest statement that the request cannot be fulfilled as asked.</summary>
public sealed record Limitation : DecisionInteraction
{
    public string Reason { get; init; } = string.Empty;

    public string? LimitationCode { get; init; }

    public override ResponseType Type => ResponseType.Limitation;
}
