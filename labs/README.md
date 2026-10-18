# Labs

One lab per week. Each lab is a **build specification**, not a tutorial: a brief, failing tests that define done, a starter skeleton, and a reference solution you should not open until your tests pass.

| Week | Lab | Module you build | Tests | Hours | Status |
|---|---|---|---|---|---|
| 1 | [Provider seam](week01-provider/README.md) | `agentlab/providers/openai_compat.py` | `tests/week01` | 8–10 | scaffolded |
| 2 | [Agent loop](week02-agent-loop/README.md) | `agentlab/loop/`, `agentlab/tools/builtin.py` | `tests/week02` | 10–12 | scaffolded |
| 3 | [Structured output](week03-structured-output/README.md) | `agentlab/schemas/` | `tests/week03` | 8–10 | scaffolded |
| 4 | [Context & memory](week04-context-memory/README.md) | `agentlab/context/` | `tests/week04` | 10–12 | scaffolded |
| 5 | [MCP](week05-mcp/README.md) | `agentlab/mcp/` | `tests/week05` | 8–10 | scaffolded |
| 6 | [Squads & approval](week06-squads/README.md) | `agentlab/orchestrator/` | `tests/week06` | 10–12 | scaffolded |
| 7 | [Evals](week07-evals/README.md) | `agentlab/evals/` | `tests/week07` | 8–10 | scaffolded |
| 8 | [Security & governance](week08-security/README.md) | `agentlab/guard/` | `tests/week08` | 8–10 | scaffolded |
| 9 | [Capstone](week09-capstone/README.md) | `agentlab/capstone/`, `agentlab/web/` | `tests/week09` | 12–16 | scaffolded |

> Status is updated as the repo evolves. If a lab you need is still marked `scaffolded` and its tests are missing, ask the AI tutor to generate it — the [scaffold contract](../docs/internals/SCAFFOLD-CONTRACT.md) defines exactly what it must contain.

## The contract for every lab

1. Read the brief and the concept note before opening the tests.
2. Run the tests; they are the specification.
3. Implement in the module named above.
4. Green &rarr; write the weekly review &rarr; add flashcards &rarr; update `docs/plan/PROGRESS.md`.
5. Only then diff against `solutions/weekNN/`.

```powershell
.\tasks.ps1 week 1       # run that week's tests
.\tasks.ps1 labs         # all lab tests (mostly red until you build them)
```

## Rules

- **No live API calls in tests.** Every lab ships with deterministic mocks; live calls are for exploration and the manual artifact.
- **One concept, one build.** If a lab starts needing three new ideas, it is a sign the design is wrong.
- **Stretch goals are optional.** The gate is the acceptance criteria, not the stretch.
