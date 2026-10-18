namespace Bridge.Shared.Decisions;

/// <summary>
/// The JSON Schema for the decision family, written only with the keywords
/// <see cref="Schema.JsonSchemaLite"/> actually enforces.
///
/// <para>
/// <b>Why the schema exists if the types already constrain the shape:</b> binding JSON to a
/// record proves the JSON is <i>parseable</i>; it does not prove the model followed the
/// contract. A missing <c>traceReference</c> binds to an empty string; a headline of 40 words
/// binds perfectly. The schema is the model-facing contract, the validator is the product
/// contract, and the typed record is the code-facing contract — three checks over one artifact,
/// each catching a different failure. SendOS's <c>OutputSchema</c> → <c>CapabilitySchemaValidator</c>
/// split is the same layering.
/// </para>
/// <para>
/// The discriminator is modelled as <c>oneOf</c> over the seven subtypes, each pinning
/// <c>responseType</c> with <c>const</c>. That makes "unknown subtype" a schema failure with a
/// readable path rather than a deserializer exception with a version-specific message.
/// </para>
/// </summary>
public static class DecisionSchema
{
    /// <summary>The schema sent to the model and used to validate its output.</summary>
    public const string Json = """
    {
      "type": "object",
      "required": ["responseType", "interactionId", "headline", "traceReference"],
      "properties": {
        "interactionId": { "type": "string" },
        "headline": { "type": "string" },
        "traceReference": { "type": "string" },
        "nextMoves": {
          "type": "array",
          "maxItems": 4,
          "items": {
            "type": "object",
            "required": ["id", "label"],
            "properties": {
              "id": { "type": "string" },
              "label": { "type": "string" }
            }
          }
        }
      },
      "oneOf": [
        {
          "required": ["responseType", "question", "options"],
          "properties": {
            "responseType": { "const": "clarificationPrompt" },
            "question": { "type": "string" },
            "options": { "type": "array", "minItems": 1, "maxItems": 3, "items": { "type": "string" } }
          }
        },
        {
          "required": ["responseType", "answer"],
          "properties": {
            "responseType": { "const": "directAnswer" },
            "answer": { "type": "string" }
          }
        },
        {
          "required": ["responseType", "meaning", "consequence", "evidenceSummary"],
          "properties": {
            "responseType": { "const": "decisionState" },
            "meaning": { "type": "string" },
            "consequence": { "type": "string" },
            "evidenceSummary": { "type": "string" }
          }
        },
        {
          "required": ["responseType", "meaning", "evidenceSummary"],
          "properties": {
            "responseType": { "const": "analysisConclusion" },
            "meaning": { "type": "string" },
            "evidenceSummary": { "type": "string" }
          }
        },
        {
          "required": ["responseType", "recommendation", "consequence", "confidence", "uncertainty", "evidenceSummary"],
          "properties": {
            "responseType": { "const": "decisionRecommendation" },
            "recommendation": { "type": "string" },
            "consequence": { "type": "string" },
            "confidence": { "type": "number" },
            "uncertainty": { "type": "string" },
            "evidenceSummary": { "type": "string" }
          }
        },
        {
          "required": ["responseType", "recommendation", "proposedActionReference"],
          "properties": {
            "responseType": { "const": "actionProposal" },
            "recommendation": { "type": "string" },
            "proposedActionReference": { "type": "string" },
            "requiresApproval": { "type": "boolean" },
            "approverRole": { "type": "string" }
          }
        },
        {
          "required": ["responseType", "reason"],
          "properties": {
            "responseType": { "const": "limitation" },
            "reason": { "type": "string" },
            "limitationCode": { "type": "string" }
          }
        }
      ]
    }
    """;
}
