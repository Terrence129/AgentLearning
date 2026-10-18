# Week 10 Quiz — Consolidation and Leverage

**Time:** 20 minutes · **Closed book, no notes, no code editor.** Pass mark: 8/10. This quiz is the final "explain" gate before the portfolio and interviews.

## Part A — Multiple choice (5 questions)

**Q1.** The point of "re-derive from memory" is to:

- A) Produce a second implementation to ship
- B) Test whether you own the mechanism or only recognise it
- C) Prove the original code was wrong
- D) Save disk space

**Q2.** Which is the strongest portfolio evidence for an agent engineer?

- A) A certificate
- B) A traced, evaluated system with a written architecture and measured failures
- C) A list of frameworks used
- D) A demo video with no code

**Q3.** `pass^k` differs from `pass@1` because it measures:

- A) Latency
- B) Reliability across repeated attempts
- C) Token cost
- D) Judge agreement

**Q4.** Approval must bind to an action hash because:

- A) Hashes are cheap
- B) Otherwise an approved proposal can be swapped or edited before execution
- C) It improves caching
- D) It satisfies the audit log format

**Q5.** Which statement about the MCP spec is correct for 2026?

- A) The `initialize` handshake is the only supported mechanism
- B) The protocol was redesigned; older tutorials describing the legacy handshake are stale
- C) MCP is deprecated in favour of A2A
- D) Only stdio is supported

## Part B — Short answer (4 questions)

**Q6.** Name the four runtime duties (observation, context, control, state/verification) and give one concrete mechanism you built for each.

**Q7.** In an interview: "Tell me about a failure you found and fixed." Which of your nine weeks gives the best story, and what is the four-part structure of the answer?

**Q8.** How will you decide the next step after this course: framework fluency, the learning loop, or agentic RL? State the decision rule.

**Q9.** Explain, in ≤ 60 seconds and without notes, the full request path of an agent run from ingress to audit row.

## Part C — Spot the bug (1 question)

**Q10.** This "from memory" loop was written during consolidation. Identify **three** defects.

```python
def run(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    while not is_done(messages):
        resp = provider.complete(messages, tools=registry.schemas())
        messages.append(resp.message)
        for call in resp.tool_calls:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": registry.call(call.name, call.arguments),
                }
            )
    return messages[-1]["content"]
```

---

## Answers and explanations

**Q1 — B.** Recognition is not ownership; rebuilding from a blank file exposes every hand-waved detail.

**Q2 — B.** Traces + evals + written architecture + honest failure analysis is the combination that survives an interview loop.

**Q3 — B.** Reliability. An agent that works 70% of the time per attempt is not production-ready; pass^k exposes that.

**Q4 — B.** The hash is the binding between "what was approved" and "what executes"; without it the approval is a vague permission.

**Q5 — B.** The 2026 redesign changed negotiation; the plan tells you to read the changelog before coding.

**Q6 — model answer.** Observation: structured step traces (`trace.py` events) with tool results and timings. Context: priority-class window + compaction with a retention test. Control: the ReAct loop with `max_steps` and top-of-iteration budget checks. State/verification: typed decisions with schema validation and the eval harness/regression gate.

**Q7 — model answer.** Week 3 (schema repair) or week 7 (eval regression) gives the best story. Structure: (1) the concrete symptom, with numbers/logs; (2) the diagnosis — which assumption was wrong and how the trace proved it; (3) the fix and the test that locks it; (4) what generalizes — the control you now add by default.

**Q8 — model answer.** If eval/data plumbing is not solid, fix that first — RL on noisy evals optimises noise. If it is solid and your goal is SendOS impact, build the learning loop (trace→candidate→publish). Framework fluency is the cheapest, so do it only when a role or team requires that specific stack. The rule: choose the option that compounds what you already measured.

**Q9 — model answer.** Request ingress → auth/quota/tenant resolution → model adapter call (budget check, retries) → typed decision (schema validated, repaired if needed) → topology/shape selection → plan executed by specialists with isolated contexts → any write action becomes a proposal → approval check bound to actor, tenant, action hash, authority snapshot, expiry → at-most-once execution with idempotency record → same-path audit append with before/after evidence → trace/outcome event emitted for evals.

**Q10 — model answer.** (1) `is_done(messages)` is undefined/naive (typically a substring check) — the loop can stop on an intermediate message or never stop; termination must be "final answer with no pending tool calls" plus `max_steps`. (2) No budget check and no `max_steps` guard — runaway cost. (3) Tool exceptions crash the run instead of becoming observations; also `messages[-1]["content"]` may not be the final answer, and tool results are not truncated. Fix: explicit done predicate, step cap, top-of-loop budget check, error-as-observation, bounded outputs.
