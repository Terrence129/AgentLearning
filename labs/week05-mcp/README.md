# Week 5 — MCP and interoperability

**第 5 周 — MCP 与互操作性**

> **Lab id:** `week05-mcp` · **Owned package:** `agentlab/mcp/`
> **Starter:** the files in `agentlab/mcp/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week05/agentlab/mcp/`
> **Tests:** `tests/week05/` (in-memory transport, no subprocess, no network)
>
> **实验（lab）ID：** `week05-mcp` · **负责的包：** `agentlab/mcp/`
> **起始代码：** `agentlab/mcp/` 中的文件（它们会抛出 `NotImplementedError`）
> **参考实现：** `solutions/week05/agentlab/mcp/`
> **测试：** `tests/week05/`（内存传输，不启动子进程，不联网）

> **Read this before coding:** the MCP specification was redesigned in
> 2026-07-28. It is **stateless**: `initialize`, sessions, `ping`,
> `logging/setLevel`, the HTTP GET stream and `resources/subscribe` are gone;
> `server/discover` is mandatory; every request carries its version and client
> capabilities in `_meta`; every result carries `resultType`. Most tutorials in
> the wild describe the deprecated handshake. Verify against the
> [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
> before believing any blog post.
>
> **写代码前先读这段：** MCP 规范在 2026-07-28 进行了重新设计。它是**无状态的**：`initialize`、会话、`ping`、`logging/setLevel`、HTTP GET 流和 `resources/subscribe` 都已移除；`server/discover` 是必需的；每个请求都在 `_meta` 中携带其版本和客户端能力；每个结果都携带 `resultType`。网上的大多数教程描述的还是已废弃的握手流程。在相信任何博客文章之前，先对照 [变更日志](https://modelcontextprotocol.io/specification/2026-07-28/changelog) 核实。

## 1. Why this week exists

**1. 为什么要有这一周**

Writing a bespoke integration per tool does not scale, and bespoke integrations
drift. MCP standardises the three operations that matter — discover, list, call
— over JSON-RPC 2.0, with tools (model-controlled), resources
(application-controlled) and prompts (user-controlled) as the unit of
capability. Building both sides yourself is the fastest way to stop treating the
protocol as magic, and the 2026 stateless redesign is a case study in turning a
stateful handshake into a boring, horizontally scalable integration layer
([`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §1.1).
Without this week you can consume a server you were shown, but you cannot reason
about version negotiation, tool poisoning, or why your connector surface is
still bespoke.

为每个工具编写定制集成是无法扩展的，而且定制集成会逐渐偏离。MCP 基于 JSON-RPC 2.0 标准化了三个关键操作 —— 发现、列举、调用 —— 并以工具（由模型控制）、资源（由应用控制）和提示词（由用户控制）作为能力单元。亲手构建协议的两端，是不再把协议当作魔法的最快方式；而 2026 年的无状态重新设计，则是一个把有状态握手变成平淡无奇、可水平扩展的集成层的案例研究（[`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §1.1）。没有这一周的内容，你能使用别人给你看过的服务器，却无法推理版本协商、工具投毒，或者为什么你的连接器接口仍然是定制的。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **Time:** 8–10 h (build ≈ 5 h, spec reading ≈ 2 h, security review ≈ 1 h).

  **时间：** 8–10 小时（动手构建 ≈ 5 小时，阅读规范 ≈ 2 小时，安全审查 ≈ 1 小时）。

- **Must be green:** foundation (`pytest -q` on the repo root).

  **必须通过（变绿）：** 基础部分（在仓库根目录运行 `pytest -q`）。

- **Reading:** the current MCP changelog and the discovery / tools / resources /
  transports pages; `docs/research/02-frameworks-protocols.md` §1.1.

  **阅读：** 当前的 MCP 变更日志，以及 discovery / tools / resources / transports 这几个页面；`docs/research/02-frameworks-protocols.md` §1.1。

- **Does not depend on the `mcp` package.** Do not add it — build the subset.

  **不依赖 `mcp` 包。** 不要添加它 —— 自己构建这个子集。

## 3. The spec

**3. 规格说明**

Implement every `NotImplementedError` in `agentlab/mcp/`. Docstrings are the
contract.

实现 `agentlab/mcp/` 中的每一个 `NotImplementedError`。docstring 就是契约。

| File<br>文件 | Public surface<br>公开接口 | Contract summary<br>契约摘要 |
|---|---|---|
| `jsonrpc.py` | `make_request`, `make_notification`, `make_result`, `make_error`, `parse_message`, `is_notification`, `encode_message`, `JSONRPCError`, error-code and `_meta` constants<br>`make_request`、`make_notification`、`make_result`、`make_error`、`parse_message`、`is_notification`、`encode_message`、`JSONRPCError`、错误码与 `_meta` 常量 | JSON-RPC 2.0 shape validation; `_meta` merged into `params`, never top level; parse/invalid-request errors typed; ids may be string/int/absent but never float/bool; `resultType` values `"complete"` / `"input_required"`. Error codes: standard `-327xx`; MCP-reserved `-32020..-32099`, including `UNSUPPORTED_PROTOCOL_VERSION = -32022`.<br>JSON-RPC 2.0 结构校验；`_meta` 合并进 `params`，绝不放在顶层；解析错误/无效请求错误是带类型的；id 可以是字符串/整数/缺省，但绝不能是浮点数/布尔值；`resultType` 取值为 `"complete"` / `"input_required"`。错误码：标准的 `-327xx`；MCP 保留的 `-32020..-32099`，其中包括 `UNSUPPORTED_PROTOCOL_VERSION = -32022`。 |
| `transport.py` | `Transport`, `InMemoryTransport`, `StdioServerTransport`, `encode_line`, `decode_line`, `serve_stdio`, `TransportError`, `TransportClosed`, `TransportTimeout`, `PROTOCOL_VERSION` | Synchronous request/response channel; in-memory transport records every message in `.sent`; stdio framing is one JSON message per line (blank lines skipped, EOF raises `TransportClosed`); `serve_stdio` survives malformed lines by answering a parse error, converts handler `JSONRPCError`s, and optionally stops after `max_messages`.<br>同步的请求/响应通道；内存传输把每条消息记录在 `.sent` 中；stdio 分帧为每行一条 JSON 消息（跳过空行，遇到 EOF 抛出 `TransportClosed`）；`serve_stdio` 遇到格式错误的行时以回复解析错误的方式继续运行，会转换 handler 抛出的 `JSONRPCError`，并可选择在 `max_messages` 条之后停止。 |
| `server.py` | `MCPServer`, `MCPTool`, `MCPResource`, `build_demo_server`, `main` | Stateless dispatch: every request must carry `params._meta[protocolVersion]`; missing → `-32602`, unsupported → `-32022` with `data.supported`/`data.requested`. `server/discover` advertises versions, identity, capabilities and `ttlMs`/`cacheScope`. `tools/list` is deterministically sorted; `tools/call` distinguishes protocol errors (unknown tool/missing name) from tool-level errors (`isError: true`); `resources/read` unknown → `-32602`; unknown method → `-32601`; notifications are never answered; every result carries `resultType: "complete"` and `_meta[serverInfo]`. `build_demo_server` exposes 3 offline tools + 1 resource; `python -m agentlab.mcp.server` serves it over stdio.<br>无状态分发：每个请求都必须携带 `params._meta[protocolVersion]`；缺失 → `-32602`，不支持 → `-32022`，并附带 `data.supported`/`data.requested`。`server/discover` 公布版本、身份、能力以及 `ttlMs`/`cacheScope`。`tools/list` 按确定性顺序排序；`tools/call` 区分协议错误（未知工具/缺少名称）与工具级错误（`isError: true`）；`resources/read` 遇到未知资源 → `-32602`；未知方法 → `-32601`；通知永远不回复；每个结果都携带 `resultType: "complete"` 和 `_meta[serverInfo]`。`build_demo_server` 暴露 3 个离线工具 + 1 个资源；`python -m agentlab.mcp.server` 通过 stdio 提供服务。 |
| `client.py` | `MCPClient`, `MCPError`, `DiscoverResult`, `ServerInfo`, `RemoteTool`, `ResourceContents` | Every request carries `_meta` (version, clientInfo, clientCapabilities). `discover` validates the response and negotiated version; `list_tools` returns declarations with canonical digests; `call_tool` returns `ToolResult` and turns protocol/transport/timeout failures into observations; `read_resource` returns text; `as_tool_registry` maps remote declarations onto the local `ToolRegistry` so a remote tool is indistinguishable from a local one; `resultType: "input_required"` is detected and rejected as unsupported in this subset.<br>每个请求都携带 `_meta`（版本、clientInfo、clientCapabilities）。`discover` 校验响应和协商出的版本；`list_tools` 返回带规范化摘要的声明；`call_tool` 返回 `ToolResult`，并把协议/传输/超时失败转换为观察结果；`read_resource` 返回文本；`as_tool_registry` 把远程声明映射到本地的 `ToolRegistry` 上，使远程工具与本地工具无法区分；`resultType: "input_required"` 会被检测到，并在本子集中作为不支持的情况予以拒绝。 |
| `security.py` | `tool_digest`, `ServerTrustPolicy`, `ToolPinStore`, `TokenPassthroughPolicy`, `MCPClientSecurity`, `SecurityPolicyError` + subclasses<br>`tool_digest`、`ServerTrustPolicy`、`ToolPinStore`、`TokenPassthroughPolicy`、`MCPClientSecurity`、`SecurityPolicyError` + 子类 | Canonical sha-256 over `{name, description, inputSchema}`; trust list by server identity; pin-on-first-contact then verify — a mutated declaration or an unpinned new tool raises `ToolPoisoningError`; credential-like argument keys (`access_token`, `authorization`, ...) never cross the boundary; optional tool allowlist. Security checks run *before* anything is sent.<br>对 `{name, description, inputSchema}` 计算规范化的 sha-256；按服务器身份维护信任列表；首次接触时固定（pin），之后进行校验 —— 被篡改的声明或未固定的新工具会抛出 `ToolPoisoningError`；类似凭据的参数键（`access_token`、`authorization` 等）绝不会越过边界；可选的工具白名单。安全检查在发送任何内容*之前*执行。 |

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
# 1. starter red
.\.venv\Scripts\python.exe -m pytest tests/week05 -m week -q

# 2. green after implementing
.\.venv\Scripts\python.exe -m pytest tests/week05 -m week -q

# 3. lint
.\.venv\Scripts\ruff.exe check agentlab/mcp tests/week05

# 4. foundation green
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
# 1. starter red
uv run pytest tests/week05 -m week -q

# 2. green after implementing
uv run pytest tests/week05 -m week -q

# 3. lint
uv run ruff check agentlab/mcp tests/week05

# 4. foundation green
uv run pytest -q
```

Manual acceptance (the learning-plan deliverable): build a small multi-step task
where an agent calls a remote tool through `MCPClient.as_tool_registry()` (a
local mini-loop in a script is fine — do **not** import `agentlab.loop` from the
week-5 tests), then produce a security checklist pass: trust list populated,
pins persisted, no credentials in arguments, origin/tenant of the server
recorded.

手动验收（学习计划中的交付物）：构建一个小型多步任务，让 Agent 通过 `MCPClient.as_tool_registry()` 调用一个远程工具（在脚本中写一个本地迷你循环即可 —— **不要**在第 5 周的测试中导入 `agentlab.loop`），然后完成一遍安全检查清单：信任列表已填充、固定（pin）已持久化、参数中没有凭据、已记录服务器的来源/租户。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. **Get the response `id` right.** The client must match responses by id; an
   async client with several in-flight requests is where this bites in real
   life. Use a monotonically increasing integer per client.

   **把响应的 `id` 处理对。** 客户端必须按 id 匹配响应；在真实场景中，有多个并发请求在途的异步客户端正是这里出问题的地方。每个客户端使用一个单调递增的整数。

2. `make_request` accepts `meta` separately from `params`; merge it under
   `params["_meta"]`. MCP 2026-07-28 has no other place to put the version.

   `make_request` 把 `meta` 与 `params` 分开接收；把它合并到 `params["_meta"]` 之下。MCP 2026-07-28 中没有其他地方可以放置版本。

3. Server ordering: sort tools by `name` and resources by `uri` — the spec says
   `tools/list` *SHOULD* be deterministic so prompt caches can hit, and the tests
   assert it.

   服务器端排序：工具按 `name` 排序，资源按 `uri` 排序 —— 规范规定 `tools/list` *应当（SHOULD）* 是确定性的，以便提示词缓存能够命中，而且测试会对此进行断言。

4. Protocol errors vs tool errors: `tools/call` with an unknown name is a
   JSON-RPC **error**; a handler that raises becomes a *successful* JSON-RPC
   result with `isError: true`. Keep them distinct — callers recover differently.

   协议错误与工具错误：用未知名称调用 `tools/call` 是一个 JSON-RPC **错误**；而 handler 抛出异常则变成一个带 `isError: true` 的*成功* JSON-RPC 结果。把两者区分开 —— 调用方的恢复方式不同。

5. Security ordering in `call_tool`: token passthrough check first, then
   allowlist, then send. A blocked call must leave `transport.sent` empty.

   `call_tool` 中的安全检查顺序：先检查 token 透传，再检查白名单，最后发送。被拦截的调用必须让 `transport.sent` 保持为空。

6. Pin digests over the declaration only (`name`, `description`, `inputSchema`),
   not over handler output; a tool whose output changes is not a poisoned tool.

   只对声明（`name`、`description`、`inputSchema`）计算并固定摘要，而不是对 handler 的输出；输出会变化的工具并不是被投毒的工具。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| `KeyError: 'id'` in a notification test<br>通知测试中出现 `KeyError: 'id'` | Notifications have no `id`; `is_notification` must check for *absence*, not truthiness (an `id: null` request is not a notification).<br>通知没有 `id`；`is_notification` 必须检查 id 是否*缺失*，而不是检查其真值（`id: null` 的请求不是通知）。 |
| Server returns `-32601` for `server/discover`<br>服务器对 `server/discover` 返回 `-32601` | You dispatch methods by suffix or forgot that the method string is exactly `server/discover`.<br>你按后缀分发方法，或者忘了方法字符串必须精确等于 `server/discover`。 |
| `tools/list` order flaps between runs<br>`tools/list` 的顺序在不同运行之间来回变化 | You iterated a dict without sorting; also check the client doesn't reorder by description.<br>你遍历字典时没有排序；同时检查客户端没有按 description 重新排序。 |
| Pinning test fails on the second `list_tools`<br>固定测试在第二次 `list_tools` 时失败 | `check_tools` must pin on first contact, then *verify*; or your canonical JSON uses insertion order for schema keys — use `sort_keys=True, separators=(",", ":")`.<br>`check_tools` 必须在首次接触时固定，之后进行*校验*；或者你的规范化 JSON 对 schema 的键使用了插入顺序 —— 请使用 `sort_keys=True, separators=(",", ":")`。 |
| Timeout test returns `ok=True`<br>超时测试返回 `ok=True` | `call_tool` catches `MCPError` and returns `ToolResult.failure`; make sure `_request` re-raises the timeout as `MCPError`, not `ToolResult`.<br>`call_tool` 会捕获 `MCPError` 并返回 `ToolResult.failure`；确保 `_request` 把超时重新抛出为 `MCPError`，而不是 `ToolResult`。 |
| `serve_stdio` loops forever on bad input<br>`serve_stdio` 遇到错误输入时无限循环 | Parse errors must consume one line and `continue`; `max_messages` counts valid messages only, and EOF ends the loop.<br>解析错误必须消耗掉一行并 `continue`；`max_messages` 只统计有效消息，而 EOF 会结束循环。 |

## 7. Spec conformance notes

**7. 规范符合性说明**

This lab implements a deliberately small, **synchronous** subset of MCP
**2026-07-28**. What is faithful:

本实验实现的是 MCP **2026-07-28** 的一个刻意保持精简的**同步**子集。忠实于规范的部分：

- **Stateless core.** No `initialize`/`notifications/initialized`, no sessions,
  no `Mcp-Session-Id`. Every request carries
  `_meta[io.modelcontextprotocol/protocolVersion]` (+ `clientInfo`,
  `clientCapabilities`); mismatches return `-32022` with
  `data.supported`/`data.requested`; servers must implement `server/discover`.

  **无状态核心。** 没有 `initialize`/`notifications/initialized`，没有会话，没有 `Mcp-Session-Id`。每个请求都携带 `_meta[io.modelcontextprotocol/protocolVersion]`（+ `clientInfo`、`clientCapabilities`）；版本不匹配时返回 `-32022`，并附带 `data.supported`/`data.requested`；服务器必须实现 `server/discover`。

- **`resultType` on every result** (`"complete"` / `"input_required"`); clients
  treat a missing field as `"complete"` for older servers.

  **每个结果都带 `resultType`**（`"complete"` / `"input_required"`）；对于较旧的服务器，客户端把缺失该字段视为 `"complete"`。

- **MCP-reserved error codes** `-32020..-32099`; implemented
  `UNSUPPORTED_PROTOCOL_VERSION = -32022`. Resource-not-found uses `-32602`
  (the 2026 revision replaced the old `-32002`).

  **MCP 保留错误码** `-32020..-32099`；已实现 `UNSUPPORTED_PROTOCOL_VERSION = -32022`。资源未找到使用 `-32602`（2026 年的修订替换了旧的 `-32002`）。

- **Cacheable results** carry `ttlMs` and `cacheScope` on `server/discover`,
  `tools/list`, `resources/list` and `resources/read`; `tools/list` is
  deterministically ordered.

  **可缓存的结果**：`server/discover`、`tools/list`、`resources/list` 和 `resources/read` 的结果都携带 `ttlMs` 和 `cacheScope`；`tools/list` 按确定性顺序排列。

- **Modern-only.** Roots, Sampling and Logging are deprecated and not
  implemented; prompts are not implemented; OAuth is not implemented (see
  below).

  **只实现现代特性。** Roots、Sampling 和 Logging 已被废弃，未实现；提示词（prompts）未实现；OAuth 未实现（见下文）。

Known divergences, in order of how likely they are to bite:

已知的偏差，按照它们给你带来麻烦的可能性排序：

1. **Transport.** Only a synchronous in-memory channel and newline-delimited
   stdio framing are implemented. Streamable HTTP (single POST endpoint with
   JSON or request-scoped SSE), `subscriptions/listen`, the removed GET stream,
   and resumability are out of scope. `StdioServerTransport` operates on
   `TextIO`; tests use `io.StringIO`, and no process is spawned anywhere.

   **传输。** 只实现了同步的内存通道和以换行分隔的 stdio 分帧。Streamable HTTP（单个 POST 端点，返回 JSON 或请求作用域的 SSE）、`subscriptions/listen`、已被移除的 GET 流以及可恢复性都不在范围内。`StdioServerTransport` 基于 `TextIO` 工作；测试使用 `io.StringIO`，任何地方都不会启动进程。

2. **Multi Round-Trip Requests (MRTR).** `resultType: "input_required"` is
   *detected and rejected* with `MCPError`; the client does not implement
   `inputRequests`/`inputResponses` retries, so elicitation/sampling/roots-style
   flows cannot complete.

   **多轮往返请求（MRTR）。** `resultType: "input_required"` 会被*检测到并以* `MCPError` *拒绝*；客户端没有实现 `inputRequests`/`inputResponses` 重试，所以 elicitation/sampling/roots 风格的流程无法完成。

3. **Auth.** MCP's transport-level OAuth (authorization-code + PKCE, RFC 8707
   resource indicators, RFC 9207 `iss` validation, Client ID Metadata Documents)
   is not implemented. This week's `security.py` is client-side *policy*
   (trust list, digests, token passthrough) — complementary to OAuth, not a
   replacement: it protects against a server you already connected to, not
   against connecting to the wrong server.

   **认证。** MCP 的传输层 OAuth（authorization-code + PKCE、RFC 8707 资源指示符、RFC 9207 `iss` 校验、Client ID Metadata Documents）未实现。本周的 `security.py` 是客户端侧的*策略*（信任列表、摘要、token 透传）—— 它是 OAuth 的补充，而不是替代：它防范的是你已经连接上的服务器，而不是防止你连接到错误的服务器。

4. **Error-code breadth.** `-32020` (`HeaderMismatch`) and `-32021`
   (`MissingRequiredClientCapability`) are defined but never raised, because
   there are no HTTP headers and no client-capability enforcement in this
   subset.

   **错误码覆盖范围。** `-32020`（`HeaderMismatch`）和 `-32021`（`MissingRequiredClientCapability`）已定义但从未被抛出，因为在这个子集中没有 HTTP 头，也没有对客户端能力的强制检查。

5. **Discovery result shape is approximated.** The documented fields
   (`protocolVersions`, `serverInfo`, `capabilities`) follow the spec page; the
   caching hints and any optional fields (`instructions`, `icons`, extension
   blocks) are a plausible subset, not verified field-for-field against the JSON
   schema — check the schema page before interoperating with a real 2026-07-28
   server.

   **发现结果的结构是近似的。** 有文档说明的字段（`protocolVersions`、`serverInfo`、`capabilities`）遵循规范页面；缓存提示和所有可选字段（`instructions`、`icons`、扩展块）是一个看似合理的子集，并未对照 JSON schema 逐字段核实 —— 在与真实的 2026-07-28 服务器互操作之前，请先查看 schema 页面。

6. **Caching is advertised, not implemented.** `ttlMs`/`cacheScope` are returned
   and recorded on `DiscoverResult`; the client never caches, revalidates, or
   respects `listChanged` notifications.

   **缓存只是被公布，并未实现。** `ttlMs`/`cacheScope` 会被返回并记录在 `DiscoverResult` 上；客户端从不缓存、从不重新验证，也不响应 `listChanged` 通知。

7. **No extensions/tasks.** The extension negotiation field and the official
   `io.modelcontextprotocol/tasks` extension (polling `tasks/get`,
   `tasks/update`) are out of scope.

   **没有扩展/任务。** 扩展协商字段和官方的 `io.modelcontextprotocol/tasks` 扩展（轮询 `tasks/get`、`tasks/update`）都不在范围内。

8. **Batch requests, progress notifications, pagination cursors and structured
   output schemas** are not implemented; `tools/call` returns
   `structuredContent` only when the handler returns a dict.

   **批量请求、进度通知、分页游标和结构化输出 schema** 都未实现；只有当 handler 返回字典时，`tools/call` 才会返回 `structuredContent`。

9. **Schema validation is the handler's job.** The server does not validate
   `arguments` against `inputSchema`; a production server should (the spec
   mandates validation where strict schemas are declared).

   **schema 校验是 handler 的职责。** 服务器不会根据 `inputSchema` 校验 `arguments`；生产环境的服务器应当这样做（规范要求在声明了严格 schema 的地方进行校验）。

10. **HTTP transport concerns** (`Mcp-Method`/`Mcp-Name` headers, Origin
    validation, localhost-only binding, AI-extension headers) do not apply to
    this in-memory/stdio subset.

    **HTTP 传输相关的问题**（`Mcp-Method`/`Mcp-Name` 头、Origin 校验、仅绑定 localhost、AI 扩展头）不适用于这个内存/stdio 子集。

Anything above that you need for an integration decision: read the linked spec
pages rather than extrapolating from this lab. Accuracy about the stateless
redesign is the point; breadth is not.

上面任何你在做集成决策时需要的内容：请阅读链接的规范页面，而不是从本实验中推断。重点在于准确理解无状态的重新设计，而不在于覆盖面。

## 8. SendOS bridge

**8. SendOS 对照**

Read (30 min, read-only): the connector manifest → registry path
(`ICapabilityManifestProvider`, `CapabilityCatalogueAssembler`) and the
execution-origin stamping around connector results. Cross-reference
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§3 topics 8/17 and §4.2.

阅读（30 分钟，只读）：连接器清单 → 注册表的路径（`ICapabilityManifestProvider`、`CapabilityCatalogueAssembler`），以及围绕连接器结果的执行来源标记。交叉参考 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §3 的主题 8/17 和 §4.2。

Answer in your lab notes:

在你的实验笔记中回答：

1. Which parts of SendOS's connector surface would an MCP server replace
   cleanly (discovery, tool declarations, invocation) and which would *not*
   (governed entitlements, approval gates, tenant scoping)?

   SendOS 的连接器接口中，哪些部分可以被 MCP 服务器干净地替换（发现、工具声明、调用），哪些*不能*（受治理的权限授予、审批关卡、租户作用域）？

2. If the catalogue exported `server.json` + an MCP server, who would be the
   OAuth resource server, and how would the client's authority map onto the
   server's scopes without becoming a confused deputy?

   如果能力目录导出 `server.json` + 一个 MCP 服务器，谁会是 OAuth 资源服务器？客户端的权限如何映射到服务器的作用域上，而不至于成为一个“混淆代理人”（confused deputy）？

3. Where does SendOS stamp "real vs simulated" execution origin, and what is the
   MCP analogue of that metadata (tool result `_meta`, trace context, both)?

   SendOS 在哪里标记“真实 vs 模拟”的执行来源？这一元数据在 MCP 中对应的是什么（工具结果的 `_meta`、trace 上下文，还是两者都有）？

## 9. Stretch (optional)

**9. 拓展（可选）**

1. **Expose your agent over A2A.** Write the `/.well-known/agent-card.json` an
   agent would publish (skills, auth schemes, capabilities) and explain what the
   card must **not** reveal (internal tool names, tenant data, prompt contents).

   **通过 A2A 暴露你的 Agent。** 编写一个 Agent 会发布的 `/.well-known/agent-card.json`（技能、认证方案、能力），并解释这张卡片**绝不能**透露什么（内部工具名称、租户数据、提示词内容）。

2. **A Streamable-HTTP-shaped transport.** Implement a `Transport` adapter whose
   `send` performs one POST and returns JSON (no SSE), then explain what breaks
   for notifications/subscriptions — the framing is easy, the state story is not.

   **一个 Streamable HTTP 形态的传输。** 实现一个 `Transport` 适配器，其 `send` 执行一次 POST 并返回 JSON（没有 SSE），然后解释通知/订阅会在哪里出问题 —— 分帧很容易，状态的处理却不容易。

## 10. Reflection (weekly review)

**10. 反思（每周复盘）**

1. **Conceptual:** why did the MCP designers remove the `initialize` handshake?
   What does statelessness cost a client, and what does it buy an operator?

   **概念层面：** 为什么 MCP 的设计者移除了 `initialize` 握手？无状态让客户端付出了什么代价，又为运维方换来了什么？

2. **Architectural:** tool-description digest pinning protects against a server
   that changes behaviour after approval. Where in a production host should that
   pin be stored (client cache, catalogue, approval record) and why?

   **架构层面：** 对工具描述摘要进行固定，可以防范在审批之后改变行为的服务器。在生产环境的宿主中，这个固定值应该存放在哪里（客户端缓存、能力目录、审批记录），为什么？

3. **Transfer:** your day job has bespoke connectors. Which one would you expose
   over MCP first, and what would you refuse to expose over MCP even if the
   protocol allowed it?

   **迁移层面：** 你日常工作中有一些定制的连接器。你会首先通过 MCP 暴露哪一个？又有什么是即使协议允许，你也会拒绝通过 MCP 暴露的？
