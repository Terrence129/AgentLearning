using Bridge.Shared;
using Bridge.Shared.Decisions;

namespace StructuredDecisionBridge;

/// <summary>
/// Offline mechanism checks for the week-3 bridge lab.
///
/// <para>
/// Every check is deterministic and takes microseconds: the decision family, the schema, the
/// validator and the repair loop are all pure code, and the mock provider is scripted. That is
/// the point — the parts of an agent that decide whether output is trustworthy should not
/// require a model call to test.
/// </para>
/// </summary>
internal static class SelfTest
{
    private static int _failures;

    public static async Task<int> RunAsync()
    {
        ConsoleUi.Title("StructuredDecisionBridge — self-test (offline)");
        ConsoleUi.Dim("No API key, no network. Each check proves one week-3 mechanism.");
        Console.WriteLine();

        _failures = 0;

        await CheckAsync("an excluded artifact type is rejected at the schema stage", async () =>
        {
            var result = DecisionParser.Parse(DecisionSamples.ExcludedArtifact);

            Assert(!result.IsOk, "an unrepresentable artifact must not parse");
            Assert(result.Decision is null, "a failed parse must not return a decision");
            Assert(result.Issues.All(i => i.Stage == ParseStage.Schema), "the rejection belongs to the schema stage");
            Assert(
                result.Issues.Any(i => i.Message.Contains("oneOf", StringComparison.Ordinal)),
                $"the message should explain the oneOf failure: {result.Describe()}");
            await Task.CompletedTask;
        });

        await CheckAsync("missing required properties are rejected at the schema stage", async () =>
        {
            var result = DecisionParser.Parse(DecisionSamples.SchemaBroken);

            Assert(!result.IsOk, "a decision missing required properties must not parse");
            Assert(
                result.Issues.Any(i => i.Message.Contains("traceReference", StringComparison.Ordinal)),
                $"the missing traceReference must be named: {result.Describe()}");
        });

        await CheckAsync("an over-budget decision is rejected at the budget stage", async () =>
        {
            var result = DecisionParser.Parse(DecisionSamples.BudgetBroken);

            Assert(!result.IsOk, "an over-budget decision must not parse");
            Assert(result.Issues.All(i => i.Stage == ParseStage.Budget), "the rejection belongs to the budget stage");
            Assert(
                result.Issues.Any(i => i.Message.Contains("headline", StringComparison.Ordinal)),
                $"headline violation must be named: {result.Describe()}");
            Assert(
                result.Issues.Any(i => i.Message.Contains("meaning", StringComparison.Ordinal)),
                $"meaning violation must be named: {result.Describe()}");
        });

        await CheckAsync("a valid decision state parses to its typed subtype", async () =>
        {
            var result = DecisionParser.Parse(DecisionSamples.ValidDecisionState);

            Assert(result.IsOk, $"expected a valid decision: {result.Describe()}");
            Assert(result.Decision is DecisionState, $"expected DecisionState, got {result.Decision?.GetType().Name}");
            Assert(result.Decision!.Type == ResponseType.DecisionState, "the discriminator must project to the typed value");
        });

        await CheckAsync("valid clarification and action proposal parse", async () =>
        {
            var clarification = DecisionParser.Parse(DecisionSamples.ValidClarification);
            Assert(clarification.IsOk, $"valid clarification rejected: {clarification.Describe()}");
            Assert(clarification.Decision is ClarificationPrompt { Options.Count: 3 }, "clarification options lost in binding");

            var proposal = DecisionParser.Parse(DecisionSamples.ValidActionProposal);
            Assert(proposal.IsOk, $"valid proposal rejected: {proposal.Describe()}");
            Assert(
                proposal.Decision is ActionProposal { ProposedActionReference: "action-77f3" },
                "the action reference must survive binding — it is the approval binding token");
        });

        await CheckAsync("serialise → parse round-trips the subtype intact", async () =>
        {
            var original = DecisionParser.Parse(DecisionSamples.ValidDecisionState).Decision!;
            var json = DecisionParser.Serialize(original, indented: false);
            var reparsed = DecisionParser.Parse(json);

            Assert(reparsed.IsOk, $"round-trip parse failed: {reparsed.Describe()}");
            Assert(reparsed.Decision is DecisionState, "round-trip changed the subtype");
            var state = (DecisionState)reparsed.Decision!;
            Assert(state.Meaning == ((DecisionState)original).Meaning, "round-trip lost field content");
            Assert(json.Contains("\"responseType\":\"decisionState\"", StringComparison.Ordinal), $"discriminator missing from wire JSON: {json}");
        });

        await CheckAsync("headline budget boundary is exact (12 passes, 13 fails)", async () =>
        {
            var twelve = BuildState(Words(12));
            Assert(DecisionValidator.Validate(twelve).Count == 0, "12 words must pass the 12-word budget");

            var thirteen = BuildState(Words(13));
            var errors = DecisionValidator.Validate(thirteen);
            Assert(errors.Count > 0, "13 words must fail the 12-word budget");
            Assert(errors.Any(e => e.StartsWith("headline:", StringComparison.Ordinal)), $"expected a headline error, got: {string.Join("; ", errors)}");
        });

        await CheckAsync("sentence counting is deterministic and boundary-correct", async () =>
        {
            Assert(DecisionValidator.SentenceCount("") == 0, "empty text is zero sentences");
            Assert(DecisionValidator.SentenceCount("One") == 1, "no terminator is still one sentence");
            Assert(DecisionValidator.SentenceCount("One. Two.") == 2, "two terminators is two sentences");
            Assert(DecisionValidator.SentenceCount("One! Two? Three.") == 3, "all terminators count");
            await Task.CompletedTask;
        });

        await CheckAsync("clarification rules: one question, 1–3 options", async () =>
        {
            var valid = (ClarificationPrompt)DecisionParser.Parse(DecisionSamples.ValidClarification).Decision!;

            var twoQuestions = valid with { Question = "Which revenue definition? And for which period?" };
            Assert(DecisionValidator.Validate(twoQuestions).Any(e => e.StartsWith("question:", StringComparison.Ordinal)), "two question marks must fail");

            var fourOptions = valid with { Options = ["a", "b", "c", "d"] };
            Assert(DecisionValidator.Validate(fourOptions).Any(e => e.StartsWith("options:", StringComparison.Ordinal)), "four options must fail");

            var zeroOptions = valid with { Options = [] };
            Assert(DecisionValidator.Validate(zeroOptions).Any(e => e.StartsWith("options:", StringComparison.Ordinal)), "zero options must fail");
        });

        await CheckAsync("confidence outside 0..1 is rejected", async () =>
        {
            var recommendation = new DecisionRecommendation
            {
                InteractionId = "i-200",
                Headline = "Recommend the discount",
                TraceReference = "t-200",
                Recommendation = "Approve a 10% discount.",
                Consequence = "Margin falls 1 point.",
                Confidence = 1.5,
                Uncertainty = "Renewal may still churn.",
                EvidenceSummary = "CRM opportunity + margin table",
            };

            var errors = DecisionValidator.Validate(recommendation);
            Assert(errors.Any(e => e.StartsWith("confidence:", StringComparison.Ordinal)), "1.5 confidence must fail");

            var fixedDecision = recommendation with { Confidence = 0.7 };
            Assert(DecisionValidator.Validate(fixedDecision).Count == 0, "0.7 confidence must pass");
            await Task.CompletedTask;
        });

        await CheckAsync("repair loop converges over the four scripted failure stages", async () =>
        {
            var provider = new MockDecisionProvider();
            var outcome = await RepairLoop.RunAsync(provider, "Why did revenue fall?");

            Assert(outcome.Success, "the default script must end in a valid decision");
            Assert(outcome.Attempts.Count == 4, $"expected 4 attempts (1 call + 3 repairs), got {outcome.Attempts.Count}");
            Assert(outcome.Decision is DecisionState, "the accepted decision must be the scripted DecisionState");

            Assert(outcome.Attempts[0].Result.Issues[0].Stage == ParseStage.Schema, "attempt 1 must fail at schema");
            Assert(outcome.Attempts[1].Result.Issues[0].Stage == ParseStage.Schema, "attempt 2 must fail at schema");
            Assert(outcome.Attempts[2].Result.Issues[0].Stage == ParseStage.Budget, "attempt 3 must fail at budget");
            Assert(outcome.Attempts[3].Result.IsOk, "attempt 4 must be accepted");
            Assert(provider.Calls == 4, $"provider should have been called 4 times, got {provider.Calls}");
        });

        await CheckAsync("repair loop gives up honestly and never returns a partial decision", async () =>
        {
            var provider = new MockDecisionProvider([DecisionSamples.BudgetBroken]);
            var outcome = await RepairLoop.RunAsync(provider, "Why did revenue fall?", maxRepairs: 2);

            Assert(!outcome.Success, "an always-invalid provider must fail");
            Assert(outcome.Decision is null, "a failed repair loop must not return a best-effort decision");
            Assert(outcome.Attempts.Count == 3, $"expected 3 attempts (1 call + 2 repairs), got {outcome.Attempts.Count}");
            Assert(outcome.Attempts.All(a => a.Result.Decision is null), "no attempt may carry a decision");
            Assert(outcome.FailureSummary is not null, "a failure must carry a human-readable reason");
        });

        await CheckAsync("maxRepairs = 0 makes exactly one attempt", async () =>
        {
            var provider = new MockDecisionProvider([DecisionSamples.BudgetBroken, DecisionSamples.ValidDecisionState]);
            var outcome = await RepairLoop.RunAsync(provider, "goal", maxRepairs: 0);

            Assert(!outcome.Success, "with no repairs, the first invalid response must fail the run");
            Assert(outcome.Attempts.Count == 1, $"expected exactly 1 attempt, got {outcome.Attempts.Count}");
            Assert(provider.Calls == 1, "the provider must not be called again when repairs are disabled");
        });

        await CheckAsync("repair instruction names every violation", async () =>
        {
            var result = DecisionParser.Parse(DecisionSamples.BudgetBroken);
            var instruction = result.ToRepairInstruction();

            foreach (var issue in result.Issues)
            {
                Assert(
                    instruction.Contains(issue.Message, StringComparison.Ordinal),
                    $"repair instruction omitted an issue: {issue.Message}");
            }

            Assert(
                instruction.Contains("ONLY the corrected JSON", StringComparison.Ordinal),
                "repair instruction must forbid commentary");
            await Task.CompletedTask;
        });

        await CheckAsync("the family structurally excludes chart/dashboard artifacts", async () =>
        {
            var derived = typeof(DecisionInteraction)
                .Assembly.GetTypes()
                .Where(t => typeof(DecisionInteraction).IsAssignableFrom(t) && t != typeof(DecisionInteraction))
                .ToList();

            Assert(derived.Count == 7, $"expected 7 decision subtypes, found {derived.Count}");

            string[] forbidden = ["Chart", "Dashboard", "Visualisation", "ReportCanvas", "AnalyticsWorkspace"];
            foreach (var type in derived)
            {
                Assert(
                    !forbidden.Any(word => type.Name.Contains(word, StringComparison.OrdinalIgnoreCase)),
                    $"the family must not be able to represent '{type.Name}'");
            }

            // And the excluded artifact cannot even round-trip: the discriminator is unknown.
            Assert(!DecisionParser.Parse(DecisionSamples.ExcludedArtifact).IsOk, "a chartSpec must never bind");
            await Task.CompletedTask;
        });

        Console.WriteLine();
        if (_failures == 0)
        {
            ConsoleUi.Good("all checks passed");
            return 0;
        }

        ConsoleUi.Bad($"{_failures} check(s) failed");
        return 1;
    }

    private static DecisionState BuildState(string headline) => new()
    {
        InteractionId = "i-300",
        Headline = headline,
        TraceReference = "t-300",
        Meaning = "Revenue fell. Renewals slipped.",
        Consequence = "The target is at risk.",
        EvidenceSummary = "CRM closed-won, 30 days",
    };

    private static string Words(int count) => string.Join(' ', Enumerable.Range(1, count).Select(i => $"w{i}"));

    private static void Assert(bool condition, string message)
    {
        if (!condition)
        {
            throw new AssertionException(message);
        }
    }

    private static async Task CheckAsync(string name, Func<Task> check)
    {
        try
        {
            await check();
            ConsoleUi.Pass(name);
        }
        catch (Exception ex)
        {
            _failures++;
            ConsoleUi.Fail(name, ex.Message);
        }
    }

    private sealed class AssertionException(string message) : Exception(message);
}
