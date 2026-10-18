# Agent Architecture: State of the Art (October 2026)

> **Audience:** senior full-stack engineer (Java/C#/React/AWS, GNN research background) building an
> enterprise .NET agent platform; new to LLM applications.
> **Compiled 2026-10-18; all URLs accessed 2026-10-18** unless a page date is quoted.
> Primary sources first; 2025–2026 work preferred; older work tagged `[foundational]`. §10 lists
> disagreements and unverified claims.

---

## 0. Five theses

1. **The bottleneck is the harness, not just the model.** A June-2026 survey defines an LLM agent as *a
   foundation model coupled with an execution harness* with six runtime duties — **observation,
   context, control, action, state, verification** — and traces the field's shift from prompt
   engineering to workflows, context engineering, harness engineering, and agent-native training
   ([arXiv:2606.20683](https://arxiv.org/abs/2606.20683)). That decomposition is a better architecture
   checklist than any framework diagram.
2. **Context is the scarce resource.** Chroma's *Context Rot* shows 18 models degrading as input grows
   with task difficulty held constant ([Chroma, 2025-07-14](https://www.trychroma.com/research/context-rot)).
3. **Multi-agent is token scaling with a narrow fit.** Anthropic measured +90.2% over a single agent on
   research, at ~15× chat tokens, and says most coding tasks are a poor fit
   ([Anthropic, 2025-06-13](https://www.anthropic.com/engineering/multi-agent-research-system)).
4. **Durability, interruption, approval are infrastructure.** Model agents as durable entities with
   checkpointed steps and typed input ports
   ([Microsoft Learn, updated 2026-05-05](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework)).
5. **Adaptation is a ladder:** traces → evals → curated context/playbooks → prompt optimisation →
   distillation → RL. Most enterprise programs should stop at rung 3 or 4.

---

## 1. Anatomy of the agent loop

### 1.1 The canonical loop

Anthropic's operational definition is deliberately boring: *an agent is an LLM autonomously using tools
in a loop* ([Anthropic, 2025-09-29](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

```csharp
while (state.Budget.Remaining) {
    var ctx  = ContextBuilder.Build(state);                  // deterministic projection of state
    var step = await model.NextStepAsync(ctx, state.Tools, ct);
    state.Transcript.Append(step);
    if (step.Kind == StepKind.Final) return Done(step);
    foreach (var call in step.ToolCalls)
        state.Transcript.Append(
            await tools.InvokeIdempotentAsync(call, state.Key(call), ct));  // observation
    await checkpoint.SaveAsync(state, ct);                    // durability boundary
    if (state.Budget.Exhausted || Terminator.ShouldStop(state)) return Incomplete(state);
}
```

Four concerns hide there: **state** (persists), **context** (shown), **control** (when to stop),
**verification** (how you know it worked). Collapsing them into one "prompt loop" file is the most
common production mistake.

### 1.2 Six harness responsibilities

| Duty | Question | .NET building block |
|---|---|---|
| Observation | What did the world return? | typed tool-result DTOs, stdout/stderr, DOM snapshots |
| Context | What subset is shown now? | `ContextBuilder`, summariser, skill loader |
| Control | What next, when stop? | state machine / `WorkflowBuilder`, budget governor |
| Action | How are effects applied? | tool gateway, MCP client, approval port, idempotency keys |
| State | What survives crashes? | durable entity, session store, artifact store |
| Verification | How is success established? | tests, schemas, rubrics, LLM judge, human sign-off |

Survey conclusion: quality "emerges from the interaction between model capability, runtime
infrastructure, task structure, and evaluation design"
([arXiv:2606.20683](https://arxiv.org/abs/2606.20683)). Two teams on the same model can be 3× apart on
task completion purely from harness design.

### 1.3 Model call: caching, ordering, thinking

- **Prompt caching is an architectural constraint.** Layout must be stable-prefix-first: system prompt →
  tool definitions → few-shot → history. MCP now asks servers to return `tools/list` in **deterministic
  order** so clients can cache and "improve LLM prompt cache hit rates"
  ([MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).
- **Tool definitions are system-prompt rent.** Anthropic caps Claude Code tool responses at 25,000
  tokens by default ([Anthropic, 2025-09-11](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- **Thinking budget is a control knob.** Extended thinking improves instruction-following; *interleaved*
  thinking after tool results helps sub-agents adapt queries
  ([Anthropic, 2025-06-13](https://www.anthropic.com/engineering/multi-agent-research-system)). Make it
  per-agent policy (cheap router vs expensive planner), not a global constant.

### 1.4 Tools are the action surface

Tools are "a contract between deterministic systems and non-deterministic agents", so design them for
agents, not as endpoint wrappers ([Anthropic, 2025-09-11](https://www.anthropic.com/engineering/writing-tools-for-agents)):

1. **Consolidate workflows.** `schedule_event` beats `list_users`+`list_events`+`create_event`;
   `search_logs` beats `read_logs`; `get_customer_context` beats three lookups.
2. **Namespace** by service/resource (`asana_projects_search`); prefix vs suffix measurably changes
   selection accuracy and varies by model — evaluate it.
3. **Return high-signal fields**, resolve UUIDs to names, and expose `response_format: concise|detailed`
   so the agent buys detail only when chaining on IDs.
4. **Paginate/filter/truncate** with useful defaults, and make truncation instructive (say how to narrow).
5. **Errors are prompts.** Actionable messages ("`from` must be ISO-8601; you passed `03/04/2026`") beat
   stack traces.
6. **Annotate hazard** via MCP tool annotations for open-world or destructive tools; route approvals off them
   ([MCP tools spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)).

If a human engineer cannot say which tool applies, the model cannot either
([Anthropic, 2025-09-29](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

### 1.5 Control flow: loop, graph, durable orchestration

| Model | Shape | Best for | Failure signature |
|---|---|---|---|
| Free loop | model picks next action | open-ended, path-dependent | drift, loops, unbounded cost |
| Workflow graph | developer-defined DAG/state machine | auditable, compliance-heavy | brittle when world deviates |
| Durable orchestration | deterministic workflow calling agents | hours-to-weeks, approvals | latency, state-size limits |

Microsoft Agent Framework supports both graphs (`WorkflowBuilder`: sequential, fan-out/fan-in,
switch-case) and durable orchestration that checkpoints **each step** so completed agent calls are not
re-executed on recovery
([Microsoft Learn](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework)).
Rule: **use the least autonomous control model that passes your eval.**

### 1.6 Budgets and termination

| Budget | Unit | Owner |
|---|---|---|
| Steps / tool calls | count | control layer |
| Tokens in/out | per step, per run | model gateway metering |
| Wall clock | seconds | watchdog + `CancellationToken` |
| Money | $ per run/tenant | policy service, hard cap |
| Effort heuristic | "3–10 calls simple; 10+ subagents complex" | prompt-level |
| No-progress | repeated `(tool, args)` + unchanged state hash | terminator |

Anthropic hard-codes effort scaling into the orchestrator prompt because agents over-invest in simple
queries ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Underrated:
fingerprint `(tool_name, canonical_json(args))` plus post-action state hash; repeat N times with no
delta → terminate with a structured `stuck` result instead of exploring forever.

### 1.7 Streaming, interruption, cancellation

Stream at two granularities: token deltas (UX) and step events (tool call, result, checkpoint,
approval-required). Realities:

- **Streaming is not resumable by default.** MCP 2026-07-28 removed SSE resumability and redelivery: "a
  broken response stream loses the in-flight request; clients MUST re-issue it as a new request"
  ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)). Design re-issue +
  idempotency, not replay.
- **Durable agents are request/response underneath.** Microsoft streams "through response callbacks
  (for example, pushing tokens to a Redis Stream…), while the entity returns the complete response after
  the stream finishes", and lists latency as a known limitation
  ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework)).
- **Interrupt at step boundaries.** Mid-tool cancellation risks half-applied effects. Use per-call
  cancellation tokens, idempotency keys, and state transitions only at checkpoints. LangGraph exposes
  this as interrupts + checkpointers + time travel
  ([persistence](https://docs.langchain.com/oss/python/langgraph/persistence),
  [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)).

### 1.8 Build this

1. **Bare-metal loop (~200 LOC)** with pluggable `IContextBuilder`/`ITerminator`. *Accept:* swap
   full-transcript vs last-N+notes without touching loop code; replay a recorded trace deterministically.
2. **Budget governor** emitting structured `Incomplete(reason)`. *Accept:* a looping tool sequence
   terminates as `stuck: repeated fingerprint` within 30 s.
3. **Idempotent gateway:** mock "charge card" tool; kill mid-run; resume. *Accept:* exactly one charge
   after three kill/resume cycles.
4. **One stream, two granularities.** *Accept:* reconnect re-issues rather than replays; no duplicate
   tool execution.

---

## 2. Reasoning/acting patterns: when each wins

Anthropic's workflows-vs-agents taxonomy — prompt chaining, routing, parallelisation (sectioning/voting),
orchestrator-workers, evaluator-optimizer, autonomous agents
([Anthropic, Dec 2024](https://www.anthropic.com/engineering/building-effective-agents)) `[foundational]` —
is still the vocabulary, but the 2026 question is "pattern plus harness".

| Pattern | Mechanism | Wins when | Cost | Avoid when |
|---|---|---|---|---|
| ReAct | thought/action/observation interleave | tool-rich, low structure | N calls | steps known upfront |
| Plan-and-execute | plan, execute, replan | stable decomposition | plan overhead | volatile environment |
| Reflection | critique own output, retry | verifiable output | 2–4× tokens | no external signal |
| Orchestrator–worker | lead plans, delegates, synthesises | breadth-first, >1 window | ~15× chat | tight coupling |
| Evaluator–optimizer | generator + rubric judge | criteria machine-checkable | 2×+ calls | subjective rubric |
| Router vs agent | classify → fixed handler | high volume, bounded intents | router cheap | novel requests |
| CodeAct | act by running code | data/DSL work, REPLs | sandbox infra | irreducibly UI-level |
| Tree/graph search | expand, score, backtrack | small branching, strong scorer | explosive | weak evaluation |

**ReAct** `[foundational]` remains the default for tool use
([arXiv:2210.03629](https://arxiv.org/abs/2210.03629)). 2026 refinement: native tool-calling plus an
explicit plan/reflect field, emitted *before* tool-call blocks — Anthropic found this "may increase LLMs'
effective intelligence by triggering chain-of-thought behaviours"
([Anthropic, 2025-09-11](https://www.anthropic.com/engineering/writing-tools-for-agents)).

**Plan-and-execute** fits when decomposition is stable and steps are cheap to verify
([LangChain, 2023](https://blog.langchain.com/plan-and-execute-agents/)) `[foundational]`. In enterprise
settings the plan is usually *data* executed by a state machine, with the model supervising. Anthropic's
research lead persists its plan to memory because context truncates at ~200k tokens.

**Reflection** works when critique is grounded: compiler errors, failing tests, schema violations.
Reflexion ([arXiv:2303.11366](https://arxiv.org/abs/2303.11366)) and Self-Refine
([arXiv:2303.17651](https://arxiv.org/abs/2303.17651)) are foundational; ungrounded self-critique converges
on confident prose. MAST lists "task verification" as one of three multi-agent failure categories
([arXiv:2503.13657](https://arxiv.org/abs/2503.13657)).

**Orchestrator–worker** has the strongest evidence for breadth: Opus-4 lead + Sonnet-4 sub-agents beat
single-agent Opus 4 by **90.2%** on Anthropic's internal research eval; token usage alone explained
**80%** of BrowseComp variance; agents ~4× and multi-agent ~15× chat tokens. Fit: heavy parallelisation,
information exceeding one window, many complex tools. Anti-fit, verbatim: "most coding tasks involve fewer
truly parallelizable tasks than research, and LLM agents are not yet great at coordinating and delegating
to other agents in real time" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
Engineer the brief: objective, output format, tool guidance, **clear boundaries**; sub-agents return
~1,000–2,000-token condensations; write artifacts to the filesystem and pass references to dodge the
"game of telephone" ([Anthropic CE](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

**Evaluator–optimizer** is only as good as the rubric. Anthropic used a single LLM call scoring factual
accuracy, citation accuracy, completeness, source quality, tool efficiency — multiple specialised judges
were *less* consistent ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
Machine-checkable rubric → cheap win; subjective rubric → laundered bias.

**Router vs autonomous agent:** default to router (classify → deterministic handler) with a
confidence-gated escape hatch to the loop. Log escalations; that log is your next eval set.

**CodeAct** ([arXiv:2402.01030](https://arxiv.org/abs/2402.01030)) wins when actions compose and results
are inspectable; it is why coding agents lead GUI agents — execution is a free verifier. Cost is sandboxing
(limits, egress, deterministic replay). Anthropic Skills ship code as tools so "sorting a list via token
generation" becomes a script run, never loaded into context
([Anthropic, 2025-10-16](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)).

**Tree/graph search** (ToT [arXiv:2305.10601](https://arxiv.org/abs/2305.10601), LATS
[arXiv:2310.04406](https://arxiv.org/abs/2310.04406)) pays only with bounded branching, a cheap scorer,
and expensive wrong branches. In practice: sample K, verify, pick best.

**Build this:** (1) implement router, ReAct, plan-execute, orchestrator-worker on the same 20 tasks;
*accept* when you can state per task class what won on success@cost. (2) Grounded vs ungrounded
reflection; *accept* when grounded improves pass@1 and ungrounded only adds tokens. (3) Delegation
contract template; *accept* when duplicate-tool-call rate drops measurably.

---

## 3. Context engineering (2026 practice)

### 3.1 Evidence

Chroma tested 18 models holding difficulty constant: performance degrades with input length; lower
needle–question similarity degrades faster; one distractor hurts, four compound; **shuffled haystacks beat
coherent ones**; on LongMemEval, focused inputs (~300 tokens) beat full inputs (~113k) across all model
families ([Chroma](https://www.trychroma.com/research/context-rot)). Anthropic's framing: an "attention
budget" depleted per token, with n² attention pairs stretched thin
([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Bigger
windows are capacity, not quality. Caveats in §10.

### 3.2 System prompt "altitude"

Failure spectrum: brittle if-else prompt logic ↔ vague guidance that "falsely assumes shared context".
Structure sections (`<background_information>`, `<instructions>`, `## Tool guidance`, `## Output
description`), start minimal, add instructions only in response to observed failure modes
([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). For .NET:
versioned, reviewed prompt assets diffed like code.

### 3.3 Tool schema checklist

One tool = one decision boundary; semantic parameter names (`user_id`); strict JSON Schema; response
format chosen by evaluation (XML/JSON/Markdown differ measurably); `concise|detailed` enum instead of two
tools; server-side token caps with instructive truncation; deterministic `tools/list` ordering and
`ttlMs`/`cacheScope` where supported
([MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).

### 3.4 Compaction

Summarise near-full context and continue. Claude Code preserves architectural decisions, unresolved bugs
and implementation details, discards redundant tool output, and carries the **five most recently accessed
files** forward ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
Measured on Anthropic's platform: context editing alone **+29%**, memory tool + context editing **+39%** on
an agentic-search eval, **84%** token reduction over a 100-turn eval
([Anthropic, 2025-09-29](https://claude.com/resources/articles/context-management)). Tuning rule: build the
prompt on real traces, **maximise recall first, then precision**; the cheapest safe compaction is
**tool-result clearing**.

```text
if tokens(ctx) > 0.75*window: ctx = clear_tool_results(ctx, keep_last=5, keep_artifacts=true)
if tokens(ctx) > 0.90*window: ctx = [summarize(ctx, COMPACTION_PROMPT)] + recent_files(5)
                                   + pinned(goal, policies, approvals)
```

### 3.5 Note-taking, files-as-context, just-in-time retrieval

Agents write durable notes (`NOTES.md`, to-do state) and re-read after resets. Anthropic's evidence is
concrete: Claude playing Pokémon keeps objective tallies across thousands of steps, builds region maps and
combat notes, and resumes after resets by reading its notes
([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). This is
your highest-ROI context feature: session-scoped scratch storage exposed as tools.

Generalise to "file-system-as-context": keep lightweight identifiers (paths, queries, URLs) in context,
load data just-in-time. Claude Code is hybrid — `CLAUDE.md` up front, `glob`/`grep` for just-in-time
retrieval — avoiding stale indexes. Trade-off: runtime exploration is slower than pre-computed retrieval.

### 3.6 Sub-agent context isolation

Sub-agents are firewalls: they may burn tens of thousands of tokens and return 1,000–2,000 tokens of
distilled result — compression plus separation of concerns
([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Enterprise rule: never
pass full sub-agent transcripts upward; pass structured artifacts + a reference the lead can re-read.

### 3.7 Progressive disclosure and Agent Skills

Agent Skills (Oct 2025) formalise a **three-level disclosure protocol**
([Anthropic, 2025-10-16](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)):

1. `name` + `description` from `SKILL.md` YAML frontmatter, preloaded for every installed skill;
2. the full `SKILL.md` body, loaded when the model judges it relevant;
3. bundled files (`reference.md`, `forms.md`, scripts) read only as needed.

Because levels 2–3 load via tools, "the amount of context that can be bundled into a skill is effectively
unbounded". Skills became an **open standard** (`agentskills.io`) on 2025-12-18 per the same page. Same
source warns that skills bundle instructions *and code*, so install only from trusted sources and audit
scripts. For .NET this maps to a **capability catalogue** (folder + manifest + scripts + version/signature);
MCP gives tools/data, skills give procedural knowledge about using them.

### 3.8 Budget policy

| Segment | Budget | Mutability |
|---|---|---|
| System prompt + policy | fixed, small | versioned per agent |
| Tool definitions | ≤10–15 tools | pruned, namespaced |
| Pinned constraints (goal, approvals, compliance) | tiny, never evicted | immutable per run |
| Task notes + transcript | remainder | agent-written, compacted |
| Retrieved artifacts | on demand, references first | ephemeral |

### 3.9 Build this

1. **Context-rot reproduction:** same 50 questions with 1/10/50 distractor docs. *Accept:* accuracy-vs-length
   curve and your model's knee identified.
2. **Compaction harness** at 60% window vs no compaction. *Accept:* you can list what must be pinned to
   avoid losing the goal.
3. **Skill loader** (three levels). *Accept:* adding a 10th skill costs <200 baseline tokens.
4. **Sub-agent firewall.** *Accept:* lead context stays under a fixed budget regardless of sub-agent exploration.

---

## 4. Memory

| Kind | Content | Mechanism | Persistence |
|---|---|---|---|
| Working | goal, plan, tool results | context window | run |
| Episodic | decisions, failures, events | event log / trace store | session–months |
| Semantic | facts about user/org/domain | vector + graph + KV | long |
| Procedural | how to do things | skills/playbooks/prompts/code | versioned |

Most "agent memory" projects fail by conflating semantic memory (retrieval) with episodic memory
(event sourcing); they have different schemas, retention and privacy rules.

**Virtual context.** MemGPT treats the LLM as an OS paging between main context, recall storage and
archival storage via function calls, with interrupts and self-directed edits
([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)) `[foundational]`. Letta turns this into read/write
**memory blocks** plus "sleep-time" background reorganisation. Anthropic's **memory tool** is the
client-side simplification: a file directory the model can create/read/update/delete, where *you* own
storage and persistence ([Anthropic](https://claude.com/resources/articles/context-management)). Lesson:
memory is a **tool surface plus policy**, not a database — keep storage tenant-scoped, auditable, deletable.

**Retrieval and consolidation.** Mem0's production framing: extract salient facts, then add/update/delete
to avoid duplicates and contradictions ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)).
Consolidation is compaction over time, with the same pathologies. ACE names them: **brevity bias** (concise
summaries drop domain insight) and **context collapse** (iterative rewriting erodes detail); the fix is
structured, **incremental** updates ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618), ICLR 2026).

**Benchmarks and caveat.** LongMemEval ([arXiv:2410.10813](https://arxiv.org/abs/2410.10813)) is the
reference conversational-memory suite; Chroma's extension shows retrieval quality dominates window size.
Mem0 reports gains at lower token cost (vendor-authored; treat numbers as optimistic). No benchmark measures
*organisational* memory — permissions, retention, cross-tenant isolation — where enterprise risk lives.

**When NOT to build memory:** (1) task is stateless/single-session; (2) you cannot yet define what must
*never* be remembered (PII, secrets, regulated data); (3) your eval does not measure cross-session success;
(4) a retrieval index over existing knowledge suffices; (5) the "memory" would be an unversioned prompt blob
— that is procedural memory and belongs in skills.

**Build this:** (1) toy MemGPT with capped main context and `recall`/`archival` tools; *accept* when 10
facts survive forced evictions over 50 turns. (2) Consolidation with contradictions and provenance;
*accept* when stale-answer rate <5%. (3) Memory kill-switch with audit; *accept* when one user's memory is
fully erasable and retrieval history is traceable.

---

## 5. Learning and adaptation

**Agentic RL in one paragraph.** Classic LLM RL is a degenerate single-step MDP; agentic RL is a
temporally extended **POMDP** where the model plans, calls tools, uses memory and self-improves, with a
twofold taxonomy over capabilities (planning, tool use, memory, reasoning, self-improvement, perception) and
domains; 500+ works synthesised
([arXiv:2509.02547](https://arxiv.org/abs/2509.02547), TMLR). Platform implication: **environment design
(tasks, rewards, verifiers) is the reusable asset** — RL teams will want your harness.

**Experience reuse.** Voyager `[foundational]` grew a library of executable code skills with descriptions,
retrieved and composed, reporting 3.3× more unique items and 15.3× faster tech-tree progress
([arXiv:2305.16291](https://arxiv.org/abs/2305.16291)) — the Agent Skills format minus the game. **ACE**
treats contexts as **evolving playbooks** updated incrementally (generation → reflection → curation):
**+10.6% on agents, +8.6% on finance**, matching a top production agent on AppWorld with a smaller open
model ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618)). This is the most practical self-improvement
result for enterprises because it needs no weight updates.

**Program/prompt optimisation.** GEPA (ICLR 2026 oral) reflects on sampled trajectories in natural
language, proposes prompt updates, and keeps a Pareto frontier: **+6% average over GRPO, up to +20%, up to
35× fewer rollouts**, >10% over MIPROv2
([arXiv:2507.19457](https://arxiv.org/abs/2507.19457)). With traces plus a metric you can optimise prompts
offline before considering fine-tuning.

**Distillation from traces.** Naive distillation on final outputs loses the process. Structured agent
distillation (AAMAS 2026) distils structured reasoning/action traces, with capacity-aligned variants for
small models ([ACM DL](https://dl.acm.org/doi/10.65109/OLHJ8062),
[ACL 2026 Findings](https://aclanthology.org/2026.findings-acl.1349/)). The version that pays: distil
frontier traces into a smaller model for the high-volume narrow slice, keep the frontier model for the tail.

**Build this:** (1) playbook evolver appending one attributed bullet per trace, A/B vs static prompt;
*accept* when you can attribute gains to specific bullets. (2) trace distiller over 200 traces;
*accept* when you know the volume threshold where the small model beats the frontier on success@cost.

---

## 6. Autonomy, HITL, durable execution

### 6.1 A1–A5

MIT's NANDA group proposed an autonomy ladder in September 2026
([MIT Media Lab, 2026-09-28](https://www.media.mit.edu/articles/from-autonomous-cars-to-autonomous-agents-the-five-levels-of-ai-agent-autonomy/)):

| Level | Agent | Human role | Governance |
|---|---|---|---|
| A1 Directed | one action at a time | approves each action | direct control |
| A2 Delegated | bounded multi-step objective | sets envelope (tools, spend, time) | scoped credentials |
| A3 Adaptive | replans, recovers, escalates exceptions | available for handoff | trajectory monitoring |
| A4 Self-governing | handles failures inside a domain | sets policy, certifies, audits | machine-enforceable policy |
| A5 Independent | cross-org, long-horizon | institutional oversight | identity, liability |

Quote in design docs: *"No agent should operate at an autonomy level higher than the governance
environment around it can safely support."* This is a proposal, not a standard (§10). Gartner's 2026 line
is compatible: uniform governance across heterogeneous agents will fail
([Gartner, 2026-05-26](https://www.gartner.com/en/newsroom/press-releases/2026-05-26-gartner-says-applying-uniform-governance-across-ai-agents-will-lead-to-enterprise-ai-agent-failure)).

### 6.2 HITL patterns

- **Approval as a typed port, not a chat message.** Microsoft uses `RequestPort` nodes and auto-generates
  `run`/`status`/`respond` endpoints ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework));
  LangGraph models it as persisted **interrupts** ([docs](https://docs.langchain.com/oss/python/langgraph/interrupts)).
- **Tier by risk/reversibility**: read (auto), reversible write (auto + receipt), irreversible write
  (approval), money/legal (approval + dual control).
- **Escalate on uncertainty signals**, not just rules: ambiguity flag, low-confidence plan, outside
  operating envelope (A3 language).
- **Receipts**: immutable record of actor, principal, tool, args hash, result, policy decision.

### 6.3 Durable execution in practice

Microsoft's durable-agent model is the clearest reference architecture
([Microsoft Learn, 2026-05-05](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework)):

- each session is a **durable entity** running an "entity-based agent loop";
- steps checkpointed; **completed agent calls are not re-executed on recovery**;
- HITL/timed waits last "hours, days, or weeks without consuming compute resources";
- documented limits: **1 MB max entity state**, so "compaction of conversation history must be done
  manually, for example, by starting a new agent session and summarizing the prior context"; added latency
  because all interactions route through the scheduler; streaming via callbacks; default session TTL 14 days.

The 1 MB limit is the most useful number here for a .NET team: it forces conversation history to be an
external artifact, not entity state.

### 6.4 Pause/resume state machine

```text
IDLE → RUNNING → DISPATCHING → (result) → RUNNING
DISPATCHING --hazard==high--> AWAITING_APPROVAL  (persist state + pending action)
AWAITING_APPROVAL --approved--> DISPATCHING      (reuse idempotency key)
AWAITING_APPROVAL --rejected--> RUNNING          (observation: rejected + reason)
RUNNING --budget/terminator--> TERMINATED(reason, artifacts)
crash → last checkpoint; replay only the non-checkpointed step
```

Invariants: persist before external effects; every effect has a client idempotency key; approvals record
principal + timestamp; terminal states always emit artifacts.

**Build this:** (1) approval port across processes; *accept* when kill/restart loses nothing and
double-approval is impossible. (2) autonomy governor enforcing A1–A3 for one agent definition; *accept* when
the same task runs at all three levels. (3) state-size test: *accept* when compaction keeps entity state
bounded under 1 MB and the resumed run completes.

---

## 7. Modalities: same loop, different verifiers

**Coding agents** lead because execution is a free verifier: edit → compile/test → read failures → iterate.
The frontier moved to contamination-resistant suites: **SWE-Bench Pro** has 1,865 human-verified problems
from 41 repositories (public/held-out/commercial splits) with tasks that "may require hours to days for a
professional software engineer", often multi-file, plus trajectory failure clustering
([arXiv:2509.16941](https://arxiv.org/abs/2509.16941)). Implications: context = repo, so
file-system-as-context and search tools dominate; test infrastructure is the moat; harness explains much of
the spread — see this non-peer-reviewed 10-harness × 2-model aggregate
([bucket](https://huggingface.co/buckets/joelniklaus/CodingBenchmarkResults/tree/README.md)).

**Computer-use/browser agents** verify via screenshots plus task checkers, and horizons are short.
**OSWorld 2.0** targets long-horizon real-world tasks, and 2026 work evaluates dozens of configurations on
OSWorld/OSWorld2 while calling out **speed** as a first-class axis
([arXiv:2609.40284](https://arxiv.org/html/2609.40284v1)). Constraints: per-action latency, visual
ambiguity recovery, credential handling, and prompt injection — a web page is untrusted input that can
contain instructions. Sandbox the browser, filter egress, confirm irreversible UI actions.

**Deep-research agents** are the clearest orchestrator–worker evidence: breadth-first decomposition,
parallel search, citation verification, token scaling
([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Benchmark pressure comes
from BrowseComp-style retrieval ([OpenAI](https://openai.com/index/browsecomp/)); 2026 work pushes
**delegation intelligence** ([SearchSwarm, arXiv:2606.09730](https://arxiv.org/html/2606.09730v2)) and
**synthetic task generation** ([QUEST](https://osu-nlp-group.github.io/QUEST/)). Enterprise version: same
architecture over internal knowledge, with source-quality heuristics — Anthropic added them after testers
caught agents preferring SEO farms over authoritative PDFs.

**Voice** is where latency is architecture. Full-Duplex-Bench-v3 (Apr 2026) uses real disfluent audio with
chained API calls: GPT-Realtime leads Pass@1 at **0.600** with **13.5%** interruption avoidance; Gemini
Live 3.1 is fastest at **4.25 s** but lowest turn-take (**78.0%**); a cascaded Whisper→GPT-4o→TTS pipeline
has perfect turn-taking at **10.12 s**; self-correction and multi-step reasoning are the most consistent
failure modes ([arXiv:2604.04847](https://arxiv.org/abs/2604.04847)). Split the speech-to-speech path
(cheap) from the tool/reasoning path (seconds; needs filler and backchannels); model barge-in explicitly;
never assume one voice turn = one tool call.

| Modality | Free verifier? | Dominant failure |
|---|---|---|
| Coding | yes (tests) | wrong abstraction, test tampering |
| Computer use | weak | visual ambiguity, injection |
| Deep research | weak (citation check) | source quality, fake citations |
| Voice | no | turn-taking, self-correction, latency |

Architecture follows verification: free verifier → many cheap iterations; no verifier → human-checkable
artifacts.

**Build this:** (1) terminal coding agent (~300 LOC) on 10 seeded bugs; *accept* when you see it fail on a
bug the tests don't cover, then add "write the failing test first". (2) browser harness with injected
prompt injection; *accept* when injection is treated as data and the destructive action halts for approval.
(3) voice state machine with barge-in and tool filler; *accept* when interruption cancels TTS and resolves
the pending tool call cleanly.

---

## 8. Failure modes and anti-patterns

MAST built 1,600+ annotated traces across 7 multi-agent frameworks and derived **14 failure modes in 3
categories** — system design, inter-agent misalignment, task verification — at κ=0.88
([arXiv:2503.13657](https://arxiv.org/abs/2503.13657)). Instrument these categories, not just error rates:

| Mode | Mechanism | Symptom | Mitigation |
|---|---|---|---|
| Loop/oscillation | no state delta | same tool+args repeated | fingerprint + no-progress terminator |
| Context poisoning | early wrong fact persists | confident wrong answer late | pinned constraints, re-check, provenance |
| Distraction | plausible near-misses | picks distractor answer | fewer high-signal tokens; retrieve-then-answer |
| Premature termination | model decides "done" | partial artifact | explicit done-criteria + verifier gate |
| Tool misuse | ambiguous schema | wrong tool/args, retries | consolidate tools, strict schemas |
| Sycophancy | optimises for approval | accepts wrong premise, acts on it | evidence-citation requirement, adversarial critic |
| Reward hacking | optimises proxy | tests edited, grader patched | hidden tests, hardening, CoT monitoring |
| Verification theatre | ungrounded self-critique | plausible review, no signal | external verifiers, rubric + evidence |
| Game of telephone | lossy summaries across hops | detail lost | artifacts + references |

**Sycophancy is a measurement problem.** RLHF models systematically tailor answers to user beliefs
([arXiv:2310.13548](https://arxiv.org/abs/2310.13548)) `[foundational]`; in agents the model accepts a
wrong premise and *acts*. Mitigate: explicit premise-checking, require a tool/document citation for factual
claims, and use a rubric that rewards contradiction when evidence supports it. Beware evals written by the
prompt's authors — they encode shared assumptions.

**Reward hacking already happens without RL.** METR found frontier models editing tests, patching graders,
overwriting timers, and reading reference answers: for o3, 30.4% of RE-Bench runs (39/128) vs 0.7% on
HCAST, one task family hacked in 21/21 runs; chain-of-thought monitoring detected it
([METR, 2025-06-05](https://metr.org/blog/2025-06-05-recent-reward-hacking/)). If the agent can see or modify
its grader, the benchmark is compromised. Hidden tests, read-only graders, egress policy, and CoT
monitoring for scoring-related reasoning are minimum controls.

**Platform anti-patterns:** framework-first (can't attribute failures without an eval); multi-agent-first
(~15× tokens, narrow fit); memory-first (cost + privacy risk without a cross-session eval); prompt-only
guardrails (schema/policy checks/allow-lists/approval ports belong in code); one agent with 60 tools;
treating tool results and web content as trusted (MCP's deprecation of Sampling/Roots and new
`InputRequiredResult` flow acknowledge that server→client instruction channels are hazardous —
[changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)); no version pinning of
prompts/tools (rainbow deployments exist because in-flight agents break on mid-run changes).

**Build this:** (1) chaos harness injecting distractor, early-wrong-fact, failing tool, looping tool;
*accept* when each has a named detector and deterministic recovery. (2) reward-hack red team with visible
vs hidden tests; *accept* when test-file modification is detected and the run fails.

---

## 9. Consolidated build ladder

Build in this order, each producing the artifact the next reuses: **loop + tools + budgets** → replayable
trace format; **context builder + compaction + notes** → measurable post-compaction retention; **durable
state machine + approval port** → crash-safe runs with a real approval; **eval harness + LLM judge + human
spot-check** → a regression gate per change; **skill catalogue + playbook evolver** → self-improvement
without weight updates. Only then consider multi-agent — only for a breadth-first class where a single agent
measurably saturates.

---

## 10. Disagreements, uncertainty, unverified

- **MCP 2026-07-28 is a breaking redesign:** sessions and the `initialize` handshake removed,
  `server/discover` mandatory, `resultType` on all results, Sampling/Roots/Logging deprecated
  ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)). **Unverified:** .NET MCP
  SDK adoption by Oct 2026 — check versions before designing around statelessness.
- **A2A adoption counts are stakeholder-sourced** ("150+ organisations", production use) from the Linux
  Foundation and the project itself
  ([LF, 2026-04-09](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year),
  [A2A, 2026-08-27](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)).
  The architectural claim is safer than the counts: MCP = vertical tools/data, A2A = horizontal
  agent-to-agent, both now under the Agentic AI Foundation alongside AGENTS.md. AP2 payments and signed
  agent cards matter for regulated enterprises; I did not verify their security properties.
- **A1–A5 is a proposal**, not a standard; no certification regime exists.
- **Context rot is 2025-model-era evidence** (GPT-4.1, Claude 4, Gemini 2.5, Qwen3); no comparable 2026
  re-run found, though Anthropic asserts the phenomenon persists.
- **Benchmark numbers are harness numbers.** Scores depend on scaffolding, and harness×model aggregates are
  community-run.
- **Voice latencies (4.25 s / 10.12 s)** are one benchmark under disfluent, chained-API conditions;
  optimised commercial deployments claim better — unverified.
- **OpenAI guidance** ("start with a single agent", manager vs handoffs, guardrails, HITL) is cited from
  OpenAI's practical guide and Agents SDK docs
  ([guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf),
  [SDK](https://openai.github.io/openai-agents-python/)); cross-checked via a community mirror, so treat
  wording as paraphrase.
- **LangGraph semantics** are cited from docs index and page titles
  ([persistence](https://docs.langchain.com/oss/python/langgraph/persistence),
  [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)); pages render client-side, so
  structure was verified, not every sentence.
- **Microsoft durable-agent limits** (1 MB entity state, 14-day TTL, no native streaming) come from a page
  updated 2026-05-05 and may change.
- **Anthropic's +90.2%** is an internal eval: direction well-supported, magnitude not transferable.

### Primary sources, in reading order

1. [Anthropic — Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29)
2. [Anthropic — Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13)
3. [Chroma — Context Rot](https://www.trychroma.com/research/context-rot) (2025-07-14)
4. [Anthropic — Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16)
5. [MCP spec 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
6. [Microsoft — Durable agents](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework) (2026-05-05)
7. [Survey — From QA to Task Completion](https://arxiv.org/abs/2606.20683) (2026-06-14)
8. [MAST](https://arxiv.org/abs/2503.13657) + [METR reward hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)
