using System.Net;
using System.Net.Http.Headers;
using System.Text;

namespace Bridge.Shared.Testing;

/// <summary>
/// A scripted HTTP transport: replay a list of responses instead of calling a provider.
///
/// <para>
/// <b>Why this exists:</b> every interesting behaviour in the bridge labs — retry, streaming
/// fragmentation, malformed model output, error taxonomy — is hard to trigger on demand against
/// a real endpoint and impossible to trigger reliably in CI. A scripted transport makes each of
/// them deterministic, free and offline. SendOS uses the same technique at scale: its unit tests
/// substitute provider adapters and HTTP clients rather than dialling out.
/// </para>
/// <para>
/// Responses are consumed in order. Exhausting the script throws, because a test that silently
/// accepts extra requests is a test that cannot catch a retry loop that never stops.
/// </para>
/// <para>
/// This type lives in the shared library so <c>ProviderBridge --selftest</c> and
/// <c>StructuredDecisionBridge --selftest</c> can both prove their mechanisms with no network —
/// which is also how the week-1/week-3 Python tests stay offline.
/// </para>
/// </summary>
public sealed class ScriptedHttpMessageHandler : HttpMessageHandler
{
    private readonly Queue<Func<HttpRequestMessage, HttpResponseMessage>> _script = new();
    private readonly List<string> _requestBodies = [];

    /// <summary>How many requests actually reached the transport (retries included).</summary>
    public int RequestCount { get; private set; }

    /// <summary>The request bodies received, in order, for assertions about payload shape.</summary>
    public IReadOnlyList<string> RequestBodies => _requestBodies;

    /// <summary>Records a successful JSON response.</summary>
    public ScriptedHttpMessageHandler EnqueueJson(string json, HttpStatusCode status = HttpStatusCode.OK)
    {
        _script.Enqueue(_ => new HttpResponseMessage(status)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json"),
        });
        return this;
    }

    /// <summary>
    /// Records an SSE response whose body is delivered in small chunks.
    ///
    /// <para>
    /// The deliberate fragmentation is the point: a real socket hands you arbitrary slices, and a
    /// parser tested only with whole frames is a parser that breaks on the first real response.
    /// </para>
    /// </summary>
    public ScriptedHttpMessageHandler EnqueueSse(string sseText, int chunkSize = 7)
    {
        _script.Enqueue(_ =>
        {
            var content = new StreamContent(new ChunkedTextStream(sseText, chunkSize));
            content.Headers.ContentType = new MediaTypeHeaderValue("text/event-stream");
            return new HttpResponseMessage(HttpStatusCode.OK) { Content = content };
        });
        return this;
    }

    /// <summary>Records an error response, optionally with a <c>Retry-After</c> header.</summary>
    public ScriptedHttpMessageHandler EnqueueStatus(
        HttpStatusCode status,
        string body = "",
        int? retryAfterSeconds = null)
    {
        _script.Enqueue(_ =>
        {
            var response = new HttpResponseMessage(status)
            {
                Content = new StringContent(body, Encoding.UTF8, "application/json"),
            };

            if (retryAfterSeconds is { } seconds)
            {
                response.Headers.RetryAfter = new RetryConditionHeaderValue(TimeSpan.FromSeconds(seconds));
            }

            return response;
        });
        return this;
    }

    /// <summary>Records a transport-level failure (no HTTP response at all).</summary>
    public ScriptedHttpMessageHandler EnqueueTransportFailure(string message = "connection reset by peer")
    {
        _script.Enqueue(_ => throw new HttpRequestException(message));
        return this;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        RequestCount++;

        if (request.Content is { } content)
        {
            _requestBodies.Add(await content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false));
        }
        else
        {
            _requestBodies.Add(string.Empty);
        }

        if (_script.Count == 0)
        {
            throw new InvalidOperationException(
                $"ScriptedHttpMessageHandler has no response for request #{RequestCount}. " +
                "A retry likely fired more times than the script expected.");
        }

        return _script.Dequeue()(request);
    }

    /// <summary>
    /// A read-only stream over text that returns at most <c>chunkSize</c> bytes per read.
    /// Simulates socket fragmentation without a socket.
    /// </summary>
    private sealed class ChunkedTextStream : Stream
    {
        private readonly byte[] _bytes;
        private readonly int _chunkSize;
        private int _offset;

        public ChunkedTextStream(string text, int chunkSize)
        {
            _bytes = Encoding.UTF8.GetBytes(text);
            _chunkSize = Math.Max(1, chunkSize);
        }

        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => _bytes.Length;

        public override long Position
        {
            get => _offset;
            set => throw new NotSupportedException();
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            var remaining = _bytes.Length - _offset;
            if (remaining <= 0)
            {
                return 0;
            }

            var take = Math.Min(Math.Min(count, _chunkSize), remaining);
            Array.Copy(_bytes, _offset, buffer, offset, take);
            _offset += take;
            return take;
        }

        public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var remaining = _bytes.Length - _offset;
            if (remaining <= 0)
            {
                return ValueTask.FromResult(0);
            }

            var take = Math.Min(Math.Min(buffer.Length, _chunkSize), remaining);
            _bytes.AsMemory(_offset, take).CopyTo(buffer);
            _offset += take;
            return ValueTask.FromResult(take);
        }

        public override void Flush() { }
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
    }
}
