# Week 8 Quiz — Security, Governance, Cost, Reliability

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** Indirect prompt injection arrives via:

- A) The user typing "ignore previous instructions"
- B) Content the agent reads — web pages, files, tool results, emails
- C) A malicious API key
- D) A malformed JSON schema

**Q2.** The "lethal trifecta" is:

- A) Three agents in one squad
- B) Private data + untrusted content + external communication in the same agent
- C) Three retries without backoff
- D) Read, write and delete tools together

**Q3.** Effective authority should be computed as:

- A) The union of all grants so the agent is never blocked
- B) The intersection over independent grants, deny-by-default
- C) Whatever the model proposes
- D) The last grant applied

**Q4.** The safest default for an autonomous system is:

- A) Allow, then audit
- B) Deny by default; require explicit grants
- C) Ask the model to self-police
- D) Allow only during business hours

**Q5.** `read_file` must validate paths against an allowlist because:

- A) It improves latency
- B) Path traversal (`../`) and absolute paths can reach outside the workspace
- C) The model cannot generate paths
- D) It reduces token usage

**Q6.** The difference between a trace and an audit log is:

- A) They are the same thing
- B) Traces debug behaviour; audit logs are tamper-evident evidence of actions with before/after state
- C) Audit logs are cheaper
- D) Traces contain PII, audit logs do not

## Part B — Short answer (3 questions)

**Q7.** Explain credential isolation as a structural defence and why it beats better prompting.

**Q8.** Give a concrete fail-closed vs fail-open decision for a model router: which failures should route to a fallback and which must abort? Justify.

**Q9.** Your `read_file` tool will be exposed to an untrusted-content workflow. List the defence-in-depth controls you would stack, beyond the allowlist check.

## Part C — Spot the bug (1 question)

**Q10.** This tool is the only filesystem guard in the system. Identify **three** defects.

```python
WORKSPACE = "/srv/agent/workspace"


def read_file(path: str) -> str:
    if not path.startswith(WORKSPACE):
        raise PermissionError("outside workspace")
    with open(path) as f:
        return f.read()
```

---

## Answers and explanations

**Q1 — B.** Indirect injection is the dominant real-world attack: the agent trusts content it fetched, and that content contains instructions.

**Q2 — B.** Any two of the three are manageable; all three in one agent means a successful injection can exfiltrate private data outward.

**Q3 — B.** Intersection prevents one source (or the model) widening access. Union is how privilege-escalation bugs are born.

**Q4 — B.** Deny-by-default with explicit grants is the only default that fails safely.

**Q5 — B.** String prefix checks are not path validation; traversal, symlinks and normalization defeat them.

**Q6 — B.** Audit is evidence with integrity and before/after payloads, retained for compliance; traces are for debugging and may be sampled.

**Q7 — model answer.** Keep secrets out of the sandbox where model-generated code runs: tokens live in a vault/proxy, and the sandbox gets short-lived capability-scoped handles instead. If injection succeeds, the agent still cannot read the credential, so it cannot spawn new sessions or exfiltrate. Prompt-level instructions ("never reveal secrets") are probabilistic and fail exactly under the adversarial conditions that matter.

**Q8 — model answer.** Degrade by *bounded fallback*, never by bypass. `CostAwareRouter.complete` falls back to the next viable candidate on a transient `ProviderError(retryable=True)`, up to `max_attempts`; non-retryable provider errors and `RequestCancelled` propagate immediately, the budget is re-checked before each attempt, and `BudgetExceeded` propagates. `select` fails closed: if no candidate is viable it raises `RoutingError` with the exclusion map rather than "pick anything". So an availability failure may shift model, while authority, budget, cancellation and policy failures abort — routing around a control defeats the control.

**Q9 — model answer.** (1) Resolve and normalize the path (realpath) before the allowlist check; reject symlinks that escape. (2) Cap size and apply truncation with an explicit marker. (3) Treat file content as untrusted: wrap it in delimited data markers and never let it act as instructions. (4) Redact or refuse likely-secret files (`.env`, key material) via pattern/basename rules. (5) Log an audit record per read with correlation id. (6) Keep read tools separate from write tools and require approval for writes.

**Q10 — model answer.** (1) Prefix check on the raw string is bypassable: `"/srv/agent/workspace/../etc/passwd"` starts with the workspace, and `os.path.realpath`/`normpath` is never applied; absolute-vs-relative forms also slip through. (2) No symlink handling — a link inside the workspace can point outside. (3) No size limit, no truncation, no encoding/error handling and no audit event. Fix: resolve with `Path.resolve()`, assert it is relative to the resolved workspace root, reject symlinks that resolve outside, cap read size, and record an audit row.
