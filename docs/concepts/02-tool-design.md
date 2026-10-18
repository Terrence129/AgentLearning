# 02 — Tool Design

> **Week 2 · just-in-time concept note.** Read before the [agent loop lab](../../labs/week02-agent-loop/README.md) (~20 min). The loop is the machinery; tools are the product surface. Most "the agent is dumb" complaints are tool-design bugs.

## The failure mode this prevents

The tool museum. Somebody wraps every endpoint in the service — `list_customers`, `get_customer`, `get_customer_by_email`, `search_customers`, `update_customer`, `send_email`, and forty more — and the model now has to choose among overlapping tools using names that differ by one word. It picks `list_customers` and receives 400 KB of JSON; the transcript grows by 60k tokens in one step; the next model call is slower, more expensive, and worse at the actual task. Then, on a retry after a 500, `send_email` runs twice, because the loop retried the step and nothing about the tool was idempotent. And when a tool finally raises a `KeyError`, the agent dies at step 9 with a Python traceback instead of reading the error and trying a different parameter — because tool errors were raised, not observed.

This note is how you avoid all four: one schema/handler contract, agent-shaped schemas and descriptions, token-bounded outputs, errors as observations, and a hard read/write distinction.

## If you remember five things

> 1. **A tool is a two-sided contract**: the JSON Schema the model sees and the handler you run. Keep them in one object ([`agentlab/tools/registry.py`](../../agentlab/tools/registry.py)) so they cannot drift.
> 2. **The schema is validation and the description is a prompt.** Both are loaded into context on every step, so both are design surfaces with a token cost.
> 3. **Errors are observations.** `invoke()` never raises for a tool-level problem; it returns `ok=False` with actionable text the model can act on.
> 4. **Output is context.** Truncate, filter, paginate and instruct — an unbounded tool result is a context-window incident waiting to happen.
> 5. **Read vs write is the safety axis.** `is_write=True` implies approval, an idempotency key, a receipt and (in SendOS) post-condition verification. Read tools can be parallel and unrestricted; write tools cannot.

## The model in one page

### Two halves, one object

```python
@dataclass
class Tool:
    name: str  # stable, verb-shaped; namespaced when shared
    description: str  # prompt text: what it does, when to use, when not to
    parameters: JSONSchema  # what the model may send
    handler: Callable  # what actually runs
    input_model: type[BaseModel]  # pydantic; produces the schema and validates
    is_write: bool = False  # drives approval/idempotency policy
    max_output_chars: int = 8_000
```

The registry turns `input_model` into JSON Schema with `additionalProperties: false`, validates arguments *before* execution, and converts exceptions into `ToolResult.failure(...)` ([`registry.py`](../../agentlab/tools/registry.py)). The docstring rule is the whole design: validate at the boundary, never halfway through a side effect.

### Schema design for models

| Rule | Why | Bad → good |
|---|---|---|
| Object root, `additionalProperties: false`, `strict: true` where supported | removes a class of malformed calls; still validate locally | `{}` → `{"type":"object","properties":{...},"required":[...],"additionalProperties":false}` |
| Semantic parameter names | models reason over names; `user` is ambiguous | `user` → `user_id`; `date` → `start_date_iso8601` |
| Enums, formats, units in the description | turns guessing into selecting | `"format": "date-time"`, `"unit": "USD cents"` |
| Required-first; avoid all-optional schemas | optional-everything invites omissions | mark five fields required before adding optionals |
| Discriminated union for variants | one tool with `kind` beats five near-identical tools | `{kind: "refund" \| "void", ...}` |
| Depth ≤ 2, arrays of scalars preferred | deep nesting multiplies schema and error surface | flatten or split |
| No free-form `dict`/`Any` | unvalidatable input becomes runtime bugs | `dict[str, str]` with documented keys |

Week 3's structured-output lab builds the pydantic → JSON Schema path you use here; the same discipline applies to tool arguments, which are just structured output the model emits as a side effect.

### Descriptions are prompts

The tool name and description decide whether the model selects the tool at all. Write them for a competent new hire: what it does, when to use it, when **not** to, what the return looks like, one example argument. Anthropic's tool-writing guidance found that even small description refinements produced large accuracy changes — and that namespace schemes (service first vs resource first) have model-dependent effects worth evaluating rather than guessing ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)). The corollary: descriptions are versioned, reviewed assets, not comments. SendOS makes this literal — a capability is a published, version-pinned asset, and an undeclared capability is not invokable ([research 05 §2.3](../research/05-sendos-concept-map.md)).

### Outputs: filter, truncate, instruct

Tools should return **high-signal fields**, not the raw provider response. Resolve opaque IDs to names where the agent has to reason about them, keep raw IDs only when they are needed for the next call, and expose a `response_format: concise | detailed` enum when both use cases exist — Claude Code caps tool responses at 25,000 tokens by default for exactly this reason ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).

`agentlab`'s default is 8,000 characters, and `ToolResult.truncated` is part of the contract. Truncation must **instruct**: `"...[truncated; refine with query= or page=]"` teaches the model to narrow instead of retrying blindly. Pagination, range selection and filters belong in the schema, with sane defaults.

### Errors as observations

```python
return ToolResult.failure(
    f"arguments for tool 'schedule_event' do not match its schema: "
    f"start_at must be ISO-8601 (got 'tomorrow 3pm')"
)
```

Three properties matter: the model can see *which* argument is wrong, it gets a fixable instruction, and the loop continues. Unknown tool names should list what *is* available (`available tools: read_file, list_dir, search_text`) — that message is the model's only map. Keep a distinction between retryable (timeout, transient 5xx) and terminal (schema violation, authorization denied) errors; for terminal errors the right move is often to change strategy, not retry.

Week 8 pushes this further: tool output is untrusted input, so observations must be delimited and never treated as instructions (note 08).

### Parallel tool calls

A single assistant message can request several tools. Execute them concurrently, then append **one tool message per call, in the original order** — order is part of the wire contract and makes traces readable. Decide the partial-failure policy up front: all-or-nothing for transactional workflows, best-effort with per-call errors for research. The lab's `MockProvider.tool_turn(extra_calls=...)` scripts exactly this case.

Parallel *reads* are cheap and safe; parallel *writes* need independent idempotency keys and, in a governed system, separate approvals. Parallelism also multiplies rate-limit pressure — the provider seam should own concurrency limits, not each tool.

### Read vs write

Make `is_write` explicit and treat it as a risk declaration, not a label. Write tools need: an idempotency key (the retry story), an approval gate when the effect is irreversible or external (week 6/8), an audit receipt (who/what/args hash/result), and ideally a readback verification — SendOS models this with `IResultVerifier` and `ReadbackVerification` states (`Verified/Contradicted/Unconfirmed/NotPerformed`) precisely because "the API returned 200" is not evidence the business outcome happened ([research 05 §2.3](../research/05-sendos-concept-map.md)). Read tools need none of that, which is why the distinction buys you both safety and latency.

### When not to use a tool

- **Deterministic work belongs in code.** If a step is a fixed transformation, a tool call is a slow, expensive, probabilistic function call.
- **Merge tools the model cannot choose between.** If two tools overlap, you created a decision problem; fix the design.
- **Filter inside the tool, not after.** `search_logs` beats `read_logs` — return the rows the decision needs, not everything plus a request to narrow ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- **Code-mode for large catalogues.** Presenting MCP servers as importable code lets the agent load only what it needs and keep intermediate results out of context: one Anthropic task dropped from ~150k to ~2k tokens (98.7%) ([Anthropic, 2025-11](https://www.anthropic.com/engineering/code-execution-with-mcp)). The cost is a sandbox you must operate.
- **Sometimes the answer is "no tool".** Answering from context is cheaper and lower-risk when the model already has the facts.

## Common misconceptions

| Misconception | Reality |
|---|---|
| "More tools make the agent more capable." | Beyond a dozen, selection accuracy and per-step cost both degrade. Curate; consolidate; namespace. |
| "Strict mode means I don't need local validation." | Only some providers/models support it, and it validates schema, not semantics. Validate at your boundary regardless. |
| "Tool errors should raise so bugs are visible." | Tool-level failures are observations. Raise only for harness bugs; log both. |
| "Return the full API response, the model can filter." | Every token is context rent. Return the fields the decision needs. |
| "Read/write is a UI label." | It determines approvals, idempotency, sandboxing, receipts and verification. |
| "Tool descriptions are documentation." | They are prompt text loaded every step, and they decide selection. Version and test them. |

## How this shows up in SendOS

- **A governed registry, not a pile of wrappers.** `CapabilityCatalogueAssembler.cs:34-120` merges three declaration sources with **published-wins**, and matching filters by tenant and declared shape (read vs action kind). That is your `ToolRegistry` plus the governance layer you will build in weeks 6–8 ([research 05 §2.3](../research/05-sendos-concept-map.md)).
- **Risk is part of the contract.** SendOS capabilities carry risk level, approval requirement and read/write metadata; the execution path differs by declared shape (`DirectCapabilityHandler`). Your `is_write` flag is the miniature of that idea — keep it, and let it drive policy rather than documentation.
- **Writes are verified, not assumed.** `IResultVerifier` + `ReadbackVerification` exist because a 200 response is not an outcome. When you build `write_file` in week 2, notice that "wrote the file" is a claim you can verify cheaply — a good habit to carry into week 8.

## Check yourself

1. Your schema has `additionalProperties: false` and the provider supports strict mode. Name two classes of bad input that still reach your handler.
2. You have both `list_contacts` and `search_contacts`. What observable agent behaviour tells you this is a design bug, and what are your two options?
3. Rewrite this observation so a model can recover: `ERROR: 400 Bad Request`. What must it include, and what must it avoid?
4. Which of your tools need an idempotency key, and why does parallel tool calling make the answer sharper rather than optional?
5. You must expose 30 tools. Describe three ways to cut per-step context cost, and one downside of each.

## Reading

- [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09) — naming, token-efficient returns, error surfaces, and the evaluate-your-tools loop.
- [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) (2025-11) — progressive tool disclosure and the 150k → 2k token result; read it before designing a large tool catalogue.
- [SWE-agent](https://arxiv.org/abs/2405.15793) (2024) — the agent–computer interface paper: command design as the main lever.
- [smolagents](https://github.com/huggingface/smolagents) — read the whole ~1k-line core to see tools, executor and memory in one small system.
- **Companion book:** *AI Agents in Depth* v2.0, ch.4 §4.1–4.2 and §4.4 + ch.2 §2.4.6 — capability-expression forms, the art of tool descriptions, parameter fidelity, and what to do when the catalogue outgrows the context. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).
