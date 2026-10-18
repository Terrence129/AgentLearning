# Portfolio Write-up — Mini-SendOS

> Template. Replace every `_italic prompt_` with real content; delete this block when done.
> **Target:** 800–1,500 words. Written for a senior engineer or hiring manager who has 10 minutes.
> Include one architecture diagram (ASCII or an image), one results table, and one "what I'd do next".

## Title

_Mini-SendOS: a governed agent runtime built from scratch, in ten weeks_ (adjust)

**One-line summary:** _An offline, test-driven agent platform where every model output is a typed decision, every write is an approval-bound proposal, and every step is an append-only audit row — built from primitives, not frameworks._

## 1. Problem

_What agent systems get wrong in production (pick 2–3, with evidence): model-authored approvals, duplicate side effects, unbounded cost, no trace, context loss. Why is this hard? Which failure did you personally reproduce in a lab?_

## 2. Architecture

_Paste the request-path diagram: goal -> decision -> catalogue check -> proposal -> approval -> execution -> audit. Name the module for each arrow and the week that taught it. Mark which parts are provided infrastructure and which you implemented._

## 3. Decisions and trade-offs

_3–5 decisions, each as: context -> options considered -> choice -> cost of being wrong. Suggested candidates:_
- _Closed decision union vs free-text output with a parser._
- _Proposal persisted before approval vs approving an in-memory object._
- _Published-wins catalogue vs field-level merge between declaration sources._
- _At-most-once execution via persisted approval state vs idempotency keys on the tool._
- _Optional FastAPI surface vs server-rendered CLI output._

## 4. Evidence

| Metric | Result | How measured |
|---|---|---|
| Capstone tests green | _46/46_ | `pytest tests/week09 -m week -q` |
| Demo runs offline | _exit code 0_ | `python scripts/demo_capstone.py` |
| Foundation tests | _N passed_ | `pytest -q` |
| Avg. end-to-end latency (mock) | _N ms_ | _timing script_ |
| Tokens / cost per happy path | _N / $N_ | _trace + pricing table_ |
| Audit rows per lifecycle | _N_ | `audit_trail()` |
| Security invariants tested | _N_ | _list the B1–B6 tests_ |

## 5. What I checked, not just built

_List the invariants you tested yourself (replay, hash mismatch, cross-tenant, fail-closed write, budget breach). One sentence each on what would break without the control._

## 6. Threats considered

_Injection via tool output, approval replay, cross-tenant access, budget exhaustion, model error. For each: control, residual risk, and what you deliberately left out of the miniature._

## 7. Limitations (be honest)

_At least three: in-memory persistence, single process, no auth, mock-only model in the demo, no retry/backoff on execution, no durable suspend/resume._

## 8. What I'd do next

_One concretely-scoped improvement, preferably the one you proposed to SendOS. What would you build, how would you measure it, what is the risk?_

## 9. What I can now explain without notes

_5–8 bullets: the agent loop and where budgets are enforced; why tool output is context; compaction's order of operations; why memory needs provenance; why approvals bind to a hash; why pass^k beats pass@1; MCP's current revision and what changed; how SendOS's governance sandwich maps onto your capstone._

---

**Links:** _repo path, demo video, lab brief, this write-up published at …_
