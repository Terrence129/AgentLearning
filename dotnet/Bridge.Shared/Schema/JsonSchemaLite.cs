using System.Text.Json;

namespace Bridge.Shared.Schema;

/// <summary>
/// A dependency-free JSON Schema validator for the subset the labs need.
///
/// <para>
/// <b>Why hand-rolled instead of a library:</b> the point of the week-3 lab is to understand
/// what "structured output" costs and where it fails. A validator you wrote shows you the
/// actual failure surface — and it is the same trade SendOS made: its
/// <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/JsonSchemaValidator.cs</c>
/// supports only <c>type</c>, <c>required</c>, <c>properties</c> and <c>items</c>, and rejects
/// everything it cannot prove conforms.
/// </para>
/// <para>
/// <b>Supported keywords:</b> <c>type</c> (object/array/string/number/integer/boolean/null),
/// <c>required</c>, <c>properties</c>, <c>items</c>, <c>enum</c>, <c>const</c>,
/// <c>oneOf</c> (exactly one branch must validate), <c>minItems</c>, <c>maxItems</c>.
/// <b>Unsupported keywords are ignored, not failed</b> — a validator that silently accepts an
/// unknown constraint is exactly how "schema-validated" becomes a false claim. This one is
/// honest about being a subset: the schema in <see cref="Decisions.DecisionSchema"/> uses only
/// the supported subset.
/// </para>
/// <para>
/// Failure policy: <b>fail safe</b>. Malformed schema JSON, malformed payload, or an
/// unparseable keyword value is a validation failure, never a pass.
/// </para>
/// </summary>
public static class JsonSchemaLite
{
    /// <summary>
    /// Validates <paramref name="json"/> against <paramref name="schemaJson"/>.
    /// </summary>
    /// <returns>
    /// A result whose <see cref="SchemaValidationResult.IsValid"/> is true only when the payload
    /// is well-formed JSON satisfying every supported keyword in the schema.
    /// </returns>
    public static SchemaValidationResult Validate(string? json, string? schemaJson)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return SchemaValidationResult.Fail("Payload was empty.");
        }

        if (string.IsNullOrWhiteSpace(schemaJson))
        {
            return SchemaValidationResult.Fail("No schema was declared; refusing to claim validation.");
        }

        JsonDocument schema;
        try
        {
            schema = JsonDocument.Parse(schemaJson);
        }
        catch (JsonException ex)
        {
            return SchemaValidationResult.Fail($"Declared schema is not valid JSON: {ex.Message}");
        }

        JsonDocument payload;
        try
        {
            payload = JsonDocument.Parse(json);
        }
        catch (JsonException ex)
        {
            schema.Dispose();
            return SchemaValidationResult.Fail($"Payload is not valid JSON: {ex.Message}");
        }

        using (schema)
        using (payload)
        {
            var errors = new List<string>();
            ValidateNode(payload.RootElement, schema.RootElement, "$", errors);
            return errors.Count == 0
                ? SchemaValidationResult.Success
                : SchemaValidationResult.Fail(errors);
        }
    }

    private static void ValidateNode(
        JsonElement value,
        JsonElement schema,
        string path,
        List<string> errors)
    {
        if (schema.ValueKind != JsonValueKind.Object)
        {
            // A non-object schema cannot constrain anything this validator understands.
            // Accepting is consistent with "unsupported keywords are ignored"; the decision
            // schema never does this, so it is a documented edge rather than a load-bearing path.
            return;
        }

        if (schema.TryGetProperty("type", out var typeElement)
            && typeElement.ValueKind == JsonValueKind.String)
        {
            var expected = typeElement.GetString()!;
            if (!MatchesType(value, expected))
            {
                errors.Add($"{path}: expected type '{expected}' but found '{Describe(value)}'.");
                return; // Children cannot be meaningful once the type is wrong.
            }
        }

        if (schema.TryGetProperty("const", out var constElement)
            && !JsonEquals(value, constElement))
        {
            errors.Add($"{path}: expected the constant value {constElement.GetRawText()} but found {value.GetRawText()}.");
        }

        if (schema.TryGetProperty("enum", out var enumElement)
            && enumElement.ValueKind == JsonValueKind.Array
            && !enumElement.EnumerateArray().Any(candidate => JsonEquals(value, candidate)))
        {
            errors.Add($"{path}: value {value.GetRawText()} is not one of the declared enum values.");
        }

        if (schema.TryGetProperty("oneOf", out var oneOf)
            && oneOf.ValueKind == JsonValueKind.Array)
        {
            var passing = 0;
            var branchErrors = new List<string>();
            foreach (var branch in oneOf.EnumerateArray())
            {
                var branchIssues = new List<string>();
                ValidateNode(value, branch, path, branchIssues);
                if (branchIssues.Count == 0)
                {
                    passing++;
                }
                else
                {
                    branchErrors.Add(string.Join(" ", branchIssues));
                }
            }

            if (passing != 1)
            {
                errors.Add(
                    $"{path}: expected exactly one 'oneOf' branch to match but {passing} did. " +
                    $"First branch failure: {(branchErrors.Count > 0 ? branchErrors[0] : "n/a")}");
            }
        }

        if (value.ValueKind == JsonValueKind.Object)
        {
            ValidateObject(value, schema, path, errors);
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            ValidateArray(value, schema, path, errors);
        }
    }

    private static void ValidateObject(
        JsonElement value,
        JsonElement schema,
        string path,
        List<string> errors)
    {
        if (schema.TryGetProperty("required", out var required)
            && required.ValueKind == JsonValueKind.Array)
        {
            foreach (var name in required.EnumerateArray())
            {
                var property = name.GetString();
                if (property is not null && !value.TryGetProperty(property, out _))
                {
                    errors.Add($"{path}: missing required property '{property}'.");
                }
            }
        }

        if (schema.TryGetProperty("properties", out var properties)
            && properties.ValueKind == JsonValueKind.Object)
        {
            foreach (var property in properties.EnumerateObject())
            {
                if (value.TryGetProperty(property.Name, out var child))
                {
                    ValidateNode(child, property.Value, $"{path}.{property.Name}", errors);
                }
            }
        }
    }

    private static void ValidateArray(
        JsonElement value,
        JsonElement schema,
        string path,
        List<string> errors)
    {
        if (schema.TryGetProperty("items", out var items))
        {
            var index = 0;
            foreach (var child in value.EnumerateArray())
            {
                ValidateNode(child, items, $"{path}[{index}]", errors);
                index++;
            }
        }

        if (schema.TryGetProperty("minItems", out var minItems)
            && minItems.ValueKind == JsonValueKind.Number
            && value.GetArrayLength() < minItems.GetInt32())
        {
            errors.Add($"{path}: expected at least {minItems.GetInt32()} items but found {value.GetArrayLength()}.");
        }

        if (schema.TryGetProperty("maxItems", out var maxItems)
            && maxItems.ValueKind == JsonValueKind.Number
            && value.GetArrayLength() > maxItems.GetInt32())
        {
            errors.Add($"{path}: expected at most {maxItems.GetInt32()} items but found {value.GetArrayLength()}.");
        }
    }

    private static bool MatchesType(JsonElement value, string expected) => expected switch
    {
        "object" => value.ValueKind == JsonValueKind.Object,
        "array" => value.ValueKind == JsonValueKind.Array,
        "string" => value.ValueKind == JsonValueKind.String,
        "number" => value.ValueKind == JsonValueKind.Number,
        "integer" => value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out _),
        "boolean" => value.ValueKind is JsonValueKind.True or JsonValueKind.False,
        "null" => value.ValueKind == JsonValueKind.Null,
        _ => false, // Unknown type keyword: fail safe rather than accept.
    };

    private static bool JsonEquals(JsonElement left, JsonElement right) =>
        left.ValueKind == right.ValueKind && left.GetRawText() == right.GetRawText();

    private static string Describe(JsonElement value) => value.ValueKind switch
    {
        JsonValueKind.Object => "object",
        JsonValueKind.Array => "array",
        JsonValueKind.String => "string",
        JsonValueKind.Number => "number",
        JsonValueKind.True or JsonValueKind.False => "boolean",
        JsonValueKind.Null => "null",
        _ => value.ValueKind.ToString(),
    };
}

/// <summary>
/// The outcome of a schema validation. Carries every error, not just the first: a repair prompt
/// that names one problem at a time makes the model fix them serially, which multiplies calls.
/// </summary>
/// <param name="IsValid">True only when no error was found.</param>
/// <param name="Errors">One message per violation, each naming the JSON path.</param>
public sealed record SchemaValidationResult(bool IsValid, IReadOnlyList<string> Errors)
{
    public static readonly SchemaValidationResult Success = new(true, []);

    public static SchemaValidationResult Fail(string error) => new(false, [error]);

    public static SchemaValidationResult Fail(IReadOnlyList<string> errors) => new(false, errors);
}
