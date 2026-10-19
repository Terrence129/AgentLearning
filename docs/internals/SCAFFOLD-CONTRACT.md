# Scaffold contract (internal)

Rules for every lab scaffold in this repo. If you are an AI assistant or a future contributor generating a week, follow this exactly — consistency is what makes nine weeks feel like one course.

---

## 1. Ownership map (no two builders write the same path)

| Week | Owned module(s) under `agentlab/` | Tests | Lab brief |
|---|---|---|---|
| 1 | `providers/` (starter exists; extend only `openai_compat.py` and add nothing else) | `tests/week01/` | `labs/week01-provider/` |
| 2 | `loop/`, `tools/builtin.py` | `tests/week02/` | `labs/week02-agent-loop/` |
| 3 | `schemas/` | `tests/week03/` | `labs/week03-structured-output/` |
| 4 | `context/` | `tests/week04/` | `labs/week04-context-memory/` |
| 5 | `mcp/` | `tests/week05/` | `labs/week05-mcp/` |
| 6 | `orchestrator/` | `tests/week06/` | `labs/week06-squads/` |
| 7 | `evals/` | `tests/week07/` | `labs/week07-evals/` |
| 8 | `guard/` | `tests/week08/` | `labs/week08-security/` |
| 9 | `capstone/`, `web/` | `tests/week09/` (optional) | `labs/week09-capstone/` |

Never edit: `agentlab/{types,config,trace,budget,pricing,errors,cli}.py`, `agentlab/testing/*`, `agentlab/tools/registry.py`, `tests/test_core.py`, `tests/conftest.py`, `pyproject.toml`, `docs/plan/*`, `README.md`, `START-HERE.md`, `_research/*`. If you believe one of these is wrong, report it — do not edit it.

---

## 2. Independence rule (critical)

Each week's tests must pass using only:

- the Python standard library,
- the **provided infrastructure** (`agentlab.types`, `.config`, `.trace`, `.budget`, `.pricing`, `.errors`, `.testing`, `.tools.registry`), and
- the module that week owns.

Do **not** make `tests/week04` depend on an implemented `agentlab.loop` — earlier weeks may still be unfinished while you verify. Integration between weeks is exercised by the learner manually and by the week 9 capstone demo.

If a test genuinely needs a loop-like driver, build a tiny local helper inside the test file.

---

## 3. Starter code style

- File header docstring: why the mechanism exists, what breaks without it, and what the learner should read first.
- Public functions/classes have precise docstrings stating the **contract** (inputs, outputs, error policy). Docstrings are the spec; tests are the proof.
- Unimplemented functions:

```python
def resolve(self, request: FooRequest) -> FooResult:
    """<contract>"""
    raise NotImplementedError("Week 4 lab: implement Compactor.compact")
```

- Hints: 2–5 short hints as comments or docstring bullets. Never a full algorithm.
- No hidden magic: no dynamic imports, no metaclasses, no clever decorators unless the lab is *about* that mechanism.
- Type hints everywhere; `from __future__ import annotations` at the top; Python 3.12.
- `ruff` clean, line length 110.

---

## 4. Test style

- First line after imports: `pytestmark = pytest.mark.week` (module-level marker; this is what `pytest -m week` selects).
- One behaviour per test, descriptive names: `test_rejects_edited_approval_after_approval`.
- Every test must fail on the starter and pass on the solution, for the *intended* reason.
- No network, no sleeps > 50 ms, no flakiness, no randomness without a seed. Whole week suite < 10 s.
- Use `agentlab.testing.MockProvider` for any model interaction; use `MemorySink` for traces; use `tmp_path` for files.
- Prefer asserting on **observable contracts** (messages sent, events emitted, errors raised) over internal state.
- A handful of property-style tests with plain loops are welcome; do not add `hypothesis` as a dependency.

---

## 5. Solution layout

```
solutions/weekNN/agentlab/<module path>.py
```

This mirrors the repo root, so `.\tasks.ps1 solution N` (Windows) / `./tasks.sh solution N` (macOS/Linux) can copy `solutions/weekNN/*` over the root. Also include `solutions/weekNN/NOTES.md` only if the approach is non-obvious.

The solution must make `pytest tests/weekNN -m week` fully green.

---

## 6. Verification procedure (every builder must actually run this)

```powershell
# Windows (PowerShell)

# 1. starter must be red
.\.venv\Scripts\python.exe -m pytest tests/weekNN -m week -q

# 2. back up the starter, apply the solution
Copy-Item agentlab\<path> agentlab\<path>.starter -Force
Copy-Item solutions/weekNN/* . -Recurse -Force

# 3. solution must be green
.\.venv\Scripts\python.exe -m pytest tests/weekNN -m week -q

# 4. restore starter
Move-Item agentlab\<path>.starter agentlab\<path> -Force
```

```bash
# macOS / Linux (bash or zsh)

# 1. starter must be red
uv run pytest tests/weekNN -m week -q

# 2. back up the starter, apply the solution
cp -R agentlab/<path> agentlab/<path>.starter
cp -R solutions/weekNN/. .

# 3. solution must be green
uv run pytest tests/weekNN -m week -q

# 4. restore starter
mv agentlab/<path>.starter agentlab/<path>
```

If step 1 passes or step 3 fails, the scaffold is wrong — fix it before reporting.

---

## 7. Lab brief structure

`labs/weekNN-<slug>/README.md`:

1. **Why this week exists** — the failure mode it prevents, in 2–3 sentences.
2. **Prerequisites & time budget** — hours, what must be green before starting.
3. **The spec** — table of files/functions to implement, with the contract.
4. **Acceptance criteria** — exact command(s) that must pass.
5. **Hints** — progressive, from "re-read X" to "watch out for Y", never the answer.
6. **Debugging guide** — 3–5 common failures and what they mean.
7. **SendOS bridge** — specific C# files/types to read, and 3 questions to answer.
8. **Stretch** — 1–2 optional extensions.
9. **Reflection** — 3 questions for the weekly review (one conceptual, one architectural, one transfer).

---

## 8. Quality bar

- A senior engineer should be able to read the starter and know exactly what to build without asking.
- A beginner should be able to start without reading a framework.
- No dead code, no placeholder TODOs unrelated to the lab, no "magic constants" without explanation.
- If something can be tested, it is tested.
