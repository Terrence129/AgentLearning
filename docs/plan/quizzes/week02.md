# Week 2 Quiz — Tools and the Agent Loop

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** Which is the main advantage of native tool calling over text-parsed ReAct?

- A) It uses fewer tokens in every case
- B) The provider returns structured `tool_calls` with ids and JSON arguments, removing brittle parsing
- C) It removes the need for a maximum step count
- D) It guarantees the model picks the correct tool

**Q2.** The loop receives a `tool_call` with `id="call_7"`. What must the tool-result message contain?

- A) Only the content; the model infers the association
- B) `role="tool"`, the matching `tool_call_id`, and the result content
- C) `role="assistant"` with the result appended
- D) A new assistant turn summarising the result

**Q3.** Where should the token/cost budget check happen in the loop?

- A) After every tool execution
- B) At the top of each iteration, before the model call
- C) Only at the end of the run
- D) Inside the provider adapter

**Q4.** A tool raises `FileNotFoundError`. What should the loop do?

- A) Crash — programming errors must surface
- B) Return the error text to the model as a tool observation so it can adapt
- C) Retry the tool three times with backoff
- D) Replace the tool with a fallback tool automatically

**Q5.** Why is tool-output truncation part of loop design, not an optional nicety?

- A) Truncation improves model creativity
- B) A single verbose tool result can consume most of the context window and cost
- C) Providers reject outputs over 1 KB
- D) It is required for parallel tool calls

**Q6.** Which statement is the most defensible design principle?

- A) Prefer an agent over a workflow because agents are more capable
- B) Prefer a workflow over an agent unless the task genuinely requires model-directed control flow
- C) Prefer multiple agents for any multi-step task
- D) Prefer the largest available model so the loop can stay simple

## Part B — Short answer (3 questions)

**Q7.** A loop's budget check is placed **after** the model call instead of before it. Explain the concrete failure this creates.

**Q8.** Give one task that should be a **workflow** and one that should be an **agent**, and state the property that separates them.

**Q9.** You are designing a `write_file` tool. Name three things in its definition/schema that matter for safety and say why.

## Part C — Spot the bug (1 question)

**Q10.** This loop is supposed to be a minimal agent. Identify **three** defects that would make it hang, lose tool results, or overspend.

```python
def run(goal):
    messages = [{"role": "user", "content": goal}]
    while True:
        resp = provider.complete(messages, tools=registry.schemas())
        for call in resp.tool_calls:
            result = registry.call(call.name, call.arguments)
            messages.append({"role": "tool", "content": result})
        if resp.content:
            return resp.content
```

---

## Answers and explanations

**Q1 — B.** Native tool calling removes the parse-a-text-protocol problem and gives stable ids. It does not guarantee choice quality, reduce tokens universally (schemas cost tokens), or replace step limits. *Why it matters: it is the first real improvement over naive ReAct, but it does not remove loop control.*

**Q2 — B.** The tool message must carry `tool_call_id` so the provider can pair request and result. Without it, providers reject the turn or the model misattributes results.

**Q3 — B.** Checking before the call prevents starting a turn you cannot afford. Checking after means every overrun costs one full model call plus its tools. *Why it matters: budget enforcement is a loop invariant, not a post-hoc report.*

**Q4 — B.** Errors are observations: the model can retry with a corrected path or choose another tool. Crashing converts a recoverable condition into an outage. *Why it matters: error-as-observation is what makes an agent robust.*

**Q5 — B.** A directory listing or file dump can be tens of thousands of tokens; truncation (head/tail, byte caps, "N more lines" markers) preserves signal at bounded cost.

**Q6 — B.** Use the least autonomy that passes the eval. Workflows are predictable, cheaper and easier to audit; agents are for cases where the path cannot be predefined.

**Q7 — model answer.** The loop can start a call that its remaining budget cannot pay for, so the run always overspends by at least one model call (plus any tool side effects it triggers). With parallel tool calls or expensive models the overrun can be large, and the recorded cost is then unreliable. Fix: reserve/estimate cost before the call and fail closed when the estimate exceeds the remaining budget.

**Q8 — model answer.** Workflow: "extract fields from these 200 invoices and write a CSV" — fixed steps, no model-directed branching. Agent: "find why CI is failing on this branch and fix it" — the number and nature of steps cannot be known in advance and depends on tool feedback. The separating property is whether the control flow can be encoded before runtime.

**Q9 — model answer.** (1) `is_write=True` metadata on the `Tool` (the registry carries it; read tools leave it `False`) so policy, approval and audit can gate it. (2) Workspace-relative path semantics: `WriteFileInput.path` is documented as relative to the workspace root and `FileSandbox.resolve` enforces containment — the JSON Schema cannot stop `../`, so the tool must. (3) An explicit write contract in the description (parents are created, existing files are overwritten) plus bounded content size, so the model does not have to guess. Bonus: failures return as observations via `ToolResult.failure`, never as exceptions escaping the loop.

**Q10 — model answer.** (1) No `max_steps`/budget guard and no increment — a model that keeps calling tools loops forever. (2) The assistant turn containing `tool_calls` is never appended, and tool results omit `tool_call_id` — the conversation is malformed; many providers will error or ignore the results. (3) Termination is `if resp.content` — an intermediate assistant message with prose ("Let me check the files…") ends the run prematurely; the correct condition is a final answer with no pending tool calls. Also: tool results are not truncated.
