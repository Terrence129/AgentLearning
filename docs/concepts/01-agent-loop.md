# 01 — The Agent Loop

> **Weeks 1–2 · just-in-time concept note.** Read before the labs (~25 min): [provider seam](../../labs/week01-provider/README.md), then [agent loop](../../labs/week02-agent-loop/README.md). You do not need framework knowledge. You need to know exactly what goes over the wire, where state lives, and how the loop stops.

## The failure mode this prevents

An agent that never ends, and a bill that does. A task starts looping: the model keeps calling the same search tool, each result is appended to the transcript, every iteration grows the context and costs money. Nothing checks steps, tokens, dollars or repeated calls, so after forty iterations you have a 180k-token transcript, a `$6` charge on a `$0.50`-budget task, and no answer — and because you logged only the final response, you cannot say which step went wrong. The second version of the same bug is quieter: the model asks for a tool (`finish_reason="tool_calls"`), your code reads `response.text` (empty), treats it as the final answer, and the agent replies nothing. The third is a retry storm: a 429 is caught inside the loop and the *whole step* — model call plus tool side effect — is retried, so the write happens twice.

Weeks 1–2 make these structurally impossible: a typed provider seam that owns retries, a loop that checks budgets at the top of every iteration, tool errors fed back as observations, and a trace that records every step.

## If you remember five things

> 1. **The model is stateless.** One call is `(messages, tools) → one assistant message`. The conversation lives in *your* loop, not in the provider.
> 2. **`finish_reason` is a control signal, not metadata.** `stop` ends; `tool_calls` dispatches; `length` means truncated; `content_filter` is a policy stop; `error` is retryable or not depending on the error class.
> 3. **Budgets belong at the top of the iteration** (`steps`, tokens in/out, USD, wall clock), and a no-progress detector is worth more than a bigger `max_steps`.
> 4. **Tool failures are observations, not exceptions.** The model sees `ERROR: ...` text as a tool message and can recover; a raised exception usually cannot.
> 5. **Streaming is a transport protocol and it is not resumable.** Tool-call arguments arrive as fragments; a broken stream is retried as a new request, not replayed.

## The model in one page

### What actually goes over the wire

Every provider you will meet — OpenAI, DeepSeek, Anthropic behind a thin adapter — reduces to four roles and two link fields ([`agentlab/types.py`](../../agentlab/types.py)):

| Role | Contains | Required link |
|---|---|---|
| `system` | instructions, policy, tool guidance | — |
| `user` | the task or follow-up | — |
| `assistant` | text and/or `tool_calls` (content may be `null`) | — |
| `tool` | one result per requested call | `tool_call_id` matching the assistant's call `id` |

The linkage matters more than it looks. An assistant turn that only calls tools has no text; the next request must contain a `tool` message for **every** `tool_call_id`, or the provider rejects the turn (and some providers accept it while silently losing the result). Tool arguments arrive as a JSON **string** that you parse and validate at the provider/tool boundary — `agentlab.providers.base.parse_tool_arguments` is the seam.

### The loop is a state machine, not a `while True`

```python
while True:
    budget.assert_ok(what="run")  # steps/tokens/$ checked BEFORE spending
    tracer.emit("step", "iteration", {"n": budget.steps})
    resp = provider.complete(request)  # seam owns retries, usage, finish_reason
    budget.charge(resp.model, resp.usage)
    transcript.append(resp.message)  # assistant turn (possibly tool calls)
    if not resp.wants_tools:  # stop | length | content_filter
        return AgentResult(answer=resp.text, stop_reason=resp.finish_reason)
    for call in resp.tool_calls:  # parallel calls: one message each
        result = registry.invoke(call.name, call.arguments)  # never raises
        transcript.append(Message.tool_result(call.id, result.as_observation()))
        tracer.emit("tool_result", call.name, {"ok": result.ok, "truncated": result.truncated})
```

That is the whole of week 2's `agentlab/loop/react.py` plus `runner.py`. The interesting engineering is in what surrounds it:

- **Stop conditions** are composable (`agentlab/loop/stop.py`): final answer, `max_steps`, any budget ceiling, and no-progress. Fingerprint `(tool_name, canonical_json(args))` plus a hash of the observable state; if the fingerprint repeats with no state delta, terminate with `stop_reason="stuck"` and the partial result.
- **Partial results on failure.** `MaxStepsExceeded` and `BudgetExceeded` are normal outcomes in a platform: return the work done, the steps taken and the stop reason. A production agent that fails with "step limit" is debuggable; one that raises `RuntimeError` is not.
- **Trace before you optimise.** From week 2, every run emits `run_start`, `step`, `model_call`, `tool_call`, `tool_result`, `run_end` through [`agentlab/trace.py`](../../agentlab/trace.py). These are the same events your week 7 eval harness and a future OTel exporter consume.

### `finish_reason`: five values, five behaviours

| Value | Meaning | Loop behaviour |
|---|---|---|
| `stop` | model finished the turn | return answer |
| `tool_calls` | model wants tools | dispatch, append results, continue |
| `length` | hit `max_tokens` mid-output | repair: continue with "resume" instruction, or fail loudly — never accept truncated JSON as complete |
| `content_filter` | provider refused | terminal policy outcome; surface it, do not retry the same prompt |
| `error` | transport/parse issue | adapter-level retry or raise `ProviderError` |

### Why the harness dominates the model

Same model, different loop, different reliability. SWE-agent's central result was that the **agent–computer interface** — command set, feedback format, guardrails — materially changed benchmark outcomes independent of the model ([arXiv:2405.15793](https://arxiv.org/abs/2405.15793)); Anthropic's tool-writing work reports the same for tool descriptions ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)). The 2026 survey formalises it: an agent is "a foundation model coupled with an execution harness", and quality emerges from observation, context, control, action, state and verification together ([arXiv:2606.20683](https://arxiv.org/abs/2606.20683)). Your week-2 loop is small, but all six duties are present — which is why you build it instead of importing one.

### Streaming, caching, retries

- **Streaming** is SSE frames of text deltas plus tool-call fragments keyed by index, with usage often arriving only in the final chunk. You implement a parser that tolerates fragmented frames and prove the property `assemble_stream(stream(req)) == complete(req)` — the same invariant [`agentlab/providers/base.py`](../../agentlab/providers/base.py) documents. Streaming is not a UI nicety: it is how you get time-to-first-token down and how the model API models long outputs.
- **Streams are not resumable.** The MCP 2026-07-28 revision removed stream resumability for the same reason ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)); assume any long-lived response can die and design re-issue, not replay.
- **Prompt caching** rewards a stable prefix: system prompt → tool definitions → few-shot → history. Put volatile content (timestamps, run IDs, retrieved chunks) at the end; track `Usage.cached_input_tokens` so you can see whether caching is actually working. Token accounting is a first-class feature, not a nice-to-have.
- **Retries belong in the adapter**: 429 with `Retry-After`, 5xx, transport errors, exponential backoff with jitter; never retry a 400/401/403. The loop never sees a vendor error code. Model calls are safe to retry (they are reads); **tool calls are not** — that is why tools need idempotency keys and write tools need approvals (note 02 and week 8).

### Surviving many context windows

Compaction keeps a single run alive, but it is not memory: each new session still starts blank. Anthropic's long-running harness adds the missing half — an *initializer* session that writes `init.sh`, a progress file, a JSON feature list and a first git commit, then *coding* sessions that read progress + git log, pick one feature, and finish by committing and updating progress ([Anthropic, 2025-11-26](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). Note 03 makes this concrete; for now, notice that "state" is a file and git history, not a clever prompt.

## Common misconceptions

| Misconception | Reality |
|---|---|
| "The model remembers the conversation." | It does not. You resend the whole transcript every call; that is why context size is a budget. |
| "A tool exception should propagate." | Tool-level failures are observations. Raise only for bugs you cannot represent (e.g. `KeyboardInterrupt`). |
| "Streaming is a UI feature." | It is the wire format for deltas, including fragmented tool-call arguments. Reassembly and equivalence are testable contracts. |
| "More steps means a thorough agent." | More steps means more cost, more context and more ways to loop. Effort should scale with task complexity, not with hope. |
| "Retries are generic middleware." | While-loop retries duplicate side effects. Retries belong in the adapter for model calls; tool writes need idempotency + approval. |
| "The harness is boilerplate." | It is the product. Two teams on the same model can differ several-fold on task success because of loop, tool and context design. |

## How this shows up in SendOS

- **The provider seam already exists.** `apps/Send.Model.Adapter` (reached through `ISpecialistReasoner`) is `agentlab/providers/base.py` at enterprise scale: provider-independent completion, schema-validated output, budget-aware routing, retries and cost accounting behind one interface ([research 05 §2.2](../research/05-sendos-concept-map.md)). Yours is deliberately synchronous and simpler; the seam is the lesson.
- **The loop is the same machine, governed.** `BoundedIterativeExecutionLoop`, `GoalCompletionLoop`, `IterationBudget` and `BudgetGuard` (`apps/Send.Agent.Runtime/.../Domain/Execution/BudgetGuard.cs`) enforce the same three ceilings you build in week 2 — but aggregated per workstream and checked before every model call. When you read them, compare *where* the budget is checked, not just that it is checked.
- **Your tracer becomes `TurnStage`.** SendOS records 45 named stages, each `Ran/Skipped/Failed` with a reason, plus an append-only `IOutcomeTraceEmitter` (`apps/Send.Agent.Runtime/.../Application/Runtime/TurnStage.cs:29-203`). Week 2's `step`/`model_call`/`tool_call`/`tool_result` events are the same design at a smaller scale — which is exactly what makes week 7's eval harness possible.

## Check yourself

1. An assistant message has `content=null` and two `tool_calls`. What must the next request contain before the model can see tool results at all, and which field links each result to its call?
2. `finish_reason="length"` arrives mid-plan. Name three legitimate responses and the trade-off each one makes.
3. Why does a budget check at the **top** of the iteration prevent a class of bug that a check after the model call cannot?
4. Tool-call arguments stream as fragments across several SSE deltas. What bug appears if you parse each delta independently, and what is the correct accumulation key?
5. Your adapter retries a 500 twice. Why is that safe for the model call but unsafe if you copy the same policy to tool execution?

## Reading

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024, 2026 update note) — the vocabulary of workflows vs agents, and the tool-design appendix.
- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) (2022) — the loop's research ancestor; read for the thought/action/observation structure.
- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) (2025) — "own your prompt, context, control flow and state" as a production checklist.
- [SWE-agent: agent–computer interfaces](https://arxiv.org/abs/2405.15793) (2024) — the evidence that the harness, not just the model, moves benchmark results.
