namespace Bridge.Shared.Decisions;

/// <summary>
/// Canned model responses used by <c>--mock</c> and <c>--selftest</c>.
///
/// <para>
/// Each sample exists to exercise exactly one failure stage, in the order a real model tends to
/// produce them:
/// </para>
/// <list type="number">
///   <item><description><see cref="ExcludedArtifact"/> — the model answers with a chart spec.
///   The family cannot represent it (SendOS's structural exclusion, rebuilt): schema failure.</description></item>
///   <item><description><see cref="SchemaBroken"/> — right subtype, missing required properties:
///   schema failure with repair.</description></item>
///   <item><description><see cref="BudgetBroken"/> — structurally valid, violates presentation
///   budgets: budget failure.</description></item>
///   <item><description><see cref="ValidDecisionState"/> / <see cref="ValidClarification"/> /
///   <see cref="ValidActionProposal"/> — accepted.</description></item>
/// </list>
/// <para>
/// Having the broken variants as data (not as code paths) means the repair loop is tested
/// deterministically and offline — the same reason SendOS's property tests use scripted fakes
/// instead of a live model.
/// </para>
/// </summary>
public static class DecisionSamples
{
    /// <summary>A response the family deliberately cannot represent: an analytics artifact.</summary>
    public const string ExcludedArtifact = """
    {
      "responseType": "chartSpec",
      "interactionId": "i-100",
      "headline": "Revenue by month",
      "traceReference": "t-100",
      "chartType": "bar",
      "series": [12, 14, 9]
    }
    """;

    /// <summary>Correct subtype, missing required properties — schema failure.</summary>
    public const string SchemaBroken = """
    {
      "responseType": "decisionState",
      "interactionId": "i-101",
      "headline": "Revenue is down",
      "meaning": "Revenue fell this month.",
      "consequence": "Margin is squeezed."
    }
    """;

    /// <summary>Structurally valid but over budget: 15-word headline and a 3-sentence meaning.</summary>
    public const string BudgetBroken = """
    {
      "responseType": "decisionState",
      "interactionId": "i-102",
      "headline": "Revenue has declined this month across the enterprise segment and the mid market segment too",
      "traceReference": "t-102",
      "meaning": "Revenue fell twelve percent this month. The enterprise segment lost two renewals. The mid-market segment was flat.",
      "consequence": "Margin is squeezed.",
      "evidenceSummary": "CRM opportunities closed-won, 30 days",
      "nextMoves": [
        { "id": "why", "label": "Why?" },
        { "id": "evidence", "label": "Show evidence" }
      ]
    }
    """;

    /// <summary>A fully valid decision state.</summary>
    public const string ValidDecisionState = """
    {
      "responseType": "decisionState",
      "interactionId": "i-103",
      "headline": "Revenue is down 12% this month",
      "traceReference": "t-103",
      "meaning": "Closed-won revenue fell twelve percent month over month. Two enterprise renewals slipped.",
      "consequence": "The quarter's target is at risk.",
      "evidenceSummary": "CRM opportunities closed-won, trailing 30 days",
      "nextMoves": [
        { "id": "why", "label": "Why?" },
        { "id": "evidence", "label": "Show evidence" }
      ]
    }
    """;

    /// <summary>A fully valid clarification prompt: one question, three options.</summary>
    public const string ValidClarification = """
    {
      "responseType": "clarificationPrompt",
      "interactionId": "i-104",
      "headline": "Which revenue view do you mean?",
      "traceReference": "t-104",
      "question": "Which revenue definition should I use?",
      "options": ["Booked revenue", "Recognised revenue", "Pipeline value"]
    }
    """;

    /// <summary>A fully valid action proposal: approval-gated and bound to an action reference.</summary>
    public const string ValidActionProposal = """
    {
      "responseType": "actionProposal",
      "interactionId": "i-105",
      "headline": "Prepare the discount approval",
      "traceReference": "t-105",
      "recommendation": "Approve a 10% discount for the Meridian renewal.",
      "proposedActionReference": "action-77f3",
      "requiresApproval": true,
      "approverRole": "sales-director",
      "nextMoves": [
        { "id": "proceed", "label": "Approve and proceed" },
        { "id": "stop", "label": "Don't proceed" }
      ]
    }
    """;
}
