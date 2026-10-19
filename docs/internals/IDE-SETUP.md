# IDE and editor setup

**Recommendation: VS Code.** It is already installed on this machine (1.141) with the Python, Pylance, Jupyter, C# Dev Kit, Java and Rust extensions, so there is nothing new to learn or install. Keep **Rider / Visual Studio** for SendOS `.NET` work and for the optional [C# bridge labs](../../dotnet/README.md); this repo is Python + Markdown, and VS Code handles both with the least friction.

Why VS Code for this specific repo:

- **Reads the failing tests like source.** The whole curriculum is "open the test, satisfy the contract"; VS Code's Test Explorer and Ctrl+click navigation are the fastest way to jump between `tests/weekNN/` and `agentlab/`.
- **Integrated terminal for the task runner.** `.\tasks.ps1 week N`, `chat`, `doctor` all run in one panel, so you never lose context.
- **First-class Markdown** for the 65+ docs, lab briefs and the book chapter map, with link validation.
- **Polyglot.** The same window covers the Python labs, the C# bridge labs (`dotnet/`), and the YAML/TOML/Markdown around them.
- **Already shipped config.** [`.vscode/`](../../.vscode/) sets the interpreter, test discovery, formatter, tasks and debugger for you.

---

## 1. What is preconfigured

| Area | Setting | Effect |
|---|---|---|
| Interpreter | `.venv/Scripts/python.exe` | Python 3.12 with the project installed editable |
| Tests | pytest on `tests/` | Test Explorer shows **all** tests; the lab weeks are red until you build them — expected |
| Formatting | Ruff (format + import sort on save) | Matches CI (`ruff format --check`) |
| Tasks | `Terminal → Run Task…` | setup, doctor, foundation tests, all lab tests, **week N** (prompts for N), chat, check, format |
| Debug | `Run and Debug` | current test file, `agentlab chat`, `agentlab doctor`, capstone demo |
| Validation | Markdown link checking | Catches broken relative links before I do |
| Exclusions | `.venv`, `bin`, `obj`, caches | Search stays fast |

## 2. First open (3 minutes)

1. **File → Open Folder** → `D:\DevRepo\MyProjects\AgentLearning` (not the parent folder — the workspace config lives here).
2. Accept the **recommended extensions** prompt ([`.vscode/extensions.json`](../../.vscode/extensions.json)): Ruff, PowerShell, Markdown All in One, Error Lens, GitLens, Todo Tree, Code Spell Checker.
3. `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv\Scripts\python.exe` (usually auto-detected).
4. `Ctrl+Shift+P` → **Tasks: Run Task** → **AgentLab: doctor**. It should report the placeholder-key failure until you edit `.env`.
5. `Ctrl+Shift+P` → **Python: Configure Tests** → **pytest** → **`tests`** (only if discovery did not start automatically).
6. Open the Testing sidebar; you should see `tests/test_core.py` green (30) and `tests/weekNN` red.

Useful defaults while working a lab:

- **Run the current test file:** open it, press the ▶ gutter icon, or `Ctrl+Shift+P → Tasks: Run Task → AgentLab: week N tests`.
- **Debug a failing test:** open the test file → Run and Debug → *Debug: current test file* → F9 on the assertion.
- **Re-run only the last failure:** Testing sidebar → the red test → rerun.

## 3. If you prefer JetBrains: PyCharm Pro

PyCharm is a legitimate choice (and free with your student licence), especially if you already live in IntelliJ keymaps:

1. Open the folder as a project; set the interpreter to `.venv\Scripts\python.exe`.
2. Mark `agentlab/` as a **Sources Root** (so imports resolve as `agentlab.*`).
3. Settings → Tools → Python Integrated Tools → default test runner **pytest**.
4. Create a pytest run configuration: target `tests`, working directory = repo root, additional arguments `-m week` for lab weeks.
5. Set the formatter to Ruff (plugin) or leave formatting to `.\tasks.ps1 fmt`.

Do **not** use PyCharm's built-in "install package" prompts against this project — dependencies are managed by `uv sync`; let the task runner own the environment.

## 4. AI assistants inside the IDE — a guardrail

This machine already has the **Claude Code** and **ChatGPT/Codex** VS Code extensions. They are excellent tools, and they are also capable of solving every lab for you in seconds, which would defeat the point.

Use this rule:

| Use AI for | Do not use AI for |
|---|---|
| Explaining a failing test or a stack trace | Writing `agentlab/loop/react.py` for you |
| Reviewing your implementation after it is green | Generating the lab before you read the brief |
| "Why does this invariant matter?" | "Make these tests pass" |

Practical setup: create a VS Code **Profile** named *AgentLab Study* with the AI extensions disabled, and switch to it while doing a lab (bottom-left gear → Profiles). Use your normal profile for reading docs and reviewing SendOS code.

## 5. Troubleshooting

| Symptom | Fix |
|---|---|
| "No Python interpreter selected" | `Ctrl+Shift+P` → Python: Select Interpreter → `.venv\Scripts\python.exe`. If `.venv` is missing, run `.\tasks.ps1 setup`. |
| Tests not discovered | Python: Configure Tests → pytest → `tests`; check output panel *Python* for errors. |
| `pytest` runs the wrong Python | Integrated terminal may be outside the venv — the task runner always uses `uv run`, so prefer `Terminal → Run Task`. |
| PowerShell says execution policy blocks scripts | The tasks pass `-ExecutionPolicy Bypass`; if you run `.\tasks.ps1` manually and it is blocked, use `powershell -ExecutionPolicy Bypass -File .\tasks.ps1 ...`. |
| Ruff extension does nothing | Install `charliermarsh.ruff`; the repo also exposes `.\tasks.ps1 fmt` as a fallback. |
| Markdown links flagged | Run `python scripts/check_links.py` — the source of truth for link validity. |
| VS Code is slow / indexing huge folders | Check that `.venv`, `bin`, `obj` are excluded (they are by default in this workspace). |

## 6. VS Code extensions — what is actually useful here

Already installed: Python, Pylance, debugpy, Jupyter, C# Dev Kit, Java pack, Rust, Docker, Claude Code, ChatGPT.

Recommended additions (the workspace prompt will offer them): **Ruff**, **PowerShell**, **Markdown All in One**, **Error Lens**, **GitLens**, **Todo Tree**, **Code Spell Checker**. Skip anything else; extension sprawl is its own productivity tax.

---

**Bottom line:** open the folder in VS Code, accept the extension recommendations, select `.venv`, and use `Terminal → Run Task → AgentLab: week 1 tests`. Rider/Visual Studio stay for SendOS `.NET`; the C# bridge labs in [`dotnet/`](../../dotnet/README.md) build from the terminal either way.
