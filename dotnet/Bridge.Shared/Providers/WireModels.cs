using System.Text.Json.Serialization;

namespace Bridge.Shared.Providers;

/// <summary>
/// The wire shapes of the OpenAI-compatible chat-completions API, kept deliberately close to
/// the JSON rather than wrapped in a framework abstraction.
///
/// <para>
/// This is the same decision <c>agentlab/types.py</c> makes in Python and the same one SendOS
/// makes in <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Contracts</c>: learn the wire
/// format once and every SDK becomes a thin wrapper you can read. Only fields the labs use are
/// modelled; everything else is dropped on read (never sent as <c>null</c> — see
/// <see cref="ChatCompletionRequest"/>).
/// </para>
/// </summary>
public sealed record ChatMessage(string Role, string Content)
{
    public static ChatMessage System(string content) => new("system", content);
    public static ChatMessage User(string content) => new("user", content);
    public static ChatMessage Assistant(string content) => new("assistant", content);
}

/// <summary>
/// A chat-completions request body.
///
/// <para><b>Two rules encoded here:</b></para>
/// <list type="number">
///   <item><description>
///   Optional fields are omitted, not serialised as <c>null</c>. Several providers reject
///   <c>"temperature": null</c> even though the schema says the property is nullable — an
///   absent field and an explicitly-null field are not the same request.
///   </description></item>
///   <item><description>
///   <c>Stream</c> is part of the request, not a separate method on the wire: streaming is a
///   protocol choice that changes the response <i>shape</i> (SSE instead of one JSON body).
///   </description></item>
/// </list>
/// </summary>
public sealed record ChatCompletionRequest
{
    [JsonPropertyName("model")]
    public required string Model { get; init; }

    [JsonPropertyName("messages")]
    public required IReadOnlyList<ChatMessage> Messages { get; init; }

    [JsonPropertyName("stream")]
    public bool? Stream { get; init; }

    [JsonPropertyName("temperature")]
    public double? Temperature { get; init; }

    [JsonPropertyName("max_tokens")]
    public int? MaxTokens { get; init; }

    /// <summary>
    /// OpenAI-compatible "JSON mode" marker. The subset of providers the labs target understand
    /// <c>{"type":"json_object"}</c>; the schema is enforced by this repo's validator, not by the
    /// provider, because not all compatible hosts implement schema-constrained decoding.
    /// </summary>
    [JsonPropertyName("response_format")]
    public ResponseFormat? ResponseFormat { get; init; }

    /// <summary>
    /// Asks the provider to include token usage in the final streamed chunk. Without this a
    /// streamed call reports no usage and cost becomes unmeasurable — one of the small wire
    /// details that separates a demo from an instrumented client.
    /// </summary>
    [JsonPropertyName("stream_options")]
    public StreamOptions? StreamOptions { get; init; }
}

/// <summary>Provider JSON-output mode.</summary>
public sealed record ResponseFormat
{
    [JsonPropertyName("type")]
    public required string Type { get; init; }

    public static ResponseFormat JsonObject { get; } = new() { Type = "json_object" };
}

/// <summary>Stream options accepted by OpenAI-compatible hosts.</summary>
public sealed record StreamOptions
{
    [JsonPropertyName("include_usage")]
    public bool IncludeUsage { get; init; }
}

/// <summary>A non-streamed completion response.</summary>
public sealed record ChatCompletionResponse
{
    [JsonPropertyName("id")]
    public string? Id { get; init; }

    [JsonPropertyName("model")]
    public string? Model { get; init; }

    [JsonPropertyName("choices")]
    public IReadOnlyList<ChatChoice> Choices { get; init; } = [];

    [JsonPropertyName("usage")]
    public TokenUsage? Usage { get; init; }

    /// <summary>The first choice's text, or an empty string when the provider returned no choices.</summary>
    public string FirstText() =>
        Choices.Count == 0 ? string.Empty : Choices[0].Message?.Content ?? string.Empty;

    /// <summary>Why generation stopped: <c>stop</c>, <c>length</c>, <c>content_filter</c>, …</summary>
    public string? FinishReason() => Choices.Count == 0 ? null : Choices[0].FinishReason;
}

public sealed record ChatChoice
{
    [JsonPropertyName("index")]
    public int Index { get; init; }

    [JsonPropertyName("message")]
    public ChatMessage? Message { get; init; }

    [JsonPropertyName("finish_reason")]
    public string? FinishReason { get; init; }
}

public sealed record TokenUsage
{
    [JsonPropertyName("prompt_tokens")]
    public int PromptTokens { get; init; }

    [JsonPropertyName("completion_tokens")]
    public int CompletionTokens { get; init; }

    [JsonPropertyName("total_tokens")]
    public int TotalTokens { get; init; }
}

/// <summary>One parsed delta from a streamed response. Content can be null on role-only chunks.</summary>
public sealed record ChatDelta
{
    [JsonPropertyName("content")]
    public string? Content { get; init; }
}

public sealed record ChatDeltaChoice
{
    [JsonPropertyName("index")]
    public int Index { get; init; }

    [JsonPropertyName("delta")]
    public ChatDelta? Delta { get; init; }

    [JsonPropertyName("finish_reason")]
    public string? FinishReason { get; init; }
}

/// <summary>A single streamed chunk. <c>Usage</c> is only present on the final chunk when requested.</summary>
public sealed record ChatCompletionChunk
{
    [JsonPropertyName("id")]
    public string? Id { get; init; }

    [JsonPropertyName("model")]
    public string? Model { get; init; }

    [JsonPropertyName("choices")]
    public IReadOnlyList<ChatDeltaChoice> Choices { get; init; } = [];

    [JsonPropertyName("usage")]
    public TokenUsage? Usage { get; init; }
}
