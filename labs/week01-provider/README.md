# Week 1 lab — The model, demystified (provider seam)

## 1. Why this week exists

Most agent bugs are blamed on the model but live in the adapter: a tool call whose JSON arguments were never parsed, a 429 retried forever, a stream that silently loses the tool-call fragments after the first one, a 400 that gets retried and burns budget. This week you build the one layer that owns all of that — the provider seam — so the rest of the course never touches vendor-specific wire formats, retries or SSE frames again. You will also measure tokens and cached tokens, because from week 2 onward every run is budgeted.

## 2. Prerequisites & time budget

- **8–10 hours** (build sessions ~5 h, reading ~2 h, SendOS bridge + review ~2 h).
- Foundation green: `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux) runs `tests/` (not `tests/week*`) and must pass.
- Read first: [`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md) (25 min), [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §1.3 and §1.6, [`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §3.
- You need no API key for the tests. One live call is recommended for the lab artifact (cost cap: a fraction of a cent).

## 3. The spec

Implement in [`agentlab/providers/openai_compat.py`](../../agentlab/providers/openai_compat.py). The docstrings there are the contract; the tests are the proof.

| Member | Contract |
|---|---|
| `_build_payload(request, *, stream)` | Request → JSON body: model fallback, message mapping, optional fields only when set, tools omitted when empty, `stream_options={"include_usage": True}` when streaming, `extra` merged **last**. |
| `_parse_response(payload, *, fallback_model)` | First choice → assistant `Message` (text and/or tool calls), parsed JSON arguments, `Usage` incl. `cached_input_tokens`, `finish_reason`, raw payload retained; malformed arguments become `ProviderError`; no `choices` → `ProviderError`. |
| `complete(request)` | POST `{base_url}/chat/completions`; at most `max_retries + 1` attempts; retry `RETRYABLE_STATUS` and `httpx.TransportError`; exact `Retry-After` when numeric, else exponential backoff with jitter; no retry for other 4xx; every failure becomes `ProviderError(status, retryable, retry_after, truncated body)`; never leaks `httpx` types. |
| `stream(request)` | POST with `stream=True`; parse SSE lines (`data:` only, comments/`event:` ignored, `[DONE]` terminates), tolerate frames split across chunks, forward tool-call argument fragments verbatim, emit `text` / `tool_call_delta` / `usage` events and exactly one `done` with `finish_reason`; mid-stream error frames and non-200 statuses raise `ProviderError`; no retries mid-stream. |

Definition of done includes the equivalence contract: `assemble_stream(provider.stream(req))` equals `provider.complete(req)` for the same logical response.

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week01 -m week -q   # all green
.\.venv\Scripts\ruff.exe check agentlab/providers/openai_compat.py
```

```bash
# macOS / Linux
uv run pytest tests/week01 -m week -q   # all green
uv run ruff check agentlab/providers/openai_compat.py
```

Optional live artifact (needs `.env` with a provider key): run `.\tasks.ps1 chat` (Windows) / `./tasks.sh chat` (macOS/Linux), complete one streaming turn, and confirm the printed per-turn token/cost line. Compare `stream` vs `--no-stream` answers for the same prompt.

## 5. Hints (read in order; stop as soon as you are unblocked)

1. Re-read the four docstrings and `tests/week01/` top to bottom before writing code. Each test encodes one wire fact.
2. `_build_payload` and `_parse_response` are pure functions. Implement and test them first; `complete` and `stream` are plumbing around them.
3. For retries, keep one `last_error: ProviderError` and decide on `attempt >= max_retries`; when `backoff_base == 0`, sleep 0 (tests patch `time.sleep` and will fail if you skip the call on *non-zero* delays only).
4. In `stream`, iterate **lines**, not chunks: `response.iter_lines()` already buffers partial lines. A frame split across chunks is only a problem if you treat each network chunk as a complete frame.
5. Tool-call deltas are not JSON. Forward `function.arguments` fragments exactly as received; the provided `assemble_stream` concatenates them.
6. The `done` event must be emitted on `[DONE]` **and** on a stream that ends without it — track `done_emitted` and `last_finish_reason`.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| `KeyError: 'choices'` / `IndexError` in parsing | You indexed `payload["choices"][0]` before checking for an empty list — the contract requires `ProviderError`. |
| A 400 test times out or counts 4 requests | Your retry predicate retries every non-2xx instead of `RETRYABLE_STATUS` only. |
| Retry-After test sees `2.4` or `2.5+` | You added jitter to a server-requested delay, or slept `retry_after * 2**attempt`. Obey `Retry-After` exactly. |
| Streaming test assembles only the first tool call | You emit the delta only when `delta.tool_calls` has an `id`; continuation frames carry `index`/`arguments` without `id`. |
| `assemble_stream` equality fails but text matches | Missing/duplicated `usage` event, or `done` emitted twice, or `finish_reason` defaulted to `stop` on a tool-call stream. |

## 7. SendOS bridge

Read `apps/Send.Model.Adapter/src/**` (the provider-independent completion path) and the relevant parts of [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.5 and §4.4. Focus on `StructuredCompletionHandler`, `JsonSchemaValidator` and `CompletionHandler.cs:60-210` only as *contrast* — you build those in week 3.

Answer in 5 bullets in your weekly review:

1. Which three responsibilities does your provider seam share with Send's model adapters (wire mapping, retry/error taxonomy, usage/cost accounting)?
2. Where does Send's adapter stop being "just an adapter" (routing, structured completion, cancellation, budget) — and why is splitting those concerns the right call?
3. What would break in SendOS if retries lived in the agent loop instead of the adapter? Name a concrete duplicate-side-effect scenario.

## 8. Stretch

1. **Anthropic adapter behind the same `Provider` protocol.** Different system-prompt placement, content blocks and tool schema; map them into `Message`/`ToolSpec` so no caller changes. Write 150 words on which seams held and which leaked.
2. **Retry observability.** Count retries and time slept inside the adapter (no logging), expose a `stats` dict, and make `complete` report total attempts per call. Argue whether that belongs in the trace instead.

## 9. Reflection (weekly review)

1. **Conceptual:** Why is streaming "a protocol, not a feature"? What does a streamed response have to guarantee for `assemble_stream` equivalence to be meaningful?
2. **Architectural:** Which decisions belong in the provider seam versus the agent loop? Give an example this week placed correctly and one that later weeks must move upward.
3. **Transfer:** Your C# adapter and this Python adapter both hide vendors. Which concern is harder to keep behind the seam in a strongly typed .NET codebase, and why?
