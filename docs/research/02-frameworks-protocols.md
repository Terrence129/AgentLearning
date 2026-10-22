# Agent Frameworks, SDKs & Protocols — Landscape Brief (as of 2026-10-18)

**Agent 框架、SDK 与协议——全景简报（截至 2026-10-18）**

> **Audience:** senior Java/C#/React/AWS engineer new to LLM apps, working on an enterprise .NET agent platform (Model Adapter over OpenAI/Anthropic/Bedrock + governed-asset catalogue).
> **Method:** primary specs, vendor docs and release feeds fetched 2026-10-18. ✅ = verified on a primary source that day; ⚠️ = second-hand, inferred or version-uncertain. Re-verify versions before procurement.
> **Thesis:** protocols converged (MCP for tools, A2A for agents, AG-UI for users); frameworks did not — learn the protocol seams and one workflow runtime deeply, and let most frameworks stay documentation.
>
> **读者：** 刚接触 LLM 应用的资深 Java/C#/React/AWS 工程师，正在开发一个企业级 .NET Agent 平台（基于 OpenAI/Anthropic/Bedrock 的 Model Adapter + 受治理资产目录）。
> **方法：** 一手规范、厂商文档和发布源，均抓取于 2026-10-18。✅ = 当天已在一手来源上核实；⚠️ = 二手、推断得出或版本不确定。采购前请重新核实版本。
> **论点：** 协议已经收敛（工具用 MCP，Agent 之间用 A2A，面向用户用 AG-UI）；框架却没有——深入学习协议接缝（seam）和一个工作流运行时，让大多数框架停留在“读过文档”的层面即可。

---

## 0. Five takeaways

**五个要点**

1. **MCP became infrastructure, not a feature.** The latest spec (✅ `2026-07-28`) went **stateless**: `initialize`, protocol sessions, `Mcp-Session-Id`, the HTTP GET stream and `ping`/`logging.setLevel` are gone; version negotiation moved into `_meta`, servers must implement `server/discover`, and server→client requests became **Multi Round-Trip Requests** ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)). Roots, Sampling and Logging are **deprecated**. MCP is now a boring, scalable HTTP integration layer — exactly what a catalogue team should standardise on.

   **MCP 成了基础设施，而不是一项功能。** 最新规范（✅ `2026-07-28`）转向了**无状态**：`initialize`、协议会话、`Mcp-Session-Id`、HTTP GET 流以及 `ping`/`logging.setLevel` 都已移除；版本协商移到了 `_meta` 中，服务器必须实现 `server/discover`，而服务器→客户端的请求变成了**多轮往返请求**（Multi Round-Trip Requests）（[changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)）。Roots、Sampling 和 Logging 已被**弃用**。MCP 如今是一个平淡无奇、可扩展的 HTTP 集成层——这恰恰是目录团队应当统一采用的标准。

2. **A2A is the horizontal standard, governed by a foundation, not a vendor.** v1.0 shipped 2026-03-12 with a TSC spanning AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP and ServiceNow ([announcement](https://a2a-protocol.org/dev/blog/2026/03/12/a2a-protocol-ships-v10-production-ready-standard-for-agent-to-agent-communication/)); it joined the **Agentic AI Foundation (AAIF)** on 2026-08-27 with **150+ organisations** and native support in Google Cloud, Bedrock AgentCore and Azure AI Foundry ([AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)).

   **A2A 是横向标准，由基金会而非某个厂商治理。** v1.0 于 2026-03-12 发布，其 TSC 成员涵盖 AWS、Cisco、Google、IBM Research、Microsoft、Salesforce、SAP 和 ServiceNow（[公告](https://a2a-protocol.org/dev/blog/2026/03/12/a2a-protocol-ships-v10-production-ready-standard-for-agent-to-agent-communication/)）；它于 2026-08-27 加入 **Agentic AI Foundation（AAIF）**，拥有 **150+ 家组织**，并在 Google Cloud、Bedrock AgentCore 和 Azure AI Foundry 中获得原生支持（[AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)）。

3. **Agent frameworks split into three families** — (a) *harness SDKs* (Claude, OpenAI) rent you a production loop; (b) *workflow runtimes* (LangGraph, MAF, ADK 2.0, Mastra, Pydantic AI) make you own the graph; (c) *platforms* (AgentCore, Temporal, Cloudflare) sell durability. Choose by bottleneck.

   **Agent 框架分化为三大类**——(a) *harness（运行框架）SDK*（Claude、OpenAI）把一个生产级循环租给你；(b) *工作流运行时*（LangGraph、MAF、ADK 2.0、Mastra、Pydantic AI）要求你自己掌控图；(c) *平台*（AgentCore、Temporal、Cloudflare）售卖的是持久性。按瓶颈来选。

4. **Provider APIs are converging on "stateful Responses + server tools".** OpenAI's Responses API (GPT‑6‑class models) adds background mode, WebSocket mode, mid-turn steering, multi-agent, compaction, webhooks and a Decisions API; Assistants was **sunset 2026-08-26** ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)). Anthropic ships server tools (web search/fetch, code execution, advisor, tool search, MCP connector) plus client tools (memory, bash, text editor, computer/browser toolsets) ([tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)). An adapter that only does chat completions is already behind.

   **模型提供商（provider）的 API 正在向“有状态 Responses + 服务器端工具”收敛。** OpenAI 的 Responses API（GPT‑6 级模型）新增了后台模式、WebSocket 模式、轮次中途引导（mid-turn steering）、多 Agent、压缩（compaction）、webhook 以及 Decisions API；Assistants 已于 **2026-08-26 停用**（[迁移指南](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)）。Anthropic 提供服务器端工具（web search/fetch、代码执行、advisor、工具搜索、MCP 连接器）以及客户端工具（memory、bash、文本编辑器、computer/browser 工具集）（[工具参考](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)）。只支持 chat completions 的适配器已经落后了。

5. **Your highest-leverage .NET skill is not a framework — it is exposing the governed-asset catalogue over MCP (OAuth, registry metadata, OpenTelemetry), then wrapping the Model Adapter as a `Microsoft.Extensions.AI` chat client** so Microsoft Agent Framework consumes it without rewrites. Python-wise: **Pydantic AI → LangGraph → OpenAI Agents SDK or Claude Agent SDK** is the shortest path to designing the platform's agent layer.

   **你杠杆最高的 .NET 技能不是某个框架——而是通过 MCP 暴露受治理资产目录（OAuth、注册中心元数据、OpenTelemetry），再把 Model Adapter 包装成一个 `Microsoft.Extensions.AI` 聊天客户端**，让 Microsoft Agent Framework 无需重写即可使用它。Python 方面：**Pydantic AI → LangGraph → OpenAI Agents SDK 或 Claude Agent SDK** 是设计平台 Agent 层的最短路径。

---

## 1. Protocol layer

**协议层**

### 1.1 MCP — Model Context Protocol

**MCP——Model Context Protocol（模型上下文协议）**

**Status:** production standard under AAIF governance (joined 2025-12-09). Latest spec ✅ **2026-07-28**; previous revision 2025-11-25; older 2025-06-18 deployments are still common.

**状态：** AAIF 治理下的生产级标准（2025-12-09 加入）。最新规范 ✅ **2026-07-28**；上一修订版为 2025-11-25；基于更早的 2025-06-18 版的部署仍然很常见。

**What changed in 2026-07-28 (the release that matters for platform design)** — from the [official changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog):

**2026-07-28 版改变了什么（对平台设计至关重要的一个版本）**——摘自[官方 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)：

- **Stateless core.** No `initialize` handshake; every request carries protocol version and client capabilities in `_meta`; mismatches return `UnsupportedProtocolVersionError`; servers MUST implement `server/discover`.

  **无状态核心。** 没有 `initialize` 握手；每个请求都在 `_meta` 中携带协议版本和客户端能力；不匹配时返回 `UnsupportedProtocolVersionError`；服务器必须（MUST）实现 `server/discover`。

- **No protocol-level sessions.** `Mcp-Session-Id` removed; cross-call state uses explicit server-minted handles passed as ordinary tool args (SEP-2567).

  **没有协议级会话。** `Mcp-Session-Id` 已移除；跨调用的状态使用由服务器签发、作为普通工具参数传递的显式句柄（SEP-2567）。

- **`subscriptions/listen`** replaces the GET endpoint and `resources/subscribe`: one long-lived POST-response stream for opt-in list/resource change notifications.

  **`subscriptions/listen`** 取代了 GET 端点和 `resources/subscribe`：一个长期存活的 POST 响应流，用于按需订阅的列表/资源变更通知。

- **Multi Round-Trip Requests (MRTR)** replace server-initiated `sampling`/`elicitation`/`roots`: servers return `InputRequiredResult` (`resultType: "input_required"`) with `inputRequests`; clients retry the original call with `inputResponses` (SEP-2322). All results now carry `resultType`.

  **多轮往返请求**（MRTR）取代了由服务器发起的 `sampling`/`elicitation`/`roots`：服务器返回带有 `inputRequests` 的 `InputRequiredResult`（`resultType: "input_required"`）；客户端带着 `inputResponses` 重试原始调用（SEP-2322）。现在所有结果都携带 `resultType`。

- **Extensions** first-class; experimental **tasks** moved to `io.modelcontextprotocol/tasks` (poll `tasks/get`, input `tasks/update`).

  **扩展**（Extensions）成为一等公民；实验性的 **tasks** 移到了 `io.modelcontextprotocol/tasks`（通过 `tasks/get` 轮询，通过 `tasks/update` 提供输入）。

- **Caching, headers, tracing:** list/read results must include `ttlMs`/`cacheScope`; Streamable HTTP POSTs carry `Mcp-Method`/`Mcp-Name` headers (plus per-tool `x-mcp-header`); tools SHOULD be listed deterministically to improve prompt-cache hits; OpenTelemetry context (`traceparent`, `tracestate`, `baggage`) travels in `_meta`.

  **缓存、请求头、追踪：** list/read 结果必须包含 `ttlMs`/`cacheScope`；Streamable HTTP 的 POST 请求携带 `Mcp-Method`/`Mcp-Name` 请求头（外加按工具设置的 `x-mcp-header`）；工具应当（SHOULD）以确定性的顺序列出，以提高提示词缓存命中率；OpenTelemetry 上下文（`traceparent`、`tracestate`、`baggage`）在 `_meta` 中传递。

- **Deprecated:** Roots, Sampling, Logging; HTTP+SSE transport; OAuth **Dynamic Client Registration** in favour of **Client ID Metadata Documents**; SSE resumability/`Last-Event-ID` removed outright.

  **已弃用：** Roots、Sampling、Logging；HTTP+SSE 传输；OAuth 的**动态客户端注册**（Dynamic Client Registration）被弃用，改用 **Client ID 元数据文档**（Client ID Metadata Documents）；SSE 可续传性/`Last-Event-ID` 则被直接移除。

**Transports.** `stdio` (local) and **Streamable HTTP** — one POST endpoint answering with JSON or a request-scoped SSE stream ([transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)). Servers MUST validate `Origin`, SHOULD bind localhost-only, SHOULD authenticate; no session affinity means trivial multi-replica deployment.

**传输方式。** `stdio`（本地）和 **Streamable HTTP**——单个 POST 端点，以 JSON 或请求作用域内的 SSE 流作答（[传输规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)）。服务器必须（MUST）校验 `Origin`，应当（SHOULD）只绑定 localhost，应当（SHOULD）进行认证；没有会话亲和性意味着多副本部署轻而易举。

**Auth.** Transport-level OAuth: authorization-code + PKCE, RFC 8707 resource indicators, RFC 9207 `iss` validation, issuer-keyed credentials, scope step-up ([authorization spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index)). Copy the shape: **MCP server = OAuth resource server; catalogue = authorization + entitlement data**.

**认证。** 传输层 OAuth：授权码 + PKCE、RFC 8707 资源指示符、RFC 9207 `iss` 校验、按签发方（issuer）区分的凭据、scope 升级（step-up）（[授权规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index)）。照搬这个形态：**MCP 服务器 = OAuth 资源服务器；目录 = 授权 + 权益数据**。

**Registry.** The [official MCP Registry](https://modelcontextprotocol.io/registry/about) is in **preview**: `server.json`, DNS/GitHub namespace verification, REST + OpenAPI for aggregators, no private-network servers (self-host a private registry against the same OpenAPI). Map catalogue entries to `server.json` early.

**注册中心。** [官方 MCP Registry](https://modelcontextprotocol.io/registry/about) 目前处于**预览**阶段：`server.json`、DNS/GitHub 命名空间验证、面向聚合器的 REST + OpenAPI、不收录私有网络中的服务器（可基于同一套 OpenAPI 自建私有注册中心）。尽早把目录条目映射到 `server.json`。

**MCP Apps** (first official extension, ✅ 2026-01-26): tools declare `_meta.ui.resourceUri` pointing at a `ui://` resource; hosts render bundled HTML/JS in sandboxed iframes with JSON-RPC over `postMessage`; supported in Claude, Goose, VS Code Insiders and ChatGPT ([announcement](https://modelcontextprotocol.info/blog/mcp-apps-ui-capabilities/)). ⚠️ Third-party UI is untrusted code: sandbox, consent for UI-initiated tool calls, log everything.

**MCP Apps**（第一个官方扩展，✅ 2026-01-26）：工具声明一个指向 `ui://` 资源的 `_meta.ui.resourceUri`；宿主在沙箱化的 iframe 中渲染打包好的 HTML/JS，并通过 `postMessage` 承载 JSON-RPC；Claude、Goose、VS Code Insiders 和 ChatGPT 均已支持（[公告](https://modelcontextprotocol.info/blog/mcp-apps-ui-capabilities/)）。⚠️ 第三方 UI 是不可信代码：要沙箱化，由 UI 发起的工具调用须经用户同意，并记录一切。

**Security posture.** Origin checks and auth do not solve semantic risk — tool poisoning, prompt injection through tool output, over-broad scopes, confused deputies. Build MCP servers narrow, read-mostly and per-asset-scope.

**安全态势。** Origin 检查和认证解决不了语义层面的风险——工具投毒、通过工具输出进行的提示词注入、过宽的 scope、混淆代理人（confused deputy）。构建 MCP 服务器时要做到功能收窄、以只读为主，并按资产划分 scope。

### 1.2 A2A — Agent2Agent

**A2A——Agent2Agent**

**Status:** ✅ v1.0 stable since 2026-03-12; **AAIF Growth Stage project** since 2026-08-27 ([AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)). TSC: AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow.

**状态：** ✅ 自 2026-03-12 起 v1.0 稳定；自 2026-08-27 起成为 **AAIF 成长阶段（Growth Stage）项目**（[AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)）。TSC：AWS、Cisco、Google、IBM Research、Microsoft、Salesforce、SAP、ServiceNow。

**Spec facts worth knowing** (from the [v1.0 "what's new" doc](https://a2a-protocol.org/v1.0.0/whats-new-v1/)):

**值得了解的规范要点**（摘自 [v1.0 “what's new” 文档](https://a2a-protocol.org/v1.0.0/whats-new-v1/)）：

- Core objects: **AgentCard, Task, Message, Artifact**, unified `Part`; `a2a.proto` is the normative source of truth; three bindings with equivalence guarantees: **JSON-RPC 2.0**, **gRPC**, **HTTP+JSON/REST**. Discovery at `/.well-known/agent-card.json`; per-interface `protocolVersion` and `A2A-Version` / `A2A-Extensions` headers.

  核心对象：**AgentCard、Task、Message、Artifact**，以及统一的 `Part`；`a2a.proto` 是具有规范效力的唯一事实来源；三种绑定，并保证彼此等价：**JSON-RPC 2.0**、**gRPC**、**HTTP+JSON/REST**。发现地址为 `/.well-known/agent-card.json`；按接口声明 `protocolVersion`，并使用 `A2A-Version` / `A2A-Extensions` 请求头。

- Operations are PascalCase (`SendMessage`, `SendStreamingMessage`, `GetTask`, `ListTasks`, `CancelTask`, `SubscribeToTask`, push-notification CRUD, `GetExtendedAgentCard`); streaming via SSE; async via push webhooks or polling.

  操作名采用 PascalCase（`SendMessage`、`SendStreamingMessage`、`GetTask`、`ListTasks`、`CancelTask`、`SubscribeToTask`、推送通知的 CRUD、`GetExtendedAgentCard`）；流式输出通过 SSE；异步则通过推送 webhook 或轮询。

- **Enterprise features:** multi-tenancy (`tenant` on all requests), **signed Agent Cards** (JWS + RFC 8785), mTLS, modern OAuth 2.0 (device code RFC 8628, PKCE-required flag), `google.rpc.Status` errors, cursor pagination, ISO-8601 timestamps.

  **企业级特性：** 多租户（所有请求都带 `tenant`）、**签名的 Agent Card**（JWS + RFC 8785）、mTLS、现代 OAuth 2.0（设备码 RFC 8628、强制 PKCE 的标志）、`google.rpc.Status` 错误、游标分页、ISO-8601 时间戳。

- **Breaking vs v0.3:** enums became SCREAMING_SNAKE_CASE (`TASK_STATE_COMPLETED`, `ROLE_USER`), `kind` discriminators removed, compound IDs replaced by UUIDs + separate fields, `/v1` prefix removed from HTTP paths, `supportedInterfaces[]` replaced `preferredTransport`.

  **相对 v0.3 的破坏性变更：** 枚举改为 SCREAMING_SNAKE_CASE（`TASK_STATE_COMPLETED`、`ROLE_USER`），移除了 `kind` 判别字段，复合 ID 被 UUID + 独立字段取代，HTTP 路径去掉了 `/v1` 前缀，`supportedInterfaces[]` 取代了 `preferredTransport`。

**Adoption evidence:** 150+ organisations; native A2A in Google Cloud, **AWS Bedrock AgentCore Runtime** and **Azure AI Foundry**; ServiceNow/Salesforce/Atlassian/SAP workflows; framework support in LangGraph, CrewAI, Pydantic AI, AG2 and IBM BeeAI ([AAIF post](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/), [LF press release](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)). SDKs: Python, Go, Java, JS, **.NET**, Rust ([a2a-protocol.org](https://a2a-protocol.org)).

**采用证据：** 150+ 家组织；Google Cloud、**AWS Bedrock AgentCore Runtime** 和 **Azure AI Foundry** 原生支持 A2A；ServiceNow/Salesforce/Atlassian/SAP 的工作流；LangGraph、CrewAI、Pydantic AI、AG2 和 IBM BeeAI 提供框架支持（[AAIF 文章](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)，[LF 新闻稿](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)）。SDK：Python、Go、Java、JS、**.NET**、Rust（[a2a-protocol.org](https://a2a-protocol.org)）。

### 1.3 AG-UI — Agent–User Interaction Protocol

**AG-UI——Agent 与用户交互协议**

**Status:** ✅ **spec 1.0** ([spec](https://docs.ag-ui.com/spec/1.0/index)). "One request in, one ordered stream of typed events out" — the missing browser-facing leg: MCP = agent↔tools, A2A = agent↔agent, **AG-UI = agent↔user**.

**状态：** ✅ **规范 1.0**（[规范](https://docs.ag-ui.com/spec/1.0/index)）。“一个请求进，一条有序的类型化事件流出”——这是此前缺失的、面向浏览器的那一环：MCP = Agent↔工具，A2A = Agent↔Agent，**AG-UI = Agent↔用户**。

- Event families: run/step lifecycle, text, tool calls, reasoning, shared state (snapshot–delta), activity, subagents, raw/custom passthrough. Middleware runs before enforcement, unknown material survives, malformed known values are fatal, conformance is per stream.

  事件类别：运行/步骤生命周期、文本、工具调用、推理、共享状态（快照–增量（delta））、活动、子 Agent、原始/自定义透传。中间件在强制校验之前运行，未知内容会被保留，格式错误的已知值属于致命错误，合规性按每条流单独判定。

- Transports: **HTTP+SSE**, **HTTP+Protobuf**, custom bindings with a contract; patterns include streaming, snapshot–delta state and interrupt–resume (HITL), plus a Generative UI proposal.

  传输方式：**HTTP+SSE**、**HTTP+Protobuf**，以及带契约的自定义绑定；模式包括流式输出、快照–增量状态和中断–恢复（即人在回路，HITL），另有一个生成式 UI（Generative UI）提案。

- SDKs: TypeScript, Python, **.NET**, Kotlin/Go. Integrations are unusually broad: LangGraph, **Microsoft Agent Framework**, Google ADK, Antigravity, Strands, Mastra, Pydantic AI, Agno, LlamaIndex, CrewAI, AG2, Langroid, Cloudflare Agents, **Claude Agent SDK/Managed Agents**; front-end via CopilotKit; AgentCore runtime support ([integrations](https://docs.ag-ui.com/integrations)).

  SDK：TypeScript、Python、**.NET**、Kotlin/Go。集成范围异常广泛：LangGraph、**Microsoft Agent Framework**、Google ADK、Antigravity、Strands、Mastra、Pydantic AI、Agno、LlamaIndex、CrewAI、AG2、Langroid、Cloudflare Agents、**Claude Agent SDK/Managed Agents**；前端通过 CopilotKit 接入；AgentCore 运行时也提供支持（[集成列表](https://docs.ag-ui.com/integrations)）。

- **Why it matters to you:** cleanly decouples a React SPA from agent runtimes, gives typed tool-call/reasoning/state events instead of prose, and doubles as an audit stream.

  **为什么这对你很重要：** 它把 React SPA 与 Agent 运行时干净地解耦，提供类型化的工具调用/推理/状态事件而不是大段文字，还能兼作审计流。

### 1.4 The rest of the alphabet (and which are noise)

**其余的协议“字母表”（以及哪些只是噪音）**

- **ACP = three different things.** (a) **Agent Client Protocol** (Zed): editor↔coding-agent stdio JSON-RPC; an **ACP Registry is live** — the layer behind "bring Claude Code/Codex/Gemini CLI into your editor" ([Zed](https://zed.dev/blog/acp-registry)). (b) **IBM Agent Communication Protocol**: REST messaging, effectively **absorbed by A2A**; ⚠️ status unverified, do not build on it ([IBM](https://www.ibm.com/think/topics/agent-communication-protocol), [guide](https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/)). (c) **Agentic Commerce Protocol** (OpenAI/Stripe) — see payments.

  **ACP 指的是三种不同的东西。** (a) **Agent Client Protocol**（Zed）：编辑器↔编码 Agent 之间基于 stdio 的 JSON-RPC；**ACP Registry 已经上线**——它就是“把 Claude Code/Codex/Gemini CLI 带进你的编辑器”背后的那一层（[Zed](https://zed.dev/blog/acp-registry)）。(b) **IBM Agent Communication Protocol**：基于 REST 的消息传递，实际上已**被 A2A 吸收**；⚠️ 状态未核实，不要在其上构建（[IBM](https://www.ibm.com/think/topics/agent-communication-protocol)，[指南](https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/)）。(c) **Agentic Commerce Protocol**（OpenAI/Stripe）——见下文支付部分。

- **AGNTCY (Cisco/Outshift):** agent directory **DIR** (content-addressed, OCI-style), **OASF** agent records, **SLIM** secure messaging; active releases ([DIR](https://github.com/agntcy/dir/releases), [intro](https://outshift.prod.eticloud.io/blog/agntcy-agent-directory-find-and-publish-ai-agents)). ⚠️ Real but niche outside Cisco pilots — watch, don't standardise.

  **AGNTCY（Cisco/Outshift）：** Agent 目录 **DIR**（内容寻址、OCI 风格）、**OASF** Agent 记录、**SLIM** 安全消息传递；版本发布活跃（[DIR](https://github.com/agntcy/dir/releases)，[介绍](https://outshift.prod.eticloud.io/blog/agntcy-agent-directory-find-and-publish-ai-agents)）。⚠️ 确实存在，但在 Cisco 的试点之外很小众——保持关注即可，不要把它定为标准。

- **Payments: AP2 vs ACP.** Google's **AP2** uses mandates (Intent/Cart/Payment) with verifiable credentials; ⚠️ **donated to the FIDO Alliance**, now standards work rather than a shipping product ([FIDO](https://fidoalliance.org/google-donates-agent-payments-protocol-to-fido-alliance/), [Google](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)). **Agentic Commerce Protocol** is a checkout-flow spec, and ⚠️ reported pull-back from in-chat checkout suggests churn ([research](https://www.foresightventures.com/details?details_id=90&details_type=research), [Forkast](https://forkast.news/openai-built-in-chat-checkout-for-ai-commerce-five-months-later-it-walked-away/)). Neither should gate your roadmap in 2026.

  **支付：AP2 vs ACP。** Google 的 **AP2** 使用基于可验证凭证的授权指令（mandate，分为 Intent/Cart/Payment）；⚠️ 它已**捐赠给 FIDO Alliance**，如今属于标准化工作，而不是一款正在交付的产品（[FIDO](https://fidoalliance.org/google-donates-agent-payments-protocol-to-fido-alliance/)，[Google](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)）。**Agentic Commerce Protocol** 是一份结账流程规范，而 ⚠️ 据报道其已从聊天内结账中撤退，说明方向仍在变动（[研究报告](https://www.foresightventures.com/details?details_id=90&details_type=research)，[Forkast](https://forkast.news/openai-built-in-chat-checkout-for-ai-commerce-five-months-later-it-walked-away/)）。在 2026 年，两者都不应成为你路线图的前置条件。

- **`agent.json`:** a W3C AI-VS community-group *proposal* for a universal manifest plus "quality graph" trust scoring — discussion only, **not a standard** ([W3C archive](https://lists.w3.org/Archives/Public/public-aivs/2026May/0000.html)).

  **`agent.json`：** W3C AI-VS 社区小组的一份*提案*，提出一种通用清单（manifest）外加“质量图谱（quality graph）”信任评分——仅停留在讨论阶段，**并非标准**（[W3C 存档](https://lists.w3.org/Archives/Public/public-aivs/2026May/0000.html)）。

- **`llms.txt`:** still a convention; a 137k-site Ahrefs study found **~97% of `llms.txt` files never get fetched** — SEO folklore, not agent discovery ([Ahrefs](https://ahrefs.com/blog/llmstxt-study/)).

  **`llms.txt`：** 仍然只是一种约定；Ahrefs 对 13.7 万个站点的研究发现，**约 97% 的 `llms.txt` 文件从未被抓取过**——这是 SEO 圈的民间说法，而不是 Agent 发现机制（[Ahrefs](https://ahrefs.com/blog/llmstxt-study/)）。

- **`AGENTS.md`:** won. A plain-Markdown instruction file supported across coding agents (including a Claude Code fallback) and an AAIF sibling project alongside MCP, goose and A2A ([DevOps.com](https://devops.com/claude-code-adds-agents-md-fallback-cutting-instruction-file-sprawl/), [AAIF](https://aaif.io/projects)). Adopt it for repo onboarding today.

  **`AGENTS.md`：** 胜出了。它是一种纯 Markdown 的指令文件，得到各类编码 Agent 的支持（包括 Claude Code 的回退机制），也是与 MCP、goose 和 A2A 并列的 AAIF 兄弟项目（[DevOps.com](https://devops.com/claude-code-adds-agents-md-fallback-cutting-instruction-file-sprawl/)，[AAIF](https://aaif.io/projects)）。今天就用它来做仓库的上手引导吧。

### 1.5 Protocol comparison

**协议对比**

| Protocol<br>协议 | Current spec / version (date)<br>当前规范 / 版本（日期） | Transport<br>传输方式 | Auth model<br>认证模型 | Adoption evidence<br>采用证据 | Confidence<br>可信度 |
|---|---|---|---|---|---|
| **MCP** | 2026-07-28 (latest); 2025-11-25 prev.<br>2026-07-28（最新）；2025-11-25（上一版） | stdio; Streamable HTTP (single POST endpoint, per-request SSE); HTTP+SSE deprecated<br>stdio；Streamable HTTP（单一 POST 端点，按请求的 SSE）；HTTP+SSE 已弃用 | OAuth: auth-code+PKCE, RFC 8707 resource indicators, client-ID metadata documents (DCR deprecated)<br>OAuth：授权码 + PKCE、RFC 8707 资源指示符、Client ID 元数据文档（DCR 已弃用） | Official registry (preview), MCP Apps in Claude/ChatGPT/VS Code/Goose, AAIF project; de-facto tool standard<br>官方注册中心（预览）、MCP Apps 已进入 Claude/ChatGPT/VS Code/Goose、AAIF 项目；事实上的工具标准 | ✅ high<br>✅ 高 |
| **A2A** | v1.0 (2026-03-12) | JSON-RPC 2.0, gRPC, HTTP+JSON/REST; SSE streaming + webhooks<br>JSON-RPC 2.0、gRPC、HTTP+JSON/REST；SSE 流式输出 + webhook | OAuth 2.0 (device code, PKCE), mTLS, **signed Agent Cards (JWS)**, tenant scoping<br>OAuth 2.0（设备码、PKCE）、mTLS、**签名的 Agent Card（JWS）**、租户作用域 | 150+ orgs; Google Cloud, AgentCore, Azure AI Foundry; SAP/ServiceNow/Salesforce; .NET SDK; AAIF project<br>150+ 家组织；Google Cloud、AgentCore、Azure AI Foundry；SAP/ServiceNow/Salesforce；.NET SDK；AAIF 项目 | ✅ high<br>✅ 高 |
| **AG-UI** | 1.0 | HTTP+SSE; HTTP+Protobuf; custom bindings<br>HTTP+SSE；HTTP+Protobuf；自定义绑定 | Delegated to app/transport; consent + trust-boundary rules in spec; no wire auth<br>交由应用/传输层负责；规范中包含用户同意 + 信任边界规则；没有线上（wire）认证 | Broad framework integrations (MAF, ADK, LangGraph, Pydantic AI, Claude SDKs); CopilotKit; AgentCore support<br>广泛的框架集成（MAF、ADK、LangGraph、Pydantic AI、Claude SDK）；CopilotKit；AgentCore 支持 | ✅ spec; ⚠️ governance<br>✅ 规范；⚠️ 治理 |
| **ACP (Agent Client Protocol)** | pre-1.0, registry live 2026<br>1.0 之前，注册中心于 2026 年上线 | stdio JSON-RPC between editor and coding agent<br>编辑器与编码 Agent 之间的 stdio JSON-RPC | Local trust, agent-declared permissions<br>本地信任，由 Agent 声明权限 | Zed + editor ecosystem; embeds Claude Code/Codex/Gemini CLI<br>Zed + 编辑器生态；可嵌入 Claude Code/Codex/Gemini CLI | ⚠️ medium<br>⚠️ 中 |
| **ACP (IBM Agent Communication)** | legacy<br>遗留 | REST/HTTP | Bearer/OAuth | Folded toward A2A; low new adoption<br>正在并入 A2A；新增采用很少 | ⚠️ low<br>⚠️ 低 |
| **AGNTCY DIR** | active releases 2026<br>2026 年版本发布活跃 | OCI-style content-addressed directory; SLIM messaging<br>OCI 风格的内容寻址目录；SLIM 消息传递 | Identity via OASF records / enterprise IdP<br>通过 OASF 记录 / 企业 IdP 提供身份 | Cisco/Outshift-led pilots<br>Cisco/Outshift 主导的试点 | ⚠️ medium<br>⚠️ 中 |
| **AP2** | donated to FIDO (2026)<br>已捐赠给 FIDO（2026） | HTTP + verifiable credentials/mandates<br>HTTP + 可验证凭证/授权指令 | Cryptographic mandates, VC/JWT<br>密码学授权指令、VC/JWT | Spec + partner pilots; not GA infra<br>规范 + 合作伙伴试点；尚非 GA 级基础设施 | ⚠️ low/medium<br>⚠️ 低/中 |
| **Agentic Commerce Protocol** | evolving<br>演进中 | HTTP checkout APIs<br>HTTP 结账 API | Merchant OAuth/keys<br>商户 OAuth/密钥 | OpenAI/Stripe experiments; churn<br>OpenAI/Stripe 的实验；变动频繁 | ⚠️ low<br>⚠️ 低 |
| **agent.json** | proposal (2026-05)<br>提案（2026-05） | n/a | n/a | W3C CG discussion<br>W3C CG 讨论 | ⚠️ low<br>⚠️ 低 |
| **AGENTS.md** | convention, de-facto<br>约定，事实标准 | n/a (file)<br>n/a（文件） | n/a | Multi-vendor coding agents, AAIF project<br>多厂商编码 Agent、AAIF 项目 | ✅ medium-high<br>✅ 中高 |
| **llms.txt** | convention<br>约定 | n/a (file)<br>n/a（文件） | n/a | ~97% never fetched<br>约 97% 从未被抓取 | ⚠️ low<br>⚠️ 低 |

**Reading the table:** build on MCP + A2A + AG-UI; ACP-client is an editor convenience; AGNTCY/AP2/agent.json are watch-list.

**如何解读此表：** 基于 MCP + A2A + AG-UI 来构建；ACP 客户端只是编辑器层面的便利；AGNTCY/AP2/agent.json 列入观察名单即可。

---

## 2. Framework comparison

**框架对比**

Versions from release feeds fetched 2026-10-18; ⚠️ = unconfirmed. "Adoption" is qualitative, not measured market share.

版本信息来自 2026-10-18 抓取的发布源；⚠️ = 未确认。“采用度”是定性判断，并非实测的市场份额。

| Framework (version)<br>框架（版本） | Lang<br>语言 | Paradigm<br>范式 | Tools<br>工具 | HITL<br>人在回路 | Durability<br>持久性 | Observability<br>可观测性 | Prod<br>生产就绪度 | Adoption<br>采用度 | Curve<br>学习曲线 | Best fit<br>最适合 |
|---|---|---|---|---|---|---|---|---|---|---|
| **OpenAI Agents SDK** 0.24 | Py, TS | Agent loop + handoffs<br>Agent 循环 + 交接（handoff） | Functions, hosted tools, MCP<br>函数、托管工具、MCP | Approvals, deferred approvals<br>审批、延迟审批 | RunState + session stores; Temporal extra<br>RunState + 会话存储；Temporal 扩展 | Built-in tracing<br>内置追踪 | High; 0.x churn<br>高；0.x 版本变动频繁 | Very high<br>非常高 | Low<br>低 | OpenAI-first products<br>以 OpenAI 为主的产品 |
| **Claude Agent SDK** 0.2.168 | Py, TS | Claude Code harness<br>Claude Code 的 harness | Built-in file/bash tools, MCP, plugins<br>内置文件/bash 工具、MCP、插件 | Hooks + permission callbacks<br>钩子 + 权限回调 | Session resume/fork<br>会话恢复/分叉 | Hook/stream events<br>钩子/流事件 | High (coding)<br>高（编码场景） | High<br>高 | Low–Med<br>低–中 | Coding/computer automation<br>编码/计算机自动化 |
| **Google ADK** 2.12 | Py, TS, Go | Graph workflows + multi-agent<br>图工作流 + 多 Agent | Functions, toolsets, MCP<br>函数、工具集、MCP | `require_confirmation` | Workflow runtime + session stores<br>工作流运行时 + 会话存储 | OTel, BigQuery, Agent Engine | High (GA)<br>高（GA） | High; GCP-centric<br>高；以 GCP 为中心 | Med<br>中 | Gemini/Vertex; deterministic graphs<br>Gemini/Vertex；确定性图 |
| **MS Agent Framework** 1.0 | .NET, Py | Agents + workflows + orchestrations<br>Agent + 工作流 + 编排 | Functions, MCP, A2A, OpenAPI<br>函数、MCP、A2A、OpenAPI | Approvals, hosted agents<br>审批、托管 Agent | Checkpoints, durable sessions<br>检查点、持久会话 | OTel built-in<br>内置 OTel | High (LTS)<br>高（LTS） | High enterprise<br>企业中采用度高 | Low–Med<br>低–中 | .NET enterprise default<br>.NET 企业的默认选择 |
| **LangGraph** 1.2.16 + LangChain v1 | Py, TS | Explicit graph/state machine<br>显式图/状态机 | Tools, MCP, subgraphs<br>工具、MCP、子图 | `interrupt()` + resume<br>`interrupt()` + 恢复 | Checkpointers, time travel<br>检查点器（checkpointer）、时间回溯 | LangSmith/OTel | High<br>高 | Very high<br>非常高 | Med<br>中 | Auditable deterministic workflows<br>可审计的确定性工作流 |
| **Pydantic AI** 2.57 | Py | Typed loop + graphs<br>类型化循环 + 图 | Typed tools, MCP<br>类型化工具、MCP | Deferred tools, ask-user<br>延迟工具、询问用户 | Temporal/DBOS/Prefect/Restate adapters<br>Temporal/DBOS/Prefect/Restate 适配器 | Logfire/OTel | High & rising<br>高且在上升 | Growing<br>增长中 | Low–Med<br>低–中 | Type-safe, provider-agnostic services<br>类型安全、与提供商无关的服务 |
| **CrewAI** 1.15.27 | Py | Role crews + flows<br>角色团队（crew）+ 流程（flow） | Tools, MCP, A2A<br>工具、MCP、A2A | HITL steps<br>人在回路步骤 | Flow persistence<br>Flow 持久化 | Listeners<br>监听器 | Med–High<br>中–高 | Large<br>大 | Low<br>低 | Prototypes, back-office<br>原型、后台业务 |
| **Mastra** 1.78 core | TS | Agent + durable workflows<br>Agent + 持久化工作流 | Tools, MCP, routes<br>工具、MCP、路由 | Approval hooks, signals<br>审批钩子、信号 | Durable workflows, resume<br>持久化工作流、恢复 | OTel + exporters<br>OTel + 导出器 | High<br>高 | Large TS/React<br>在 TS/React 圈子中大 | Low–Med<br>低–中 | React/Next.js products<br>React/Next.js 产品 |
| **Vercel AI SDK** 7 | TS | Model abstraction + UI primitives<br>模型抽象 + UI 原语 | Typed tools, MCP client<br>类型化工具、MCP 客户端 | Tool approval, UI interrupts<br>工具审批、UI 中断 | Harness packages; BYO runtime<br>harness 包；自带运行时（BYO） | OTel spans<br>OTel span | High<br>高 | Massive<br>海量 | Low<br>低 | Streaming UI, provider abstraction<br>流式 UI、提供商抽象 |
| **smolagents** | Py | Minimal code-agent loop<br>极简的代码 Agent 循环 | Python functions, code exec<br>Python 函数、代码执行 | Limited<br>有限 | Minimal<br>极少 | Minimal<br>极少 | Med<br>中 | Niche<br>小众 | Very low<br>非常低 | Learning internals<br>学习内部原理 |
| **Agno** 3.1.4 | Py | Agents/teams/workflows + AgentOS<br>Agent/团队/工作流 + AgentOS | Toolkits, MCP, A2A<br>工具包、MCP、A2A | Approvals, background runs<br>审批、后台运行 | Durable Postgres queue, checkpoints<br>持久化 Postgres 队列、检查点 | OTel | High<br>高 | Growing<br>增长中 | Low–Med<br>低–中 | Full-stack Python services<br>全栈 Python 服务 |
| **DSPy** 3.x ⚠️ | Py | Compile/optimise programs<br>编译/优化程序 | Typed predictors/modules<br>类型化预测器/模块 | n/a | n/a | Evals<br>评测（eval） | Med<br>中 | Large research<br>在研究界规模大 | High<br>高 | Eval-driven optimisation<br>评测驱动的优化 |
| **Haystack** 2.26 ⚠️ | Py | Pipelines + agents<br>流水线 + Agent | Tools, MCP<br>工具、MCP | Basic<br>基础 | Checkpointing<br>检查点 | OTel | High (RAG)<br>高（RAG） | Large<br>大 | Med<br>中 | RAG/search<br>RAG/搜索 |
| **LlamaIndex Workflows** ⚠️ | Py, TS | Event-driven workflows<br>事件驱动的工作流 | Toolsets, MCP, query engines<br>工具集、MCP、查询引擎 | Interrupt/resume<br>中断/恢复 | Context serialisation<br>上下文序列化 | Instrumentation<br>插桩（instrumentation） | High (data apps)<br>高（数据应用） | Large<br>大 | Med<br>中 | Document/data agents<br>文档/数据 Agent |
| **Letta** ⚠️ | Py | Memory-first stateful agents<br>记忆优先的有状态 Agent | Tools, MCP<br>工具、MCP | Approval<br>审批 | Server-persisted state<br>服务器端持久化状态 | Limited<br>有限 | Med<br>中 | Niche<br>小众 | Med<br>中 | Long-lived memory agents<br>长期记忆型 Agent |
| **Bedrock AgentCore** | Managed + SDK<br>托管 + SDK | Managed harness/runtime/gateway<br>托管的 harness/运行时/网关 | MCP gateway, web search, KB<br>MCP 网关、网页搜索、知识库 | Approvals, gateway policy<br>审批、网关策略 | MicroVM sessions, checkpoints<br>MicroVM 会话、检查点 | OTel/CloudWatch | High<br>高 | AWS enterprises<br>AWS 企业用户 | Low<br>低 | AWS-native governed runtime<br>AWS 原生的受治理运行时 |
| **Cloudflare Agents** 0.16 | TS | Stateful agents on Durable Objects<br>基于 Durable Objects 的有状态 Agent | Tools, MCP<br>工具、MCP | Tool approval<br>工具审批 | DO storage, alarms<br>DO 存储、定时唤醒（alarm） | Workers observability<br>Workers 可观测性 | Med–High<br>中–高 | Edge apps<br>边缘应用 | Low<br>低 | Edge stateful chat<br>边缘有状态聊天 |
| **Temporal** (SDK 1.34) | Py/TS/Java/.NET/Go | Durable execution<br>持久化执行 | BYO<br>自带（BYO） | Signals/queries<br>信号/查询 | Best-in-class replay<br>一流的重放能力 | OTel | Very high<br>非常高 | Massive<br>海量 | Med<br>中 | Mission-critical long-running agents<br>关键任务型长时运行 Agent |
| **Inngest** | TS/Py/Go | Event-driven durable workflows<br>事件驱动的持久化工作流 | `step`, `waitForEvent` | Approval via events<br>通过事件进行审批 | Excellent<br>优秀 | OTel | High<br>高 | Growing<br>增长中 | Low–Med<br>低–中 | Event-driven agents<br>事件驱动的 Agent |

### 2.1 Cluster notes (what the table hides)

**分组说明（表格没有体现的内容）**

**Harness SDKs (Claude, OpenAI).** You adopt someone else's loop, tools and safety model: Claude Code's harness (hooks, permissions, subagents, skills, MCP, sessions) is the most battle-tested coding loop in production, exposed as a library ([overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). OpenAI's SDK turned the same way in 2026 — sandboxing, a new model harness, durable `RunState`, deferred approvals, MCP annotations, optional Temporal/Vercel extras ([v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0), [DevOps.com](https://devops.com/openai-upgrades-its-agents-sdk-with-sandboxing-and-a-new-model-harness/)). Risk: 0.x churn and provider gravity.

**Harness SDK（Claude、OpenAI）。** 你采用的是别人的循环、工具和安全模型：Claude Code 的 harness（钩子、权限、子 Agent、skills、MCP、会话）是生产环境中久经考验的编码循环，并以库的形式开放出来（[概览](https://code.claude.com/docs/en/agent-sdk/overview.md)）。OpenAI 的 SDK 在 2026 年也转向了同一方向——沙箱、新的模型 harness、持久化的 `RunState`、延迟审批、MCP 注解，以及可选的 Temporal/Vercel 扩展（[v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0)，[DevOps.com](https://devops.com/openai-upgrades-its-agents-sdk-with-sandboxing-and-a-new-model-harness/)）。风险：0.x 版本的频繁变动，以及被提供商“引力”绑定。

**Workflow runtimes (LangGraph, MAF, ADK 2.0, Mastra, Pydantic Graph).** Everything became a graph. ADK 2.0 replaced its hierarchical executor with a **Workflow runtime** where agents are nodes (`BaseNode`, `RetryConfig`, resumable pauses) — a breaking migration ([ADK 2.0](https://adk.dev/2.0/index.md)). Microsoft Agent Framework unifies Semantic Kernel + AutoGen with workflows, orchestrations and checkpointing ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)). LangGraph remains the reference implementation, with LangChain v1's `create_agent` as the on-ramp ([LangChain v1](https://docs.langchain.com/oss/python/releases/langchain-v1.md)). For auditability and replay, this is the family.

**工作流运行时（LangGraph、MAF、ADK 2.0、Mastra、Pydantic Graph）。** 一切都变成了图。ADK 2.0 用一个 **Workflow 运行时**取代了原先的层级式执行器，Agent 在其中是节点（`BaseNode`、`RetryConfig`、可恢复的暂停）——这是一次破坏性迁移（[ADK 2.0](https://adk.dev/2.0/index.md)）。Microsoft Agent Framework 统一了 Semantic Kernel + AutoGen，并提供工作流、编排和检查点（[1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)）。LangGraph 仍然是参考实现，而 LangChain v1 的 `create_agent` 是入门的匝道（[LangChain v1](https://docs.langchain.com/oss/python/releases/langchain-v1.md)）。若看重可审计性和重放，就选这一类。

**Type-safe service stacks (Pydantic AI, Agno, Haystack).** Pydantic AI feels like typed Python — DI, typed tools, output schemas — plus durable-execution adapters (Temporal/DBOS/Prefect/Restate) and AG-UI/Vercel AI UI integrations ([durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/)). Fastest mental mapping for a C#/Java engineer.

**类型安全的服务栈（Pydantic AI、Agno、Haystack）。** Pydantic AI 用起来就像类型化的 Python——依赖注入（DI）、类型化工具、输出 schema——外加持久化执行适配器（Temporal/DBOS/Prefect/Restate）以及 AG-UI/Vercel AI UI 集成（[持久化执行](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/)）。对 C#/Java 工程师来说，这是心智映射最快的一类。

**Team/role frameworks (CrewAI, AG2).** Great demos, dangerous defaults when control flow must be explicit. Prefer deterministic Flows for production; treat crews as prototyping (⚠️ verify in current docs; [changelog](https://docs.crewai.com/v1.15.27/en/changelog)).

**团队/角色框架（CrewAI、AG2）。** 演示效果很棒，但当控制流必须显式化时，它们的默认设置很危险。生产环境优先使用确定性的 Flows；把 crew 当作原型工具（⚠️ 请对照当前文档核实；[changelog](https://docs.crewai.com/v1.15.27/en/changelog)）。

**Platforms (Bedrock AgentCore, Cloudflare Agents, Temporal, Inngest).** AgentCore is the most complete governed-agent platform: Managed Harness (model + prompt + tools, microVM per session), Gateway with MCP/web search, managed knowledge base, Recommendations/Batch evals/A-B testing, 5,000 concurrent sessions, native A2A/AG-UI ([AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)). Temporal and Inngest are where mature teams go when "the agent must survive a deploy" ([ZenML](https://www.zenml.io/blog/inngest-vs-temporal)).

**平台（Bedrock AgentCore、Cloudflare Agents、Temporal、Inngest）。** AgentCore 是最完整的受治理 Agent 平台：Managed Harness（模型 + 提示词 + 工具，每个会话一个 microVM）、带 MCP/网页搜索的 Gateway、托管知识库、Recommendations/批量评测/A-B 测试、5,000 个并发会话、原生 A2A/AG-UI（[AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)）。当“Agent 必须能扛过一次部署”时，成熟团队会选择 Temporal 和 Inngest（[ZenML](https://www.zenml.io/blog/inngest-vs-temporal)）。

**The TS/React lane (Mastra, Vercel AI SDK).** With your React strength this is the fastest demo path: Mastra 1.x is a real server framework — durable workflows, memory, evals, agent scopes ([1.78](https://github.com/mastra-ai/mastra/releases)); Vercel AI SDK v7 is the best model/UI abstraction. Neither should be the orchestration core in a .NET shop.

**TS/React 路线（Mastra、Vercel AI SDK）。** 凭借你在 React 上的优势，这是最快的演示路径：Mastra 1.x 是一个真正的服务端框架——持久化工作流、记忆、评测、Agent 作用域（[1.78](https://github.com/mastra-ai/mastra/releases)）；Vercel AI SDK v7 是最好的模型/UI 抽象。但在以 .NET 为主的团队里，两者都不应成为编排核心。

---

## 3. Model-provider agent capabilities (what your Model Adapter must expose)

**模型提供商的 Agent 能力（你的 Model Adapter 必须暴露的内容）**

**OpenAI — Responses API is the agent primitive.** Built-in tools (web/file search, computer use, code interpreter, remote MCP), stateful context (`store`, `previous_response_id`, Conversations API), encrypted reasoning for ZDR, typed Items, typed SSE events, `text.format` structured outputs, agentic loop by default ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)). The docs index also shows **background mode, WebSocket mode, mid-turn steering, multi-agent, webhooks, compaction and a Decisions API**, with GPT‑6‑class models (`gpt-6-astra`, `gpt-6.1-sol`). Chat Completions still works but is feature-frozen; Assistants was **sunset 2026-08-26**. Adapter implication: expose *items, tool calls, reasoning summaries, response ids* — not just `choices`.

**OpenAI——Responses API 是 Agent 的基本原语。** 内置工具（网页/文件搜索、computer use、代码解释器、远程 MCP）、有状态上下文（`store`、`previous_response_id`、Conversations API）、面向 ZDR 的加密推理、类型化的 Items、类型化的 SSE 事件、`text.format` 结构化输出，默认即为 Agent 式循环（[迁移指南](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)）。文档索引中还列出了**后台模式、WebSocket 模式、轮次中途引导、多 Agent、webhook、压缩以及 Decisions API**，并配有 GPT‑6 级模型（`gpt-6-astra`、`gpt-6.1-sol`）。Chat Completions 仍然可用，但功能已冻结；Assistants 已于 **2026-08-26 停用**。对适配器的影响：要暴露 *items、工具调用、推理摘要、response id*——而不只是 `choices`。

**Anthropic — Messages API plus a large server-tool surface.** Server-side: web search/fetch, code execution (including programmatic tool calling), advisor, tool search, MCP connector; client-side: memory, bash, text editor, computer/browser toolsets (dated types; `computer_toolset_20260801` current) ([tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)). Context management is first-class: prompt caching on tool definitions, context editing, mid-conversation system messages/tool changes, compaction, thinking/effort/fast-mode. Anthropic also sells **Managed Agents** — hosted harness, Anthropic-managed or self-hosted sandbox — competing with AgentCore ([Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)).

**Anthropic——Messages API 加上庞大的服务器端工具面。** 服务器端：web search/fetch、代码执行（包括程序化工具调用）、advisor、工具搜索、MCP 连接器；客户端：memory、bash、文本编辑器、computer/browser 工具集（带日期的类型；当前为 `computer_toolset_20260801`）（[工具参考](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)）。上下文管理是一等公民：工具定义上的提示词缓存、上下文编辑、对话中途的系统消息/工具变更、压缩、thinking/effort/fast-mode。Anthropic 还提供 **Managed Agents**——托管的 harness，沙箱可由 Anthropic 管理或自托管——与 AgentCore 竞争（[Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)）。

**Google — Gemini 4 generation, Live API, Interactions API.** Docs promote **Gemini 4 "Argon"**; Live API is stateful **WebSocket** streaming (16 kHz PCM in / 24 kHz out, images ≤1 FPS, barge-in, tool use, ephemeral tokens) ([Live API](https://ai.google.dev/gemini-api/docs/live-api)). Around it: function calling, Search/Maps grounding, code execution, URL context, computer use, file search and a newer **Interactions API** with managed agents/Antigravity ([docs](https://ai.google.dev/gemini-api/docs)). WebSocket streaming and thought signatures need first-class adapter support if voice/vision is on the roadmap.

**Google——Gemini 4 代模型、Live API、Interactions API。** 文档主推 **Gemini 4 “Argon”**；Live API 是有状态的 **WebSocket** 流式传输（16 kHz PCM 输入 / 24 kHz 输出，图像 ≤1 FPS，支持插话（barge-in）、工具使用、临时 token）（[Live API](https://ai.google.dev/gemini-api/docs/live-api)）。围绕它的还有：函数调用、Search/Maps grounding、代码执行、URL 上下文、computer use、文件搜索，以及一个较新的、带托管 Agent/Antigravity 的 **Interactions API**（[文档](https://ai.google.dev/gemini-api/docs)）。如果语音/视觉在路线图上，WebSocket 流式传输和思维签名（thought signature）都需要适配器提供一等支持。

**Bedrock / AgentCore.** Bedrock supplies models; AgentCore supplies runtime, gateway, identity, memory, browser/code-interpreter and evals, with native A2A/AG-UI and an MCP-based gateway ([AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)). Reuse its governance primitives rather than rebuild them.

**Bedrock / AgentCore。** Bedrock 提供模型；AgentCore 提供运行时、网关、身份、记忆、浏览器/代码解释器和评测，并原生支持 A2A/AG-UI，还有一个基于 MCP 的网关（[AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)）。复用它的治理原语，而不是自己重建。

**DeepSeek and local (vLLM/Ollama).** ⚠️ First-party DeepSeek agent tooling was not verified; assume OpenAI-compatible chat + reasoning models, strong price/perf, weaker tool-calling polish, no server tools. vLLM/Ollama are OpenAI-compatible for chat but **tool calling and structured output vary by model template and server feature**, so the adapter needs per-model capability flags, not one global "supports tools" boolean.

**DeepSeek 与本地部署（vLLM/Ollama）。** ⚠️ DeepSeek 的第一方 Agent 工具链未经核实；可假定它是兼容 OpenAI 的聊天 + 推理模型，性价比高，工具调用的打磨较弱，没有服务器端工具。vLLM/Ollama 在聊天方面兼容 OpenAI，但**工具调用和结构化输出会因模型模板和服务器特性而异**，因此适配器需要按模型设置的能力标志，而不是一个全局的“supports tools”布尔值。

**Structured outputs and reasoning — document these in the adapter:** strict schema output is table stakes, but reasoning models degrade when forced into tool-calling + heavy schemas (from GPT‑5.4, OpenAI does **not** support tool calling on Chat Completions with `reasoning_effort` other than `none` — a strong reason to standardise on Responses); reasoning tokens are billed and must round-trip (encrypted reasoning/thought signatures); cache efficiency is now an agent-design variable (stable prefixes, deterministic tool order — which MCP now mandates — and `defer_loading` for large catalogues).

**结构化输出与推理——要在适配器中把这些记录清楚：** 严格的 schema 输出只是基本门槛，但推理模型在被强制使用工具调用 + 繁重的 schema 时表现会退化（从 GPT‑5.4 起，当 `reasoning_effort` 不为 `none` 时，OpenAI 在 Chat Completions 上**不**支持工具调用——这是统一采用 Responses 的有力理由）；推理 token 要计费，并且必须完整回传（加密推理/思维签名）；缓存效率如今已是 Agent 设计中的一个变量（稳定的前缀、确定性的工具顺序——MCP 现已强制要求——以及针对大型目录的 `defer_loading`）。

---

## 4. Reference agent-native tools worth reading as architecture

**值得作为架构范本来阅读的 Agent 原生参考工具**

You do not need to clone these; you need to **read their harness design** because the harness, not the model, is where the engineering is.

你不需要克隆这些项目；你需要的是**阅读它们的 harness 设计**，因为工程的重心在 harness，而不在模型。

| Tool<br>工具 | What to steal<br>可以借鉴什么 | Where to look<br>去哪里看 |
|---|---|---|
| **Claude Code / Agent SDK** | Permission model (auto-allow vs ask), lifecycle hooks, subagents for context isolation, skills as progressively disclosed instructions, compaction, sandbox policy<br>权限模型（自动允许 vs 询问）、生命周期钩子、用于上下文隔离的子 Agent、作为渐进式披露指令的 skills、压缩、沙箱策略 | [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md); [harness essay](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)<br>[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md)；[harness 文章](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code) |
| **OpenAI Codex CLI / harness** | Approval matrix, sandboxed command execution, patch/diff discipline; the harness was **open-sourced Aug 2026**<br>审批矩阵、沙箱化的命令执行、patch/diff 纪律；其 harness 已于 **2026 年 8 月开源** | [Open Source For You](https://www.opensourceforu.com/2026/08/openai-open-sources-codex-harness/) |
| **OpenHands** | Event-stream architecture (actions/observations), sandboxed runtime, trajectory replay, SWE-bench-style evaluation<br>事件流架构（动作/观察）、沙箱化运行时、轨迹重放、SWE-bench 式评测 | [Harness engineering survey](https://export.arxiv.org/pdf/2609.00006)<br>[Harness 工程综述](https://export.arxiv.org/pdf/2609.00006) |
| **SWE-agent** | Agent-Computer Interface: tool ergonomics beat raw model IQ; guardrailed shell/file editing<br>Agent-计算机接口（ACI）：工具的易用性设计胜过模型的原始智商；带护栏的 shell/文件编辑 | [ACI paper](https://arxiv.org/abs/2405.15793)<br>[ACI 论文](https://arxiv.org/abs/2405.15793) |
| **Aider** | Repo map (symbol graph in prompt), diff-based edits, token-efficient context<br>仓库地图（放进提示词的符号图）、基于 diff 的编辑、节省 token 的上下文 | [aider.chat](https://aider.chat) |
| **Cursor** | Trained retrieval/long-horizon behaviour (Composer), self-summarisation, latency/UX trade-offs<br>经过训练的检索/长程行为（Composer）、自我摘要、延迟/用户体验之间的权衡 | [Composer blog](https://cursor.com/en/blog/self-summarization)<br>[Composer 博客](https://cursor.com/en/blog/self-summarization) |

Cross-cutting lessons: **context engineering dominates prompt engineering** — tool-output truncation, deferred loading, compaction and summarisation are the real quality levers; the **permission/sandbox boundary is part of the product**; and **trajectories are the debugging artefact** — full event streams with tool arguments/results are mandatory for evals and audits.

贯穿各家的经验：**上下文工程的重要性压倒提示词工程**——工具输出截断、延迟加载、压缩和摘要才是真正的质量杠杆；**权限/沙箱边界是产品的一部分**；**轨迹（trajectory）是调试的核心产物**——包含工具参数/结果的完整事件流，对评测和审计来说是必需的。

---

## 5. Decision matrix: what to learn first

**决策矩阵：先学什么**

### 5.1 Python — learn these 3, in this order

**Python——按此顺序学这 3 个**

| Order<br>顺序 | Stack<br>技术栈 | Why for *you specifically*<br>为什么*特别适合你* | Effort<br>投入 | Transfers to .NET?<br>能迁移到 .NET 吗？ | Verdict<br>结论 |
|---|---|---|---|---|---|
| 1 | **Pydantic AI** (2–3 wks)<br>**Pydantic AI**（2–3 周） | Typed models ≈ C# records; DI ≈ constructor injection; provider-agnostic model layer mirrors your Model Adapter; tools, structured outputs, evals and durable execution in one mental model — concepts without framework archaeology.<br>类型化模型 ≈ C# record；DI ≈ 构造函数注入；与提供商无关的模型层正好对应你的 Model Adapter；工具、结构化输出、评测和持久化执行都在同一个心智模型里——直接学概念，无需做框架考古。 | Low–Med<br>低–中 | High (concepts)<br>高（概念层面） | **First.** Build a "governed-asset Q&A + tool call" agent with typed outputs and a tiny eval suite.<br>**第一个。** 构建一个带类型化输出和小型评测套件的“受治理资产问答 + 工具调用”Agent。 |
| 2 | **LangGraph + LangChain v1** (3–4 wks)<br>**LangGraph + LangChain v1**（3–4 周） | Durable state machine with checkpointers, replay, `interrupt()` HITL and time travel — the Python analogue of enterprise governance. Middleware (PII redaction, summarisation, HITL) maps to platform policy points.<br>带检查点器、重放、`interrupt()` 人在回路和时间回溯的持久化状态机——相当于企业治理在 Python 世界中的对应物。中间件（PII 脱敏、摘要、人在回路）可映射到平台的策略点。 | Med<br>中 | High (→ MAF workflows)<br>高（→ MAF 工作流） | **Second.** 3-node graph with Postgres checkpointer, approval interrupt, replay demo.<br>**第二个。** 一个 3 节点的图，带 Postgres 检查点器、审批中断和重放演示。 |
| 3 | **OpenAI Agents SDK** (if OpenAI/Azure-first) **or Claude Agent SDK** (if coding/computer automation) (2 wks)<br>**OpenAI Agents SDK**（如果以 OpenAI/Azure 为主）**或 Claude Agent SDK**（如果做编码/计算机自动化）（2 周） | Both are production loops to read and steal from: OpenAI handoffs/guardrails/sessions/RunState/tracing ([v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0)); Claude hooks/subagents/permissions/skills harness ([overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). Read the Python source — it is small.<br>两者都是值得阅读和借鉴的生产级循环：OpenAI 的 handoff/护栏/会话/RunState/追踪（[v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0)）；Claude 的钩子/子 Agent/权限/skills harness（[概览](https://code.claude.com/docs/en/agent-sdk/overview.md)）。去读 Python 源码——它的规模很小。 | Low<br>低 | Med (patterns)<br>中（模式层面） | **Pick one, not both.** Then stop collecting frameworks.<br>**二选一，不要两个都学。** 然后就别再收集框架了。 |

**Explicit non-recommendations:** don't start with CrewAI/AG2 swarms (demo magic, not engineering); don't write your own loop before reading OpenAI's; don't invest in DSPy until you have an eval set; skip Python MCP servers — your leverage is .NET; AgentCore/Cloudflare are deployment decisions, not learning material. If your employer standardises on GCP, swap #3 for **Google ADK 2.0** — its graph runtime is the closest sibling to MAF, with `to_a2a`/`RemoteA2aAgent` interop.

**明确不推荐：** 不要从 CrewAI/AG2 的 swarm（群体）入手（那是演示魔法，不是工程）；在读过 OpenAI 的循环之前，不要自己写循环；在拥有评测集之前，不要投入 DSPy；跳过 Python 版的 MCP 服务器——你的杠杆在 .NET；AgentCore/Cloudflare 是部署决策，而不是学习材料。如果你的雇主以 GCP 为标准，就把第 3 项换成 **Google ADK 2.0**——它的图运行时是与 MAF 最接近的“兄弟”，并支持 `to_a2a`/`RemoteA2aAgent` 互操作。

### 5.2 .NET — what makes you immediately useful at work

**.NET——让你在工作中立刻派上用场的内容**

| Priority<br>优先级 | What<br>内容 | Concrete deliverable<br>具体交付物 | Why it lands<br>为什么有效 |
|---|---|---|---|
| **P0** | **Microsoft Agent Framework .NET 1.x** (`Microsoft.Agents.AI` + OpenAI/Anthropic/Bedrock connectors, workflows, orchestrations, hosting)<br>**Microsoft Agent Framework .NET 1.x**（`Microsoft.Agents.AI` + OpenAI/Anthropic/Bedrock 连接器、工作流、编排、托管） | One vertical slice: an `AIAgent` with 2–3 catalogue tools inside a workflow with an approval step and OpenTelemetry spans<br>一个垂直切片：一个带 2–3 个目录工具的 `AIAgent`，运行在包含审批步骤和 OpenTelemetry span 的工作流中 | Likely strategic SDK: 1.0 April 2026, LTS, unifies Semantic Kernel + AutoGen; .NET and Python first-class ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/))<br>很可能是战略级 SDK：2026 年 4 月发布 1.0，LTS，统一了 Semantic Kernel + AutoGen；.NET 和 Python 都是一等公民（[1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)） |
| **P0** | **`Microsoft.Extensions.AI` `IChatClient` adapter** for your Model Adapter<br>为你的 Model Adapter 编写的 **`Microsoft.Extensions.AI` `IChatClient` 适配器** | One `IChatClient` routing to OpenAI/Anthropic/Bedrock, exposing tool calls, streaming, reasoning metadata and capability flags<br>一个路由到 OpenAI/Anthropic/Bedrock 的 `IChatClient`，暴露工具调用、流式输出、推理元数据和能力标志 | MAF is built on Microsoft.Extensions.AI, so one wrapper lets every MAF agent/workflow/tool use your governed adapter — policy stays in one place ⚠️ verify abstraction version in your platform<br>MAF 构建在 Microsoft.Extensions.AI 之上，因此一个包装层就能让每个 MAF Agent/工作流/工具都使用你的受治理适配器——策略集中在一处 ⚠️ 请核实你平台中的抽象层版本 |
| **P1** | **MCP server in .NET for the governed-asset catalogue**<br>**用 .NET 为受治理资产目录实现的 MCP 服务器** | search/get/lineage/entitlement tools, OAuth resource-server auth, `server.json`, deterministic ordering, `ttlMs`/`cacheScope`, OTel in `_meta`<br>search/get/lineage/entitlement 工具、OAuth 资源服务器认证、`server.json`、确定性排序、`ttlMs`/`cacheScope`、`_meta` 中的 OTel | Highest-leverage protocol work: makes the catalogue consumable by Claude/ChatGPT/VS Code/Copilot *and* every internal agent; stateless spec scales easily behind your gateway ([spec](https://modelcontextprotocol.io/specification/2026-07-28/changelog))<br>杠杆最高的协议工作：让目录既能被 Claude/ChatGPT/VS Code/Copilot 使用，*也*能被每个内部 Agent 使用；无状态规范放在你的网关后面可以轻松扩展（[规范](https://modelcontextprotocol.io/specification/2026-07-28/changelog)） |
| **P1** | **A2A .NET SDK** | Signed agent cards for 1–2 platform agents (tenant scoping), streaming call to another team's agent<br>为 1–2 个平台 Agent 提供签名的 Agent Card（租户作用域），并以流式方式调用另一个团队的 Agent | Cross-org standard, 150+ orgs, native cloud support ([a2a-protocol.org](https://a2a-protocol.org))<br>跨组织标准，150+ 家组织，云平台原生支持（[a2a-protocol.org](https://a2a-protocol.org)） |
| **P2** | **AG-UI .NET + React** | Typed agent events (tool calls, state, approvals) into your React front-end instead of a chat blob<br>把类型化的 Agent 事件（工具调用、状态、审批）送入你的 React 前端，而不是一整团聊天文本 | Reuses your React strength; first-class MAF support ([integrations](https://docs.ag-ui.com/integrations))<br>复用你的 React 优势；MAF 提供一等支持（[集成列表](https://docs.ag-ui.com/integrations)） |
| **P2** | **Semantic Kernel bridge**<br>**Semantic Kernel 桥接** | Map SK plugins/planners onto MAF tools/workflows; keep SK only where deployed<br>把 SK 的插件/规划器映射到 MAF 的工具/工作流上；只在已部署的地方保留 SK | SK knowledge remains a migration asset ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/))<br>SK 知识仍然是一项迁移资产（[1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)） |

**Governance mapping for your platform** (the opinionated part):

**你所在平台的治理映射**（带有鲜明主张的部分）：

1. **Keep the Model Adapter as the only provider boundary.** Point each framework at your adapter endpoint; normalise items/messages, tool calls, structured-output mode, reasoning blobs, cache controls, usage and per-model capability flags.

   **让 Model Adapter 成为唯一的提供商边界。** 把每个框架都指向你的适配器端点；对 items/消息、工具调用、结构化输出模式、推理数据块、缓存控制、用量以及按模型的能力标志做统一的规范化。

2. **Make the catalogue the source of truth for tools, not the framework.** Every callable asset = MCP tool + `server.json` metadata + A2A agent card (if an agent) + policy attributes (owner, classification, scopes) — frameworks become interchangeable consumers.

   **让目录而不是框架成为工具的事实来源。** 每个可调用资产 = MCP 工具 + `server.json` 元数据 + A2A Agent Card（如果它是 Agent）+ 策略属性（所有者、密级、scope）——框架由此变成可互换的消费者。

3. **Treat HITL as a platform primitive.** One approval service (who, what, why, expiry, replayable decision) wired to LangGraph `interrupt`, MAF human-in-loop, ADK `require_confirmation`, AG-UI interrupts and A2A `TASK_STATE_INPUT_REQUIRED`.

   **把人在回路当作平台原语。** 一个审批服务（谁、做什么、为什么、何时过期、可重放的决策），接入 LangGraph `interrupt`、MAF 人在回路、ADK `require_confirmation`、AG-UI 中断以及 A2A `TASK_STATE_INPUT_REQUIRED`。

4. **OTel GenAI semantics + MCP trace propagation are the audit trail** (`traceparent`/`tracestate`/`baggage` in `_meta`); support both MCP revisions (2025-11-25, 2026-07-28) as routing, not a code fork.

   **OTel GenAI 语义约定 + MCP trace 传播就是审计轨迹**（`_meta` 中的 `traceparent`/`tracestate`/`baggage`）；对两个 MCP 修订版（2025-11-25、2026-07-28）的支持要做成路由，而不是代码分叉。

### 5.3 A 90-day plan (2–4 hrs/week)

**90 天计划（每周 2–4 小时）**

| Weeks<br>周次 | Focus<br>重点 | Output<br>产出 |
|---|---|---|
| 1–4 | Provider APIs + Pydantic AI: typed tools, structured output, evals; MCP client consumption<br>提供商 API + Pydantic AI：类型化工具、结构化输出、评测；以 MCP 客户端身份调用 | Adapter capability matrix; "governed-asset Q&A" agent + 10-case eval suite<br>适配器能力矩阵；“受治理资产问答”Agent + 含 10 个用例的评测套件 |
| 5–8 | LangGraph (checkpointer, interrupt, replay) + .NET MCP server + MAF slice with `IChatClient` adapter and OTel<br>LangGraph（检查点器、中断、重放）+ .NET MCP 服务器 + 带 `IChatClient` 适配器和 OTel 的 MAF 切片 | Durable approval workflow; catalogue MCP server; vertical slice inside the platform<br>持久化审批工作流；目录 MCP 服务器；平台内的垂直切片 |
| 9–12 | A2A signed agent card + cross-agent task; AG-UI stream into React; hardening and policy<br>A2A 签名 Agent Card + 跨 Agent 任务；AG-UI 流接入 React；加固与策略 | Two agents delegating; typed UI stream; architecture decision record<br>两个相互委派任务的 Agent；类型化 UI 流；架构决策记录 |

**What "learned" means:** you predict a framework's breaking changes from its changelog, you can move an agent between runtimes without touching the catalogue, and you can tell a security reviewer exactly where prompts, tool arguments, approvals and traces live.

**“学会了”意味着什么：** 你能从一个框架的 changelog 预判它的破坏性变更，能在不改动目录的情况下把 Agent 在不同运行时之间迁移，并且能准确地告诉安全评审人员：提示词、工具参数、审批和 trace 分别存放在哪里。

---

## 6. Uncertainty register (claims I could not fully verify)

**不确定性登记表（我未能完全核实的说法）**

| Claim<br>说法 | Status<br>状态 |
|---|---|
| Exact versions for smolagents, DSPy, Haystack, LlamaIndex Workflows, Letta server<br>smolagents、DSPy、Haystack、LlamaIndex Workflows、Letta server 的确切版本 | ⚠️ **unverified** (partial release evidence only)<br>⚠️ **未核实**（仅有部分发布证据） |
| Microsoft Agent Framework **.NET** patch version (Python 1.22.0 confirmed; .NET uses separate tags)<br>Microsoft Agent Framework **.NET** 的补丁版本（Python 1.22.0 已确认；.NET 使用独立的标签） | ⚠️ **unverified**; 1.0 GA date confirmed<br>⚠️ **未核实**；1.0 GA 日期已确认 |
| IBM ACP status; AGNTCY production maturity<br>IBM ACP 的状态；AGNTCY 的生产成熟度 | ⚠️ second-hand / medium confidence<br>⚠️ 二手信息 / 中等可信度 |
| AP2 adoption after FIDO donation; Agentic Commerce Protocol direction<br>捐赠给 FIDO 之后 AP2 的采用情况；Agentic Commerce Protocol 的方向 | ⚠️ low confidence; standards in flux<br>⚠️ 低可信度；标准仍在变动 |
| AG-UI governance model (CopilotKit-originated; foundation status)<br>AG-UI 的治理模式（源自 CopilotKit；基金会归属状态） | ⚠️ spec 1.0 + integrations verified; governance not<br>⚠️ 规范 1.0 + 集成已核实；治理未核实 |
| MCP auth exact "OAuth 2.1" label; model codenames<br>MCP 认证的确切“OAuth 2.1”标签；模型代号 | ✅ flows/codenames in official docs; ⚠️ labels change<br>✅ 流程/代号见于官方文档；⚠️ 标签会变 |
| DeepSeek first-party agent tooling; "97% of llms.txt never read"<br>DeepSeek 第一方 Agent 工具链；“97% 的 llms.txt 从未被读取” | ⚠️ not verified; ✅ Ahrefs-reported<br>⚠️ 未核实；✅ Ahrefs 报告 |

**Bottom line for your first month:** read the three specs (MCP 2026-07-28, A2A v1.0, AG-UI 1.0) — each is short — then build one MCP server in .NET and one LangGraph workflow with a Postgres checkpointer. That teaches 80% of what the platform needs, and every framework you evaluate afterwards is a variation on a theme you already understand.

**第一个月的底线：** 读完三份规范（MCP 2026-07-28、A2A v1.0、AG-UI 1.0）——每份都很短——然后用 .NET 构建一个 MCP 服务器，再构建一个带 Postgres 检查点器的 LangGraph 工作流。这能教会你平台所需的 80%，之后你评估的每一个框架，都只是你已经理解的主题的一种变奏。
