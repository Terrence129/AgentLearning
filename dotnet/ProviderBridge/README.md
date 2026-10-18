# ProviderBridge — raw provider call, SSE streaming, retry/backoff

**Week 1 bridge lab.** The Python week-1 lab writes `agentlab/providers/openai_compat.py`; this
app writes the same seam in C#: build the payload, POST it, parse the response, parse an SSE
stream, classify errors, retry the transient ones, and turn usage into money.

Timebox: **30 minutes**. Run `--selftest` first (2 seconds, offline), then `--mock --stream`, then
read `../Bridge.Shared/Providers/` in this order: `ChatCompletionsClient.cs` →
`SseParser.cs` → `RetryHandler.cs`.

---

## Run

```powershell
# 1. offline mechanism checks (no key, no network) — THE GATE
dotnet run --project dotnet/ProviderBridge -- --selftest

# 2. offline demo: scripted 429 -> success, then a streamed response
dotnet run --project dotnet/ProviderBridge -- --mock
dotnet run --project dotnet/ProviderBridge -- --mock --stream

# 3. live (needs BRIDGE_API_KEY; see ../README.md for env vars)
dotnet run --project dotnet/ProviderBridge -- --stream --prompt "Why does streaming exist?"
```

| Flag | Effect |
|---|---|
| `--selftest` | Offline checks; exit 0 = all pass |
| `--mock` | Scripted responses (includes one 429 so the retry path is visible) |
| `--stream` | Use SSE streaming instead of one JSON body |
| `--prompt <text>` | User message |
| `--temperature <n>` / `--max-tokens <n>` | Sampling and output ceiling |

If `BRIDGE_API_KEY` is missing, a live invocation explains the fix and falls back to `--mock`.

---

## What to observe

**1. The payload is a contract, not a suggestion.** The client omits absent optional fields
instead of sending `null` (some compatible hosts reject explicit nulls), and a streaming request
carries both `"stream": true` and `"stream_options": {"include_usage": true}` — without the
second, the response reports no tokens and cost becomes unmeasurable:

```json
{ "model": "deepseek-chat", "messages": [ … ], "stream": true,
  "stream_options": { "include_usage": true } }
```

**2. Streaming is a protocol, not a feature.** `--stream` changes the *response shape*: the body
is `text/event-stream`, and the client must reassemble frames from arbitrary byte slices. The
self-test feeds the parser 3-character slices to prove a frame split mid-field still parses.

**3. Retry is a policy with four traps** (all encoded in `RetryHandler.cs`, all self-tested):

| Trap | Consequence | What the code does |
|---|---|---|
| Retrying a 400/401/403 | Burns money, hides the bug | Retries only 408/429/500/502/503/504 |
| Re-sending the same `HttpRequestMessage` | `InvalidOperationException` | Clones the request (buffering content) per attempt |
| Ignoring `Retry-After` | Hammers a server that told you when to come back | Header wins over computed backoff |
| No jitter | Every client retries at the same instant | Exponential × randomised fraction |

The mock run prints the retry timeline, so you can watch a 429 turn into a success:

```
-- retry timeline
  attempt 1: status=429 -> retrying, backoff=42 ms
  attempt 2: status=200 -> final, backoff=0 ms
```

**4. Tokens become money.** `CostTable` maps model → input/output USD per 1M tokens; the demo
prints `prompt / completion / total` and an estimated cost. Note the asymmetry: output tokens are
typically 3–5× the price of input tokens, which is why output discipline dominates agent cost.

**5. Errors are data.** A provider error is a status + body + a provider code, classified as
transient or not (`ChatCompletionException.IsTransient`). That single flag is what a caller
switches on to decide "retry" vs "fix the request".

---

## Self-test coverage (11 checks)

| Check | Mechanism |
|---|---|
| frames split across chunks | SSE reassembly from 3-char fragments |
| named events, multi-line data, comments | SSE grammar subset |
| final frame with no blank line | truncated-stream handling |
| streamed deltas + usage capture | end-to-end streaming through the real client |
| 429 then success | retry classification and attempt recording |
| `Retry-After` overrides backoff | server-directed pacing |
| 400 is not retried | client-error policy |
| 503 exhausts attempts | bounded retry |
| transport failure retried | no-status failure path |
| request payload flags | `stream`, `include_usage`, roles, no nulls |
| cost arithmetic exact | 1,000 in + 500 out = `$0.00082` |
| provider error code extracted | error taxonomy |

---

## SendOS bridge (30-minute session)

Read these, in this order, with the questions in `docs/sendos/BRIDGE.md` week 1:

1. `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Interfaces/IProviderAdapter.cs` —
   the seam your `ChatCompletionsClient` implements informally.
2. `.../Infrastructure/ExternalServices/OpenAiProviderAdapter.cs` — compare payload build and
   response parse. Which fields does it model that you dropped?
3. `.../Application/Handlers/CompletionHandler.cs` — their retry loop lives in the *handler*
   around the adapter, not in a `DelegatingHandler`. Which is better, and why?
4. `.../Contracts/Routing/ModelBudget.cs` — the budget fields your lab does not enforce
   (week 8 adds them).

**What maps cleanly:** provider seam, payload/response translation, usage capture, retry on
transient status, provider-independent model id.
**What differs:** SendOS routes across candidate models with cost/latency/reliability policies,
retries at the handler level, and validates structured output (the next lab). Its adapters also
normalise provider-specific JSON-output modes — a place where "OpenAI-compatible" stops being
compatible.

---

## Exercises

1. **Measure it.** Run 10 live calls with `--stream` and 10 without; record TTFT, total latency,
   tokens, cost in a table. Write three sentences on when streaming is worth the complexity.
2. **Break the parser.** Feed `SseParser` frames with `\r\n`, split multi-byte UTF-8, and a
   `data:` line containing `\n\n` inside JSON. Which still parse? Which need fixing?
3. **Add an Anthropic adapter** behind the same shape (different system-prompt placement,
   content blocks, tool schema). What does the seam need to grow?
4. **Compare error taxonomies.** Collect the real error bodies for 401, 429, 400 and 500 from
   your provider. Does the `error.code` field always exist? If not, what should the classifier do?
