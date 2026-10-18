# Agent Frameworks, SDKs & Protocols — Landscape Brief (as of 2026-10-18)

> **Audience:** senior Java/C#/React/AWS engineer new to LLM apps, working on an enterprise .NET agent platform (Model Adapter over OpenAI/Anthropic/Bedrock + governed-asset catalogue).
> **Method:** primary specs, vendor docs and release feeds fetched 2026-10-18. ✅ = verified on a primary source that day; ⚠️ = second-hand, inferred or version-uncertain. Re-verify versions before procurement.
> **Thesis:** protocols converged (MCP for tools, A2A for agents, AG-UI for users); frameworks did not — learn the protocol seams and one workflow runtime deeply, and let most frameworks stay documentation.

---

## 0. Five takeaways

1. **MCP became infrastructure, not a feature.** The latest spec (✅ `2026-07-28`) went **stateless**: `initialize`, protocol sessions, `Mcp-Session-Id`, the HTTP GET stream and `ping`/`logging.setLevel` are gone; version negotiation moved into `_meta`, servers must implement `server/discover`, and server→client requests became **Multi Round-Trip Requests** ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)). Roots, Sampling and Logging are **deprecated**. MCP is now a boring, scalable HTTP integration layer — exactly what a catalogue team should standardise on.
2. **A2A is the horizontal standard, governed by a foundation, not a vendor.** v1.0 shipped 2026-03-12 with a TSC spanning AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP and ServiceNow ([announcement](https://a2a-protocol.org/dev/blog/2026/03/12/a2a-protocol-ships-v10-production-ready-standard-for-agent-to-agent-communication/)); it joined the **Agentic AI Foundation (AAIF)** on 2026-08-27 with **150+ organisations** and native support in Google Cloud, Bedrock AgentCore and Azure AI Foundry ([AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)).
3. **Agent frameworks split into three families** — (a) *harness SDKs* (Claude, OpenAI) rent you a production loop; (b) *workflow runtimes* (LangGraph, MAF, ADK 2.0, Mastra, Pydantic AI) make you own the graph; (c) *platforms* (AgentCore, Temporal, Cloudflare) sell durability. Choose by bottleneck.
4. **Provider APIs are converging on "stateful Responses + server tools".** OpenAI's Responses API (GPT‑6‑class models) adds background mode, WebSocket mode, mid-turn steering, multi-agent, compaction, webhooks and a Decisions API; Assistants was **sunset 2026-08-26** ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)). Anthropic ships server tools (web search/fetch, code execution, advisor, tool search, MCP connector) plus client tools (memory, bash, text editor, computer/browser toolsets) ([tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)). An adapter that only does chat completions is already behind.
5. **Your highest-leverage .NET skill is not a framework — it is exposing the governed-asset catalogue over MCP (OAuth, registry metadata, OpenTelemetry), then wrapping the Model Adapter as a `Microsoft.Extensions.AI` chat client** so Microsoft Agent Framework consumes it without rewrites. Python-wise: **Pydantic AI → LangGraph → OpenAI Agents SDK or Claude Agent SDK** is the shortest path to designing the platform's agent layer.

---

## 1. Protocol layer

### 1.1 MCP — Model Context Protocol

**Status:** production standard under AAIF governance (joined 2025-12-09). Latest spec ✅ **2026-07-28**; previous revision 2025-11-25; older 2025-06-18 deployments are still common.

**What changed in 2026-07-28 (the release that matters for platform design)** — from the [official changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog):

- **Stateless core.** No `initialize` handshake; every request carries protocol version and client capabilities in `_meta`; mismatches return `UnsupportedProtocolVersionError`; servers MUST implement `server/discover`.
- **No protocol-level sessions.** `Mcp-Session-Id` removed; cross-call state uses explicit server-minted handles passed as ordinary tool args (SEP-2567).
- **`subscriptions/listen`** replaces the GET endpoint and `resources/subscribe`: one long-lived POST-response stream for opt-in list/resource change notifications.
- **Multi Round-Trip Requests (MRTR)** replace server-initiated `sampling`/`elicitation`/`roots`: servers return `InputRequiredResult` (`resultType: "input_required"`) with `inputRequests`; clients retry the original call with `inputResponses` (SEP-2322). All results now carry `resultType`.
- **Extensions** first-class; experimental **tasks** moved to `io.modelcontextprotocol/tasks` (poll `tasks/get`, input `tasks/update`).
- **Caching, headers, tracing:** list/read results must include `ttlMs`/`cacheScope`; Streamable HTTP POSTs carry `Mcp-Method`/`Mcp-Name` headers (plus per-tool `x-mcp-header`); tools SHOULD be listed deterministically to improve prompt-cache hits; OpenTelemetry context (`traceparent`, `tracestate`, `baggage`) travels in `_meta`.
- **Deprecated:** Roots, Sampling, Logging; HTTP+SSE transport; OAuth **Dynamic Client Registration** in favour of **Client ID Metadata Documents**; SSE resumability/`Last-Event-ID` removed outright.

**Transports.** `stdio` (local) and **Streamable HTTP** — one POST endpoint answering with JSON or a request-scoped SSE stream ([transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)). Servers MUST validate `Origin`, SHOULD bind localhost-only, SHOULD authenticate; no session affinity means trivial multi-replica deployment.

**Auth.** Transport-level OAuth: authorization-code + PKCE, RFC 8707 resource indicators, RFC 9207 `iss` validation, issuer-keyed credentials, scope step-up ([authorization spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index)). Copy the shape: **MCP server = OAuth resource server; catalogue = authorization + entitlement data**.

**Registry.** The [official MCP Registry](https://modelcontextprotocol.io/registry/about) is in **preview**: `server.json`, DNS/GitHub namespace verification, REST + OpenAPI for aggregators, no private-network servers (self-host a private registry against the same OpenAPI). Map catalogue entries to `server.json` early.

**MCP Apps** (first official extension, ✅ 2026-01-26): tools declare `_meta.ui.resourceUri` pointing at a `ui://` resource; hosts render bundled HTML/JS in sandboxed iframes with JSON-RPC over `postMessage`; supported in Claude, Goose, VS Code Insiders and ChatGPT ([announcement](https://modelcontextprotocol.info/blog/mcp-apps-ui-capabilities/)). ⚠️ Third-party UI is untrusted code: sandbox, consent for UI-initiated tool calls, log everything.

**Security posture.** Origin checks and auth do not solve semantic risk — tool poisoning, prompt injection through tool output, over-broad scopes, confused deputies. Build MCP servers narrow, read-mostly and per-asset-scope.

### 1.2 A2A — Agent2Agent

**Status:** ✅ v1.0 stable since 2026-03-12; **AAIF Growth Stage project** since 2026-08-27 ([AAIF](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)). TSC: AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow.

**Spec facts worth knowing** (from the [v1.0 "what's new" doc](https://a2a-protocol.org/v1.0.0/whats-new-v1/)):

- Core objects: **AgentCard, Task, Message, Artifact**, unified `Part`; `a2a.proto` is the normative source of truth; three bindings with equivalence guarantees: **JSON-RPC 2.0**, **gRPC**, **HTTP+JSON/REST**. Discovery at `/.well-known/agent-card.json`; per-interface `protocolVersion` and `A2A-Version` / `A2A-Extensions` headers.
- Operations are PascalCase (`SendMessage`, `SendStreamingMessage`, `GetTask`, `ListTasks`, `CancelTask`, `SubscribeToTask`, push-notification CRUD, `GetExtendedAgentCard`); streaming via SSE; async via push webhooks or polling.
- **Enterprise features:** multi-tenancy (`tenant` on all requests), **signed Agent Cards** (JWS + RFC 8785), mTLS, modern OAuth 2.0 (device code RFC 8628, PKCE-required flag), `google.rpc.Status` errors, cursor pagination, ISO-8601 timestamps.
- **Breaking vs v0.3:** enums became SCREAMING_SNAKE_CASE (`TASK_STATE_COMPLETED`, `ROLE_USER`), `kind` discriminators removed, compound IDs replaced by UUIDs + separate fields, `/v1` prefix removed from HTTP paths, `supportedInterfaces[]` replaced `preferredTransport`.

**Adoption evidence:** 150+ organisations; native A2A in Google Cloud, **AWS Bedrock AgentCore Runtime** and **Azure AI Foundry**; ServiceNow/Salesforce/Atlassian/SAP workflows; framework support in LangGraph, CrewAI, Pydantic AI, AG2 and IBM BeeAI ([AAIF post](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/), [LF press release](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)). SDKs: Python, Go, Java, JS, **.NET**, Rust ([a2a-protocol.org](https://a2a-protocol.org)).

### 1.3 AG-UI — Agent–User Interaction Protocol

**Status:** ✅ **spec 1.0** ([spec](https://docs.ag-ui.com/spec/1.0/index)). "One request in, one ordered stream of typed events out" — the missing browser-facing leg: MCP = agent↔tools, A2A = agent↔agent, **AG-UI = agent↔user**.

- Event families: run/step lifecycle, text, tool calls, reasoning, shared state (snapshot–delta), activity, subagents, raw/custom passthrough. Middleware runs before enforcement, unknown material survives, malformed known values are fatal, conformance is per stream.
- Transports: **HTTP+SSE**, **HTTP+Protobuf**, custom bindings with a contract; patterns include streaming, snapshot–delta state and interrupt–resume (HITL), plus a Generative UI proposal.
- SDKs: TypeScript, Python, **.NET**, Kotlin/Go. Integrations are unusually broad: LangGraph, **Microsoft Agent Framework**, Google ADK, Antigravity, Strands, Mastra, Pydantic AI, Agno, LlamaIndex, CrewAI, AG2, Langroid, Cloudflare Agents, **Claude Agent SDK/Managed Agents**; front-end via CopilotKit; AgentCore runtime support ([integrations](https://docs.ag-ui.com/integrations)).
- **Why it matters to you:** cleanly decouples a React SPA from agent runtimes, gives typed tool-call/reasoning/state events instead of prose, and doubles as an audit stream.

### 1.4 The rest of the alphabet (and which are noise)

- **ACP = three different things.** (a) **Agent Client Protocol** (Zed): editor↔coding-agent stdio JSON-RPC; an **ACP Registry is live** — the layer behind "bring Claude Code/Codex/Gemini CLI into your editor" ([Zed](https://zed.dev/blog/acp-registry)). (b) **IBM Agent Communication Protocol**: REST messaging, effectively **absorbed by A2A**; ⚠️ status unverified, do not build on it ([IBM](https://www.ibm.com/think/topics/agent-communication-protocol), [guide](https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/)). (c) **Agentic Commerce Protocol** (OpenAI/Stripe) — see payments.
- **AGNTCY (Cisco/Outshift):** agent directory **DIR** (content-addressed, OCI-style), **OASF** agent records, **SLIM** secure messaging; active releases ([DIR](https://github.com/agntcy/dir/releases), [intro](https://outshift.prod.eticloud.io/blog/agntcy-agent-directory-find-and-publish-ai-agents)). ⚠️ Real but niche outside Cisco pilots — watch, don't standardise.
- **Payments: AP2 vs ACP.** Google's **AP2** uses mandates (Intent/Cart/Payment) with verifiable credentials; ⚠️ **donated to the FIDO Alliance**, now standards work rather than a shipping product ([FIDO](https://fidoalliance.org/google-donates-agent-payments-protocol-to-fido-alliance/), [Google](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)). **Agentic Commerce Protocol** is a checkout-flow spec, and ⚠️ reported pull-back from in-chat checkout suggests churn ([research](https://www.foresightventures.com/details?details_id=90&details_type=research), [Forkast](https://forkast.news/openai-built-in-chat-checkout-for-ai-commerce-five-months-later-it-walked-away/)). Neither should gate your roadmap in 2026.
- **`agent.json`:** a W3C AI-VS community-group *proposal* for a universal manifest plus "quality graph" trust scoring — discussion only, **not a standard** ([W3C archive](https://lists.w3.org/Archives/Public/public-aivs/2026May/0000.html)).
- **`llms.txt`:** still a convention; a 137k-site Ahrefs study found **~97% of `llms.txt` files never get fetched** — SEO folklore, not agent discovery ([Ahrefs](https://ahrefs.com/blog/llmstxt-study/)).
- **`AGENTS.md`:** won. A plain-Markdown instruction file supported across coding agents (including a Claude Code fallback) and an AAIF sibling project alongside MCP, goose and A2A ([DevOps.com](https://devops.com/claude-code-adds-agents-md-fallback-cutting-instruction-file-sprawl/), [AAIF](https://aaif.io/projects)). Adopt it for repo onboarding today.

### 1.5 Protocol comparison

| Protocol | Current spec / version (date) | Transport | Auth model | Adoption evidence | Confidence |
|---|---|---|---|---|---|
| **MCP** | 2026-07-28 (latest); 2025-11-25 prev. | stdio; Streamable HTTP (single POST endpoint, per-request SSE); HTTP+SSE deprecated | OAuth: auth-code+PKCE, RFC 8707 resource indicators, client-ID metadata documents (DCR deprecated) | Official registry (preview), MCP Apps in Claude/ChatGPT/VS Code/Goose, AAIF project; de-facto tool standard | ✅ high |
| **A2A** | v1.0 (2026-03-12) | JSON-RPC 2.0, gRPC, HTTP+JSON/REST; SSE streaming + webhooks | OAuth 2.0 (device code, PKCE), mTLS, **signed Agent Cards (JWS)**, tenant scoping | 150+ orgs; Google Cloud, AgentCore, Azure AI Foundry; SAP/ServiceNow/Salesforce; .NET SDK; AAIF project | ✅ high |
| **AG-UI** | 1.0 | HTTP+SSE; HTTP+Protobuf; custom bindings | Delegated to app/transport; consent + trust-boundary rules in spec; no wire auth | Broad framework integrations (MAF, ADK, LangGraph, Pydantic AI, Claude SDKs); CopilotKit; AgentCore support | ✅ spec; ⚠️ governance |
| **ACP (Agent Client Protocol)** | pre-1.0, registry live 2026 | stdio JSON-RPC between editor and coding agent | Local trust, agent-declared permissions | Zed + editor ecosystem; embeds Claude Code/Codex/Gemini CLI | ⚠️ medium |
| **ACP (IBM Agent Communication)** | legacy | REST/HTTP | Bearer/OAuth | Folded toward A2A; low new adoption | ⚠️ low |
| **AGNTCY DIR** | active releases 2026 | OCI-style content-addressed directory; SLIM messaging | Identity via OASF records / enterprise IdP | Cisco/Outshift-led pilots | ⚠️ medium |
| **AP2** | donated to FIDO (2026) | HTTP + verifiable credentials/mandates | Cryptographic mandates, VC/JWT | Spec + partner pilots; not GA infra | ⚠️ low/medium |
| **Agentic Commerce Protocol** | evolving | HTTP checkout APIs | Merchant OAuth/keys | OpenAI/Stripe experiments; churn | ⚠️ low |
| **agent.json** | proposal (2026-05) | n/a | n/a | W3C CG discussion | ⚠️ low |
| **AGENTS.md** | convention, de-facto | n/a (file) | n/a | Multi-vendor coding agents, AAIF project | ✅ medium-high |
| **llms.txt** | convention | n/a (file) | n/a | ~97% never fetched | ⚠️ low |

**Reading the table:** build on MCP + A2A + AG-UI; ACP-client is an editor convenience; AGNTCY/AP2/agent.json are watch-list.

---

## 2. Framework comparison

Versions from release feeds fetched 2026-10-18; ⚠️ = unconfirmed. "Adoption" is qualitative, not measured market share.

| Framework (version) | Lang | Paradigm | Tools | HITL | Durability | Observability | Prod | Adoption | Curve | Best fit |
|---|---|---|---|---|---|---|---|---|---|---|
| **OpenAI Agents SDK** 0.24 | Py, TS | Agent loop + handoffs | Functions, hosted tools, MCP | Approvals, deferred approvals | RunState + session stores; Temporal extra | Built-in tracing | High; 0.x churn | Very high | Low | OpenAI-first products |
| **Claude Agent SDK** 0.2.168 | Py, TS | Claude Code harness | Built-in file/bash tools, MCP, plugins | Hooks + permission callbacks | Session resume/fork | Hook/stream events | High (coding) | High | Low–Med | Coding/computer automation |
| **Google ADK** 2.12 | Py, TS, Go | Graph workflows + multi-agent | Functions, toolsets, MCP | `require_confirmation` | Workflow runtime + session stores | OTel, BigQuery, Agent Engine | High (GA) | High; GCP-centric | Med | Gemini/Vertex; deterministic graphs |
| **MS Agent Framework** 1.0 | .NET, Py | Agents + workflows + orchestrations | Functions, MCP, A2A, OpenAPI | Approvals, hosted agents | Checkpoints, durable sessions | OTel built-in | High (LTS) | High enterprise | Low–Med | .NET enterprise default |
| **LangGraph** 1.2.16 + LangChain v1 | Py, TS | Explicit graph/state machine | Tools, MCP, subgraphs | `interrupt()` + resume | Checkpointers, time travel | LangSmith/OTel | High | Very high | Med | Auditable deterministic workflows |
| **Pydantic AI** 2.57 | Py | Typed loop + graphs | Typed tools, MCP | Deferred tools, ask-user | Temporal/DBOS/Prefect/Restate adapters | Logfire/OTel | High & rising | Growing | Low–Med | Type-safe, provider-agnostic services |
| **CrewAI** 1.15.27 | Py | Role crews + flows | Tools, MCP, A2A | HITL steps | Flow persistence | Listeners | Med–High | Large | Low | Prototypes, back-office |
| **Mastra** 1.78 core | TS | Agent + durable workflows | Tools, MCP, routes | Approval hooks, signals | Durable workflows, resume | OTel + exporters | High | Large TS/React | Low–Med | React/Next.js products |
| **Vercel AI SDK** 7 | TS | Model abstraction + UI primitives | Typed tools, MCP client | Tool approval, UI interrupts | Harness packages; BYO runtime | OTel spans | High | Massive | Low | Streaming UI, provider abstraction |
| **smolagents** | Py | Minimal code-agent loop | Python functions, code exec | Limited | Minimal | Minimal | Med | Niche | Very low | Learning internals |
| **Agno** 3.1.4 | Py | Agents/teams/workflows + AgentOS | Toolkits, MCP, A2A | Approvals, background runs | Durable Postgres queue, checkpoints | OTel | High | Growing | Low–Med | Full-stack Python services |
| **DSPy** 3.x ⚠️ | Py | Compile/optimise programs | Typed predictors/modules | n/a | n/a | Evals | Med | Large research | High | Eval-driven optimisation |
| **Haystack** 2.26 ⚠️ | Py | Pipelines + agents | Tools, MCP | Basic | Checkpointing | OTel | High (RAG) | Large | Med | RAG/search |
| **LlamaIndex Workflows** ⚠️ | Py, TS | Event-driven workflows | Toolsets, MCP, query engines | Interrupt/resume | Context serialisation | Instrumentation | High (data apps) | Large | Med | Document/data agents |
| **Letta** ⚠️ | Py | Memory-first stateful agents | Tools, MCP | Approval | Server-persisted state | Limited | Med | Niche | Med | Long-lived memory agents |
| **Bedrock AgentCore** | Managed + SDK | Managed harness/runtime/gateway | MCP gateway, web search, KB | Approvals, gateway policy | MicroVM sessions, checkpoints | OTel/CloudWatch | High | AWS enterprises | Low | AWS-native governed runtime |
| **Cloudflare Agents** 0.16 | TS | Stateful agents on Durable Objects | Tools, MCP | Tool approval | DO storage, alarms | Workers observability | Med–High | Edge apps | Low | Edge stateful chat |
| **Temporal** (SDK 1.34) | Py/TS/Java/.NET/Go | Durable execution | BYO | Signals/queries | Best-in-class replay | OTel | Very high | Massive | Med | Mission-critical long-running agents |
| **Inngest** | TS/Py/Go | Event-driven durable workflows | `step`, `waitForEvent` | Approval via events | Excellent | OTel | High | Growing | Low–Med | Event-driven agents |

### 2.1 Cluster notes (what the table hides)

**Harness SDKs (Claude, OpenAI).** You adopt someone else's loop, tools and safety model: Claude Code's harness (hooks, permissions, subagents, skills, MCP, sessions) is the most battle-tested coding loop in production, exposed as a library ([overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). OpenAI's SDK turned the same way in 2026 — sandboxing, a new model harness, durable `RunState`, deferred approvals, MCP annotations, optional Temporal/Vercel extras ([v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0), [DevOps.com](https://devops.com/openai-upgrades-its-agents-sdk-with-sandboxing-and-a-new-model-harness/)). Risk: 0.x churn and provider gravity.

**Workflow runtimes (LangGraph, MAF, ADK 2.0, Mastra, Pydantic Graph).** Everything became a graph. ADK 2.0 replaced its hierarchical executor with a **Workflow runtime** where agents are nodes (`BaseNode`, `RetryConfig`, resumable pauses) — a breaking migration ([ADK 2.0](https://adk.dev/2.0/index.md)). Microsoft Agent Framework unifies Semantic Kernel + AutoGen with workflows, orchestrations and checkpointing ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)). LangGraph remains the reference implementation, with LangChain v1's `create_agent` as the on-ramp ([LangChain v1](https://docs.langchain.com/oss/python/releases/langchain-v1.md)). For auditability and replay, this is the family.

**Type-safe service stacks (Pydantic AI, Agno, Haystack).** Pydantic AI feels like typed Python — DI, typed tools, output schemas — plus durable-execution adapters (Temporal/DBOS/Prefect/Restate) and AG-UI/Vercel AI UI integrations ([durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/)). Fastest mental mapping for a C#/Java engineer.

**Team/role frameworks (CrewAI, AG2).** Great demos, dangerous defaults when control flow must be explicit. Prefer deterministic Flows for production; treat crews as prototyping (⚠️ verify in current docs; [changelog](https://docs.crewai.com/v1.15.27/en/changelog)).

**Platforms (Bedrock AgentCore, Cloudflare Agents, Temporal, Inngest).** AgentCore is the most complete governed-agent platform: Managed Harness (model + prompt + tools, microVM per session), Gateway with MCP/web search, managed knowledge base, Recommendations/Batch evals/A-B testing, 5,000 concurrent sessions, native A2A/AG-UI ([AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)). Temporal and Inngest are where mature teams go when "the agent must survive a deploy" ([ZenML](https://www.zenml.io/blog/inngest-vs-temporal)).

**The TS/React lane (Mastra, Vercel AI SDK).** With your React strength this is the fastest demo path: Mastra 1.x is a real server framework — durable workflows, memory, evals, agent scopes ([1.78](https://github.com/mastra-ai/mastra/releases)); Vercel AI SDK v7 is the best model/UI abstraction. Neither should be the orchestration core in a .NET shop.

---

## 3. Model-provider agent capabilities (what your Model Adapter must expose)

**OpenAI — Responses API is the agent primitive.** Built-in tools (web/file search, computer use, code interpreter, remote MCP), stateful context (`store`, `previous_response_id`, Conversations API), encrypted reasoning for ZDR, typed Items, typed SSE events, `text.format` structured outputs, agentic loop by default ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses.md)). The docs index also shows **background mode, WebSocket mode, mid-turn steering, multi-agent, webhooks, compaction and a Decisions API**, with GPT‑6‑class models (`gpt-6-astra`, `gpt-6.1-sol`). Chat Completions still works but is feature-frozen; Assistants was **sunset 2026-08-26**. Adapter implication: expose *items, tool calls, reasoning summaries, response ids* — not just `choices`.

**Anthropic — Messages API plus a large server-tool surface.** Server-side: web search/fetch, code execution (including programmatic tool calling), advisor, tool search, MCP connector; client-side: memory, bash, text editor, computer/browser toolsets (dated types; `computer_toolset_20260801` current) ([tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference.md)). Context management is first-class: prompt caching on tool definitions, context editing, mid-conversation system messages/tool changes, compaction, thinking/effort/fast-mode. Anthropic also sells **Managed Agents** — hosted harness, Anthropic-managed or self-hosted sandbox — competing with AgentCore ([Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)).

**Google — Gemini 4 generation, Live API, Interactions API.** Docs promote **Gemini 4 "Argon"**; Live API is stateful **WebSocket** streaming (16 kHz PCM in / 24 kHz out, images ≤1 FPS, barge-in, tool use, ephemeral tokens) ([Live API](https://ai.google.dev/gemini-api/docs/live-api)). Around it: function calling, Search/Maps grounding, code execution, URL context, computer use, file search and a newer **Interactions API** with managed agents/Antigravity ([docs](https://ai.google.dev/gemini-api/docs)). WebSocket streaming and thought signatures need first-class adapter support if voice/vision is on the roadmap.

**Bedrock / AgentCore.** Bedrock supplies models; AgentCore supplies runtime, gateway, identity, memory, browser/code-interpreter and evals, with native A2A/AG-UI and an MCP-based gateway ([AWS](https://builder.aws.com/content/3GHDdjiXvGA5tgSHyD9vJKXLBJH/bedrock-agentcore-managed-harness-reaches-ga-in-2026)). Reuse its governance primitives rather than rebuild them.

**DeepSeek and local (vLLM/Ollama).** ⚠️ First-party DeepSeek agent tooling was not verified; assume OpenAI-compatible chat + reasoning models, strong price/perf, weaker tool-calling polish, no server tools. vLLM/Ollama are OpenAI-compatible for chat but **tool calling and structured output vary by model template and server feature**, so the adapter needs per-model capability flags, not one global "supports tools" boolean.

**Structured outputs and reasoning — document these in the adapter:** strict schema output is table stakes, but reasoning models degrade when forced into tool-calling + heavy schemas (from GPT‑5.4, OpenAI does **not** support tool calling on Chat Completions with `reasoning_effort` other than `none` — a strong reason to standardise on Responses); reasoning tokens are billed and must round-trip (encrypted reasoning/thought signatures); cache efficiency is now an agent-design variable (stable prefixes, deterministic tool order — which MCP now mandates — and `defer_loading` for large catalogues).

---

## 4. Reference agent-native tools worth reading as architecture

You do not need to clone these; you need to **read their harness design** because the harness, not the model, is where the engineering is.

| Tool | What to steal | Where to look |
|---|---|---|
| **Claude Code / Agent SDK** | Permission model (auto-allow vs ask), lifecycle hooks, subagents for context isolation, skills as progressively disclosed instructions, compaction, sandbox policy | [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md); [harness essay](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code) |
| **OpenAI Codex CLI / harness** | Approval matrix, sandboxed command execution, patch/diff discipline; the harness was **open-sourced Aug 2026** | [Open Source For You](https://www.opensourceforu.com/2026/08/openai-open-sources-codex-harness/) |
| **OpenHands** | Event-stream architecture (actions/observations), sandboxed runtime, trajectory replay, SWE-bench-style evaluation | [Harness engineering survey](https://export.arxiv.org/pdf/2609.00006) |
| **SWE-agent** | Agent-Computer Interface: tool ergonomics beat raw model IQ; guardrailed shell/file editing | [ACI paper](https://arxiv.org/abs/2405.15793) |
| **Aider** | Repo map (symbol graph in prompt), diff-based edits, token-efficient context | [aider.chat](https://aider.chat) |
| **Cursor** | Trained retrieval/long-horizon behaviour (Composer), self-summarisation, latency/UX trade-offs | [Composer blog](https://cursor.com/en/blog/self-summarization) |

Cross-cutting lessons: **context engineering dominates prompt engineering** — tool-output truncation, deferred loading, compaction and summarisation are the real quality levers; the **permission/sandbox boundary is part of the product**; and **trajectories are the debugging artefact** — full event streams with tool arguments/results are mandatory for evals and audits.

---

## 5. Decision matrix: what to learn first

### 5.1 Python — learn these 3, in this order

| Order | Stack | Why for *you specifically* | Effort | Transfers to .NET? | Verdict |
|---|---|---|---|---|---|
| 1 | **Pydantic AI** (2–3 wks) | Typed models ≈ C# records; DI ≈ constructor injection; provider-agnostic model layer mirrors your Model Adapter; tools, structured outputs, evals and durable execution in one mental model — concepts without framework archaeology. | Low–Med | High (concepts) | **First.** Build a "governed-asset Q&A + tool call" agent with typed outputs and a tiny eval suite. |
| 2 | **LangGraph + LangChain v1** (3–4 wks) | Durable state machine with checkpointers, replay, `interrupt()` HITL and time travel — the Python analogue of enterprise governance. Middleware (PII redaction, summarisation, HITL) maps to platform policy points. | Med | High (→ MAF workflows) | **Second.** 3-node graph with Postgres checkpointer, approval interrupt, replay demo. |
| 3 | **OpenAI Agents SDK** (if OpenAI/Azure-first) **or Claude Agent SDK** (if coding/computer automation) (2 wks) | Both are production loops to read and steal from: OpenAI handoffs/guardrails/sessions/RunState/tracing ([v0.24](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0)); Claude hooks/subagents/permissions/skills harness ([overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). Read the Python source — it is small. | Low | Med (patterns) | **Pick one, not both.** Then stop collecting frameworks. |

**Explicit non-recommendations:** don't start with CrewAI/AG2 swarms (demo magic, not engineering); don't write your own loop before reading OpenAI's; don't invest in DSPy until you have an eval set; skip Python MCP servers — your leverage is .NET; AgentCore/Cloudflare are deployment decisions, not learning material. If your employer standardises on GCP, swap #3 for **Google ADK 2.0** — its graph runtime is the closest sibling to MAF, with `to_a2a`/`RemoteA2aAgent` interop.

### 5.2 .NET — what makes you immediately useful at work

| Priority | What | Concrete deliverable | Why it lands |
|---|---|---|---|
| **P0** | **Microsoft Agent Framework .NET 1.x** (`Microsoft.Agents.AI` + OpenAI/Anthropic/Bedrock connectors, workflows, orchestrations, hosting) | One vertical slice: an `AIAgent` with 2–3 catalogue tools inside a workflow with an approval step and OpenTelemetry spans | Likely strategic SDK: 1.0 April 2026, LTS, unifies Semantic Kernel + AutoGen; .NET and Python first-class ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)) |
| **P0** | **`Microsoft.Extensions.AI` `IChatClient` adapter** for your Model Adapter | One `IChatClient` routing to OpenAI/Anthropic/Bedrock, exposing tool calls, streaming, reasoning metadata and capability flags | MAF is built on Microsoft.Extensions.AI, so one wrapper lets every MAF agent/workflow/tool use your governed adapter — policy stays in one place ⚠️ verify abstraction version in your platform |
| **P1** | **MCP server in .NET for the governed-asset catalogue** | search/get/lineage/entitlement tools, OAuth resource-server auth, `server.json`, deterministic ordering, `ttlMs`/`cacheScope`, OTel in `_meta` | Highest-leverage protocol work: makes the catalogue consumable by Claude/ChatGPT/VS Code/Copilot *and* every internal agent; stateless spec scales easily behind your gateway ([spec](https://modelcontextprotocol.io/specification/2026-07-28/changelog)) |
| **P1** | **A2A .NET SDK** | Signed agent cards for 1–2 platform agents (tenant scoping), streaming call to another team's agent | Cross-org standard, 150+ orgs, native cloud support ([a2a-protocol.org](https://a2a-protocol.org)) |
| **P2** | **AG-UI .NET + React** | Typed agent events (tool calls, state, approvals) into your React front-end instead of a chat blob | Reuses your React strength; first-class MAF support ([integrations](https://docs.ag-ui.com/integrations)) |
| **P2** | **Semantic Kernel bridge** | Map SK plugins/planners onto MAF tools/workflows; keep SK only where deployed | SK knowledge remains a migration asset ([1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)) |

**Governance mapping for your platform** (the opinionated part):
1. **Keep the Model Adapter as the only provider boundary.** Point each framework at your adapter endpoint; normalise items/messages, tool calls, structured-output mode, reasoning blobs, cache controls, usage and per-model capability flags.
2. **Make the catalogue the source of truth for tools, not the framework.** Every callable asset = MCP tool + `server.json` metadata + A2A agent card (if an agent) + policy attributes (owner, classification, scopes) — frameworks become interchangeable consumers.
3. **Treat HITL as a platform primitive.** One approval service (who, what, why, expiry, replayable decision) wired to LangGraph `interrupt`, MAF human-in-loop, ADK `require_confirmation`, AG-UI interrupts and A2A `TASK_STATE_INPUT_REQUIRED`.
4. **OTel GenAI semantics + MCP trace propagation are the audit trail** (`traceparent`/`tracestate`/`baggage` in `_meta`); support both MCP revisions (2025-11-25, 2026-07-28) as routing, not a code fork.

### 5.3 A 90-day plan (2–4 hrs/week)

| Weeks | Focus | Output |
|---|---|---|
| 1–4 | Provider APIs + Pydantic AI: typed tools, structured output, evals; MCP client consumption | Adapter capability matrix; "governed-asset Q&A" agent + 10-case eval suite |
| 5–8 | LangGraph (checkpointer, interrupt, replay) + .NET MCP server + MAF slice with `IChatClient` adapter and OTel | Durable approval workflow; catalogue MCP server; vertical slice inside the platform |
| 9–12 | A2A signed agent card + cross-agent task; AG-UI stream into React; hardening and policy | Two agents delegating; typed UI stream; architecture decision record |

**What "learned" means:** you predict a framework's breaking changes from its changelog, you can move an agent between runtimes without touching the catalogue, and you can tell a security reviewer exactly where prompts, tool arguments, approvals and traces live.

---

## 6. Uncertainty register (claims I could not fully verify)

| Claim | Status |
|---|---|
| Exact versions for smolagents, DSPy, Haystack, LlamaIndex Workflows, Letta server | ⚠️ **unverified** (partial release evidence only) |
| Microsoft Agent Framework **.NET** patch version (Python 1.22.0 confirmed; .NET uses separate tags) | ⚠️ **unverified**; 1.0 GA date confirmed |
| IBM ACP status; AGNTCY production maturity | ⚠️ second-hand / medium confidence |
| AP2 adoption after FIDO donation; Agentic Commerce Protocol direction | ⚠️ low confidence; standards in flux |
| AG-UI governance model (CopilotKit-originated; foundation status) | ⚠️ spec 1.0 + integrations verified; governance not |
| MCP auth exact "OAuth 2.1" label; model codenames | ✅ flows/codenames in official docs; ⚠️ labels change |
| DeepSeek first-party agent tooling; "97% of llms.txt never read" | ⚠️ not verified; ✅ Ahrefs-reported |

**Bottom line for your first month:** read the three specs (MCP 2026-07-28, A2A v1.0, AG-UI 1.0) — each is short — then build one MCP server in .NET and one LangGraph workflow with a Postgres checkpointer. That teaches 80% of what the platform needs, and every framework you evaluate afterwards is a variation on a theme you already understand.
