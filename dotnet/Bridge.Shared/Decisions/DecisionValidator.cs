using System.Text.RegularExpressions;

namespace Bridge.Shared.Decisions;

/// <summary>
/// Validates a bound decision against the product contract: presence, budgets, and the
/// type-specific rules that JSON Schema cannot express.
///
/// <para>
/// <b>Three deliberate separations:</b>
/// </para>
/// <list type="number">
///   <item><description>
///   <b>Binding ≠ validation.</b> Deserialization succeeds on empty strings; the validator is
///   what refuses them. SendOS's <c>StructuredCompletionHandler</c> makes the same move: it
///   returns <c>SchemaValid=false</c> rather than a partially-usable object.
///   </description></item>
///   <item><description>
///   <b>Structure ≠ semantics.</b> Schema says "a question is a string"; the validator says
///   "a clarification prompt asks exactly one question and offers one to three options".
///   </description></item>
///   <item><description>
///   <b>Every error is returned.</b> A repair prompt listing all violations lets the model fix
///   them in one pass; returning only the first multiplies calls and cost.
///   </description></item>
/// </list>
/// <para>
/// The validator is pure and deterministic, so it is unit-testable with no provider and no
/// network — which is why the <c>--selftest</c> can prove every rule offline.
/// </para>
/// </summary>
public static class DecisionValidator
{
    /// <summary>
    /// Validates <paramref name="decision"/> and returns every violation found.
    /// An empty list means the decision satisfies the contract.
    /// </summary>
    public static IReadOnlyList<string> Validate(DecisionInteraction? decision, PresentationBudget? budget = null)
    {
        var rules = budget ?? PresentationBudget.Default;
        var errors = new List<string>();

        if (decision is null)
        {
            errors.Add("decision: no decision was bound.");
            return errors;
        }

        RequireNonEmpty(errors, "interactionId", decision.InteractionId);
        RequireNonEmpty(errors, "traceReference", decision.TraceReference);
        RequireNonEmpty(errors, "headline", decision.Headline);

        var headlineWords = WordCount(decision.Headline);
        if (headlineWords > rules.MaxHeadlineWords)
        {
            errors.Add(
                $"headline: {headlineWords} words exceeds the {rules.MaxHeadlineWords}-word budget " +
                $"(\"{Truncate(decision.Headline, 80)}\").");
        }

        if (decision.NextMoves.Count > rules.MaxNextMoves)
        {
            errors.Add($"nextMoves: {decision.NextMoves.Count} moves exceeds the {rules.MaxNextMoves} budget.");
        }

        for (var i = 0; i < decision.NextMoves.Count; i++)
        {
            var move = decision.NextMoves[i];
            RequireNonEmpty(errors, $"nextMoves[{i}].id", move.Id);
            RequireNonEmpty(errors, $"nextMoves[{i}].label", move.Label);
        }

        switch (decision)
        {
            case ClarificationPrompt prompt:
                ValidateClarification(errors, prompt, rules);
                break;

            case DirectAnswer answer:
                RequireNonEmpty(errors, "answer", answer.Answer);
                break;

            case DecisionState state:
                ValidateSentences(errors, "meaning", state.Meaning, rules.MaxMeaningSentences, required: true);
                ValidateSentences(errors, "consequence", state.Consequence, rules.MaxConsequenceSentences, required: true);
                RequireNonEmpty(errors, "evidenceSummary", state.EvidenceSummary);
                break;

            case AnalysisConclusion conclusion:
                ValidateSentences(errors, "meaning", conclusion.Meaning, rules.MaxMeaningSentences, required: true);
                RequireNonEmpty(errors, "evidenceSummary", conclusion.EvidenceSummary);
                break;

            case DecisionRecommendation recommendation:
                ValidateSentences(
                    errors, "recommendation", recommendation.Recommendation, rules.MaxRecommendationSentences, required: true);
                ValidateSentences(
                    errors, "consequence", recommendation.Consequence, rules.MaxConsequenceSentences, required: true);
                RequireNonEmpty(errors, "uncertainty", recommendation.Uncertainty);
                RequireNonEmpty(errors, "evidenceSummary", recommendation.EvidenceSummary);
                if (recommendation.Confidence is < 0 or > 1 || double.IsNaN(recommendation.Confidence))
                {
                    errors.Add($"confidence: {recommendation.Confidence} is outside 0..1.");
                }

                break;

            case ActionProposal proposal:
                ValidateSentences(
                    errors, "recommendation", proposal.Recommendation, rules.MaxRecommendationSentences, required: true);
                RequireNonEmpty(errors, "proposedActionReference", proposal.ProposedActionReference);
                break;

            case Limitation limitation:
                RequireNonEmpty(errors, "reason", limitation.Reason);
                break;

            default:
                errors.Add($"responseType: '{decision.Type}' has no validator rule; refusing to pass an unvalidated subtype.");
                break;
        }

        return errors;
    }

    private static void ValidateClarification(
        List<string> errors,
        ClarificationPrompt prompt,
        PresentationBudget rules)
    {
        RequireNonEmpty(errors, "question", prompt.Question);

        var questionMarks = prompt.Question.Count(c => c == '?');
        if (questionMarks != 1)
        {
            // "Exactly one question" is the product guarantee. Two question marks is a compound
            // question the person cannot answer in one reply — the failure the budget exists for.
            errors.Add($"question: expected exactly one question mark but found {questionMarks} (one question per clarification).");
        }

        if (prompt.Options.Count < rules.MinClarificationOptions
            || prompt.Options.Count > rules.MaxClarificationOptions)
        {
            errors.Add(
                $"options: {prompt.Options.Count} options is outside " +
                $"{rules.MinClarificationOptions}..{rules.MaxClarificationOptions}.");
        }

        for (var i = 0; i < prompt.Options.Count; i++)
        {
            RequireNonEmpty(errors, $"options[{i}]", prompt.Options[i]);
        }
    }

    private static void ValidateSentences(
        List<string> errors,
        string field,
        string value,
        int maxSentences,
        bool required)
    {
        if (required)
        {
            RequireNonEmpty(errors, field, value);
        }

        var sentences = SentenceCount(value);
        if (sentences > maxSentences)
        {
            errors.Add($"{field}: {sentences} sentences exceeds the {maxSentences}-sentence budget.");
        }
    }

    private static void RequireNonEmpty(List<string> errors, string field, string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            errors.Add($"{field}: is required and must not be empty.");
        }
    }

    /// <summary>
    /// Counts sentences by terminator characters. Deliberately simple: the budget is about
    /// comprehension, and a regex that "understands" abbreviations would make the rule harder to
    /// explain than the thing it enforces.
    /// </summary>
    public static int SentenceCount(string? text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return 0;
        }

        var count = 0;
        var hasContent = false;
        foreach (var c in text)
        {
            if (c is '.' or '!' or '?')
            {
                if (hasContent)
                {
                    count++;
                    hasContent = false;
                }
            }
            else if (!char.IsWhiteSpace(c))
            {
                hasContent = true;
            }
        }

        return hasContent ? count + 1 : count;
    }

    /// <summary>Counts whitespace-separated words, ignoring runs of spaces.</summary>
    public static int WordCount(string? text) =>
        string.IsNullOrWhiteSpace(text)
            ? 0
            : Regex.Split(text.Trim(), @"\s+").Length;

    private static string Truncate(string value, int max) =>
        value.Length <= max ? value : value[..max] + "…";
}
