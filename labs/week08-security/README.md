# Week 8 — Security, governance, cost, reliability

Assume the model **will** be manipulated. Design so that it does not matter.

## 1. Why this week exists

Prompt injection is unsolved, so the security boundary cannot be the prompt — it has to be the architecture around the model. If the agent can read private data, read untrusted content *and* send data outward, an attacker who controls one document can exfiltrate everything; if the model can choose paths, commands and models freely, a jailbreak becomes RCE or a denial-of-wallet incident. This week builds the confinement layer: untrusted content is data, tools run in a sandbox with approvals, authority only narrows, audit is append-only, quotas are per tenant, and routing fails safe.

## 2. Prerequisites & time budget

- **8–10 hours** (security work rewards a second pass on the tests).
- Green: weeks 1–2 at minimum (`Tool`, `ToolRegistry` and the provider seam are used by this lab); weeks 3–7 help but are not required to pass `tests/week08`.
- Read first: [`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §3 (threat model, MCP hardening, sandbox/audit/red team), §4.4 (multi-tenant isolation), §5 (cost/latency levers); [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.2 (authority intersection) and §4.4 (budgeted routing).
- Also read the OWASP GenAI Top 10 2026 rows for prompt injection, excessive agency and unbounded consumption (links in research 03 §3.1).

## 3. The spec

Implement everything under `agentlab/guard/`. `errors.py` and `attacks.py` are provided; the red-team corpus is **data** — do not weaken it, extend it.

### `agentlab/guard/injection.py` — untrusted content is data

| Item | Contract |
|---|---|
| `wrap_untrusted(content, source)` | delimit + label untrusted content; escape delimiter spoofing; strip zero-width characters |
| `scan_injection(text)` | normalized (NFKC + casefold) rule scan; findings sorted by position; categories at least instruction override, role hijack, prompt exfiltration, tool abuse, command execution, exfiltration, hidden content, encoded payloads; benign text has no findings |
| `screen_untrusted(text, source)` | risk = max severity; `allowed = risk != "high"`; always returns the wrapped (sanitized) form |
| `build_guarded_messages(system, user, untrusted, sources)` | one system message stating the instruction hierarchy, user turn verbatim, each untrusted item as labelled data; source-length mismatch raises `ValueError` |
| `vet_output(text, secrets)` | redact secret leaks, external markdown images, data-channel URLs, credential-shaped strings; `reasons` sorted; clean text unchanged |
| `assess_lethal_trifecta(profile, mitigations)` | 3 legs ⇒ critical; 2 ⇒ elevated; 3 legs with no mitigation ⇒ **blocked** with required controls; known mitigation unblocks but risk stays critical; unknown mitigation raises `ValueError` |

### `agentlab/guard/sandbox.py` — confine execution

| Item | Contract |
|---|---|
| `resolve_sandbox_path(raw, allowed_roots)` | URL-decode once, then reject empty/absolute/UNC/NUL/`..` paths; resolve and require containment in an allowed root; `PathNotAllowed` otherwise |
| `read_text_limited(path, max_bytes)` | refuse oversize files before loading them (`SandboxLimitExceeded`); negative/zero limit raises `ValueError` |
| `run_command(argv, allowed_commands, ...)` | empty argv `ValueError`; command must be allowlisted (`ToolNotAllowed`); no shell; hard timeout (`SandboxTimeout`); output truncated; non-zero exit is data |
| `action_hash(tool, arguments)` | canonical SHA-256 binding tool **and** arguments |
| `ApprovalLedger.consume(token, now)` | expiry and at-most-once replay refused with `ApprovalRequired` |
| `require_allowed_tool` / `require_approval` | allowlist check; read tools no-op, write tools need a token matching tenant + exact action, then consume it |

### `agentlab/guard/authority.py` — deny by default, never widen

| Item | Contract |
|---|---|
| `effective_authority(tenant_id, boundaries, model_claims)` | intersection over boundaries whose tenant matches (or is platform-wide `None`); no applicable boundary ⇒ no grants; model claims never add grants and are recorded in `denied_claims`; empty tenant raises `ValueError` |
| `EffectiveAuthority.allows` / `.require` / `.delegate` | membership; raises `AuthorizationError`; delegation must be a non-empty subset of current grants |
| `reject_credential_passthrough` / `outbound_headers` | caller credentials (case-insensitive: `authorization`, `cookie`, `x-api-key`, …) are refused/ stripped; upstream uses its own token; empty upstream token raises `ValueError` |

### `agentlab/guard/audit.py` — evidence you cannot edit

| Item | Contract |
|---|---|
| `AuditRecord` | immutable row with before/after evidence, correlation id, decision, hash chain fields; `to_dict` / `from_dict` round-trip |
| `AuditLog.append` | monotonic seq from 1, clock-injected ts, hash chained to the previous row, JSONL flushed immediately when file-backed; only `allowed`/`denied` decisions |
| `AuditLog.update` / `.delete` | always raise `AuditViolation`, record the attempt, change nothing (file included) |
| `AuditLog.records` / `.find` / `.attempts` | append order; correlation-id grouping; rejected mutation log |
| `AuditLog.verify_integrity()` | seq contiguous from 1, prev-hash chain intact, stored hashes match recomputation (detects tampering) |

### `agentlab/guard/ratelimit.py` + `routing.py` — quotas and fail-safe routing

| Item | Contract |
|---|---|
| `TenantQuotaLimiter.check` / `.charge` / `.status` | fixed-window per-tenant request/token/USD budgets; `check` does not consume; `charge` is atomic and refuses without consuming; empty tenant raises `ValueError` |
| `estimate_call_usd` | `None` when price is unknown (never zero) |
| `CostAwareRouter.select` | excludes bad task type, reliability, latency, per-request and remaining budget, and unknown price; ranks by explicit `preferred`, then cost, then name; no candidate ⇒ `RoutingError` |
| `CostAwareRouter.complete` | fallback on **transient** `ProviderError` only; terminal errors and `RequestCancelled` propagate; re-checks budget per attempt and charges on success; attempts capped |

### `agentlab/guard/attacks.py` — the corpus (provided)

16 attacks across 10 categories, each naming its target guard. `tests/week08/test_attacks.py` asserts **every** one is blocked or detected; the coverage test fails if a category disappears. Add cases, never remove them.

## 4. Acceptance criteria

```powershell
.\.venv\Scripts\python.exe -m pytest tests/week08 -m week -q   # must pass
.\.venv\Scripts\ruff.exe check agentlab/guard                   # must be clean
```

Then produce the **lab artifact** (not tested, but the point of the week):

1. A `projects/security/SECURITY.md` threat model for one of your agents: lethal-trifecta audit, data flows, controls, residual risks, and what you would *not* claim to a customer.
2. A before/after table: run the corpus against an unguarded mini-agent (no sandbox, no screen, no approvals), then against the guarded version; every attack row must move from "succeeds" to "blocked".
3. One write action wired end-to-end: proposal → approval → sandbox → audit row with before/after evidence and one correlation id.

## 5. Hints (progressive)

1. **Re-read** research 03 §3.2's threat table. Every row has an *architectural* control; regexes and prompt warnings are the weakest layer, not the design.
2. Detection is not defence: `screen_untrusted` refusing high-risk content is the last line, while delimiting, hierarchy, least privilege and approvals are what hold when the detector misses.
3. Decode before you validate paths (`urllib.parse.unquote`), normalise separators, then `Path.resolve` and `is_relative_to` — checking the raw string misses `%2e%2e%2f`.
4. Approval binding is a hash of the **action**, not the tool name: approve `issue_refund($10)` and the token must not authorise `issue_refund($10_000)`. The ledger is what makes replay impossible.
5. Intersection starts from "nothing" and can only lose grants. Adding a boundary (or a model claim) that widens the result means you built a union.
6. Hash chains: include `prev_hash` in the hashed payload, otherwise deleting a middle row is undetectable.
7. Routing: `price is None` is not "free"; it is "unverifiable", and unverifiable budget must exclude the candidate. Cancellation is a terminal signal, never a retry.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| Traversal test passes with `..` but encoded form fails | validation ran on the raw string before `unquote` (or only checked `Path.parts` on the un-decoded text) |
| Timed-out subprocess hangs the suite | `subprocess.run` without `timeout=`, or the timeout exception was swallowed instead of raised as `SandboxTimeout` |
| Replay test only passes on the second call | the ledger records the ticket *after* the approval checks, but the token is re-created per call with a fresh ticket id in the test — use one token object and one ledger |
| `effective_authority` returns grants for another tenant | boundaries were unioned instead of filtered by `tenant_id in (None, tenant_id)` |
| Audit reload fails `verify_integrity` | the hash payload changed between append and verify (e.g. dict ordering, or `before`/`after` stored as tuples after JSON round-trip) |
| Fallback fires on a validation error | the `except ProviderError` branch checked only `isinstance`, not `exc.retryable`; terminal errors must re-raise |
| A quota test fails at exactly the limit | "requests > max" is the rule; `>=` rejects the last allowed request. Same for token/USD ceilings |

## 7. SendOS bridge

Read-only reference (SendOS repo): the governance controls this week miniatures.

- `.../Domain/Authority/EffectiveAuthority.cs` and `.../Application/Authority/AuthoritySources.cs` — the nine-source intersection; authority discovery vs permission.
- `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` — catalogue merge with published-wins; undeclared capabilities are not invokable.
- `.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs` and `ApprovalBindingAtMostOncePropertyTests.cs` — the invariants, as property tests.
- `apps/Send.Model.Adapter/src/.../Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs` and `.../Handlers/CompletionHandler.cs:60-210` — invalid never surfaces as valid; router excludes unverifiable budgets; cancellation never retries.
- `docs/architecture/governance-architecture.md:223-273` — the pre/post-LLM "governance sandwich" diagram.

Answer in your weekly notes:

1. Which of the nine authority sources could a model plausibly influence, and how does the intersection make that harmless? Where does your mini-version diverge?
2. SendOS records execution origin (real/simulated) per connector result. Why is origin an audit concern as well as a debugging one, and where would you stamp it in your design?
3. The licence/quota check lives at ingress. What breaks if the model can talk past it, and which of your week 8 controls would catch the resulting spend?

## 8. Stretch (optional)

- **Threat-model review of SendOS's approval path**: one page, using this week's vocabulary (binding, at-most-once, expiry, narrowing, audit evidence). Send it to a senior engineer for critique; note what they disagree with.
- **Wire the guard into the loop**: a mini red-team runner that executes the corpus against a `MockProvider` agent, records a `guardrail_block` trace event per attack, and writes a before/after markdown table — the same shape as the week 7 report.

## 9. Reflection (weekly review)

1. **Conceptual:** why is "remove a leg of the lethal trifecta" a stronger control than "detect the injection"? Give an attack your `scan_injection` rules would miss and explain which other layer still stops it.
2. **Architectural:** where is the enforcement boundary in your design — in the tool wrapper, the model adapter, or a central policy service? What are the costs of each placement in latency, blast radius and auditability?
3. **Transfer:** name one production system you run that trusts model-adjacent input (an LLM feature, a webhook, a scheduled job). Which of this week's five controls (untrusted-data handling, sandbox, authority intersection, append-only audit, per-tenant quota) does it lack, and what is the smallest first fix?
