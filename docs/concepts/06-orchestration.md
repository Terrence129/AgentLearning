# 06 — Orchestration and Approval

> **Week 6 · just-in-time concept note.** Read before the lab (~30 min). The lab builds an orchestrator, specialists and an approval gate; this note explains when each is justified and the invariants that make it trustworthy.

## The failure mode this prevents

A team ships a "swarm": one orchestrator, four specialists, a shared message bus, and a model that decides how many agents to spawn. It demos beautifully. In production it costs **~15× the tokens of a chat interaction**, runs slower than the single-agent version on most tasks, and produces inconsistent decisions: each specialist worked from a different slice of context and made conflicting implicit assumptions. Nobody can say which agent approved what, because "approval" was a boolean in the model's JSON. On retry, the write executes twice.

Orchestration is not a maturity ladder. It is a **shape** chosen from the problem's topology — and the safest default is the smallest shape that can do the job.

## If you remember five things

> 1. **Workflow vs agent is the first decision.** Workflow = LLMs/tools orchestrated through predefined code paths (deterministic, cheaper, auditable). Agent = the LLM directs its own process. Most business tasks are workflows.
> 2. **Choose the smallest sufficient shape.** One capability node → direct call. One reasoning node → single specialist. ≥2 connected nodes → one squad. ≥2 components → multi-squad. Unbacked shape → limitation, never a silent shrink.
> 3. **Multi-agent is a cost decision, not a quality switch.** Agents use ~4× chat tokens, multi-agent systems ~15×; the headline +90.2% was on breadth-first research, not on your workflow.
> 4. **Context isolation is a budget, not a wall.** Pass goal, constraints, authority, acceptance criteria and artifact references — never the transcript; return a typed artifact plus evidence.
> 5. **HITL is durable suspend/resume with a binding.** Persist the proposal before approval; bind actor, tenant, action hash, authority snapshot, expiry; execute at most once; reject edited, replayed, expired approvals.

## The model in one page

### Workflow patterns you should reach for first

Anthropic's taxonomy is the clearest: **prompt chaining**, **routing**, **parallelisation** (sectioning or voting), **orchestrator-workers** (dynamic decomposition), **evaluator-optimiser**, and only then the autonomous **agent** loop ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Each step up buys flexibility and pays in latency, cost and unpredictability. Your week-2 loop is the last rung, not the first.

### The topology decision (and why a model should not make it)

The planner decomposes a goal into workstreams bound to either a **capability** (tool/API) or a **reasoning** node (specialist model). Classify the graph, then pick exactly one shape:

| Plan shape | Execution shape | Why |
|---|---|---|
| 1 capability node | Direct capability call | No model needed; zero coordination |
| 1 reasoning node | Single specialist | One context, one accountable owner |
| ≥2 connected nodes | Single squad | Specialists collaborate; one composed result |
| ≥2 unconnected components | Multi-squad | Parallel domains; needs a coordinator |
| Derived shape unbacked | **Limitation** | Fail closed; never guess a smaller shape |

Make the classifier **pure and deterministic** — a function of the validated graph, not an importance score or the model's mood. An LLM choosing topology is how you get fifty subagents for a refund question.

### Orchestrator-worker vs handoffs vs manager

| Pattern | Who keeps control | Best for | Failure mode |
|---|---|---|---|
| **Single agent + tools** | One loop | Most tasks; continuous context | Context overflow on long tasks |
| **Orchestrator-workers** | Central planner | Breadth-first independent subtasks | Duplication, stale assumptions, 15× cost |
| **Handoffs** | Receiving agent | Routing across specialisations | Context fragmentation, ping-pong loops |
| **Manager as tools** | Manager | Delegation with one decision-maker | Manager becomes the bottleneck |

The handoff-vs-manager distinction ([OpenAI's practical guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)) usually matters less than whether you need multiple agents at all. If two specialists must agree on a detail to produce consistent output, pass that decision explicitly or do it in one agent ([Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)).

### Context isolation and the hand-off artifact

A specialist should receive a **bounded envelope**: objective, constraints, tenant/actor and delegated authority, acceptance criteria, artifact references (row IDs/URIs, not dumps), budget, and the output schema. It returns a **typed artifact**: result, evidence, confidence, cost, open questions. Its transcript stays internal. This makes parallel work composable and stops the "game of telephone" where decisions are lost between hops.

SendOS's `SpecialistContext` is exactly this: an ephemeral instance, never persisted. The definition (a published, version-pinned asset) is separate from the instance (one run's bound inputs). Keep that split in your lab: agents are configuration plus context, not mutable objects carrying history.

### The 15× reality

Anthropic measured agents at ~4× chat token usage and multi-agent systems at **~15×**, with +90.2% only on breadth-first research where subtasks were genuinely independent ([multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)). The gain came from parallel context capacity, and cost scales with loops. So the test is not "would another agent help?" but "is this subtask independent enough to justify its own loop, and is the task valuable enough to pay for it?" Budget per workstream, aggregate at the orchestrator, and kill the shape when the budget cannot cover the plan.

### Human approval: the two invariants

A human gate is not a yes/no button. It is **durable suspend/resume** with a binding:

1. **Persist before approve.** The proposal (action, parameters, evidence) is stored before anyone is asked; the approval references the stored proposal — never the reverse.
2. **Bind what was approved to what executes.** The approval binds actor, tenant, action hash, authority snapshot and expiry. At execution: re-hash the action, re-validate authority, check expiry and unconsumed state, then transition to executed **at most once**. Edited payloads, replays and expired approvals fail closed. Proposer ≠ approver; persist transitions so the audit replays.

Treat suspend/resume as state, not a paused thread: serialize pending state, let a callback or worker resume it, and guard resume with compare-and-set. SendOS built this as `CaseRuntime` but has not wired it live.

### When multi-agent is the wrong answer

- Work is sequential: each step depends on the previous one (most coding edits).
- The task is cheap; a 15× multiplier turns $0.02 into $0.30 with no accuracy gain.
- There is no typed output contract, so "combining results" is prose merge.
- You cannot trace, evaluate or budget each loop — you will not debug the failures.
- Consistency matters more than throughput; shared decisions are expensive across agents.

## Common misconceptions

| Misconception | Reality |
|---|---|
| "More agents = better accuracy." | Only when subtasks are independent and parallelisable; otherwise coordination loss exceeds the gain. |
| "Multi-agent is how you get parallelism." | Parallel tool calls inside one agent often suffice; orchestration adds planning and merge overhead. |
| "The orchestrator should decide the topology." | Topology follows from the validated plan; a pure classifier prevents fan-out driven by ambiguity. |
| "Sub-agents should inherit the full transcript." | That inflates cost and contaminates context; pass decisions, constraints and artifact refs. |
| "An approval flag in model JSON is HITL." | Without persistence, binding, revalidation and at-most-once consumption, it is decoration. |

## How this shows up in SendOS

- **Topology as a pure function.** `TopologyClassifier.cs:28-102` and `ExecutionPlanner.cs:143-230` derive one shape from the plan and emit a limitation when unbacked; ADR-0001 exists to remove fan-out driven by ambiguity. That rule is the lab's spec — copy the classifier, not any confidence heuristic.
- **Approval as state with a binding.** `ApprovalCheckpoint.cs:237-468,470-571` persists the proposal before approval, binds tenant/actor/action hash/authority snapshot/expiry (15 minutes), runs six transitions and executes at most once; `ApprovalBindingAtMostOncePropertyTests.cs` encodes the invariants. If your lab approval can be edited after approval and still execute, you missed the week.
- **Instance vs definition.** `SpecialistContext.cs` is an ephemeral, never-persisted context; `ISquadMessageBus`/`InMemorySquadMessageBus` carries structured `SquadMessage` while the transcript stays internal and exactly one `DecisionInteraction` leaves — how a squad stays auditable.

## Check yourself

1. A plan has one reasoning node and one disconnected capability node. Which shape, and what if the derived shape is unbacked?
2. What goes in a specialist's hand-off envelope, and what must never cross the boundary?
3. Estimate 1 orchestrator + 4 workers at 8 steps each versus a single agent at 12 steps. When is the squad justified?
4. An approval arrives expired and with an edited amount. Which invariant rejects each, at which check?
5. Why must topology selection be a pure function, and what failure does the classifier prevent?

## Reading

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow vs agent, the five patterns.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — 15× cost, +90.2% only on breadth-first research.
- [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — context isolation, conflicting implicit decisions.
- [Research 01 §6](../research/01-agent-architecture-sota.md) — autonomy, HITL, durable pause/resume.
