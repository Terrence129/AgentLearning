using System.Net;
using System.Net.Http.Headers;

namespace Bridge.Shared.Providers;

/// <summary>
/// Retry policy for provider calls: exponential backoff with jitter, <c>Retry-After</c>
/// honoured, and a hard attempt ceiling.
///
/// <para>
/// <b>Why this exists:</b> a 429 or a 503 is a normal operating condition of a shared inference
/// endpoint, not an exception. Retrying is the cheapest reliability feature in the stack, but
/// it is easy to get wrong in four specific ways, all handled here:
/// </para>
/// <list type="number">
///   <item><description>
///   <b>Retrying an unretryable status hides a bug.</b> Only 408/429/500/502/503/504 are
///   retried. A 400/401/403/422 is a client bug: retrying it burns money and buries the error.
///   </description></item>
///   <item><description>
///   <b>A request cannot be sent twice.</b> <see cref="HttpRequestMessage"/> throws if reused.
///   This handler clones the request (buffering its content) before every retry. Forgetting
///   this is the classic <c>InvalidOperationException: request message was already sent</c>.
///   </description></item>
///   <item><description>
///   <b>Blind exponential backoff fights the server.</b> When <c>Retry-After</c> is present it
///   wins, because the server knows when it will be ready and we do not.
///   </description></item>
///   <item><description>
///   <b>Jitter matters.</b> Without it, every client that saw the same outage retries at the
///   same instant — a thundering herd of your own making.
///   </description></item>
/// </list>
/// <para>
/// SendOS equivalent: <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Handlers/
/// CompletionHandler.cs</c> (<c>HandleRoutedAsync</c>: retry only on transient status, bounded
/// attempts, cancellation terminal) plus the Gateway's <c>CircuitBreaker</c> infrastructure.
/// </para>
/// </summary>
public sealed class RetryHandler : DelegatingHandler
{
    private readonly RetryPolicy _policy;
    private readonly List<RetryAttempt> _attempts = [];

    public RetryHandler(RetryPolicy? policy = null, HttpMessageHandler? innerHandler = null)
        : base(innerHandler ?? new HttpClientHandler())
    {
        _policy = policy ?? RetryPolicy.Default;
    }

    /// <summary>The retries actually performed, for printing and for the self-test to assert on.</summary>
    public IReadOnlyList<RetryAttempt> Attempts => _attempts;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        _attempts.Clear();

        for (var attempt = 1; ; attempt++)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var current = attempt == 1 ? request : await CloneAsync(request, cancellationToken);

            HttpResponseMessage response;
            try
            {
                response = await base.SendAsync(current, cancellationToken).ConfigureAwait(false);
            }
            catch (HttpRequestException ex) when (attempt < _policy.MaxAttempts)
            {
                // Transport failure: no status to inspect, but the same backoff applies.
                var transportDelay = _policy.DelayFor(attempt, retryAfter: null);
                _attempts.Add(new RetryAttempt(attempt, StatusCode: null, ex.Message, transportDelay));
                await Task.Delay(transportDelay, cancellationToken).ConfigureAwait(false);
                continue;
            }

            if (!_policy.IsRetryable(response.StatusCode) || attempt >= _policy.MaxAttempts)
            {
                _attempts.Add(new RetryAttempt(attempt, response.StatusCode, "final", TimeSpan.Zero));
                return response;
            }

            var wait = _policy.DelayFor(attempt, response.Headers.RetryAfter);
            _attempts.Add(new RetryAttempt(attempt, response.StatusCode, "retrying", wait));

            // Dispose before retry: keeping failed responses alive leaks connections.
            response.Dispose();
            await Task.Delay(wait, cancellationToken).ConfigureAwait(false);
        }
    }

    /// <summary>
    /// Copies a request so it can be sent again.
    ///
    /// <para>
    /// The content is buffered to a byte array first. For JSON bodies this is cheap; for a
    /// multi-megabyte upload it is not, which is the honest reason retry logic usually lives
    /// behind a policy that knows whether the body is replayable.
    /// </para>
    /// </summary>
    private static async Task<HttpRequestMessage> CloneAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var clone = new HttpRequestMessage(request.Method, request.RequestUri)
        {
            Version = request.Version,
            VersionPolicy = request.VersionPolicy,
        };

        foreach (var header in request.Headers)
        {
            clone.Headers.TryAddWithoutValidation(header.Key, header.Value);
        }

        if (request.Content is { } content)
        {
            var bytes = await content.ReadAsByteArrayAsync(cancellationToken).ConfigureAwait(false);
            var replacement = new ByteArrayContent(bytes);
            foreach (var header in content.Headers)
            {
                replacement.Headers.TryAddWithoutValidation(header.Key, header.Value);
            }

            clone.Content = replacement;
        }

        return clone;
    }
}

/// <summary>One retry decision, recorded for observability and asserted in the self-test.</summary>
/// <param name="Attempt">1-based attempt number.</param>
/// <param name="StatusCode">HTTP status, or null for a transport failure.</param>
/// <param name="Outcome">"retrying", "final", or the transport error message.</param>
/// <param name="Delay">Backoff waited before the next attempt (zero on the final attempt).</param>
public readonly record struct RetryAttempt(int Attempt, HttpStatusCode? StatusCode, string Outcome, TimeSpan Delay);

/// <summary>The retry settings, isolated from the handler so they can be reasoned about and tested alone.</summary>
public sealed class RetryPolicy
{
    private readonly Random _jitter;

    public RetryPolicy(
        int maxAttempts = 3,
        TimeSpan? baseDelay = null,
        TimeSpan? maxDelay = null,
        double jitterFraction = 0.2,
        int randomSeed = 17)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(maxAttempts, 1);
        ArgumentOutOfRangeException.ThrowIfLessThan(jitterFraction, 0);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(jitterFraction, 1);

        MaxAttempts = maxAttempts;
        BaseDelay = baseDelay ?? TimeSpan.FromMilliseconds(250);
        MaxDelay = maxDelay ?? TimeSpan.FromSeconds(20);
        JitterFraction = jitterFraction;
        _jitter = new Random(randomSeed);
    }

    public static RetryPolicy Default { get; } = new();

    /// <summary>Total attempts including the first. 1 disables retrying.</summary>
    public int MaxAttempts { get; }

    /// <summary>First backoff interval.</summary>
    public TimeSpan BaseDelay { get; }

    /// <summary>Ceiling for any single backoff.</summary>
    public TimeSpan MaxDelay { get; }

    /// <summary>0..1 fraction of the computed delay randomised.</summary>
    public double JitterFraction { get; }

    /// <summary>Statuses worth retrying: the server, not the request, is the problem.</summary>
    public bool IsRetryable(HttpStatusCode status) => status is
        HttpStatusCode.RequestTimeout or
        HttpStatusCode.TooManyRequests or
        HttpStatusCode.InternalServerError or
        HttpStatusCode.BadGateway or
        HttpStatusCode.ServiceUnavailable or
        HttpStatusCode.GatewayTimeout;

    /// <summary>
    /// The wait before the next attempt, honouring <c>Retry-After</c> when the server sent one
    /// (delta-seconds or HTTP-date), otherwise exponential backoff plus jitter.
    /// </summary>
    public TimeSpan DelayFor(int attempt, RetryConditionHeaderValue? retryAfter)
    {
        if (retryAfter is { Delta: { } delta })
        {
            return Clamp(delta);
        }

        if (retryAfter is { Date: { } date })
        {
            var until = date - DateTimeOffset.UtcNow;
            return Clamp(until > TimeSpan.Zero ? until : TimeSpan.Zero);
        }

        var exponent = Math.Pow(2, Math.Max(0, attempt - 1));
        var raw = TimeSpan.FromMilliseconds(BaseDelay.TotalMilliseconds * exponent);
        var jitter = raw.TotalMilliseconds * JitterFraction * (_jitter.NextDouble() * 2 - 1);
        return Clamp(raw + TimeSpan.FromMilliseconds(jitter));
    }

    private TimeSpan Clamp(TimeSpan value)
    {
        if (value < TimeSpan.Zero)
        {
            return TimeSpan.Zero;
        }

        return value > MaxDelay ? MaxDelay : value;
    }
}
