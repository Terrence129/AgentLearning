# 05 — MCP and Interoperability

**05 — MCP 与互操作性**

> **Week 5 · just-in-time concept note.** Read before the lab (~25 min), then read the [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) with the tab open. You need the protocol's shape, its current revision, and the attacks it does *not* stop — not memorised spec text.
>
> **第 5 周 · 即时概念笔记。** 在做实验之前阅读（约 25 分钟），然后打开 [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) 对照阅读。你需要掌握的是协议的形态、它的当前修订版，以及它*无法*阻止的攻击——而不是背下规范原文。

## The failure mode this prevents

**本机制防止的失败模式**

The integration-tax spiral: every system you connect needs a bespoke client, so the platform accumulates N connectors and N security reviews, and the tool list becomes a museum of hand-written wrappers. The same shortcut makes it dangerous: a client copies the caller's OAuth token into every downstream call, so an assistant *allowed* to read tickets can now send email. And approved tool descriptions can change server-side after review, with the model following instructions you never read.

集成税的恶性循环：你接入的每个系统都需要一个定制客户端，于是平台积累了 N 个连接器和 N 次安全评审，工具列表也变成了一座手写包装器的博物馆。同样的捷径还让它变得危险：某个客户端把调用方的 OAuth token 复制到每一个下游调用中，于是一个只*被允许*读取工单的助手现在也能发送邮件了。而且，已批准的工具描述可能在评审之后于服务器端被修改，模型就会去遵循你从未读过的指令。

MCP is not "a better REST client": it is a contract for how a host discovers and invokes tools, resources and prompts across a boundary, and it makes the scalable version (stateless HTTP) the default while leaving trust decisions to you.

MCP 不是“一个更好的 REST 客户端”：它是一份契约，规定了宿主如何跨越边界发现并调用工具、资源和提示词；它把可扩展的形式（无状态 HTTP）设为默认，同时把信任决策留给你自己。

## If you remember five things

**如果只记住五件事**

> 1. **MCP standardises tool/context integration inside one agent** — tools (model-invoked), resources (app-controlled data by URI), prompts (user-selected templates). Not agent-to-agent.
>
>    **MCP 标准化的是单个 Agent 内部的工具/上下文集成**——工具（由模型调用）、资源（由应用控制、通过 URI 访问的数据）、提示词（由用户选择的模板）。它不是 Agent 与 Agent 之间的协议。
>
> 2. **The 2026-07-28 spec is stateless.** No `initialize`, no session. Version and capabilities travel in `_meta` on every request; negotiation uses `server/discover`; results carry `resultType`.
>
>    **2026-07-28 版规范是无状态的。** 没有 `initialize`，也没有会话。版本和能力信息随每个请求放在 `_meta` 中传递；协商使用 `server/discover`；结果携带 `resultType`。
>
> 3. **Multi Round-Trip Requests replace server-initiated requests.** A server needing input returns `resultType: "input_required"` with `inputRequests`; the client retries with `inputResponses`.
>
>    **多轮往返请求（Multi Round-Trip Requests）取代了服务器发起的请求。** 需要输入的服务器返回 `resultType: "input_required"` 并附带 `inputRequests`；客户端则带着 `inputResponses` 重试。
>
> 4. **OAuth tokens are audience-bound and never passed through.** Your MCP server is a resource server: accept only tokens minted for it; never replay the caller's token downstream.
>
>    **OAuth token 绑定受众（audience），且绝不透传。** 你的 MCP 服务器是一个资源服务器：只接受专门为它签发的 token；绝不把调用方的 token 重放到下游。
>
> 5. **Use protocols only across a real boundary.** Function calling inside your process; MCP for reusable/third-party tools; A2A for another team's agent; AG-UI for a user-facing event stream.
>
>    **只在真正的边界上使用协议。** 进程内用函数调用；可复用/第三方工具用 MCP；其他团队的 Agent 用 A2A；面向用户的事件流用 AG-UI。

## The model in one page

**一页看懂模型**

### Roles and primitives

**角色与原语**

A **host** (your agent app) runs **clients**, each connected to a **server** over JSON-RPC 2.0. The server advertises capabilities; the client renders tools into the model's function-calling schema, exposes resources as app context, and prompts as user templates ([server overview](https://modelcontextprotocol.io/specification/2026-07-28/server)). The model never "speaks MCP" — it calls functions, and the host translates. That translation layer is yours, and it is where allowlists, redaction and tracing live.

一个**宿主**（你的 Agent 应用）运行若干**客户端**，每个客户端通过 JSON-RPC 2.0 连接到一个**服务器**。服务器声明自己的能力；客户端把工具渲染成模型的函数调用 schema，把资源作为应用上下文暴露出来，把提示词作为用户模板暴露出来（[服务器概览](https://modelcontextprotocol.io/specification/2026-07-28/server)）。模型从来不“说 MCP”——它调用的是函数，由宿主负责翻译。这个翻译层归你所有，白名单、脱敏和追踪都放在这里。

### The 2026-07-28 redesign: what changed

**2026-07-28 的重新设计：改变了什么**

| 2025 mental model<br>2025 年的心智模型 | 2026-07-28 reality<br>2026-07-28 的现实 |
|---|---|
| `initialize` → `notifications/initialized` handshake<br>`initialize` → `notifications/initialized` 握手 | No handshake. Version + capabilities travel in `_meta` on every request; mismatch returns `UnsupportedProtocolVersionError`<br>没有握手。版本 + 能力信息随每个请求放在 `_meta` 中传递；不匹配时返回 `UnsupportedProtocolVersionError` |
| `Mcp-Session-Id` for connection state<br>用 `Mcp-Session-Id` 保存连接状态 | No protocol sessions. Cross-call state uses explicit server-minted handles passed as tool arguments<br>没有协议级会话。跨调用的状态使用由服务器签发、作为工具参数传递的显式句柄 |
| Server-initiated `sampling` / `elicitation` / `roots`<br>由服务器发起的 `sampling` / `elicitation` / `roots` | Multi Round-Trip Requests: `InputRequiredResult` with `inputRequests`; client retries with `inputResponses`; every result carries `resultType`<br>多轮往返请求：带 `inputRequests` 的 `InputRequiredResult`；客户端带着 `inputResponses` 重试；每个结果都携带 `resultType` |
| HTTP GET stream + `resources/subscribe`<br>HTTP GET 流 + `resources/subscribe` | `subscriptions/listen` — one long-lived POST-response stream for opted-in change notifications<br>`subscriptions/listen`——一个长期存活的 POST 响应流，用于推送已订阅的变更通知 |

`ping`, `logging.setLevel` and SSE resumability are gone; HTTP+SSE and Roots/Sampling/Logging are deprecated. A stateless server scales behind any load balancer, and a broken stream is retried as a new request ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).

`ping`、`logging.setLevel` 和 SSE 可续传性都被移除了；HTTP+SSE 以及 Roots/Sampling/Logging 已被弃用。无状态服务器可以放在任何负载均衡器后面横向扩展，而中断的流会作为一个新请求重试（[changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)）。

### Transports: stdio vs Streamable HTTP

**传输方式：stdio vs Streamable HTTP**

- **stdio** — client spawns the server as a child process; newline-delimited JSON-RPC over stdin/stdout. Simple and local, inheriting your OS user; not a multi-tenant boundary.

  **stdio**——客户端把服务器作为子进程启动；通过 stdin/stdout 传输以换行分隔的 JSON-RPC。简单、本地化，继承你的操作系统用户身份；它不是一道多租户边界。

- **Streamable HTTP** — one POST endpoint; each request gets a single JSON response or a request-scoped SSE stream. Origin validation, localhost binding for local servers, and real authentication are server duties ([transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)).

  **Streamable HTTP**——一个 POST 端点；每个请求得到单个 JSON 响应，或一个限定于该请求的 SSE 流。Origin 校验、本地服务器绑定到 localhost，以及真正的身份认证，都是服务器的职责（[传输规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)）。

Streamable HTTP goes behind a gateway — the only transport where OAuth, tenant scoping and rate limiting happen.

Streamable HTTP 要放在网关后面——它是唯一会涉及 OAuth、租户作用域和限流的传输方式。

### The trust boundary: four attacks that matter

**信任边界：四种重要的攻击**

1. **Tool poisoning / rug pull.** Descriptions are attacker-controlled text the model treats as instructions, and a server can change them after approval. Mitigation: pin a digest of description + schema at approval time, re-verify on discovery.

   **工具投毒 / 卷款跑路（rug pull）。** 描述是受攻击者控制、却被模型当作指令的文本，而服务器可以在审批之后修改它们。缓解措施：在审批时锁定描述 + schema 的摘要（digest），并在每次发现时重新验证。

2. **Confused deputy.** The server holds broad credentials and an under-privileged caller asks it to use them. Mitigation: server authority never exceeds the caller's effective authority; derive downstream authz from the caller's scoped token.

   **混淆代理（confused deputy）。** 服务器持有宽泛的凭据，而一个权限不足的调用方请求它使用这些凭据。缓解措施：服务器的权限永远不超过调用方的有效权限；根据调用方限定了作用域的 token 推导下游授权。

3. **Token passthrough.** A server forwards a client token downstream, defeating audience restriction. Forbidden. Mitigation: validate `aud`/issuer, exchange tokens, never replay.

   **token 透传。** 服务器把客户端的 token 转发到下游，使受众限制失效。这是被禁止的。缓解措施：校验 `aud`/签发方，进行 token 交换，绝不重放。

4. **Prompt injection through tool output.** Results are data, not instructions — but models do not reliably honour that. Strip untrusted content, constrain the next step, gate writes behind approval.

   **通过工具输出进行的提示词注入。** 结果是数据，而不是指令——但模型并不能可靠地遵守这一点。剥离不可信内容，约束下一步操作，并让写操作必须经过审批。

All four are in the [security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices), which also covers SSRF, state-handle hijacking and scope minimisation.

这四种攻击都收录在[安全最佳实践](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)中，该文档还涵盖了 SSRF、状态句柄劫持和作用域最小化。

### Ecosystem surfaces you will meet soon

**你很快会遇到的生态组件**

- **Registry.** The official [MCP Registry](https://modelcontextprotocol.io/registry/about) is in preview: `server.json`, DNS/GitHub namespace verification, REST/OpenAPI for aggregators, no private servers. A governed catalogue maps naturally: server = asset, tools = capabilities, namespace = ownership.

  **注册中心（Registry）。** 官方的 [MCP Registry](https://modelcontextprotocol.io/registry/about) 目前处于预览阶段：`server.json`、DNS/GitHub 命名空间验证、面向聚合方的 REST/OpenAPI，不支持私有服务器。它可以自然地映射到一个受治理的目录：服务器 = 资产，工具 = 能力，命名空间 = 所有权。

- **MCP Apps.** The first official extension lets a tool point at a `ui://` resource rendered in a sandboxed iframe ([extensions](https://modelcontextprotocol.io/extensions/overview)). Treat the UI as untrusted code; require consent for UI-initiated calls.

  **MCP Apps。** 第一个官方扩展允许工具指向一个在沙箱化 iframe 中渲染的 `ui://` 资源（[扩展](https://modelcontextprotocol.io/extensions/overview)）。要把这个 UI 当作不可信代码对待；由 UI 发起的调用需要征得用户同意。

### A2A v1.0, AG-UI 1.0, and the decision table

**A2A v1.0、AG-UI 1.0 与决策表**

**A2A** is the horizontal protocol: agents discover each other through an [Agent Card](https://a2a-protocol.org/v1.0.0/whats-new-v1/) at `/.well-known/agent-card.json`, then exchange `Task`/`Message`/`Artifact` over JSON-RPC, gRPC or HTTP+JSON, with SSE/webhooks for progress. v1.0 adds signed cards, multi-tenancy and OAuth device-code/PKCE. Use it when the other side owns its model loop and data.

**A2A** 是横向协议：Agent 之间通过位于 `/.well-known/agent-card.json` 的 [Agent Card](https://a2a-protocol.org/v1.0.0/whats-new-v1/) 相互发现，然后通过 JSON-RPC、gRPC 或 HTTP+JSON 交换 `Task`/`Message`/`Artifact`，并用 SSE/webhook 传递进度。v1.0 新增了签名卡片、多租户以及 OAuth 设备码/PKCE。当对方拥有自己的模型循环和数据时，就用它。

**AG-UI** is the user-facing leg: one request in, one ordered stream of typed events (lifecycle, text, tool calls, reasoning, shared state) out, over SSE or Protobuf ([spec 1.0](https://docs.ag-ui.com/spec/1.0/index)). Use it when a React front-end must render agent behaviour without inventing a schema per framework.

**AG-UI** 是面向用户的那一段：一个请求进来，一条有序的类型化事件流（生命周期、文本、工具调用、推理、共享状态）出去，通过 SSE 或 Protobuf 传输（[规范 1.0](https://docs.ag-ui.com/spec/1.0/index)）。当 React 前端需要渲染 Agent 的行为、又不想为每个框架各发明一套 schema 时，就用它。

| You need to…<br>你需要…… | Use<br>使用 | Why not the alternative<br>为什么不用其他方案 |
|---|---|---|
| Call a function you own, in-process<br>在进程内调用你自己拥有的函数 | Plain function calling<br>普通的函数调用 | No boundary or discovery overhead<br>没有边界或发现的开销 |
| Reuse tools across hosts, or connect a third-party tool server<br>跨宿主复用工具，或接入第三方工具服务器 | **MCP** | Function calling cannot discover or transport tools across processes<br>函数调用无法跨进程发现或传输工具 |
| Delegate a task to another team's/company's agent<br>把任务委派给另一个团队/公司的 Agent | **A2A** | MCP assumes the caller drives the loop; A2A lets the remote agent own it<br>MCP 假定由调用方驱动循环；A2A 则让远端 Agent 自己掌控循环 |
| Stream agent activity into a UI<br>把 Agent 的活动以流的形式推送到 UI | **AG-UI** | A2A is agent-to-agent; MCP is tool-shaped, not presentation-shaped<br>A2A 是 Agent 对 Agent 的；MCP 是面向工具的，而不是面向展示的 |
| Long-running async work between agents<br>Agent 之间长时间运行的异步工作 | **A2A** + push webhooks/tasks<br>**A2A** + 推送 webhook/任务 | A request/response chain does not survive restarts<br>请求/响应链无法在重启后存续 |

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>现实 |
|---|---|
| "MCP replaces function calling."<br>“MCP 取代了函数调用。” | It sits *above* it: the model calls functions; the host maps calls to MCP requests over a transport.<br>它位于函数调用*之上*：模型调用函数；宿主再把这些调用映射为通过某种传输方式发送的 MCP 请求。 |
| "Once a server is connected, its tools are trusted."<br>“服务器一旦接入，它的工具就是可信的。” | Descriptions are untrusted input. Pin digests, allowlist servers, gate writes.<br>描述是不可信的输入。锁定摘要、为服务器设置白名单、为写操作设置关卡。 |
| "MCP and A2A compete."<br>“MCP 和 A2A 是竞争关系。” | MCP is inside an agent (tools/context); A2A is between agents. Mature systems use both.<br>MCP 位于 Agent 内部（工具/上下文）；A2A 位于 Agent 之间。成熟的系统两者都会用。 |
| "The `initialize` handshake is how MCP works."<br>“MCP 就是靠 `initialize` 握手工作的。” | Pre-2026 model. The current spec is stateless; such tutorials are stale.<br>那是 2026 年之前的模型。当前规范是无状态的；这类教程已经过时了。 |
| "Forwarding the user's token downstream is fine."<br>“把用户的 token 转发到下游没问题。” | Token passthrough — an explicit anti-pattern. Exchange or scope; never replay.<br>这就是 token 透传——一个明确的反模式。要交换或限定作用域；绝不重放。 |

## How this shows up in SendOS

**在 SendOS 中如何体现**

- **Catalogue vs runtime discovery.** `CapabilityCatalogueAssembler.cs:34-120` merges three declaration sources and lets published assets win. MCP discovery is runtime introspection; SendOS's registry is a governance decision at publish time. Consume MCP tools *into* a governed catalogue; undeclared capabilities must stay non-invokable.

  **目录 vs 运行时发现。** `CapabilityCatalogueAssembler.cs:34-120` 合并三个声明来源，并让已发布的资产优先。MCP 的发现是运行时的自省；而 SendOS 的注册表是发布时做出的治理决策。要把 MCP 工具*纳入*一个受治理的目录中使用；未声明的能力必须保持不可调用。

- **Audience and scope are authority narrowing.** `EffectiveAuthority.cs:8-36,114-225` intersects ten independent boundaries and `Delegate()` only narrows. An MCP token's scopes must be a subset of effective authority for that tenant/actor; a server must not widen it. RFC 8707 resource indicators, expressed as a business rule.

  **受众和作用域就是在收窄权限。** `EffectiveAuthority.cs:8-36,114-225` 对十个相互独立的边界取交集，而 `Delegate()` 只会收窄权限。MCP token 的作用域必须是该租户/操作者有效权限的子集；服务器不得扩大它。这就是用业务规则表达的 RFC 8707 资源指示符（resource indicators）。

- **Boundary crossings must be traceable.** `IOutcomeTraceEmitter.cs:24-45` is the append-only event seam. Stamp every MCP call's execution origin (server id, tool name, description digest, latency, scopes) so incidents replay.

  **跨越边界的行为必须可追踪。** `IOutcomeTraceEmitter.cs:24-45` 是只追加的事件接缝（seam）。为每一次 MCP 调用打上执行来源的标记（服务器 id、工具名、描述摘要、延迟、作用域），以便事故可以重放。

## Check yourself

**自测**

1. A 2026-07-28 client never sends `initialize`. What replaces negotiation, and what happens on version mismatch?

   一个 2026-07-28 版的客户端从不发送 `initialize`。用什么取代了协商？版本不匹配时会发生什么？

2. Give one catalogue asset that should be a tool, one a resource, one a prompt.

   分别举出一个应当作为工具、一个应当作为资源、一个应当作为提示词的目录资产。

3. A tool receives the caller's token and needs to call Graph. What is wrong with forwarding it, and what should the server do instead?

   一个工具收到了调用方的 token，并且需要调用 Graph。直接转发它有什么问题？服务器应该怎么做？

4. When is A2A right over MCP, and what must an Agent Card expose — and not expose?

   什么时候 A2A 比 MCP 更合适？Agent Card 必须暴露什么——又绝不能暴露什么？

5. You approved a server last month; its tool description now carries a new instruction. Which attack is this, and what control catches it?

   你上个月批准了一个服务器；它的工具描述现在多了一条新指令。这是哪种攻击？哪项控制措施能发现它？

## Reading

**延伸阅读**

- [MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) — the normative delta.

  [MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)——规范性的变更内容。

- [MCP security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) — confused deputy, token passthrough, SSRF, state-handle hijacking.

  [MCP security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)——混淆代理、token 透传、SSRF、状态句柄劫持。

- [A2A v1.0: what's new](https://a2a-protocol.org/v1.0.0/whats-new-v1/) — agent cards, bindings, breaking changes.

  [A2A v1.0: what's new](https://a2a-protocol.org/v1.0.0/whats-new-v1/)——Agent Card、协议绑定、破坏性变更。

- [AG-UI specification 1.0](https://docs.ag-ui.com/spec/1.0/index) — event families and conformance.

  [AG-UI specification 1.0](https://docs.ag-ui.com/spec/1.0/index)——事件类别与一致性要求。

- **Companion book:** *AI Agents in Depth* v2.0, ch.4 §4.3–4.4 — MCP in the wider tool ecosystem, skills as on-demand lookup, and proactive tool discovery. Treat the book as the map and this repo's lab as the wire-level implementation. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 4 章 §4.3–4.4——更广泛工具生态中的 MCP、作为按需查找手段的 skill，以及主动式工具发现。把这本书当作地图，把本仓库的实验当作协议层面的实现。[章节对照表](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
