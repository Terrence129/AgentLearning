# Week 1 Quiz — The Model, Demystified

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10. This quiz feeds the "Explain" gate in [`CHECKPOINTS.md`](../CHECKPOINTS.md).

## Part A — Multiple choice (6 questions)

**Q1.** Your agent sends a 12,000-token prompt and the model replies with `finish_reason: "length"`. What happened?

- A) The model refused for safety reasons
- B) Generation hit the `max_tokens` cap before finishing
- C) The request exceeded the context window
- D) The provider rate-limited the request

**Q2.** Which failure should **not** be retried automatically inside the provider adapter?

- A) HTTP 429 with `Retry-After: 2`
- B) HTTP 503 from the model gateway
- C) HTTP 400 "invalid tool schema"
- D) `httpx.ConnectError` (transient connection reset)

**Q3.** Why must the adapter apply exponential backoff **with jitter** rather than a fixed `time.sleep(1)`?

- A) Jitter makes the request cheaper
- B) Fixed delays are illegal under provider terms
- C) Without randomness, many clients retry in lockstep and amplify the outage
- D) Backoff is required for SSE parsing to work

**Q4.** A streaming response delivers tool-call arguments as many small deltas. What is the correct handling?

- A) Send each delta to the tool immediately
- B) Accumulate deltas per `tool_call.id`, then parse the complete JSON before executing
- C) Disable streaming when tools are present
- D) Parse each delta as JSON and merge dictionaries

**Q5.** Which statement best describes the purpose of a **provider seam**?

- A) It caches prompts to reduce cost
- B) It is the single interface behind which provider-specific wire formats, retries and parsing live
- C) It validates structured output against JSON Schema
- D) It enforces the per-run budget

**Q6.** You want maximum reproducibility for a regression test against a live model. Which settings fit best?

- A) `temperature=1.0, top_p=1.0`
- B) `temperature=0.0` (and leave `top_p` at its default), plus a recorded cassette
- C) `temperature=0.0, top_p=0.0`
- D) `max_tokens=1`

## Part B — Short answer (3 questions)

**Q7.** In two sentences: why do retries belong **inside** the provider adapter rather than in the calling agent loop?

**Q8.** What per-call measurement does the provider adapter return, and where does latency get recorded instead? Why the split?

**Q9.** Prompt caching rewards a specific prompt layout. State the rule and give one practical consequence for an agent whose system prompt contains the current date and time.

## Part C — Spot the bug (1 question)

**Q10.** This retry helper is used for every model call. It "works" in demos. List **three** defects and give the minimal corrected behaviour.

```python
def complete_with_retry(payload, attempts=3):
    for _ in range(attempts):
        try:
            return http.post(API_URL, json=payload)
        except Exception:
            time.sleep(1)
    raise RuntimeError("model call failed")
```

---

## Answers and explanations (do not read until you have attempted all 10)

**Q1 — B.** `finish_reason: "length"` means the output hit `max_tokens` (or the provider's output cap); the prompt itself fitted. A context-window overflow is usually rejected before generation (400) or truncates the input. Safety refusals surface as `content_filter` or a refusal message. *Why it matters: the loop must branch on `finish_reason`, not assume "any response means done".*

**Q2 — C.** 400-level errors caused by malformed requests are terminal; retrying repeats the same invalid request and burns budget. 429/503/transport errors are retryable. *Why it matters: an error taxonomy is the adapter's contract.*

**Q3 — C.** Jitter spreads retries; synchronised retries create a thundering herd and prolong the outage. Backoff also gives the provider time to recover. *Why it matters: retry storms are self-inflicted incidents.*

**Q4 — B.** Tool arguments can be split mid-string across chunks, so per-delta JSON parsing fails. Accumulate by `tool_call.id`, then validate complete arguments. *Why it matters: this is the most common streaming bug in hand-written adapters.*

**Q5 — B.** The seam hides provider differences (payload shape, error codes, SSE framing, auth) behind one protocol, which also enables mocks and later budget-aware routing. It does not itself cache, validate schemas or enforce budgets. *Why it matters: the seam is the basis of testability and provider flexibility.*

**Q6 — B.** `temperature=0` is the closest thing to determinism a hosted model offers; `top_p=0` is invalid/undefined behaviour territory and should be left alone. Even at `temperature=0`, providers are not bit-reproducible, so a cassette is what makes the test stable. *Why it matters: tests must be deterministic even when models are not.*

**Q7 — model answer.** Retry policy depends on provider-specific signals (`Retry-After`, 429 vs 400, SSE mid-stream failures) that only the adapter understands; putting it in the loop makes every caller reimplement it and lets it interact wrongly with loop-level budgets and step accounting. One seam also means one place to count retries and cost.

**Q8 — model answer.** The adapter returns a `CompletionResponse` carrying `Usage` (input/output/cached tokens) plus `finish_reason`, `model` and the raw payload; `Usage` is what cost accounting and budget enforcement consume. `CompletionResponse` has no latency field — wall-clock time is measured by the *caller's* span, and in this repo the week-2 loop emits a `model_call` trace event whose `duration_ms` comes from `Tracer.span(...)`. The split keeps the adapter stateless with respect to timing (a timer inside a retrying adapter would double-count retry and stream waits) while latency stays a property of the observed call in a run.

**Q9 — model answer.** Put stable content first and volatile content last: an identical prefix is what gets cached. If the system prompt embeds the current timestamp, the prefix changes every call and the cache never hits; move the timestamp into the last user/tool message (or round it to a longer bucket).

**Q10 — model answer.** Three defects: (1) it retries **all** exceptions, including terminal 400/auth errors; (2) it uses a fixed 1-second delay with no exponential growth and no jitter; (3) it ignores `Retry-After` and never logs/limits attempts. Bonus: it returns the raw response object without status/error-taxonomy mapping. Minimal fix: classify the exception, retry only retryable classes, sleep `max(Retry-After, base * 2**attempt + random jitter)` with a cap, and raise a typed error after the final attempt.
