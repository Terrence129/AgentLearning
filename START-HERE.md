# START HERE

Read this once, top to bottom. It takes ~10 minutes, then ~90 minutes of setup and first contact.
Do not read the whole learning plan first — you will lose momentum. Set up, see something work, then plan.

---

## 1. What you are getting (2 min)

You are an experienced full-stack engineer (Java/C#, React, AWS) who has called LLM APIs but not built
agent systems. Over ~10 weeks you will build a small agent platform from scratch, in Python, driven by
tests — and simultaneously learn to read the `.NET` agent platform you work on (SendOS) with expert eyes.

The rule that makes this work: **you write code every week, and a failing test suite defines the finish line.**

---

## 2. Setup (15 min)

Open a PowerShell terminal (Windows PowerShell 5.1 or PowerShell 7) in `D:\DevRepo\MyProjects\AgentLearning`.

```powershell
.\tasks.ps1 setup
```

This will:
1. install Python 3.12 via `uv`,
2. create `.venv` and install dependencies,
3. copy `.env.example` → `.env`,
4. run `agentlab doctor`.

Expected: the doctor table prints `python ok`, `repo root ok`, `.env file ok`, and **`provider fail`**
until you add a key. That failure is your first task.

### Add a key

Edit `.env` with Notepad/VS Code (never commit it). Minimum viable configuration:

```dotenv
DEFAULT_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...          # https://platform.deepseek.com
```

If you have an OpenAI key, add `OPENAI_API_KEY=sk-...` too — some later labs compare providers.

Then:

```powershell
.\tasks.ps1 doctor
```

All rows should be `ok`/`info` now.

> **Budget guard:** every run is capped by `AGENTLAB_RUN_BUDGET_USD` (default $0.50). Leave it on.

### Open it in VS Code (2 min)

This repo ships a ready workspace: interpreter, test discovery, Ruff on save, task runner, and debug configs.

1. **File → Open Folder** → `D:\DevRepo\MyProjects\AgentLearning` (the repo itself, not its parent).
2. Accept the recommended extensions prompt (Ruff, PowerShell, Markdown, Error Lens, GitLens, Todo Tree, Spell Checker).
3. `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv\Scripts\python.exe`.
4. `Terminal → Run Task…` → **AgentLab: doctor**.

Details, a PyCharm alternative, and AI-assistant guardrails: [`docs/internals/IDE-SETUP.md`](docs/internals/IDE-SETUP.md). Rider/Visual Studio stay for SendOS `.NET` work.

---

## 3. First contact: see the foundation work (20 min)

Run the foundation tests (these are provided, not your work):

```powershell
.\tasks.ps1 test
```

Expected: foundation tests pass; any `tests/week*` tests that exist fail on purpose — that is your work.
Read `tests/test_core.py` quickly: it demonstrates every primitive you will use later (messages, tools,
tracing, budgets, mocks, cassettes).

Now run the environment check and a **deliberately unfinished** command:

```powershell
.\tasks.ps1 doctor
.\tasks.ps1 chat
```

`chat` will tell you "Week 1 lab not implemented yet". That is correct. Run the week 1 tests to see why:

```powershell
.\tasks.ps1 week 1
```

You will see failing tests with messages like *"Week 1 lab: implement complete()"*. **That is your first
lab.** The failing tests are the specification — read them before reading the brief.

---

## 4. Read exactly three things (20 min)

In this order:

1. [`labs/week01-provider/README.md`](labs/week01-provider/README.md) — what to build this week
2. [`docs/plan/WEEKLY-RHYTHM.md`](docs/plan/WEEKLY-RHYTHM.md) — how to spend 8–12 hours well
3. [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md) — skim the 9 weeks, read week 1 carefully

Do not open the research reports yet. They are reference material, indexed by week.

---

## 5. Ten-minute planning ritual (10 min)

Open [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) and fill in:

- Start date
- This week's three sessions in your calendar (suggested: Tue 20:00, Thu 20:00, Sat 09:00–13:00)
- Week 1 goal in one sentence

Then copy [`templates/weekly-review.md`](templates/weekly-review.md) to `notes/week01-review.md` and leave it
open all week. You will fill it in on Saturday.

---

## 6. Your first 60 minutes of real work

1. Open `agentlab/providers/openai_compat.py` and read the module docstring.
2. Open `tests/week01/test_complete.py` (or whichever order the brief gives) and read the first failing test.
3. Implement `_build_payload` first. Run that test. Iterate.
4. When stuck >20 minutes, write the question down and ask your AI tutor (see below) — do not silently struggle.

---

## 7. How to use the AI tutor (me) in this repo

I have the full plan, the research, and the SendOS context. Good prompts:

- "I'm on week 2, test `test_agent_stops_on_max_steps` fails with X. Give me a hint, not the answer."
- "Review my `agentlab/loop/react.py` for the four failure modes in the week 2 brief."
- "Explain why SendOS does approval binding differently from my week 6 implementation."
- "Quiz me on week 4 concepts for 10 minutes."
- "I have 45 minutes today — what is the highest-value thing to do?"

Anti-patterns that waste your time:

- "Write this for me." — you will learn nothing and the tests will not teach you.
- Pasting the whole error without the test name and what you tried.
- Asking for the solution before running the tests.

The tutor's job is to keep you in the **productive struggle zone**: hints before answers, review after attempts.

---

## 8. Non-negotiables

| Rule | Reason |
|---|---|
| Tests green before advancing | The next week assumes this week's abstractions |
| `Budget` caps on every live run | Never debug an agent with an uncapped loop |
| One commit per step | Bisectable history, portfolio evidence |
| Weekly review + 5 flashcards | Spaced repetition is the only thing that makes terms stick |
| SendOS bridge reading on Saturday | Transfer is the point of this whole repo |
| Ask within 20 minutes of being stuck | Silence is the main way self-study fails |

---

## 9. If something breaks

| Symptom | Fix |
|---|---|
| `uv: command not found` | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` then restart the terminal |
| `doctor` says no provider | Check `.env` exists, key has no quotes/spaces, `DEFAULT_PROVIDER` matches a configured provider |
| `chat` prints week 1 panel | Correct — finish the lab |
| Tests fail on `import agentlab` | Run `.\tasks.ps1 sync` |
| `python` version wrong | `uv python install 3.12`; the repo pins it via `.python-version` |
| Cost creeping up | Lower `AGENTLAB_RUN_BUDGET_USD`, use the mock provider for tests, and prefer DeepSeek for high-volume labs |

---

**Next step:** run `.\tasks.ps1 setup`, then open [`labs/week01-provider/README.md`](labs/week01-provider/README.md).
