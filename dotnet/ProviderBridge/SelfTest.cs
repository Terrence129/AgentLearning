using System.Net;
using Bridge.Shared;
using Bridge.Shared.Configuration;
using Bridge.Shared.Providers;
using Bridge.Shared.Testing;

namespace ProviderBridge;

/// <summary>
/// Offline mechanism checks for the week-1 bridge lab.
///
/// <para>
/// <b>Why a self-test instead of a test project:</b> the lab must build with no external NuGet
/// packages, and xUnit is a package. A 150-line runner that returns an exit code gives the same
/// gate — red before the mechanism works, green after — and is readable in one screen. The real
/// Python equivalent is <c>pytest tests/week01 -m week</c>.
/// </para>
/// <para>
/// Every check is deterministic: no network, no sleeps longer than a few milliseconds (the
/// retry policy is configured with tiny backoffs), no random assertions. If a check fails, the
/// mechanism really is broken.
/// </para>
/// </summary>
internal static class SelfTest
{
    private static int _failures;

    public static async Task<int> RunAsync()
    {
        ConsoleUi.Title("ProviderBridge — self-test (offline)");
        ConsoleUi.Dim("No API key, no network. Each check proves one week-1 mechanism.");
        Console.WriteLine();

        _failures = 0;

        await CheckAsync("sse parser reassembles frames split across chunks", async () =>
        {
            var parser = new SseParser();
            var text =
                ": heartbeat\n\n" +
                "event: delta\ndata: {\"a\":1}\n\n" +
                "data: line1\ndata: line2\n\n" +
                "data: [DONE]\n\n";

            var events = new List<SseEvent>();
            foreach (var chunk in SseParser.ChunkForTest(text, 3))
            {
                events.AddRange(parser.Feed(chunk));
            }

            events.AddRange(parser.Flush());

            Assert(events.Count == 3, $"expected 3 events, got {events.Count}");
            Assert(events[0].Event == "delta", $"expected named event 'delta', got '{events[0].Event}'");
            Assert(events[0].Data == "{\"a\":1}", $"unexpected payload '{events[0].Data}'");
            Assert(events[1].Data == "line1\nline2", "multi-line data must join with a newline");
            Assert(events[2].Data == "[DONE]", "the terminator frame must survive chunking");
            await Task.CompletedTask;
        });

        await CheckAsync("sse parser flushes a final frame with no blank line", async () =>
        {
            var parser = new SseParser();
            var events = parser.Feed("data: {\"last\":true}").ToList();
            events.AddRange(parser.Flush());

            Assert(events.Count == 1, $"expected the buffered frame on flush, got {events.Count} events");
            Assert(events[0].Data == "{\"last\":true}", "flush must not discard a partial final frame");
            await Task.CompletedTask;
        });

        await CheckAsync("streaming client assembles deltas and captures usage", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueSse(MockStream, chunkSize: 11);

            using var client = new ChatCompletionsClient(BridgeSettings.ForOfflineFake(), handler);
            var text = string.Empty;
            await foreach (var delta in client.StreamAsync([ChatMessage.User("hi")]))
            {
                text += delta;
            }

            Assert(text == "Hello stream", $"expected 'Hello stream', got '{text}'");
            Assert(client.LastStreamUsage is { TotalTokens: 30 }, "usage from the final chunk must be captured");
            Assert(client.LastFinishReason == "stop", $"expected finish_reason 'stop', got '{client.LastFinishReason}'");
            Assert(handler.RequestCount == 1, $"expected 1 request, got {handler.RequestCount}");
        });

        await CheckAsync("retries 429 then succeeds", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueStatus(HttpStatusCode.TooManyRequests, """{"error":{"message":"slow down","code":"rate_limit_exceeded"}}""");
            handler.EnqueueJson(OneResponse("ok after retry"));

            using var client = NewClient(handler);
            var response = await client.CompleteAsync([ChatMessage.User("hi")]);

            Assert(response.FirstText() == "ok after retry", "the second response should be returned");
            Assert(handler.RequestCount == 2, $"expected 2 transport calls, got {handler.RequestCount}");
            Assert(client.RetryAttempts.Count == 2, "both attempts should be recorded");
            Assert(client.RetryAttempts[0].StatusCode == HttpStatusCode.TooManyRequests, "first attempt should be the 429");
        });

        await CheckAsync("a Retry-After header overrides exponential backoff", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueStatus(HttpStatusCode.TooManyRequests, retryAfterSeconds: 0);
            handler.EnqueueJson(OneResponse("ok"));

            using var client = NewClient(handler, maxAttempts: 3);
            await client.CompleteAsync([ChatMessage.User("hi")]);

            var firstWait = client.RetryAttempts[0].Delay;
            Assert(firstWait <= TimeSpan.FromMilliseconds(50), $"Retry-After: 0 should mean ~0 ms, got {firstWait.TotalMilliseconds} ms");
        });

        await CheckAsync("does not retry a client error (400)", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueStatus(HttpStatusCode.BadRequest, """{"error":{"message":"bad request"}}""");

            using var client = NewClient(handler);
            try
            {
                await client.CompleteAsync([ChatMessage.User("hi")]);
                throw new InvalidOperationException("expected ChatCompletionException");
            }
            catch (ChatCompletionException ex)
            {
                Assert(!ex.IsTransient, "400 must be classified as non-transient");
                Assert(ex.Status == HttpStatusCode.BadRequest, "status must be preserved");
            }

            Assert(handler.RequestCount == 1, $"a 400 must not be retried; got {handler.RequestCount} calls");
        });

        await CheckAsync("exhausts retries and surfaces the final failure", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueStatus(HttpStatusCode.ServiceUnavailable);
            handler.EnqueueStatus(HttpStatusCode.ServiceUnavailable);
            handler.EnqueueStatus(HttpStatusCode.ServiceUnavailable);

            using var client = NewClient(handler, maxAttempts: 3);
            try
            {
                await client.CompleteAsync([ChatMessage.User("hi")]);
                throw new InvalidOperationException("expected ChatCompletionException");
            }
            catch (ChatCompletionException ex)
            {
                Assert(ex.IsTransient, "503 must be classified as transient");
            }

            Assert(handler.RequestCount == 3, $"expected exactly 3 attempts, got {handler.RequestCount}");
        });

        await CheckAsync("transport failures are retried", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueTransportFailure("socket reset");
            handler.EnqueueJson(OneResponse("recovered"));

            using var client = NewClient(handler);
            var response = await client.CompleteAsync([ChatMessage.User("hi")]);

            Assert(response.FirstText() == "recovered", "a transport failure should be retried");
            Assert(handler.RequestCount == 2, $"expected 2 calls, got {handler.RequestCount}");
        });

        await CheckAsync("streaming request carries stream + include_usage flags", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueSse(MockStream, chunkSize: 64);

            using var client = new ChatCompletionsClient(BridgeSettings.ForOfflineFake(), handler);
            await foreach (var _ in client.StreamAsync(
                               [ChatMessage.System("be brief"), ChatMessage.User("hello")]))
            {
            }

            var body = handler.RequestBodies[0];
            Assert(body.Contains("\"stream\":true", StringComparison.Ordinal), $"stream flag missing from payload: {body}");
            Assert(body.Contains("\"include_usage\":true", StringComparison.Ordinal), "stream_options.include_usage missing");
            Assert(body.Contains("\"role\":\"system\"", StringComparison.Ordinal), "system message must be on the wire");
            Assert(!body.Contains("null", StringComparison.Ordinal), "optional fields must be omitted, not sent as null");
        });

        await CheckAsync("cost table arithmetic is exact", async () =>
        {
            var cost = CostTable.Estimate("deepseek-chat", new TokenUsage
            {
                PromptTokens = 1_000,
                CompletionTokens = 500,
                TotalTokens = 1_500,
            });

            // 1,000/1M × 0.27 + 500/1M × 1.10 = 0.00027 + 0.00055
            Assert(cost == 0.00082m, $"expected 0.00082, got {cost}");
            await Task.CompletedTask;
        });

        await CheckAsync("provider error code is extracted from the body", async () =>
        {
            var handler = new ScriptedHttpMessageHandler();
            handler.EnqueueStatus(
                HttpStatusCode.TooManyRequests,
                """{"error":{"message":"slow down","code":"rate_limit_exceeded"}}""");
            handler.EnqueueJson(OneResponse("ok"));

            using var client = NewClient(handler);
            await client.CompleteAsync([ChatMessage.User("hi")]);

            // The exception only escapes when retries are exhausted; here it is swallowed by the
            // retry. Assert the classification directly through a no-retry client instead.
            using var strict = NewClient(handler: new ScriptedHttpMessageHandler()
                .EnqueueStatus(HttpStatusCode.TooManyRequests, """{"error":{"message":"slow down","code":"rate_limit_exceeded"}}"""),
                maxAttempts: 1);
            try
            {
                await strict.CompleteAsync([ChatMessage.User("hi")]);
                throw new InvalidOperationException("expected ChatCompletionException");
            }
            catch (ChatCompletionException ex)
            {
                Assert(ex.ProviderCode == "rate_limit_exceeded", $"expected provider code, got '{ex.ProviderCode}'");
                Assert(ex.Message.Contains("slow down", StringComparison.Ordinal), "provider message should reach the caller");
            }
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

    private const string MockStream =
        "data: {\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\"}}]}\n\n" +
        "data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":\"Hello \"}}]}\n\n" +
        "data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":\"stream\"}}]}\n\n" +
        "data: {\"choices\":[{\"index\":0,\"delta\":{},\"finish_reason\":\"stop\"}]}\n\n" +
        "data: {\"choices\":[],\"usage\":{\"prompt_tokens\":10,\"completion_tokens\":20,\"total_tokens\":30}}\n\n" +
        "data: [DONE]\n\n";

    private static ChatCompletionsClient NewClient(ScriptedHttpMessageHandler handler, int maxAttempts = 3) =>
        new(
            BridgeSettings.ForOfflineFake(),
            handler,
            new RetryPolicy(
                maxAttempts: maxAttempts,
                baseDelay: TimeSpan.FromMilliseconds(5),
                maxDelay: TimeSpan.FromMilliseconds(50)));

    private static string OneResponse(string text) => $$"""
    {
      "id": "chatcmpl-test",
      "model": "mock-model",
      "choices": [{ "index": 0, "message": { "role": "assistant", "content": {{System.Text.Json.JsonSerializer.Serialize(text)}} }, "finish_reason": "stop" }],
      "usage": { "prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10 }
    }
    """;

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
