using System.Text;

namespace Bridge.Shared.Providers;

/// <summary>
/// A Server-Sent-Events frame parser.
///
/// <para>
/// <b>Why this exists:</b> HTTP responses are byte streams, not "messages". A single
/// <c>ReadAsync</c> can return half a frame, one frame, or six frames; a UTF-8 character can
/// be split across reads; and the SSE grammar is line-based, not JSON-based. The number one
/// streaming bug in agent code is assuming one read equals one event.
/// </para>
/// <para>
/// The parser is a byte-fed state machine with an internal buffer, so callers can hand it
/// arbitrary fragments (as <see cref="ChatCompletionsClient"/> does) and receive only
/// <i>complete</i> events. See <c>--selftest</c> for the fragmented-frame cases it must
/// survive: frame split mid-field, split mid-frame, CRLF line endings, multi-line
/// <c>data:</c>, comment lines, and a trailing frame with no blank line.
/// </para>
/// <para>
/// SSE spec points implemented (the subset a chat-completions stream actually uses):
/// <list type="bullet">
///   <item><c>data:</c> — payload; multiple data lines in one event are joined with <c>\n</c>.</item>
///   <item><c>event:</c> — event name, defaults to <c>message</c>.</item>
///   <item><c>:</c> — a comment/heartbeat line, ignored.</item>
///   <item><c>id:</c>/<c>retry:</c> — parsed but unused here (documented, not silently dropped).</item>
///   <item>Blank line — dispatches the accumulated event.</item>
/// </list>
/// </para>
/// <para>
/// SendOS equivalent: the SSE progress path in <c>apps/Send.Intelligence.Gateway</c>
/// (<c>Progress/InMemoryProgressStream.cs</c>) and the streaming contracts in
/// <c>apps/Send.Model.Adapter/src/Send.Model.Adapter.Contracts/Events/</c>. The line-parsing
/// problem is identical; the transport is not.
/// </para>
/// </summary>
public sealed class SseParser
{
    private readonly StringBuilder _pending = new();
    private readonly StringBuilder _data = new();
    private string _eventName = "message";
    private string? _lastId;

    /// <summary>
    /// Feeds a text fragment and returns every event that became complete.
    ///
    /// <para>
    /// The caller may pass <c>null</c>/empty to mean "no more bytes" only via
    /// <see cref="Flush"/>; a zero-length feed is legal and returns nothing.
    /// </para>
    /// </summary>
    public IReadOnlyList<SseEvent> Feed(string? chunk)
    {
        var events = new List<SseEvent>();
        if (string.IsNullOrEmpty(chunk))
        {
            return events;
        }

        _pending.Append(chunk);
        Consume(events);
        return events;
    }

    /// <summary>
    /// Signals end of stream and dispatches any buffered event that was not terminated by a
    /// blank line. Real servers usually end with one; a truncated connection often does not,
    /// and discarding the last partial frame loses the final token.
    /// </summary>
    public IReadOnlyList<SseEvent> Flush()
    {
        var events = new List<SseEvent>();
        Consume(events);

        // Whatever is left is a final line that never got its newline (truncated or a server
        // that omits the trailing blank line). Process it rather than dropping it.
        if (_pending.Length > 0)
        {
            var finalLine = _pending.ToString().TrimEnd('\r');
            _pending.Clear();
            ProcessLine(finalLine, events);
        }

        Dispatch(events);
        return events;
    }

    private void Consume(List<SseEvent> events)
    {
        while (true)
        {
            var newlineIndex = IndexOfNewline(_pending);
            if (newlineIndex < 0)
            {
                break;
            }

            var line = _pending.ToString(0, newlineIndex).TrimEnd('\r');
            _pending.Remove(0, newlineIndex + 1);
            ProcessLine(line, events);
        }
    }

    /// <summary>Applies one SSE line (or the blank line that terminates an event) to parser state.</summary>
    private void ProcessLine(string line, List<SseEvent> events)
    {
        if (line.Length == 0)
        {
            Dispatch(events);
            return;
        }

        if (line[0] == ':')
        {
            // Comment / heartbeat. Deliberately ignored, but the parse must not break on it.
            return;
        }

        var colon = line.IndexOf(':');
        var field = colon < 0 ? line : line[..colon];
        var value = colon < 0 ? string.Empty : line[(colon + 1)..];
        if (value.StartsWith(' '))
        {
            value = value[1..];
        }

        switch (field)
        {
            case "data":
                if (_data.Length > 0)
                {
                    _data.Append('\n');
                }

                _data.Append(value);
                break;
            case "event":
                _eventName = value.Length == 0 ? "message" : value;
                break;
            case "id":
                _lastId = value;
                break;
            case "retry":
                // Reconnection hint; intentionally not used by this synchronous client.
                break;
            default:
                // Unknown field: ignore per spec.
                break;
        }
    }

    private void Dispatch(List<SseEvent> events)
    {
        // A frame with no data line is not dispatched (spec), except that an explicit event
        // name with empty data is still information we choose to surface.
        if (_data.Length == 0 && _eventName == "message")
        {
            _eventName = "message";
            return;
        }

        events.Add(new SseEvent(_eventName, _data.ToString(), _lastId));
        _data.Clear();
        _eventName = "message";
    }

    private static int IndexOfNewline(StringBuilder buffer)
    {
        for (var i = 0; i < buffer.Length; i++)
        {
            if (buffer[i] == '\n')
            {
                return i;
            }
        }

        return -1;
    }

    /// <summary>
    /// Splits a text into single-line fragments at arbitrary points. Exists so the self-test can
    /// prove the parser tolerates real socket chunking rather than line-aligned test input.
    /// </summary>
    public static IEnumerable<string> ChunkForTest(string text, int size)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(size, 1);
        for (var i = 0; i < text.Length; i += size)
        {
            yield return text.Substring(i, Math.Min(size, text.Length - i));
        }
    }
}

/// <summary>One complete SSE event.</summary>
/// <param name="Event">Event name (<c>message</c> when the server sent none).</param>
/// <param name="Data">Payload with multi-line data joined by newlines.</param>
/// <param name="Id">Last <c>id:</c> value, or null. Unused today; kept so reconnection logic has a place to live.</param>
public readonly record struct SseEvent(string Event, string Data, string? Id);
