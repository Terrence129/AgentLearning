# Week 5 — MCP and interoperability

> **Lab id:** `week05-mcp` · **Owned package:** `agentlab/mcp/`
> **Starter:** the files in `agentlab/mcp/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week05/agentlab/mcp/`
> **Tests:** `tests/week05/` (in-memory transport, no subprocess, no network)

> **Read this before coding:** the MCP specification was redesigned in
> 2026-07-28. It is **stateless**: `initialize`, sessions, `ping`,
> `logging/setLevel`, the HTTP GET stream and `resources/subscribe` are gone;
> `server/discover` is mandatory; every request carries its version and client
> capabilities in `_meta`; every result carries `resultType`. Most tutorials in
> the wild describe the deprecated handshake. Verify against the
> [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
> before believing any blog post.

## 1. Why this week exists

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

## 2. Prerequisites & time budget

- **Time:** 8–10 h (build ≈ 5 h, spec reading ≈ 2 h, security review ≈ 1 h).
- **Must be green:** foundation (`pytest -q` on the repo root).
- **Reading:** the current MCP changelog and the discovery / tools / resources /
  transports pages; `docs/research/02-frameworks-protocols.md` §1.1.
- **Does not depend on the `mcp` package.** Do not add it — build the subset.

## 3. The spec

Implement every `NotImplementedError` in `agentlab/mcp/`. Docstrings are the
contract.

| File | Public surface | Contract summary |
|---|---|---|
| `jsonrpc.py` | `make_request`, `make_notification`, `make_result`, `make_error`, `parse_message`, `is_notification`, `encode_message`, `JSONRPCError`, error-code and `_meta` constants | JSON-RPC 2.0 shape validation; `_meta` merged into `params`, never top level; parse/invalid-request errors typed; ids may be string/int/absent but never float/bool; `resultType` values `"complete"` / `"input_required"`. Error codes: standard `-327xx`; MCP-reserved `-32020..-32099`, including `UNSUPPORTED_PROTOCOL_VERSION = -32022`. |
| `transport.py` | `Transport`, `InMemoryTransport`, `StdioServerTransport`, `encode_line`, `decode_line`, `serve_stdio`, `TransportError`, `TransportClosed`, `TransportTimeout`, `PROTOCOL_VERSION` | Synchronous request/response channel; in-memory transport records every message in `.sent`; stdio framing is one JSON message per line (blank lines skipped, EOF raises `TransportClosed`); `serve_stdio` survives malformed lines by answering a parse error, converts handler `JSONRPCError`s, and optionally stops after `max_messages`. |
| `server.py` | `MCPServer`, `MCPTool`, `MCPResource`, `build_demo_server`, `main` | Stateless dispatch: every request must carry `params._meta[protocolVersion]`; missing → `-32602`, unsupported → `-32022` with `data.supported`/`data.requested`. `server/discover` advertises versions, identity, capabilities and `ttlMs`/`cacheScope`. `tools/list` is deterministically sorted; `tools/call` distinguishes protocol errors (unknown tool/missing name) from tool-level errors (`isError: true`); `resources/read` unknown → `-32602`; unknown method → `-32601`; notifications are never answered; every result carries `resultType: "complete"` and `_meta[serverInfo]`. `build_demo_server` exposes 3 offline tools + 1 resource; `python -m agentlab.mcp.server` serves it over stdio. |
| `client.py` | `MCPClient`, `MCPError`, `DiscoverResult`, `ServerInfo`, `RemoteTool`, `ResourceContents` | Every request carries `_meta` (version, clientInfo, clientCapabilities). `discover` validates the response and negotiated version; `list_tools` returns declarations with canonical digests; `call_tool` returns `ToolResult` and turns protocol/transport/timeout failures into observations; `read_resource` returns text; `as_tool_registry` maps remote declarations onto the local `ToolRegistry` so a remote tool is indistinguishable from a local one; `resultType: "input_required"` is detected and rejected as unsupported in this subset. |
| `security.py` | `tool_digest`, `ServerTrustPolicy`, `ToolPinStore`, `TokenPassthroughPolicy`, `MCPClientSecurity`, `SecurityPolicyError` + subclasses | Canonical sha-256 over `{name, description, inputSchema}`; trust list by server identity; pin-on-first-contact then verify — a mutated declaration or an unpinned new tool raises `ToolPoisoningError`; credential-like argument keys (`access_token`, `authorization`, ...) never cross the boundary; optional tool allowlist. Security checks run *before* anything is sent. |

## 4. Acceptance criteria

```powershell
# 1. starter red
.\.venv\Scripts\python.exe -m pytest tests/week05 -m week -q

# 2. green after implementing
.\.venv\Scripts\python.exe -m pytest tests/week05 -m week -q

# 3. lint
.\.venv\Scripts\ruff.exe check agentlab/mcp tests/week05

# 4. foundation green
.\.venv\Scripts\python.exe -m pytest -q
```

Manual acceptance (the learning-plan deliverable): build a small multi-step task
where an agent calls a remote tool through `MCPClient.as_tool_registry()` (a
local mini-loop in a script is fine — do **not** import `agentlab.loop` from the
week-5 tests), then produce a security checklist pass: trust list populated,
pins persisted, no credentials in arguments, origin/tenant of the server
recorded.

## 5. Hints (progressive)

1. **Get the response `id` right.** The client must match responses by id; an
   async client with several in-flight requests is where this bites in real
   life. Use a monotonically increasing integer per client.
2. `make_request` accepts `meta` separately from `params`; merge it under
   `params["_meta"]`. MCP 2026-07-28 has no other place to put the version.
3. Server ordering: sort tools by `name` and resources by `uri` — the spec says
   `tools/list` *SHOULD* be deterministic so prompt caches can hit, and the tests
   assert it.
4. Protocol errors vs tool errors: `tools/call` with an unknown name is a
   JSON-RPC **error**; a handler that raises becomes a *successful* JSON-RPC
   result with `isError: true`. Keep them distinct — callers recover differently.
5. Security ordering in `call_tool`: token passthrough check first, then
   allowlist, then send. A blocked call must leave `transport.sent` empty.
6. Pin digests over the declaration only (`name`, `description`, `inputSchema`),
   not over handler output; a tool whose output changes is not a poisoned tool.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| `KeyError: 'id'` in a notification test | Notifications have no `id`; `is_notification` must check for *absence*, not truthiness (an `id: null` request is not a notification). |
| Server returns `-32601` for `server/discover` | You dispatch methods by suffix or forgot that the method string is exactly `server/discover`. |
| `tools/list` order flaps between runs | You iterated a dict without sorting; also check the client doesn't reorder by description. |
| Pinning test fails on the second `list_tools` | `check_tools` must pin on first contact, then *verify*; or your canonical JSON uses insertion order for schema keys — use `sort_keys=True, separators=(",", ":")`. |
| Timeout test returns `ok=True` | `call_tool` catches `MCPError` and returns `ToolResult.failure`; make sure `_request` re-raises the timeout as `MCPError`, not `ToolResult`. |
| `serve_stdio` loops forever on bad input | Parse errors must consume one line and `continue`; `max_messages` counts valid messages only, and EOF ends the loop. |

## 7. Spec conformance notes

This lab implements a deliberately small, **synchronous** subset of MCP
**2026-07-28**. What is faithful:

- **Stateless core.** No `initialize`/`notifications/initialized`, no sessions,
  no `Mcp-Session-Id`. Every request carries
  `_meta[io.modelcontextprotocol/protocolVersion]` (+ `clientInfo`,
  `clientCapabilities`); mismatches return `-32022` with
  `data.supported`/`data.requested`; servers must implement `server/discover`.
- **`resultType` on every result** (`"complete"` / `"input_required"`); clients
  treat a missing field as `"complete"` for older servers.
- **MCP-reserved error codes** `-32020..-32099`; implemented
  `UNSUPPORTED_PROTOCOL_VERSION = -32022`. Resource-not-found uses `-32602`
  (the 2026 revision replaced the old `-32002`).
- **Cacheable results** carry `ttlMs` and `cacheScope` on `server/discover`,
  `tools/list`, `resources/list` and `resources/read`; `tools/list` is
  deterministically ordered.
- **Modern-only.** Roots, Sampling and Logging are deprecated and not
  implemented; prompts are not implemented; OAuth is not implemented (see
  below).

Known divergences, in order of how likely they are to bite:

1. **Transport.** Only a synchronous in-memory channel and newline-delimited
   stdio framing are implemented. Streamable HTTP (single POST endpoint with
   JSON or request-scoped SSE), `subscriptions/listen`, the removed GET stream,
   and resumability are out of scope. `StdioServerTransport` operates on
   `TextIO`; tests use `io.StringIO`, and no process is spawned anywhere.
2. **Multi Round-Trip Requests (MRTR).** `resultType: "input_required"` is
   *detected and rejected* with `MCPError`; the client does not implement
   `inputRequests`/`inputResponses` retries, so elicitation/sampling/roots-style
   flows cannot complete.
3. **Auth.** MCP's transport-level OAuth (authorization-code + PKCE, RFC 8707
   resource indicators, RFC 9207 `iss` validation, Client ID Metadata Documents)
   is not implemented. This week's `security.py` is client-side *policy*
   (trust list, digests, token passthrough) — complementary to OAuth, not a
   replacement: it protects against a server you already connected to, not
   against connecting to the wrong server.
4. **Error-code breadth.** `-32020` (`HeaderMismatch`) and `-32021`
   (`MissingRequiredClientCapability`) are defined but never raised, because
   there are no HTTP headers and no client-capability enforcement in this
   subset.
5. **Discovery result shape is approximated.** The documented fields
   (`protocolVersions`, `serverInfo`, `capabilities`) follow the spec page; the
   caching hints and any optional fields (`instructions`, `icons`, extension
   blocks) are a plausible subset, not verified field-for-field against the JSON
   schema — check the schema page before interoperating with a real 2026-07-28
   server.
6. **Caching is advertised, not implemented.** `ttlMs`/`cacheScope` are returned
   and recorded on `DiscoverResult`; the client never caches, revalidates, or
   respects `listChanged` notifications.
7. **No extensions/tasks.** The extension negotiation field and the official
   `io.modelcontextprotocol/tasks` extension (polling `tasks/get`,
   `tasks/update`) are out of scope.
8. **Batch requests, progress notifications, pagination cursors and structured
   output schemas** are not implemented; `tools/call` returns
   `structuredContent` only when the handler returns a dict.
9. **Schema validation is the handler's job.** The server does not validate
   `arguments` against `inputSchema`; a production server should (the spec
   mandates validation where strict schemas are declared).
10. **HTTP transport concerns** (`Mcp-Method`/`Mcp-Name` headers, Origin
    validation, localhost-only binding, AI-extension headers) do not apply to
    this in-memory/stdio subset.

Anything above that you need for an integration decision: read the linked spec
pages rather than extrapolating from this lab. Accuracy about the stateless
redesign is the point; breadth is not.

## 8. SendOS bridge

Read (30 min, read-only): the connector manifest → registry path
(`ICapabilityManifestProvider`, `CapabilityCatalogueAssembler`) and the
execution-origin stamping around connector results. Cross-reference
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§3 topics 8/17 and §4.2.

Answer in your lab notes:

1. Which parts of SendOS's connector surface would an MCP server replace
   cleanly (discovery, tool declarations, invocation) and which would *not*
   (governed entitlements, approval gates, tenant scoping)?
2. If the catalogue exported `server.json` + an MCP server, who would be the
   OAuth resource server, and how would the client's authority map onto the
   server's scopes without becoming a confused deputy?
3. Where does SendOS stamp "real vs simulated" execution origin, and what is the
   MCP analogue of that metadata (tool result `_meta`, trace context, both)?

## 9. Stretch (optional)

1. **Expose your agent over A2A.** Write the `/.well-known/agent-card.json` an
   agent would publish (skills, auth schemes, capabilities) and explain what the
   card must **not** reveal (internal tool names, tenant data, prompt contents).
2. **A Streamable-HTTP-shaped transport.** Implement a `Transport` adapter whose
   `send` performs one POST and returns JSON (no SSE), then explain what breaks
   for notifications/subscriptions — the framing is easy, the state story is not.

## 10. Reflection (weekly review)

1. **Conceptual:** why did the MCP designers remove the `initialize` handshake?
   What does statelessness cost a client, and what does it buy an operator?
2. **Architectural:** tool-description digest pinning protects against a server
   that changes behaviour after approval. Where in a production host should that
   pin be stored (client cache, catalogue, approval record) and why?
3. **Transfer:** your day job has bespoke connectors. Which one would you expose
   over MCP first, and what would you refuse to expose over MCP even if the
   protocol allowed it?
