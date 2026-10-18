# 05 — MCP and Interoperability

> **Week 5 · just-in-time concept note.** Read before the lab (~25 min), then read the [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) with the tab open. You need the protocol's shape, its current revision, and the attacks it does *not* stop — not memorised spec text.

## The failure mode this prevents

The integration-tax spiral: every system you connect needs a bespoke client, so the platform accumulates N connectors and N security reviews, and the tool list becomes a museum of hand-written wrappers. The same shortcut makes it dangerous: a client copies the caller's OAuth token into every downstream call, so an assistant *allowed* to read tickets can now send email. And approved tool descriptions can change server-side after review, with the model following instructions you never read.

MCP is not "a better REST client": it is a contract for how a host discovers and invokes tools, resources and prompts across a boundary, and it makes the scalable version (stateless HTTP) the default while leaving trust decisions to you.

## If you remember five things

> 1. **MCP standardises tool/context integration inside one agent** — tools (model-invoked), resources (app-controlled data by URI), prompts (user-selected templates). Not agent-to-agent.
> 2. **The 2026-07-28 spec is stateless.** No `initialize`, no session. Version and capabilities travel in `_meta` on every request; negotiation uses `server/discover`; results carry `resultType`.
> 3. **Multi Round-Trip Requests replace server-initiated requests.** A server needing input returns `resultType: "input_required"` with `inputRequests`; the client retries with `inputResponses`.
> 4. **OAuth tokens are audience-bound and never passed through.** Your MCP server is a resource server: accept only tokens minted for it; never replay the caller's token downstream.
> 5. **Use protocols only across a real boundary.** Function calling inside your process; MCP for reusable/third-party tools; A2A for another team's agent; AG-UI for a user-facing event stream.

## The model in one page

### Roles and primitives

A **host** (your agent app) runs **clients**, each connected to a **server** over JSON-RPC 2.0. The server advertises capabilities; the client renders tools into the model's function-calling schema, exposes resources as app context, and prompts as user templates ([server overview](https://modelcontextprotocol.io/specification/2026-07-28/server)). The model never "speaks MCP" — it calls functions, and the host translates. That translation layer is yours, and it is where allowlists, redaction and tracing live.

### The 2026-07-28 redesign: what changed

| 2025 mental model | 2026-07-28 reality |
|---|---|
| `initialize` → `notifications/initialized` handshake | No handshake. Version + capabilities travel in `_meta` on every request; mismatch returns `UnsupportedProtocolVersionError` |
| `Mcp-Session-Id` for connection state | No protocol sessions. Cross-call state uses explicit server-minted handles passed as tool arguments |
| Server-initiated `sampling` / `elicitation` / `roots` | Multi Round-Trip Requests: `InputRequiredResult` with `inputRequests`; client retries with `inputResponses`; every result carries `resultType` |
| HTTP GET stream + `resources/subscribe` | `subscriptions/listen` — one long-lived POST-response stream for opted-in change notifications |

`ping`, `logging.setLevel` and SSE resumability are gone; HTTP+SSE and Roots/Sampling/Logging are deprecated. A stateless server scales behind any load balancer, and a broken stream is retried as a new request ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).

### Transports: stdio vs Streamable HTTP

- **stdio** — client spawns the server as a child process; newline-delimited JSON-RPC over stdin/stdout. Simple and local, inheriting your OS user; not a multi-tenant boundary.
- **Streamable HTTP** — one POST endpoint; each request gets a single JSON response or a request-scoped SSE stream. Origin validation, localhost binding for local servers, and real authentication are server duties ([transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)).

Streamable HTTP goes behind a gateway — the only transport where OAuth, tenant scoping and rate limiting happen.

### The trust boundary: four attacks that matter

1. **Tool poisoning / rug pull.** Descriptions are attacker-controlled text the model treats as instructions, and a server can change them after approval. Mitigation: pin a digest of description + schema at approval time, re-verify on discovery.
2. **Confused deputy.** The server holds broad credentials and an under-privileged caller asks it to use them. Mitigation: server authority never exceeds the caller's effective authority; derive downstream authz from the caller's scoped token.
3. **Token passthrough.** A server forwards a client token downstream, defeating audience restriction. Forbidden. Mitigation: validate `aud`/issuer, exchange tokens, never replay.
4. **Prompt injection through tool output.** Results are data, not instructions — but models do not reliably honour that. Strip untrusted content, constrain the next step, gate writes behind approval.

All four are in the [security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices), which also covers SSRF, state-handle hijacking and scope minimisation.

### Ecosystem surfaces you will meet soon

- **Registry.** The official [MCP Registry](https://modelcontextprotocol.io/registry/about) is in preview: `server.json`, DNS/GitHub namespace verification, REST/OpenAPI for aggregators, no private servers. A governed catalogue maps naturally: server = asset, tools = capabilities, namespace = ownership.
- **MCP Apps.** The first official extension lets a tool point at a `ui://` resource rendered in a sandboxed iframe ([extensions](https://modelcontextprotocol.io/extensions/overview)). Treat the UI as untrusted code; require consent for UI-initiated calls.

### A2A v1.0, AG-UI 1.0, and the decision table

**A2A** is the horizontal protocol: agents discover each other through an [Agent Card](https://a2a-protocol.org/v1.0.0/whats-new-v1/) at `/.well-known/agent-card.json`, then exchange `Task`/`Message`/`Artifact` over JSON-RPC, gRPC or HTTP+JSON, with SSE/webhooks for progress. v1.0 adds signed cards, multi-tenancy and OAuth device-code/PKCE. Use it when the other side owns its model loop and data.

**AG-UI** is the user-facing leg: one request in, one ordered stream of typed events (lifecycle, text, tool calls, reasoning, shared state) out, over SSE or Protobuf ([spec 1.0](https://docs.ag-ui.com/spec/1.0/index)). Use it when a React front-end must render agent behaviour without inventing a schema per framework.

| You need to… | Use | Why not the alternative |
|---|---|---|
| Call a function you own, in-process | Plain function calling | No boundary or discovery overhead |
| Reuse tools across hosts, or connect a third-party tool server | **MCP** | Function calling cannot discover or transport tools across processes |
| Delegate a task to another team's/company's agent | **A2A** | MCP assumes the caller drives the loop; A2A lets the remote agent own it |
| Stream agent activity into a UI | **AG-UI** | A2A is agent-to-agent; MCP is tool-shaped, not presentation-shaped |
| Long-running async work between agents | **A2A** + push webhooks/tasks | A request/response chain does not survive restarts |

## Common misconceptions

| Misconception | Reality |
|---|---|
| "MCP replaces function calling." | It sits *above* it: the model calls functions; the host maps calls to MCP requests over a transport. |
| "Once a server is connected, its tools are trusted." | Descriptions are untrusted input. Pin digests, allowlist servers, gate writes. |
| "MCP and A2A compete." | MCP is inside an agent (tools/context); A2A is between agents. Mature systems use both. |
| "The `initialize` handshake is how MCP works." | Pre-2026 model. The current spec is stateless; such tutorials are stale. |
| "Forwarding the user's token downstream is fine." | Token passthrough — an explicit anti-pattern. Exchange or scope; never replay. |

## How this shows up in SendOS

- **Catalogue vs runtime discovery.** `CapabilityCatalogueAssembler.cs:34-120` merges three declaration sources and lets published assets win. MCP discovery is runtime introspection; SendOS's registry is a governance decision at publish time. Consume MCP tools *into* a governed catalogue; undeclared capabilities must stay non-invokable.
- **Audience and scope are authority narrowing.** `EffectiveAuthority.cs:8-36,114-225` intersects ten independent boundaries and `Delegate()` only narrows. An MCP token's scopes must be a subset of effective authority for that tenant/actor; a server must not widen it. RFC 8707 resource indicators, expressed as a business rule.
- **Boundary crossings must be traceable.** `IOutcomeTraceEmitter.cs:24-45` is the append-only event seam. Stamp every MCP call's execution origin (server id, tool name, description digest, latency, scopes) so incidents replay.

## Check yourself

1. A 2026-07-28 client never sends `initialize`. What replaces negotiation, and what happens on version mismatch?
2. Give one catalogue asset that should be a tool, one a resource, one a prompt.
3. A tool receives the caller's token and needs to call Graph. What is wrong with forwarding it, and what should the server do instead?
4. When is A2A right over MCP, and what must an Agent Card expose — and not expose?
5. You approved a server last month; its tool description now carries a new instruction. Which attack is this, and what control catches it?

## Reading

- [MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) — the normative delta.
- [MCP security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) — confused deputy, token passthrough, SSRF, state-handle hijacking.
- [A2A v1.0: what's new](https://a2a-protocol.org/v1.0.0/whats-new-v1/) — agent cards, bindings, breaking changes.
- [AG-UI specification 1.0](https://docs.ag-ui.com/spec/1.0/index) — event families and conformance.
