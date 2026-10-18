# Learner Profile

> This file tells the AI tutor (and any future reviewer) who it is teaching. Keep it factual and current; it is read at the start of every tutoring session. Update it when constraints or goals change, not weekly.

---

## 1. Identity and background

- **Name:** Terrence (Yaqi) Chen — the repo owner.
- **Current role:** intern on **SendOS**, an enterprise `.NET` agent platform (decision-first runtime, capability catalogue, approval/governance layers, append-only outcome traces, learning loop).
- **Experience:** senior full-stack engineer — **Java/Spring**, **C#/.NET**, **React/TypeScript**, **AWS**. Comfortable with APIs, typed contracts, tests, CI, distributed systems.
- **Education:** NUS ISS graduate diploma; CDUT BSc. Co-author of an **IEEE GNN paper** — so research papers are readable, but ML training experience is not the goal here.
- **Prior LLM experience:** basic — has called LLM APIs, knows the chat-completions shape, no production agent systems built from scratch.
- **Languages:** Chinese (native) and English (professional). Based in **Singapore (SGT, UTC+8)**.

## 2. Goals (why this repo exists)

| # | Goal | Success looks like | Weight |
|---|---|---|---|
| **A** | **Contribute meaningfully to SendOS faster** | Can read `DecisionRuntime`, `ApprovalCheckpoint`, `Send.Model.Adapter` and propose a concrete improvement; ships one reviewed proposal | Highest — compounding |
| **B** | **Be hireable as an AI/agent engineer** | 8 green test suites, traced agent, eval report, capstone demo, architecture write-up, 2 posts | High (output of A+D) |
| **C** | **Build an own agent product** | Weeks 2–8 modules compose into a platform; week 9 ships a UI + real domain workflow | Medium |
| **D** | **Deep technical mastery / research fluency** | From-scratch builds, one must-read paper per week, re-derivation from a blank file at week 10 | High — compounding |

**Conflict rule:** when short on time, protect **A** and **D**. B and C are by-products of doing A and D well.

## 3. Constraints

- **Time:** 8–12 h/week alongside the SendOS internship and NUS coursework. Realistic pattern: Tue 20:00 (2 h), Thu 20:00 (2 h), Sat 09:00–13:00 (3–4 h). Some weeks will be minimum-viable weeks (see [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) §8).
- **Budget:** DeepSeek primary (cheap, high-volume labs), OpenAI secondary (comparison labs). Total model spend target **under $5** for the whole curriculum; `AGENTLAB_RUN_BUDGET_USD=0.50` default stays on.
- **Machine:** Windows 11 + PowerShell 7; Python 3.12 via `uv`. Repo is `D:\DevRepo\MyProjects\AgentLearning`.
- **Context switching:** internship work is `.NET`; the curriculum is Python. The plan deliberately uses Python for learning (sample density) and C# only for the SendOS bridge.

## 4. Working preferences and strengths to exploit

- **Build-first, tests-first.** Learns fastest when a failing test defines the contract. Prefer "read the test, then the brief" over "read the theory, then code".
- **Strong systems intuition.** Already knows typed contracts, retries, budgets, observability, multi-tenancy — the curriculum maps new terms onto those existing models rather than teaching them from zero.
- **Weak spots to watch:** (1) Python fluency is below Java/C# — expect friction with language idioms, not concepts; (2) no prior eval culture experience — week 7 is the highest-risk week; (3) perfectionism on artifacts — ship at 80% (the plan's explicit countermeasure).
- **What not to do:** do not re-teach HTTP, JSON, async basics, Git, or general testing. Do not assume ML math knowledge; explain loss/RL only when week 9/10 requires it.

## 5. Environment facts

| Item | Value |
|---|---|
| Repo root | `D:\DevRepo\MyProjects\AgentLearning` |
| Python | 3.12 (uv-managed) |
| Providers | `DEFAULT_PROVIDER=deepseek` (DeepSeek API); `OPENAI_API_KEY` optional |
| Budget guard | `AGENTLAB_RUN_BUDGET_USD` (default 0.50) — never disable |
| Tests | `.\tasks.ps1 test` (all), `.\tasks.ps1 week NN` (one week) |
| Labs | `labs/weekNN-*/README.md` — the brief |
| Gates | [`CHECKPOINTS.md`](CHECKPOINTS.md) — Green / Explain / Transfer |
| Tracker | [`PROGRESS.md`](PROGRESS.md) — updated every Saturday |

## 6. Confidentiality rules (non-negotiable)

SendOS is proprietary. In this repo and with any external model:

- **Never paste C# source, internal URLs, tenant data, customer names, prompts or schema dumps** from SendOS into a public model chat. Describe mechanisms in your own words.
- The "SendOS bridge" is *reading* + *abstraction* + *your own Python miniature*. It is not a copy-paste exercise.
- If a bridge note needs an example, invent a neutral one (e.g. "a capability registry") and map it privately.
- Do not record `.env` values, API keys or tokens in notes, commits or the portfolio.

---

## 7. How to use the AI tutor

The tutor has the plan, the research and the SendOS concept map. It is most useful as a **reviewer, hint-giver and interrogator** — not as a code generator.

### 7.1 The three modes, and when to use them

| Mode | Use when | Prompt pattern |
|---|---|---|
| **Hint** (default) | You are building and stuck | "Week N, test `X` fails with `Y`. I tried `Z`. Give me one hint, not the answer." |
| **Review** | You have something that works | "Review `agentlab/loop/react.py` against the four failure modes in the week-2 brief. Be adversarial." |
| **Interrogate** | Before a quiz, gate or interview | "Quiz me on week 4 for 10 minutes. One question at a time; wait for my answer, then grade it." |

### 7.2 Rules the tutor should follow with you

1. **Hints before answers.** Escalate: question → concept → pseudocode → minimal example. Never write the lab implementation for you.
2. **Ask for the test and the error**, not the whole file. If you have not run the tests, the first response should be "run them and paste the summary".
3. **Review after attempts, not before.** Design reviews are welcome once code exists.
4. **Name the failure mode.** Every explanation should end with what breaks if the mechanism is absent.
5. **Push back on scope.** If you ask for something outside the current week, the answer is "later, here is the link".
6. **Keep answers short by default.** You can ask for depth; unrequested essays waste your time.

### 7.3 Good prompts (copy these)

- "I'm on week 3. `test_repair_feeds_validation_error` fails with `KeyError: 'error'`. Hint, not answer."
- "Here is my compaction design (6 bullets). Attack it: what context would it lose that matters later?"
- "Grade my teach-back for week 6 against the Explain gate rubric in CHECKPOINTS.md."
- "I have 45 minutes before a lecture. What is the highest-value task given my progress in PROGRESS.md?"
- "Explain the difference between my week-6 approval binding and SendOS's, using the abstraction, not their code."
- "Quiz me on week 7, focus on evals and judge calibration, 10 minutes."

### 7.4 Bad prompts (avoid)

| Prompt | Why it fails |
|---|---|
| "Write the week 4 lab for me." | The tests are the learning; you will not be able to defend it in review or interview. |
| "Fix this error: [whole traceback]" | Without the test name and what you tried, the tutor guesses; you learn less. |
| "Explain everything about agents." | Too broad; you will get a summary you could have read, and it will not stick. |
| "Is this good?" (no evidence) | Ask against a rubric or eval number instead. |
| Pasting SendOS code | Confidentiality breach; also the abstraction is what transfers. |

### 7.5 Session hygiene

- Start each tutoring session by stating week, goal and what you tried.
- End by writing **one sentence** in the lab notes: what you now understand that you did not at the start.
- If the tutor gives you an answer you asked for against these rules, convert it into a flashcard and a test — do not just apply it.
- Keep sessions under 45 minutes; long tutoring sessions crowd out the building they are meant to support.
