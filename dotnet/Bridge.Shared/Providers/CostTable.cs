using System.Globalization;

namespace Bridge.Shared.Providers;

/// <summary>
/// A tiny, explicit price table used to turn token usage into money.
///
/// <para>
/// <b>Why this exists:</b> "the model is cheap" is not a budget. A run's cost is
/// <c>promptTokens × inRate + completionTokens × outRate</c>, and the two rates are usually
/// different by a factor of 3–5, which is exactly why output-token discipline matters more than
/// input-token discipline in most agent loops. The table is data, not code, so adding a model is
/// a one-line change and a wrong price is an obvious diff.
/// </para>
/// <para>
/// Prices are illustrative USD per 1M tokens, chosen to mirror this repo's
/// <c>agentlab/pricing.py</c>. Refresh them from the provider's pricing page before quoting a
/// cost externally — a stale price table is a silent source of wrong decisions.
/// </para>
/// <para>
/// SendOS equivalent: <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Routing/
/// {IModelCostCatalog,InMemoryModelCostCatalog}.cs</c> and <c>Contracts/Routing/ModelCostProfile.cs</c>.
/// </para>
/// </summary>
public static class CostTable
{
    /// <summary>USD per 1,000,000 tokens for one model.</summary>
    public readonly record struct Rates(decimal InputPerMillion, decimal OutputPerMillion);

    private static readonly Dictionary<string, Rates> Prices = new(StringComparer.OrdinalIgnoreCase)
    {
        ["deepseek-chat"] = new(0.27m, 1.10m),
        ["deepseek-reasoner"] = new(0.55m, 2.19m),
        ["gpt-4o-mini"] = new(0.15m, 0.60m),
        ["gpt-4.1-mini"] = new(0.40m, 1.60m),
        ["mock-model"] = new(0m, 0m),
    };

    /// <summary>
    /// Rates for a model, falling back to a conservative non-zero default so an unknown model
    /// still produces a cost estimate rather than a free-looking zero.
    /// </summary>
    public static Rates For(string model) =>
        Prices.TryGetValue(model, out var rates) ? rates : new Rates(0.50m, 1.50m);

    /// <summary>Cost in USD for a reported usage, or zero when usage is absent.</summary>
    public static decimal Estimate(string model, TokenUsage? usage)
    {
        if (usage is null)
        {
            return 0m;
        }

        var rates = For(model);
        return usage.PromptTokens / 1_000_000m * rates.InputPerMillion
               + usage.CompletionTokens / 1_000_000m * rates.OutputPerMillion;
    }

    /// <summary>Formats a cost with enough precision to see a sub-cent run, without fake precision.</summary>
    public static string Format(decimal usd) =>
        usd < 0.01m
            ? $"${usd.ToString("0.00000", CultureInfo.InvariantCulture)}"
            : $"${usd.ToString("0.0000", CultureInfo.InvariantCulture)}";
}
