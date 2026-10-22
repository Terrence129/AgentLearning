# Week 1 lab — The model, demystified (provider seam)

**第 1 周实验（lab）— 揭开模型的神秘面纱（provider 接缝）**

## 1. Why this week exists

**1. 为什么要有这一周**

Most agent bugs are blamed on the model but live in the adapter: a tool call whose JSON arguments were never parsed, a 429 retried forever, a stream that silently loses the tool-call fragments after the first one, a 400 that gets retried and burns budget. This week you build the one layer that owns all of that — the provider seam — so the rest of the course never touches vendor-specific wire formats, retries or SSE frames again. You will also measure tokens and cached tokens, because from week 2 onward every run is budgeted.

大多数 Agent 的 bug 都被归咎于模型，但实际上藏在适配器里：JSON 参数从未被解析的工具调用、被无限重试的 429、在第一个工具调用之后悄悄丢掉后续工具调用片段的流、被重试而白白消耗预算的 400。本周你要构建负责所有这些问题的那一层 —— provider 接缝（seam）—— 这样课程的其余部分就再也不需要接触厂商特定的线上传输格式、重试或 SSE 帧。你还会统计 token 和缓存 token，因为从第 2 周起，每次运行都有预算。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **8–10 hours** (build sessions ~5 h, reading ~2 h, SendOS bridge + review ~2 h).

  **8–10 小时**（动手构建约 5 小时，阅读约 2 小时，SendOS 对照 + 复盘约 2 小时）。

- Foundation green: `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux) runs `tests/` (not `tests/week*`) and must pass.

  基础测试通过（变绿）：`.\tasks.ps1 test`（Windows）/ `./tasks.sh test`（macOS/Linux）会运行 `tests/`（不含 `tests/week*`），且必须全部通过。

- Read first: [`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md) (25 min), [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §1.3 and §1.6, [`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §3.

  先阅读：[`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md)（25 分钟）、[`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) 的 §1.3 和 §1.6、[`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) 的 §3。

- You need no API key for the tests. One live call is recommended for the lab artifact (cost cap: a fraction of a cent).

  跑测试不需要 API key。建议为实验产出物做一次真实调用（成本上限：不到一美分）。

## 3. The spec

**3. 规格说明**

Implement in [`agentlab/providers/openai_compat.py`](../../agentlab/providers/openai_compat.py). The docstrings there are the contract; the tests are the proof.

在 [`agentlab/providers/openai_compat.py`](../../agentlab/providers/openai_compat.py) 中实现。其中的 docstring 就是契约，测试就是证明。

| Member<br>成员 | Contract<br>契约 |
|---|---|
| `_build_payload(request, *, stream)` | Request → JSON body: model fallback, message mapping, optional fields only when set, tools omitted when empty, `stream_options={"include_usage": True}` when streaming, `extra` merged **last**.<br>请求 → JSON 请求体：模型回退、消息映射、可选字段仅在设置时才包含、工具列表为空时省略、流式输出时带上 `stream_options={"include_usage": True}`、`extra` **最后**合并。 |
| `_parse_response(payload, *, fallback_model)` | First choice → assistant `Message` (text and/or tool calls), parsed JSON arguments, `Usage` incl. `cached_input_tokens`, `finish_reason`, raw payload retained; malformed arguments become `ProviderError`; no `choices` → `ProviderError`.<br>第一个 choice → assistant `Message`（文本和/或工具调用）、解析后的 JSON 参数、包含 `cached_input_tokens` 的 `Usage`、`finish_reason`，并保留原始 payload；格式错误的参数变为 `ProviderError`；没有 `choices` → `ProviderError`。 |
| `complete(request)` | POST `{base_url}/chat/completions`; at most `max_retries + 1` attempts; retry `RETRYABLE_STATUS` and `httpx.TransportError`; exact `Retry-After` when numeric, else exponential backoff with jitter; no retry for other 4xx; every failure becomes `ProviderError(status, retryable, retry_after, truncated body)`; never leaks `httpx` types.<br>POST `{base_url}/chat/completions`；最多尝试 `max_retries + 1` 次；对 `RETRYABLE_STATUS` 和 `httpx.TransportError` 重试；`Retry-After` 为数字时严格遵守，否则使用带抖动的指数退避；其他 4xx 不重试；每个失败都变为 `ProviderError(status, retryable, retry_after, truncated body)`；绝不泄露 `httpx` 类型。 |
| `stream(request)` | POST with `stream=True`; parse SSE lines (`data:` only, comments/`event:` ignored, `[DONE]` terminates), tolerate frames split across chunks, forward tool-call argument fragments verbatim, emit `text` / `tool_call_delta` / `usage` events and exactly one `done` with `finish_reason`; mid-stream error frames and non-200 statuses raise `ProviderError`; no retries mid-stream.<br>以 `stream=True` 发送 POST；解析 SSE 行（只处理 `data:`，忽略注释/`event:`，遇到 `[DONE]` 结束），容忍跨 chunk 拆分的帧，原样转发工具调用参数片段，发出 `text` / `tool_call_delta` / `usage` 事件，并且恰好发出一个带 `finish_reason` 的 `done`；流中途的错误帧和非 200 状态码抛出 `ProviderError`；流中途不重试。 |

Definition of done includes the equivalence contract: `assemble_stream(provider.stream(req))` equals `provider.complete(req)` for the same logical response.

完成的定义包括等价性契约：对于同一个逻辑响应，`assemble_stream(provider.stream(req))` 等于 `provider.complete(req)`。

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week01 -m week -q   # all green
.\.venv\Scripts\ruff.exe check agentlab/providers/openai_compat.py
```

```bash
# macOS / Linux
uv run pytest tests/week01 -m week -q   # all green
uv run ruff check agentlab/providers/openai_compat.py
```

Optional live artifact (needs `.env` with a provider key): run `.\tasks.ps1 chat` (Windows) / `./tasks.sh chat` (macOS/Linux), complete one streaming turn, and confirm the printed per-turn token/cost line. Compare `stream` vs `--no-stream` answers for the same prompt.

可选的真实产出物（需要在 `.env` 中配置模型提供商（provider）的 key）：运行 `.\tasks.ps1 chat`（Windows）/ `./tasks.sh chat`（macOS/Linux），完成一轮流式对话，并确认打印出的每轮 token/成本行。对同一个提示词，比较 `stream` 与 `--no-stream` 的回答。

## 5. Hints (read in order; stop as soon as you are unblocked)

**5. 提示（按顺序阅读；一旦不再卡住就停下）**

1. Re-read the four docstrings and `tests/week01/` top to bottom before writing code. Each test encodes one wire fact.

   写代码之前，把四个 docstring 和 `tests/week01/` 从头到尾重读一遍。每个测试都编码了一条线上协议事实。

2. `_build_payload` and `_parse_response` are pure functions. Implement and test them first; `complete` and `stream` are plumbing around them.

   `_build_payload` 和 `_parse_response` 是纯函数。先实现并测试它们；`complete` 和 `stream` 只是围绕它们的管道代码。

3. For retries, keep one `last_error: ProviderError` and decide on `attempt >= max_retries`; when `backoff_base == 0`, sleep 0 (tests patch `time.sleep` and will fail if you skip the call on *non-zero* delays only).

   对于重试，保留一个 `last_error: ProviderError`，并根据 `attempt >= max_retries` 做判断；当 `backoff_base == 0` 时，sleep 0（测试会 patch `time.sleep`，如果你只在延迟*非零*时才调用它，测试会失败）。

4. In `stream`, iterate **lines**, not chunks: `response.iter_lines()` already buffers partial lines. A frame split across chunks is only a problem if you treat each network chunk as a complete frame.

   在 `stream` 中，按**行**迭代，而不是按 chunk：`response.iter_lines()` 已经会缓冲不完整的行。只有当你把每个网络 chunk 当作完整帧时，跨 chunk 拆分的帧才会成为问题。

5. Tool-call deltas are not JSON. Forward `function.arguments` fragments exactly as received; the provided `assemble_stream` concatenates them.

   工具调用的增量（delta）不是 JSON。按收到的原样转发 `function.arguments` 片段；提供的 `assemble_stream` 会把它们拼接起来。

6. The `done` event must be emitted on `[DONE]` **and** on a stream that ends without it — track `done_emitted` and `last_finish_reason`.

   `done` 事件必须在收到 `[DONE]` 时发出，**并且**在流没有 `[DONE]` 就结束时也要发出 —— 跟踪 `done_emitted` 和 `last_finish_reason`。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| `KeyError: 'choices'` / `IndexError` in parsing<br>解析时出现 `KeyError: 'choices'` / `IndexError` | You indexed `payload["choices"][0]` before checking for an empty list — the contract requires `ProviderError`.<br>你在检查空列表之前就索引了 `payload["choices"][0]` —— 契约要求抛出 `ProviderError`。 |
| A 400 test times out or counts 4 requests<br>400 测试超时或计数为 4 次请求 | Your retry predicate retries every non-2xx instead of `RETRYABLE_STATUS` only.<br>你的重试判断对所有非 2xx 都重试，而不是只对 `RETRYABLE_STATUS` 重试。 |
| Retry-After test sees `2.4` or `2.5+`<br>Retry-After 测试看到 `2.4` 或 `2.5+` | You added jitter to a server-requested delay, or slept `retry_after * 2**attempt`. Obey `Retry-After` exactly.<br>你给服务器要求的延迟加了抖动，或者 sleep 了 `retry_after * 2**attempt`。要严格遵守 `Retry-After`。 |
| Streaming test assembles only the first tool call<br>流式测试只拼装出第一个工具调用 | You emit the delta only when `delta.tool_calls` has an `id`; continuation frames carry `index`/`arguments` without `id`.<br>你只在 `delta.tool_calls` 带有 `id` 时才发出增量；后续的延续帧只携带 `index`/`arguments`，没有 `id`。 |
| `assemble_stream` equality fails but text matches<br>`assemble_stream` 相等性检查失败，但文本一致 | Missing/duplicated `usage` event, or `done` emitted twice, or `finish_reason` defaulted to `stop` on a tool-call stream.<br>缺少或重复了 `usage` 事件，或 `done` 发出了两次，或在工具调用流上 `finish_reason` 被默认成了 `stop`。 |

## 7. SendOS bridge

**7. SendOS 对照**

Read `apps/Send.Model.Adapter/src/**` (the provider-independent completion path) and the relevant parts of [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.5 and §4.4. Focus on `StructuredCompletionHandler`, `JsonSchemaValidator` and `CompletionHandler.cs:60-210` only as *contrast* — you build those in week 3.

阅读 `apps/Send.Model.Adapter/src/**`（与提供商无关的 completion 路径）以及 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) 中 §2.5 和 §4.4 的相关部分。`StructuredCompletionHandler`、`JsonSchemaValidator` 和 `CompletionHandler.cs:60-210` 只作为*对照*来关注 —— 这些你会在第 3 周构建。

Answer in 5 bullets in your weekly review:

在你的每周复盘中用 5 个要点回答：

1. Which three responsibilities does your provider seam share with Send's model adapters (wire mapping, retry/error taxonomy, usage/cost accounting)?

   你的 provider 接缝与 Send 的模型适配器共同承担了哪三项职责（线上格式映射、重试/错误分类、用量/成本核算）？

2. Where does Send's adapter stop being "just an adapter" (routing, structured completion, cancellation, budget) — and why is splitting those concerns the right call?

   Send 的适配器在哪里不再“只是一个适配器”（路由、结构化 completion、取消、预算）—— 为什么把这些关注点拆分开是正确的选择？

3. What would break in SendOS if retries lived in the agent loop instead of the adapter? Name a concrete duplicate-side-effect scenario.

   如果重试放在 Agent 循环里而不是适配器里，SendOS 中会出什么问题？举出一个具体的重复副作用场景。

## 8. Stretch

**8. 拓展**

1. **Anthropic adapter behind the same `Provider` protocol.** Different system-prompt placement, content blocks and tool schema; map them into `Message`/`ToolSpec` so no caller changes. Write 150 words on which seams held and which leaked.

   **在同一个 `Provider` 协议后面实现 Anthropic 适配器。** 系统提示词的位置、内容块和工具 schema 都不同；把它们映射到 `Message`/`ToolSpec`，使调用方无需任何改动。写 150 词说明哪些接缝守住了、哪些泄漏了。

2. **Retry observability.** Count retries and time slept inside the adapter (no logging), expose a `stats` dict, and make `complete` report total attempts per call. Argue whether that belongs in the trace instead.

   **重试的可观测性。** 在适配器内部统计重试次数和 sleep 时长（不使用日志），暴露一个 `stats` 字典，并让 `complete` 报告每次调用的总尝试次数。论证这些信息是否更应该放在 trace 中。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** Why is streaming "a protocol, not a feature"? What does a streamed response have to guarantee for `assemble_stream` equivalence to be meaningful?

   **概念层面：** 为什么说流式输出是“一种协议，而不是一个功能”？流式响应必须保证什么，`assemble_stream` 的等价性才有意义？

2. **Architectural:** Which decisions belong in the provider seam versus the agent loop? Give an example this week placed correctly and one that later weeks must move upward.

   **架构层面：** 哪些决策属于 provider 接缝，哪些属于 Agent 循环？举一个本周放对了位置的例子，再举一个后续几周必须往上层移动的例子。

3. **Transfer:** Your C# adapter and this Python adapter both hide vendors. Which concern is harder to keep behind the seam in a strongly typed .NET codebase, and why?

   **迁移层面：** 你的 C# 适配器和这个 Python 适配器都隐藏了厂商细节。在强类型的 .NET 代码库中，哪个关注点更难保持在接缝之后，为什么？
