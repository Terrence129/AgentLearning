# Week 4 — Context engineering and memory

**第 4 周 — 上下文工程与记忆**

> **Lab id:** `week04-context-memory` · **Owned package:** `agentlab/context/`
> **Starter:** the files in `agentlab/context/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week04/agentlab/context/` (copy it in only after trying)
> **Tests:** `tests/week04/`
>
> **实验（lab）ID：** `week04-context-memory` · **负责的包：** `agentlab/context/`
> **起始代码：** `agentlab/context/` 中的文件（它们会抛出 `NotImplementedError`）
> **参考实现：** `solutions/week04/agentlab/context/`（先自己尝试过，再把它复制进来）
> **测试：** `tests/week04/`

## 1. Why this week exists

**1. 为什么要有这一周**

A model has no memory: the prompt *is* the agent's world this turn, and it gets
worse as it grows — context rot degrades accuracy with input length, and a single
distractor is enough to hurt (see
[`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §3.1).
This week you build the two mechanisms that let a long task survive: a
**priority-aware budget** that never evicts pinned constraints, and a
**compaction** pass that replaces old transcript with a bounded carry-forward
summary. You then build the memory substrate — from-scratch retrieval, episodic
events, semantic facts with provenance — so state can live outside the window.

模型没有记忆：提示词*就是* Agent 在这一轮中的整个世界，而且它越长效果越差 —— 上下文腐化（context rot）会随着输入长度的增加而降低准确率，哪怕只有一个干扰项也足以造成伤害（参见 [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §3.1）。本周你要构建两种让长任务得以存活的机制：一个**感知优先级的预算**，它永远不会驱逐被固定（pinned）的约束；以及一个**压缩（compaction）**过程，它用一份有长度上限的延续摘要替换旧的对话记录。接着你要构建记忆的底层基础 —— 从零实现的检索、情景记忆事件、带来源（provenance）的语义记忆事实 —— 让状态可以存在于上下文窗口之外。

Without this week, a 20-turn task either overflows the provider limit or quietly
forgets the one constraint that mattered ("never refund above $500").

没有这一周的内容，一个 20 轮的任务要么会超出模型提供商（provider）的限制，要么会悄无声息地忘掉那条唯一重要的约束（“退款金额绝不超过 $500”）。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **Time:** 10–12 h (plan: build ≈ 7 h, reading ≈ 2 h, review ≈ 2 h).

  **时间：** 10–12 小时（计划：动手构建 ≈ 7 小时，阅读 ≈ 2 小时，复盘 ≈ 2 小时）。

- **Must be green before starting:** `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux) — the provided foundation.

  **开始前必须通过（变绿）：** `.\tasks.ps1 test`（Windows）/ `./tasks.sh test`（macOS/Linux）—— 即提供的基础部分。

- **Reading:** `docs/research/01-agent-architecture-sota.md` §3 and §4 (read
  §3.1 twice), plus the Anthropic context-management article linked there.

  **阅读：** `docs/research/01-agent-architecture-sota.md` 的 §3 和 §4（§3.1 读两遍），以及其中链接的 Anthropic 上下文管理文章。

- **Python:** standard library only — no numpy, no embeddings API, no network.
  `numpy` is an optional extra in `pyproject.toml`; this lab deliberately does
  not need it.

  **Python：** 只用标准库 —— 不用 numpy，不用 embedding API，不联网。`numpy` 是 `pyproject.toml` 中的一个可选依赖；本实验刻意不需要它。

## 3. The spec

**3. 规格说明**

Implement every `NotImplementedError` in `agentlab/context/`. Docstrings are the
contract; the tests are the proof.

实现 `agentlab/context/` 中的每一个 `NotImplementedError`。docstring 就是契约，测试就是证明。

| File<br>文件 | Public surface<br>公开接口 | Contract summary<br>契约摘要 |
|---|---|---|
| `window.py` | `Priority`, `ContextItem`, `TokenEstimator`, `WindowPolicy`, `ContextWindow`, `AssembledContext`, `ContextBudgetError` | Deterministic ~4-chars/token estimate with per-message overhead. Assemble under `input_budget = max_tokens - reserve_output_tokens`: PINNED always included, then TASK_STATE, RECENT_TURNS, OBSERVATIONS, HISTORY; newer wins inside a class; selected messages keep insertion order. Duplicate item ids are rejected. Pinned-over-budget is reported (`over_budget`), never silently dropped.<br>确定性的约 4 字符/token 估算，并计入每条消息的额外开销。在 `input_budget = max_tokens - reserve_output_tokens` 之内组装：PINNED 始终包含，然后依次是 TASK_STATE、RECENT_TURNS、OBSERVATIONS、HISTORY；同一类别内较新的优先；被选中的消息保持插入顺序。重复的条目 id 会被拒绝。固定条目超出预算时会被报告（`over_budget`），绝不会被悄悄丢弃。 |
| `compaction.py` | `Summarizer` (protocol), `CompactionPolicy`, `Compactor`, `CompactionResult`, `CARRY_FORWARD_ITEM_ID` | `should_compact` compares estimated tokens to the policy budget. `compact(items, objective=...)`: pinned items always survive; last `keep_recent_items` survive verbatim; older tool observations are replaced by a placeholder *before* summarisation; the injected summariser is called at most once with the older items and the objective; the carry-forward note is prefixed with the objective and hard-truncated to `max_summary_tokens`; invalid policies raise `ContextBudgetError`.<br>`should_compact` 把估算的 token 数与策略预算进行比较。`compact(items, objective=...)`：固定条目始终保留；最后 `keep_recent_items` 个条目原样保留；较旧的工具观察结果在摘要*之前*被替换为占位符；注入的摘要器最多被调用一次，传入较旧的条目和目标；延续笔记（carry-forward note）以目标作为前缀，并被硬截断到 `max_summary_tokens`；无效的策略会抛出 `ContextBudgetError`。 |
| `retrieval.py` | `tokenize`, `HashingEmbedder`, `cosine_similarity`, `chunk_text`, `Chunk`, `SearchHit`, `SqliteVectorStore`, `VectorIndex`, `Embedder` | `[a-z0-9]+` tokenizer; deterministic signed hashing embedder (blake2b, unit-norm, zero vector for no tokens); cosine with zero-vector and dimension-error policy; word-preserving overlapping chunks each ≤ `max_chars`; sqlite store with a recorded dimension (reopen with a different dim raises), duplicate-id and wrong-length rejection, exact top-k search sorted by score then chunk id; `VectorIndex` re-indexing replaces a document.<br>`[a-z0-9]+` 分词器；确定性的带符号哈希 embedder（blake2b、单位范数，没有 token 时为零向量）；带零向量和维度错误处理策略的余弦相似度；保留完整单词的重叠分块，每块 ≤ `max_chars`；记录维度的 sqlite 存储（用不同维度重新打开会抛错），拒绝重复 id 和错误长度，精确的 top-k 搜索，先按分数再按分块 id 排序；`VectorIndex` 重新索引时会替换整个文档。 |
| `memory.py` | `MemoryKind`, `Provenance`, `MemoryRecord`, `AuditEntry`, `ConsolidationReport`, `MemoryPolicy`, `MemoryPolicyViolation`, `WorkingMemory`, `EpisodicMemory`, `SemanticMemory` | Working memory is bounded and run-scoped. Episodic memory is append-only (one summary per run) with audited forget. Semantic memory requires provenance, is idempotent for identical content, supersedes on contradiction (old version stays in history), consolidates duplicate facts across keys, and supports audited erase (the memory kill-switch). `MemoryPolicy` rejects short content, missing provenance, emails / API-key-shaped secrets / SSNs, and unlisted kinds.<br>工作记忆有容量上限，且作用域限于单次运行。情景记忆只能追加（每次运行一条摘要），遗忘操作会被审计。语义记忆要求提供来源，对相同内容是幂等的，遇到矛盾时会取代旧版本（旧版本保留在历史中），会合并不同 key 下的重复事实，并支持可审计的擦除（记忆的紧急开关）。`MemoryPolicy` 会拒绝过短的内容、缺少来源的内容、邮箱 / 形似 API key 的密钥 / 社会安全号（SSN），以及未列出的类型。 |

`ContextItem.to_message()` must produce the provided `agentlab.types.Message`
shape; tool items use `Message.tool_result(...)` so the provider tool-call link
survives.

`ContextItem.to_message()` 必须生成所提供的 `agentlab.types.Message` 形状；工具条目使用 `Message.tool_result(...)`，这样与提供商工具调用的关联才得以保留。

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
# 1. starter is red (it should fail loudly with NotImplementedError)
.\.venv\Scripts\python.exe -m pytest tests/week04 -m week -q

# 2. implement, then re-run until green
.\.venv\Scripts\python.exe -m pytest tests/week04 -m week -q

# 3. lint (line length 110)
.\.venv\Scripts\ruff.exe check agentlab/context tests/week04

# 4. the foundation must stay green
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
# 1. starter is red (it should fail loudly with NotImplementedError)
uv run pytest tests/week04 -m week -q

# 2. implement, then re-run until green
uv run pytest tests/week04 -m week -q

# 3. lint (line length 110)
uv run ruff check agentlab/context tests/week04

# 4. the foundation must stay green
uv run pytest -q
```

Optional (the week's lab deliverable, described in the learning plan): run a
20-turn research task through a small driver under a 12k input-token budget,
record before/after cost, and show that ≥ 90% of pinned constraints survive every
compaction. Keep the driver local — do not edit `tests/week04/` to host it.

可选（本周的实验交付物，在学习计划中有描述）：通过一个小型驱动程序，在 12k 输入 token 的预算下运行一个 20 轮的调研任务，记录前后的成本，并证明 ≥ 90% 的固定约束在每次压缩后都得以保留。驱动程序放在本地即可 —— 不要为了放置它而修改 `tests/week04/`。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. **Re-read the contracts.** `window.ContextWindow.assemble` and
   `Compactor.compact` docstrings fully specify ordering and error behaviour;
   implement exactly that before optimising anything.

   **重读契约。** `window.ContextWindow.assemble` 和 `Compactor.compact` 的 docstring 完整规定了排序和错误行为；在做任何优化之前，先严格按其实现。

2. Token arithmetic: tests never hardcode fake budgets for items whose size is
   hard to predict — they compute with `TokenEstimator`. Use the estimator to
   check your own arithmetic instead of counting characters by hand.

   token 计算：对于大小难以预测的条目，测试从不硬编码虚假的预算 —— 它们用 `TokenEstimator` 来计算。用这个估算器来核对你自己的计算，而不是手动数字符。

3. Compaction ordering is the subtle part: pinned first, then the carry-forward
   system item, then the recent tail. `summarized_ids` is the *older* set only.

   压缩的排序是最微妙的部分：先是固定条目，然后是延续笔记这个 system 条目，最后是最近的尾部条目。`summarized_ids` 只包含*较旧*的那一组。

4. Bounding the summary: when the note is too long, truncate at
   `max_tokens * CHARS_PER_TOKEN` characters and append `"..."`, reserving the
   three characters so the estimator still lands within the bound.

   限制摘要长度：当笔记过长时，在 `max_tokens * CHARS_PER_TOKEN` 个字符处截断并追加 `"..."`，并为这三个字符预留空间，以便估算结果仍落在上限之内。

5. For retrieval, `struct`/`json` both work for storing vectors; readability wins
   in this lab. Always sort search results with a total order (`-score, chunk_id`)
   or ties will flap between runs.

   对于检索，`struct`/`json` 都可以用来存储向量；在本实验中可读性优先。始终用全序（`-score, chunk_id`）对搜索结果排序，否则分数相同的结果会在不同运行之间来回变动。

6. `SemanticMemory.remember` returns the *existing* record for an identical
   re-assertion — do not bump the version. Tests distinguish idempotent
   re-assertion from contradiction.

   对于完全相同的重复断言，`SemanticMemory.remember` 返回*已有的*记录 —— 不要提升版本号。测试会区分幂等的重复断言与矛盾的情况。

7. Do not import `agentlab.loop`; this week must be green independently.

   不要导入 `agentlab.loop`；本周必须能够独立通过。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| `ContextBudgetError: reserve_output_tokens ... leaves no input budget` | You validated `max_tokens` against `reserve_output_tokens` after subtracting, or forgot that `input_budget` is a property with validation.<br>你在做减法之后才用 `reserve_output_tokens` 校验 `max_tokens`，或者忘了 `input_budget` 是一个带校验的属性。 |
| A pinned item is missing from the assembled messages<br>组装后的消息中缺少某个固定条目 | You filtered/reordered selected items instead of selecting by priority and then emitting in insertion order. `included_ids` should read like the original sequence.<br>你对已选条目做了过滤/重排序，而不是先按优先级选择、再按插入顺序输出。`included_ids` 读起来应该和原始顺序一致。 |
| Compaction output is *larger* than the input<br>压缩输出比输入*更大* | The fake/real summariser's reply is unbounded, or the summary is placed before pinned items and you forgot to drop the older items entirely.<br>假的/真实的摘要器的回复没有长度上限，或者摘要被放在了固定条目之前，并且你忘了把较旧的条目完全丢弃。 |
| `sqlite3.IntegrityError` escapes `store.add`<br>`sqlite3.IntegrityError` 从 `store.add` 中逃逸出来 | The store converts duplicate chunk ids into `ValueError`; check `VectorIndex.index_document` deletes the document before re-adding.<br>存储层会把重复的分块 id 转换成 `ValueError`；检查 `VectorIndex.index_document` 是否在重新添加之前删除了该文档。 |
| `MemoryPolicyViolation` for legit-looking text<br>看起来正常的文本触发了 `MemoryPolicyViolation` | The default forbidden patterns are broad on purpose (email / `sk-...` / SSN). Pass the policy explicitly to test a narrower tenant policy.<br>默认的禁止模式是刻意设得很宽的（邮箱 / `sk-...` / SSN）。要测试更窄的租户策略，请显式传入策略。 |
| `test_compaction...` sees `summarized_ids` include a recent item<br>`test_compaction...` 发现 `summarized_ids` 中包含了一个最近的条目 | `keep_recent_items` counts *non-pinned* items; slicing `items[-n:]` on the full list is wrong.<br>`keep_recent_items` 统计的是*非固定*条目；在完整列表上做 `items[-n:]` 切片是错误的。 |

## 7. SendOS bridge

**7. SendOS 对照**

Read (30 min, read-only): `Send.Context.Gateway`, the "least-context envelope"
type (`SpecialistContext`), and the semantic retriever + pgvector adapter in the
SendOS repo. Cross-reference
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§3 topics 8/14 and §4.1. Their guarantee is **data minimisation**, not maximal
recall — a different objective from a chatbot's "remember everything".

阅读（30 分钟，只读）：SendOS 仓库中的 `Send.Context.Gateway`、“最小上下文信封”类型（`SpecialistContext`），以及语义检索器 + pgvector 适配器。交叉参考 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §3 的主题 8/14 和 §4.1。它们保证的是**数据最小化**，而不是最大召回 —— 这与聊天机器人“记住一切”的目标截然不同。

Answer in your lab notes:

在你的实验笔记中回答：

1. Which fields does `SpecialistContext` carry, and which of them would this
   week's `ContextEnvelope` place in `facts` vs `references`?

   `SpecialistContext` 携带了哪些字段？本周的 `ContextEnvelope` 会把其中哪些放进 `facts`，哪些放进 `references`？

2. Where does SendOS decide what context a specialist may see — at plan time, at
   dispatch time, or in the gateway — and what is the failure mode if that
   decision is silently widened?

   SendOS 在哪里决定一个专员 Agent（specialist）可以看到哪些上下文 —— 在规划时、在派发时，还是在网关中？如果这个决定被悄悄放宽，会出现什么失败模式？

3. The pgvector adapter is "one real provider" behind an interface. Which parts
   of this week's `Embedder`/`SqliteVectorStore` seam would survive a swap to
   pgvector unchanged, and which would not?

   pgvector 适配器是接口背后的“一个真实提供方”。如果切换到 pgvector，本周的 `Embedder`/`SqliteVectorStore` 接缝（seam）中哪些部分可以原封不动地保留，哪些不能？

## 8. Stretch (optional)

**8. 拓展（可选）**

1. **Real embedder comparison.** Add an `Embedder` implementation backed by a
   real embedding API (behind an env var, no network in tests) and compare
   recall@k with the hashing baseline on 20 hand-labelled queries. Report where
   hashing fails — it should be phrases with no shared vocabulary.

   **与真实 embedder 对比。** 添加一个基于真实 embedding API 的 `Embedder` 实现（通过环境变量开启，测试中不联网），并在 20 个手工标注的查询上，将其 recall@k 与哈希基线进行比较。报告哈希方法在哪里失败 —— 应该是那些没有共同词汇的短语。

2. **Poisoned context defence.** Add a `ContextItem` class for untrusted content
   and a policy that marks it `UNTRUSTED` (below OBSERVATIONS); prove a planted
   "ignore previous instructions" fact can be evicted while pinned constraints
   survive.

   **防御被投毒的上下文。** 为不可信内容添加一个 `ContextItem` 类别，以及一条将其标记为 `UNTRUSTED`（低于 OBSERVATIONS）的策略；证明一条被植入的“忽略之前的指令”事实可以被驱逐，同时固定约束得以保留。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** why is "summarise everything" a worse default than "clear
   tool results first"? What property of summaries makes numbers and constraints
   risky to keep only in prose?

   **概念层面：** 为什么“全部摘要”是比“先清除工具结果”更差的默认做法？摘要的什么特性使得只用文字保存数字和约束是有风险的？

2. **Architectural:** if you had to pick between a bigger context window and
   better retrieval for a 100-turn enterprise task, what evidence would you
   collect before deciding — and which of this week's mechanisms would you keep
   either way?

   **架构层面：** 对于一个 100 轮的企业级任务，如果你必须在更大的上下文窗口和更好的检索之间做选择，在做决定之前你会收集哪些证据？无论选哪个，你都会保留本周的哪些机制？

3. **Transfer:** which part of SendOS would you change first if you owned
   `Send.Context.Gateway`, and what would you measure to prove the change is an
   improvement?

   **迁移层面：** 如果由你负责 `Send.Context.Gateway`，你会首先修改 SendOS 的哪个部分？你会测量什么来证明这个改动确实是一种改进？
