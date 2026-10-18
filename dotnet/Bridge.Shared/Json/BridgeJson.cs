using System.Text.Json;
using System.Text.Json.Serialization;

namespace Bridge.Shared.Json;

/// <summary>
/// The one place JSON settings are configured.
///
/// <para>
/// <b>Why one place:</b> a serializer that differs between the request path, the response
/// path and the tests is a class of bug (case-sensitivity, null handling, enum representation)
/// that is invisible until a real provider sends a field in a different case. SendOS keeps the
/// same discipline with <c>Send.Shared.Utils/SendJsonSerializer</c>.
/// </para>
/// <para>
/// Deliberate choices:
/// <list type="bullet">
///   <item><c>PropertyNameCaseInsensitive</c> — providers are not consistent about
///   <c>finish_reason</c> vs <c>finishReason</c>; reading tolerantly is cheaper than a bug.</item>
///   <item><c>WhenWritingNull</c> — omit nulls rather than sending them. Some compatible hosts
///   reject explicit nulls even for nullable schema properties.</item>
///   <item><c>AllowTrailingCommas</c> + comments — model output is not machine-clean; tolerate
///   the harmless variants and reject the harmful ones through validation, not parsing.</item>
///   <item>Polymorphism is declared on the type (<see cref="Decisions.DecisionInteraction"/>),
///   not configured here, so the contract is discoverable where the type is defined.</item>
/// </list>
/// </para>
/// </summary>
public static class BridgeJson
{
    /// <summary>Options used for all provider and decision JSON.</summary>
    public static JsonSerializerOptions Options { get; } = Create();

    /// <summary>
    /// Creates fresh options. A factory exists because <see cref="JsonSerializerOptions"/> is
    /// mutable and cached internally after first use — handing the same instance to code that
    /// tweaks it is how one lab changes another's behaviour.
    /// </summary>
    public static JsonSerializerOptions Create() => new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        AllowTrailingCommas = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
        WriteIndented = false,
    };

    /// <summary>Pretty-printing options for console output only.</summary>
    public static JsonSerializerOptions Indented { get; } = new(Create())
    {
        WriteIndented = true,
    };
}
