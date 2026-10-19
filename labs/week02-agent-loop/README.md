# Week 2 lab — Tools and the agent loop

## 1. Why this week exists

An agent is a model using tools in a loop — and almost every "the agent went crazy" incident is a loop bug, not a model bug: no step ceiling, no budget check, a tool error that crashes the run, a tool result with no `tool_call_id` so the provider ignores it, or an agent that repeats one call until the invoice arrives. This week you build the loop yourself (the single most important week of the course) plus the tools it acts through: a structurally safe calculator and a filesystem confined to one workspace root. From here on, every later week is a modifier around this loop.

## 2. Prerequisites & time budget

- **10–12 hours** (core loop ~5 h, built-in tools ~3 h, trace/tests ~3 h, review ~1 h).
- Week 1 tests green (or at least `OpenAICompatibleProvider` implemented); you can also run this week against `MockProvider` alone.
- Read first: [`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md), [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §1.1–1.6, and the Anthropic *Building effective agents* essay (linked in [`docs/research/04-learning-resources.md`](../../docs/research/04-learning-resources.md)).

## 3. The spec

| File | Member | Contract |
|---|---|---|
| [`agentlab/loop/react.py`](../../agentlab/loop/react.py) | `run_loop(...)` | Budget check at the **top** of each iteration; model call; stop conditions; natural answer when no tool calls; execute tools, append assistant message then tool observations (both ok and failed); charge budget per call, count steps; terminate as data with `LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition reason>`; `MaxStepsExceeded` carries `steps` + `last_message`; emit `step`/`model_call`/`tool_call`/`tool_result` trace events. |
| [`agentlab/loop/runner.py`](../../agentlab/loop/runner.py) | `AgentRunner`, `AgentResult` | Open the conversation (`system_prompt` then goal); wrap the loop in `run_start`/`run_end` events; map `LoopOutcome` → `AgentResult(answer, steps, usage, stop_reason, trace_events, error)`; partial results survive budget/step stops. |
| [`agentlab/loop/stop.py`](../../agentlab/loop/stop.py) | `StepState`, `StopDecision`, `PredicateStop`, `FinishReasonStop`, `RepeatedToolCallStop`, `AnyOf` | One cheap decision per condition; first halt wins; a truncated/filtered response ends the run instead of being treated as an answer; repeated identical tool calls are recognised as "stuck". |
| [`agentlab/tools/builtin.py`](../../agentlab/tools/builtin.py) | `safe_eval`, `FileSandbox`, `build_builtin_tools` | Calculator accepts arithmetic only (whitelisted AST: literals, parentheses, unary, `+ - * / // % **`), rejects names/calls/attributes and abusive exponents; filesystem tools resolve every path under one root (absolute paths and traversal rejected); `write_file` is marked `is_write=True`; `search_text` is literal, skips binaries and ignored directories, caps results. |

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week02 -m week -q   # all green
.\.venv\Scripts\ruff.exe check agentlab/loop agentlab/tools/builtin.py
```

```bash
# macOS / Linux
uv run pytest tests/week02 -m week -q   # all green
uv run ruff check agentlab/loop agentlab/tools/builtin.py
```

The five golden tasks are in `tests/week02/test_runner.py`: arithmetic, file read, multi-step edit, graceful tool error, budget stop. Manual artifact: run the loop once against a real provider with `build_builtin_tools(tmp_dir)` and a `Tracer` whose `JsonlSink` writes `traces/week02-run.jsonl`; read it back with `agentlab.trace.load_trace` and check that every `tool_call` has a matching `tool_result` with the same `tool_call_id`.

## 5. Hints (progressive)

1. Start from the test file for `react.run_loop`; every assert maps to one line of the docstring's ordered contract.
2. The budget check must be the **first** statement inside the loop body. A check after the model call always overspends by one call — write the test in your head: one scripted model call must remain unused when `Budget(max_steps=1)` trips.
3. Message order matters: append the assistant message (which holds the `tool_calls`) **before** appending tool results, and give each result `Message.tool_result(call.id, result.output, name=call.name)`.
4. `registry.invoke` never raises for a bad tool or bad arguments — it returns `ToolResult(ok=False, ...)`. Append `result.output` even when `not result.ok`; that is how the model recovers.
5. Trace events: `tracer.emit(...)` **returns** the event. Collect those returns; do not add a private sink.
6. `RepeatedToolCallStop` needs state: keep the last fingerprint and a counter; reset on any change or on a text-only response. Fingerprints must canonicalise dict order (`json.dumps(..., sort_keys=True)`).
7. For the sandbox, `resolve()` once and check `Path.is_relative_to` **after** `resolve()` so symlinks and `..` are both caught. Absolute paths are simply rejected.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| `ProviderError: MockProvider script exhausted` | Your loop made one model call too many — usually it treats a text-only response as needing another turn, or the budget check is at the bottom. |
| Provider/mocks see malformed conversations | You appended tool messages without `tool_call_id`, or forgot to append the assistant message that requested the tools. |
| `test_loop_checks_budget_at_top...` fails with 2 calls | Budget check placed after the model call, or `budget.add_step()` too early/late. |
| `len(outcome.steps)` is one short on stop-condition runs | You evaluate conditions (or the natural-answer branch) before recording the `StepRecord`. |
| `search_text` leaks `.git` matches or crashes on a binary | You walk `rglob("*")` without skipping `SKIP_DIRS` or without catching `UnicodeDecodeError`. |
| `list_dir` output order differs | Sort the rendered entries (`"sub/"` sorts after files with the slash suffix), not the raw `Path` objects as the model sees them. |

## 7. SendOS bridge

Read `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/**`, `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120`, and `.../Execution/DirectCapabilityHandler.cs`; the summary lives in [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.2–2.3 and §4.2.

Answer in 5 bullets:

1. What does `CapabilityDefinition` declare that your `Tool` does not (risk level, read/write kind, approval requirement, governed-asset reference) — and which of those would need to exist before your loop could run a real write safely?
2. Trace the path from a bound plan node to `DirectCapabilityHandler` execution. Where does your `run_loop` correspond, and what does SendOS add around it (authority, approvals, idempotency, readback)?
3. Your loop treats a repeated tool call as "stuck". What does SendOS do instead of a generic detector, and why might a governance system prefer policy over heuristics?

## 8. Stretch

1. **Two loops, one task.** Implement text-parsed ReAct (`Thought:`/`Action:`/`Observation:` in plain text) next to native tool calling; run both on 3 of the golden tasks and write 150 words on when each is preferable.
2. **No-progress detector with a state hash.** Extend `RepeatedToolCallStop` with a post-action workspace hash so a loop that alternates two different calls but never changes state also terminates as `stuck`. Add the test first.

## 9. Reflection (weekly review)

1. **Conceptual:** Why are tool errors observations rather than exceptions? What breaks in the loop's reliability story if a tool failure aborts the run?
2. **Architectural:** Which parts of `run_loop` are *mechanism* and which are *policy* (stop rules, budgets, message formatting)? What would you extract first if a second agent shape were added in week 6?
3. **Transfer:** A "golden task" is an eval case before you have an eval harness. What makes the five tasks here a useful eval set, and what would you add before trusting them for a real product?
