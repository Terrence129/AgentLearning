# C# bridge labs (`dotnet/`)

Two small .NET 10 console labs that rebuild, in C#, the mechanisms the Python course builds in
weeks 1–3 — so that reading **SendOS** (the .NET agent platform this learner interns on) stops
being a translation exercise.

The repo is Python-first on purpose. These labs are a **bridge**, not a third track: they are
deliberately small, dependency-free, and mapped line-by-line to the SendOS files they mirror.

---

## Why this exists

The learner is a full-stack engineer (Java/Spring, C#/.NET, React/TS, AWS) working on SendOS, a
.NET 8/10 "AI operating system". The Python labs teach the primitives; the C# labs teach the same
primitives **in the language and idioms of the codebase they must read every day**. The bridge
is the difference between "I understand agents" and "I understand *this* agent runtime".

Every C# lab is timeboxed to a single 30-minute bridge session per week. If you only have half an
hour, run `--selftest` (proves the mechanism offline) and read the file headers.

---

## Structure

```
dotnet/
├── AgentBridgeLabs.sln          # solution (classic .sln, VS / Rider / dotnet CLI)
├── Directory.Build.props        # net10.0, nullable, implicit usings — no external packages
├── Bridge.Shared/               # the reusable seams both labs share
│   ├── Configuration/           # BridgeSettings: env vars, provider seam, redacted describe
│   ├── Providers/               # wire DTOs, SSE parser, retry handler, client, cost table
│   ├── Schema/                  # JsonSchemaLite: hand-rolled JSON Schema subset validator
│   ├── Decisions/               # typed decision family, schema, validator, three-stage parser
│   ├── Testing/                 # ScriptedHttpMessageHandler: offline transport + fragmented SSE
│   └── ConsoleUi.cs             # readable console output, NO_COLOR aware
├── ProviderBridge/              # WEEK 1: raw HttpClient, SSE streaming, retry/backoff
└── StructuredDecisionBridge/    # WEEK 3: typed decision, schema → binding → budget, repair loop
```

| Lab | Mirrors | SendOS counterpart |
|---|---|---|
| `ProviderBridge` | `agentlab/providers/openai_compat.py` (week 1) | `apps/Send.Model.Adapter/src/Send.Model.Adapter.Infrastructure/ExternalServices/*ProviderAdapter.cs`; `Application/Handlers/CompletionHandler.cs` |
| `StructuredDecisionBridge` | `agentlab/schemas/` (week 3) | `apps/Send.Model.Adapter/.../Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`; `apps/Send.Agent.Runtime/.../Domain/Decision/DecisionInteraction.cs`; `.../Application/Decision/PresentationBudgetEnforcer.cs` |

---

## Requirements and build

- **.NET SDK 10** (verified on `10.0.303`). No Node, no Python, no Docker.
- **No NuGet packages.** Everything builds from the shared framework, so the labs compile on a
  machine with no package feed access (verified: `dotnet build dotnet/AgentBridgeLabs.sln` from a
  clean `~/.nuget` cache succeeds with 0 warnings / 0 errors).

```powershell
# Windows (PowerShell)
# from the repo root
dotnet build dotnet/AgentBridgeLabs.sln

# offline mechanism checks (no API key, no network) — these are the gates
dotnet run --project dotnet/ProviderBridge           -- --selftest
dotnet run --project dotnet/ProviderBridge           -- --mock --stream
dotnet run --project dotnet/StructuredDecisionBridge -- --selftest
dotnet run --project dotnet/StructuredDecisionBridge -- --mock
```

```bash
# macOS / Linux
# from the repo root
dotnet build dotnet/AgentBridgeLabs.sln

# offline mechanism checks (no API key, no network) — these are the gates
dotnet run --project dotnet/ProviderBridge           -- --selftest
dotnet run --project dotnet/ProviderBridge           -- --mock --stream
dotnet run --project dotnet/StructuredDecisionBridge -- --selftest
dotnet run --project dotnet/StructuredDecisionBridge -- --mock
```

Live runs (optional, and the only part that costs money):

```powershell
# Windows (PowerShell)
$env:BRIDGE_API_KEY   = "sk-..."          # or OPENAI_API_KEY / DEEPSEEK_API_KEY
# $env:BRIDGE_BASE_URL = "https://api.deepseek.com/v1"   # default
# $env:BRIDGE_MODEL    = "deepseek-chat"                 # default
dotnet run --project dotnet/ProviderBridge -- --stream --prompt "Explain SSE in one sentence"
```

```bash
# macOS / Linux
export BRIDGE_API_KEY="sk-..."          # or OPENAI_API_KEY / DEEPSEEK_API_KEY
# export BRIDGE_BASE_URL="https://api.deepseek.com/v1"   # default
# export BRIDGE_MODEL="deepseek-chat"                 # default
dotnet run --project dotnet/ProviderBridge -- --stream --prompt "Explain SSE in one sentence"
```

### Environment variables

| Variable | Default | Used by | Notes |
|---|---|---|---|
| `BRIDGE_API_KEY` | — | live mode | Fallbacks: `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`. Never printed; `DescribeSafe()` redacts. |
| `BRIDGE_BASE_URL` | `https://api.deepseek.com/v1` | live mode | The path `/chat/completions` is appended. |
| `BRIDGE_MODEL` | `deepseek-chat` | both | Any OpenAI-compatible chat model. |
| `BRIDGE_MAX_COST_USD` | `0.50` | ProviderBridge | Prints a warning above this; it is a guard rail, not a hard block. |
| `BRIDGE_TIMEOUT_SECONDS` | `120` | both | Per-request HTTP timeout. |
| `NO_COLOR` | unset | both | `NO_COLOR=1` disables ANSI colour. |

**Offline-first guarantee:** `--selftest` and `--mock` never read the key, never open a socket.
A missing key in a live invocation prints the exact fix and falls back to `--mock` rather than
crashing.

---

## The two labs, and how they connect

```
week 1  ProviderBridge            week 3  StructuredDecisionBridge
──────────────────────            ─────────────────────────────────
HttpClient POST      ───────────────▶ same wire client, jsonMode: true
JSON body (no nulls)                   model returns a decision JSON object
SSE stream parsing                     JsonSchemaLite  (schema gate)
retry/backoff/jitter                   System.Text.Json polymorphism (binding gate)
usage → cost                           DecisionValidator (budget gate)
                                       RepairLoop ≤ 3 attempts
```

Read `ProviderBridge` first: it produces **text**. `StructuredDecisionBridge` consumes text and
refuses to produce anything but a **validated decision** — the central distinction of the
week-3 lab, and of SendOS's decision-first runtime.

---

## What is deliberately *not* here

Avoiding scope creep is part of the bridge's design:

- **Tool calls / the agent loop** — week 2 (`agentlab/loop/`). SendOS: `CapabilityDefinition`,
  `DirectCapabilityHandler`.
- **Budget-aware routing across models** — week 8 (`agentlab/guard/ratelimit.py`). SendOS:
  `CompletionHandler.HandleRoutedAsync`, `ModelCostProfile`.
- **Context compaction, memory, RAG** — week 4. SendOS: `Send.Context.Gateway`, `SpecialistContext`.
- **MCP / connectors** — week 5. SendOS: `Send.Connectors.Abstractions`, capability manifests.
- **Approval binding + at-most-once execution** — week 6. SendOS: `ApprovalCheckpoint`.
- **Durable suspend/resume** — weeks 6/9. SendOS: `CaseRuntime` (built but unwired).

Each of those has a Python lab; adding them here would duplicate the course and make the C#
bridge too big to finish in 30-minute sessions.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No API key found…` | No env var set | Set `BRIDGE_API_KEY`, or use `--mock` / `--selftest` |
| `HTTP 401` / `invalid_api_key` | Key wrong, expired, or from a different host | Check `BRIDGE_BASE_URL` matches the key's provider |
| `HTTP 404` / `model not found` | `BRIDGE_MODEL` not on that host | Use a model the host lists, e.g. `deepseek-chat` |
| `Expected text/event-stream but the provider returned 'application/json'` | Host ignored `stream: true` | Try without `--stream`; the client refuses to fake a stream |
| Constant `429`s | Rate limit or free-tier quota | Lower request rate; watch the retry timeline (it backs off, but cannot fix a hard quota) |
| `ScriptedHttpMessageHandler has no response for request #N` | A retry fired more times than the script expected | That is a test bug, not a transport bug — extend the script |
| Build fails with NuGet/network errors | A package reference slipped in | There are **no** `PackageReference` entries; run `dotnet build dotnet/AgentBridgeLabs.sln` and check the reported project |

---

## Verified status (2026-10-18, SDK 10.0.303)

| Check | Result |
|---|---|
| `dotnet build dotnet/AgentBridgeLabs.sln` | ✅ success, 0 warnings, 0 errors |
| `ProviderBridge --selftest` | ✅ 11/11 checks pass, exit 0 |
| `StructuredDecisionBridge --selftest` | ✅ 15/15 checks pass, exit 0 |
| `ProviderBridge --mock --stream` | ✅ runs offline; shows retry timeline, TTFT, usage |
| `StructuredDecisionBridge --mock` | ✅ runs offline; shows 4-stage repair convergence and budget utilisation |

`--selftest` is the C# equivalent of `pytest tests/weekNN -m week`: red before the mechanism
works, green after. If a check fails, the mechanism — not the environment — is broken.
