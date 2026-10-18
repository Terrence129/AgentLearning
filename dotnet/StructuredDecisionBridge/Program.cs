using Bridge.Shared;
using Bridge.Shared.Configuration;
using Bridge.Shared.Decisions;
using Bridge.Shared.Providers;

namespace StructuredDecisionBridge;

/// <summary>
/// Week-3 bridge lab: make model output a typed contract — a discriminated decision family bound
/// with <c>System.Text.Json</c>, validated in three stages, and repaired at most three times.
///
/// <para>
/// <b>What this app is for:</b> the Python week-3 lab builds <c>agentlab/schemas/</c>
/// (structured output, one repair retry, versioned prompts, a typed <c>Decision</c> family with
/// presentation budgets). This app mirrors it in C# and adds the two checks that make the
/// contract honest: a schema the model is shown, and a validator over the bound types. When you
/// then open SendOS's <c>IStructuredCompletionHandler</c>, <c>JsonSchemaValidator</c>,
/// <c>DecisionInteraction</c> and <c>PresentationBudgetEnforcer</c>, each one will map to a class
/// you have written yourself.
/// </para>
/// <para>
/// <b>Run it:</b>
/// <code>
/// dotnet run --project dotnet/StructuredDecisionBridge -- --selftest     # offline, no key
/// dotnet run --project dotnet/StructuredDecisionBridge -- --mock         # offline repair demo
/// dotnet run --project dotnet/StructuredDecisionBridge -- --prompt "Why did revenue fall last month?"
/// </code>
/// </para>
/// </summary>
internal static class Program
{
    private static async Task<int> Main(string[] args)
    {
        var options = CliOptions.Parse(args);

        if (options.ShowHelp)
        {
            CliOptions.PrintUsage();
            return 0;
        }

        if (options.SelfTest)
        {
            return await SelfTest.RunAsync().ConfigureAwait(false);
        }

        if (options.Mock)
        {
            return await RunAsync(
                    new MockDecisionProvider(),
                    BridgeSettings.ForOfflineFake(),
                    offline: true,
                    options)
                .ConfigureAwait(false);
        }

        BridgeSettings settings;
        try
        {
            settings = BridgeSettings.FromEnvironment();
        }
        catch (BridgeConfigurationException ex)
        {
            ConsoleUi.Bad(ex.Message);
            ConsoleUi.Info("Falling back to --mock so the lab still runs offline.");
            return await RunAsync(
                    new MockDecisionProvider(),
                    BridgeSettings.ForOfflineFake(),
                    offline: true,
                    options)
                .ConfigureAwait(false);
        }

        using var provider = new LiveDecisionProvider(settings);
        return await RunAsync(provider, settings, offline: false, options).ConfigureAwait(false);
    }

    private static async Task<int> RunAsync(
        IDecisionProvider provider,
        BridgeSettings settings,
        bool offline,
        CliOptions options)
    {
        ConsoleUi.Title("StructuredDecisionBridge — typed decisions, validation, repair");
        ConsoleUi.Section("run");
        ConsoleUi.Info($"provider    : {provider.Name}");
        ConsoleUi.Info($"model       : {settings.Model}");
        ConsoleUi.Info($"goal        : {Truncate(options.Prompt, 90)}");
        ConsoleUi.Info($"max repairs : {options.MaxRepairs}");
        if (offline)
        {
            ConsoleUi.Dim("offline: scripted responses, no API key, no network");
        }

        Console.WriteLine();
        ConsoleUi.Section("attempts");
        var outcome = await RepairLoop
            .RunAsync(
                provider,
                options.Prompt,
                options.MaxRepairs,
                onAttempt: PrintAttempt)
            .ConfigureAwait(false);

        Console.WriteLine();

        if (!outcome.Success || outcome.Decision is null)
        {
            ConsoleUi.Bad("no validated decision was produced");
            foreach (var issue in outcome.Attempts[^1].Result.Issues)
            {
                ConsoleUi.Info($"[{issue.Stage}] {issue.Message}");
            }

            ConsoleUi.Info(outcome.FailureSummary ?? "unknown failure");
            PrintEconomics(outcome, settings.Model);
            return 3;
        }

        ConsoleUi.Good($"accepted on attempt {outcome.Attempts.Count}");
        Console.WriteLine();
        PrintDecision(outcome.Decision, outcome.Budget);
        Console.WriteLine();
        PrintEconomics(outcome, settings.Model);

        Console.WriteLine();
        ConsoleUi.Dim("SendOS bridge: apps/Send.Model.Adapter/.../Structured/{IStructuredCompletionHandler,JsonSchemaValidator}.cs");
        ConsoleUi.Dim("               apps/Send.Agent.Runtime/.../Domain/Decision/DecisionInteraction.cs + Application/Decision/PresentationBudgetEnforcer.cs");
        return 0;
    }

    private static void PrintAttempt(RepairAttempt attempt)
    {
        var stage = attempt.Result.IsOk ? "accepted" : $"rejected at {attempt.Result.Issues[0].Stage}";
        var count = attempt.Result.Issues.Count;
        ConsoleUi.Info(
            $"#{attempt.Number}: {stage} ({count} issue{(count == 1 ? string.Empty : "s")}, " +
            $"{attempt.LatencyMs} ms, raw {attempt.Raw.Length} chars)");

        foreach (var issue in attempt.Result.Issues.Take(3))
        {
            ConsoleUi.Dim($"   - [{issue.Stage}] {Truncate(issue.Message, 110)}");
        }

        if (count > 3)
        {
            ConsoleUi.Dim($"   … and {count - 3} more");
        }
    }

    private static void PrintDecision(DecisionInteraction decision, PresentationBudget budget)
    {
        ConsoleUi.Section($"decision ({decision.Type})");
        ConsoleUi.Info($"interactionId : {decision.InteractionId}");
        ConsoleUi.Info($"headline      : {decision.Headline}");
        ConsoleUi.Info($"traceReference: {decision.TraceReference}");

        switch (decision)
        {
            case ClarificationPrompt prompt:
                ConsoleUi.Info($"question      : {prompt.Question}");
                ConsoleUi.Info($"options       : {string.Join(" | ", prompt.Options)}");
                break;
            case DirectAnswer answer:
                ConsoleUi.Info($"answer        : {answer.Answer}");
                break;
            case DecisionState state:
                ConsoleUi.Info($"meaning       : {state.Meaning}");
                ConsoleUi.Info($"consequence   : {state.Consequence}");
                ConsoleUi.Info($"evidence      : {state.EvidenceSummary}");
                break;
            case AnalysisConclusion conclusion:
                ConsoleUi.Info($"meaning       : {conclusion.Meaning}");
                ConsoleUi.Info($"evidence      : {conclusion.EvidenceSummary}");
                break;
            case DecisionRecommendation recommendation:
                ConsoleUi.Info($"recommendation: {recommendation.Recommendation}");
                ConsoleUi.Info($"consequence   : {recommendation.Consequence}");
                ConsoleUi.Info($"confidence    : {recommendation.Confidence:0.00} (uncertainty: {recommendation.Uncertainty})");
                break;
            case ActionProposal proposal:
                ConsoleUi.Info($"recommendation: {proposal.Recommendation}");
                ConsoleUi.Info($"action ref    : {proposal.ProposedActionReference}");
                ConsoleUi.Info($"approval      : required={proposal.RequiresApproval}, role={proposal.ApproverRole ?? "(any)"}");
                break;
            case Limitation limitation:
                ConsoleUi.Info($"reason        : {limitation.Reason}");
                break;
        }

        if (decision.NextMoves.Count > 0)
        {
            ConsoleUi.Info($"next moves    : {string.Join(" | ", decision.NextMoves.Select(m => m.Label))}");
        }

        Console.WriteLine();
        ConsoleUi.Section("budget utilisation");
        PrintBudget("headline words", DecisionValidator.WordCount(decision.Headline), budget.MaxHeadlineWords);
        PrintBudget("next moves", decision.NextMoves.Count, budget.MaxNextMoves);

        switch (decision)
        {
            case DecisionState state:
                PrintBudget("meaning sentences", DecisionValidator.SentenceCount(state.Meaning), budget.MaxMeaningSentences);
                PrintBudget("consequence sentences", DecisionValidator.SentenceCount(state.Consequence), budget.MaxConsequenceSentences);
                break;
            case AnalysisConclusion conclusion:
                PrintBudget("meaning sentences", DecisionValidator.SentenceCount(conclusion.Meaning), budget.MaxMeaningSentences);
                break;
            case DecisionRecommendation recommendation:
                PrintBudget("recommendation sentences", DecisionValidator.SentenceCount(recommendation.Recommendation), budget.MaxRecommendationSentences);
                PrintBudget("consequence sentences", DecisionValidator.SentenceCount(recommendation.Consequence), budget.MaxConsequenceSentences);
                break;
        }
    }

    private static void PrintBudget(string label, int used, int max)
    {
        var flag = used > max ? "OVER BUDGET" : "ok";
        ConsoleUi.Info($"{label,-26}: {used,2} / {max,-2} ({flag})");
    }

    private static void PrintEconomics(RepairOutcome outcome, string model)
    {
        ConsoleUi.Section("repair economics");
        ConsoleUi.Info($"attempts      : {outcome.Attempts.Count} ({outcome.RepairsUsed} repair{(outcome.RepairsUsed == 1 ? string.Empty : "s")})");
        var rawChars = outcome.Attempts.Sum(a => a.Raw.Length);
        var promptChars = outcome.Attempts.Sum(a => a.PromptChars);
        ConsoleUi.Info($"raw chars     : {rawChars} returned, {promptChars} resent as prompt context");
        ConsoleUi.Info($"estimated cost: {CostTable.Format(outcome.EstimatedCostUsd(model))} (estimate from character counts)");
        ConsoleUi.Dim("each repair re-sends the failing response plus the violation list, so the prompt grows — repair is not free");
    }

    private static string Truncate(string value, int max) =>
        value.Length <= max ? value : value[..max] + "…";
}

/// <summary>Command-line options for the structured-decision lab.</summary>
internal sealed record CliOptions
{
    public bool Mock { get; init; }

    public bool SelfTest { get; init; }

    public bool ShowHelp { get; init; }

    public string Prompt { get; init; } =
        "Why did revenue fall this month, and what should we do?";

    public int MaxRepairs { get; init; } = RepairLoop.DefaultMaxRepairs;

    public static CliOptions Parse(string[] args)
    {
        var options = new CliOptions();
        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--mock":
                    options = options with { Mock = true };
                    break;
                case "--selftest":
                    options = options with { SelfTest = true };
                    break;
                case "--help" or "-h" or "/?":
                    options = options with { ShowHelp = true };
                    break;
                case "--prompt":
                    if (i + 1 < args.Length)
                    {
                        options = options with { Prompt = args[++i] };
                    }

                    break;
                case "--max-repairs":
                    if (i + 1 < args.Length && int.TryParse(args[++i], out var repairs))
                    {
                        options = options with { MaxRepairs = Math.Clamp(repairs, 0, RepairLoop.MaxRepairCeiling) };
                    }

                    break;
                default:
                    ConsoleUi.Warn($"Unknown argument '{args[i]}' ignored (see --help).");
                    break;
            }
        }

        return options;
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        StructuredDecisionBridge — typed decisions, schema validation, repair retries.

        Usage:
          dotnet run --project dotnet/StructuredDecisionBridge -- [options]

        Options:
          --selftest          Run offline mechanism checks (no key, no network). Exit code 0 = pass.
          --mock              Use the scripted four-stage failure sequence (no key, no network).
          --prompt <text>     Business goal (default: a revenue diagnosis question).
          --max-repairs <n>   Repairs after the first attempt, 0..5 (default 3).
          --help              Print this help.

        Environment (live mode only):
          BRIDGE_API_KEY      Bearer key. Fallbacks: OPENAI_API_KEY, DEEPSEEK_API_KEY.
          BRIDGE_BASE_URL     Default https://api.deepseek.com/v1
          BRIDGE_MODEL        Default deepseek-chat
          NO_COLOR=1          Disable ANSI colour.
        """);
    }
}
