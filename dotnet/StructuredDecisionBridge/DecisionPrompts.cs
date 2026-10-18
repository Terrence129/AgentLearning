using Bridge.Shared.Decisions;

namespace StructuredDecisionBridge;

/// <summary>
/// The prompt contract sent to the model.
///
/// <para>
/// <b>Three things it must do, and one it must not:</b>
/// </para>
/// <list type="number">
///   <item><description>
///   Show the schema. A model cannot satisfy a contract it has not been shown, and "reply in
///   JSON" is not a schema.
///   </description></item>
///   <item><description>
///   State the budgets as numbers, not adjectives. "Be concise" is unenforceable; "headline ≤ 12
///   words" is testable.
///   </description></item>
///   <item><description>
///   Name the closed set of response types and say that anything else is invalid. This is the
///   prompt-level half of the structural exclusion the type system enforces.
///   </description></item>
///   <item><description>
///   <b>Not</b> ask for chain-of-thought or "explain your reasoning". The output is a typed
///   decision; reasoning that should not be shown is not requested, which is also the cheapest
///   way to keep it out of the artifact.
///   </description></item>
/// </list>
/// <para>
/// SendOS equivalent: the specialist output schema and prompt guidance carried as governed
/// assets (<c>PromptGuidance</c>, <c>SpecialistDefinition</c> content) and validated by
/// <c>CapabilitySchemaValidator</c> / <c>StructuredCompletionHandler</c>.
/// </para>
/// </summary>
public static class DecisionPrompts
{
    /// <summary>The system prompt: role, closed set, schema, budgets, formatting rules.</summary>
    public static string System { get; } = $$"""
    You are a decision service for a business intelligence platform.

    Reply with ONE JSON object and nothing else: no markdown fences, no commentary, no explanation.
    The object must satisfy the JSON Schema below and follow the presentation budgets.

    RESPONSE TYPES (choose exactly one; any other value is invalid):
      clarificationPrompt, directAnswer, decisionState, analysisConclusion,
      decisionRecommendation, actionProposal, limitation

    REQUIRED ENVELOPE ON EVERY OBJECT:
      responseType (string, one of the values above)
      interactionId (string, non-empty)
      headline (string, at most 12 words)
      traceReference (string, non-empty)
      nextMoves (array of {id, label}, at most 4; may be omitted)

    SUBTYPE RULES:
      clarificationPrompt: question (string, exactly one question mark) + options (1..3 strings)
      directAnswer: answer (string)
      decisionState: meaning (<= 2 sentences), consequence (<= 1 sentence), evidenceSummary (string)
      analysisConclusion: meaning (<= 2 sentences), evidenceSummary (string)
      decisionRecommendation: recommendation (<= 1 sentence), consequence (<= 1 sentence),
        confidence (0..1 number), uncertainty (string), evidenceSummary (string)
      actionProposal: recommendation (<= 1 sentence), proposedActionReference (string, non-empty),
        requiresApproval (boolean), approverRole (optional string)
      limitation: reason (string), limitationCode (optional string)

    Charts, dashboards, report canvases and other visual artifacts are NOT response types.
    If asked for one, return a decision that answers the underlying business question instead.
    If the request is too ambiguous to act on, return a clarificationPrompt with ONE question.

    JSON SCHEMA:
    {{DecisionSchema.Json}}
    """;

    /// <summary>The initial user message for a goal.</summary>
    public static string UserGoal(string goal) =>
        $"Business goal: {goal}\n\nReturn the single decision JSON object that best serves this goal.";
}
