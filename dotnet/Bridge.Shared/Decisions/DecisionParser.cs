using System.Text.Json;
using Bridge.Shared.Json;
using Bridge.Shared.Schema;

namespace Bridge.Shared.Decisions;

/// <summary>Which check rejected a model response. The stage matters: the fix differs per stage.</summary>
public enum ParseStage
{
    /// <summary>The JSON did not conform to the declared schema (wrong shape, missing property, excluded subtype).</summary>
    Schema,

    /// <summary>The JSON was well-formed but could not bind to the typed family (e.g. an unknown discriminator).</summary>
    Binding,

    /// <summary>The decision bound but violates the product contract (budgets, required fields, ranges).</summary>
    Budget,
}

/// <summary>One reason a response was rejected.</summary>
public sealed record ParseIssue(ParseStage Stage, string Message);

/// <summary>
/// The result of parsing a model response.
///
/// <para>
/// <b>There is no "partially valid" outcome.</b> Either a fully validated decision is returned
/// or it is not — the same guarantee SendOS's <c>StructuredCompletionHandler</c> makes when it
/// sets <c>StructuredOutput = null</c> on any failure. A caller that can render a half-valid
/// decision will eventually render one.
/// </para>
/// </summary>
public sealed record ParseResult
{
    private ParseResult(bool ok, DecisionInteraction? decision, IReadOnlyList<ParseIssue> issues)
    {
        IsOk = ok;
        Decision = decision;
        Issues = issues;
    }

    /// <summary>True only when every stage passed.</summary>
    public bool IsOk { get; }

    /// <summary>The validated decision, or null. Never a partially-populated object.</summary>
    public DecisionInteraction? Decision { get; }

    /// <summary>Every issue found, in stage order. Empty on success.</summary>
    public IReadOnlyList<ParseIssue> Issues { get; }

    public static ParseResult Success(DecisionInteraction decision) => new(true, decision, []);

    public static ParseResult Failure(ParseStage stage, IEnumerable<string> messages) =>
        new(false, null, messages.Select(m => new ParseIssue(stage, m)).ToList());

    /// <summary>Human-readable issue list for the console.</summary>
    public string Describe()
    {
        if (IsOk)
        {
            return "valid";
        }

        return string.Join(Environment.NewLine,
            Issues.Select(i => $"  [{i.Stage}] {i.Message}"));
    }

    /// <summary>
    /// A repair instruction to feed back to the model, naming every violation.
    ///
    /// <para>
    /// Two rules make repair work in practice: (1) list <i>all</i> violations, so one retry can
    /// fix them together; (2) demand JSON only, because a conversational apology costs tokens
    /// and does not parse.
    /// </para>
    /// </summary>
    public string ToRepairInstruction() =>
        "Your previous response was rejected. Fix ALL of the following problems and reply with ONLY the corrected JSON object, no commentary:" +
        Environment.NewLine +
        string.Join(Environment.NewLine, Issues.Select(i => $"- ({i.Stage}) {i.Message}"));
}

/// <summary>
/// Parses a provider response into a validated decision through the three-stage gate:
/// <b>schema → binding → budget</b>.
///
/// <para>
/// The ordering is deliberate. Schema first because it is the cheapest and produces the
/// clearest path names; binding second because it is the only stage that can throw on hostile
/// input; budget last because it needs typed fields. Stopping at the first failing stage keeps
/// the repair message focused — a model told "you used the wrong type AND blew the budget" tends
/// to fix one and regress the other.
/// </para>
/// <para>
/// SendOS equivalent: <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/
/// StructuredCompletionHandler.cs</c> (schema gate, never surfaces unvalidated output) followed
/// by the runtime's typed composition (<c>DecisionComposer</c> + <c>PresentationBudgetEnforcer</c>).
/// This class composes both checks in one place for teaching.
/// </para>
/// </summary>
public static class DecisionParser
{
    /// <summary>Serialises a decision back to wire JSON (pretty by default).</summary>
    public static string Serialize(DecisionInteraction decision, bool indented = true) =>
        JsonSerializer.Serialize(
            decision,
            indented ? BridgeJson.Indented : BridgeJson.Options);

    /// <summary>
    /// Runs the three-stage parse. Never throws for malformed model output; every failure is a
    /// <see cref="ParseResult"/> so the caller decides whether to repair, retry or degrade.
    /// </summary>
    public static ParseResult Parse(string? rawJson, PresentationBudget? budget = null)
    {
        // Stage 1 — schema. Catches wrong shape, missing required properties, excluded subtypes.
        var schemaResult = JsonSchemaLite.Validate(rawJson, DecisionSchema.Json);
        if (!schemaResult.IsValid)
        {
            return ParseResult.Failure(ParseStage.Schema, schemaResult.Errors);
        }

        // Stage 2 — binding. Catches anything the schema could not: discriminator values that
        // pass const checks but have no CLR type, duplicate properties, oversized integers, etc.
        DecisionInteraction? decision;
        try
        {
            decision = JsonSerializer.Deserialize<DecisionInteraction>(rawJson!, BridgeJson.Options);
        }
        catch (JsonException ex)
        {
            return ParseResult.Failure(ParseStage.Binding, [$"could not bind to the typed family: {ex.Message}"]);
        }

        if (decision is null)
        {
            return ParseResult.Failure(ParseStage.Binding, ["deserialisation produced no decision."]);
        }

        // Stage 3 — product contract. Catches decisions that are structurally perfect and still
        // unusable: a 30-word headline, a clarification with two questions, a recommendation
        // with no confidence.
        var budgetErrors = DecisionValidator.Validate(decision, budget);
        if (budgetErrors.Count > 0)
        {
            return ParseResult.Failure(ParseStage.Budget, budgetErrors);
        }

        return ParseResult.Success(decision);
    }
}
