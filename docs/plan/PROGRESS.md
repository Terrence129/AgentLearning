# Progress Tracker

**Started:** 2026-10-18 · **Plan:** 9 working weeks + 1 buffer (≈95–115 h) · **Method:** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) · **Gates:** [`CHECKPOINTS.md`](CHECKPOINTS.md)

**Update ritual (Saturday, 10 minutes):** fill the row, tick the week's checklist, add the one-sentence "what I can now explain", and log any debt. Do not edit past rows after the week closes — the history is the evidence.

---

## 1. Status at a glance

| Wk | Dates | Theme | Planned h | Actual h | G | E | T | Artifact | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2026-10-18 | Setup & baseline | 3 | | ☐ | ☐ | — | baseline note | |
| 1 | 2026-10-19 → 10-25 | Model & provider seam | 8–10 | | ☐ | ☐ | ☐ | `chat` streams + cost | |
| 2 | 2026-10-26 → 11-01 | Tools & the agent loop | 10–12 | | ☐ | ☐ | ☐ | 5 golden tasks + trace | |
| 3 | 2026-11-02 → 11-08 | Structured output | 8–10 | | ☐ | ☐ | ☐ | `analyze() -> Decision` | |
| 4 | 2026-11-09 → 11-15 | Context & memory | 10–12 | | ☐ | ☐ | ☐ | 20-turn retention run | |
| 5 | 2026-11-16 → 11-22 | MCP | 8–10 | | ☐ | ☐ | ☐ | server + client + checklist | |
| 6 | 2026-11-23 → 11-29 | Planning & approval | 10–12 | | ☐ | ☐ | ☐ | mini-Squad + approval test | |
| 7 | 2026-11-30 → 12-06 | Evals & observability | 8–10 | | ☐ | ☐ | ☐ | ≥ 25-case suite + report | |
| 8 | 2026-12-07 → 12-13 | Security & governance | 8–10 | | ☐ | ☐ | ☐ | attack suite + threat model | |
| 9 | 2026-12-14 → 12-20 | Capstone: Mini-SendOS | 12–16 | | ☐ | ☐ | ☐ | demo + eval report + write-up | |
| 10 | 2026-12-21 → 12-27 | Consolidation & leverage | 4–6 | | ☐ | ☐ | ☐ | portfolio + interview rehearsal | |
| buf | 2026-12-28 → 2027-01-03 | Holiday buffer / overflow | — | | | | | | |

**Totals:** planned ____ / 95–115 · actual ____ · weeks on schedule ____/10 · debt items ____

> Legend: **G** = tests green, **E** = quiz + teach-back, **T** = SendOS transfer. ☑ = passed, ☐ = not yet, ✗ = failed (see debt log).

---

## 2. Weekly checklists

Copy one block per week when the week starts; tick during the Saturday review.

### Week 0 — Setup & baseline

- [ ] `.\tasks.ps1 setup` (Windows) / `./tasks.sh setup` (macOS/Linux) completed; `doctor` clean
- [ ] `.env` has `DEFAULT_PROVIDER=deepseek` + `DEEPSEEK_API_KEY`
- [ ] Foundation tests green; week tests red (expected)
- [ ] One live call recorded with tokens / latency / cost in `notes/week00-baseline.md`
- [ ] Baseline answers written (token, streaming, retry failure)
- [ ] Three sessions in the calendar

### Week NN — <theme>

- [ ] Brief read (`labs/weekNN-*/README.md`)
- [ ] Failing tests read **before** coding
- [ ] Build complete against the owned module only
- [ ] `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux) green
- [ ] Quiz NN taken closed book: ____/10
- [ ] 150-word teach-back written without notes
- [ ] SendOS bridge note (matches / differs / would change)
- [ ] 5 flashcards added to `docs/plan/flashcards/weekNN.csv`
- [ ] `notes/weekNN-review.md` filled from [`../../templates/weekly-review.md`](../../templates/weekly-review.md)
- [ ] `git commit -m "week NN: gate green + review"`
- [ ] Next week's three sessions in the calendar

---

## 3. What I can now explain (cumulative)

Tick only when you can say it **aloud, without notes, in under 90 seconds**. This is the interview asset.

| Wk | Claim | ☑ | Date checked |
|---|---|---|---|
| 1 | Why retries, SSE delta assembly and usage accounting live in the provider adapter | ☐ | |
| 2 | How the loop terminates, where the budget check goes, and why tool errors are observations | ☐ | |
| 3 | Why JSON mode is not structured output, and how bounded repair + failure metrics work | ☐ | |
| 4 | How compaction, priority classes and a retention test keep a long task coherent | ☐ | |
| 5 | What MCP standardises, and the trust model that makes it safe | ☐ | |
| 6 | Why approval must bind to an action hash and an authority snapshot, and what at-most-once requires | ☐ | |
| 7 | How to build an eval suite that catches a regression before production (pass@1 vs pass^k) | ☐ | |
| 8 | Why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius | ☐ | |
| 9 | The full request path from ingress to audit row, with every failure mode and control | ☐ | |
| 10 | The four runtime duties, and how SendOS maps onto them | ☐ | |

---

## 4. Debt log (gates carried, stretch skipped, theory deferred)

| Opened | Week | Item | Type (gate / stretch / theory) | Clear by | Status |
|---|---|---|---|---|---|
| | | | | | |

**Rule:** one gate debt maximum at a time, cleared within 7 days (see [`CHECKPOINTS.md`](CHECKPOINTS.md) §4). Stretch and theory debt may be dropped — record it and move on.

---

## 5. Metrics (fill monthly, not weekly)

| Month | Hours | Weeks green | Quizzes ≥ 8 | Cards added | Cards reviewed | Artifacts shipped | Cost spent ($) |
|---|---|---|---|---|---|---|---|
| Oct 2026 | | | | | | | |
| Nov 2026 | | | | | | | |
| Dec 2026 | | | | | | | |

**Health checks:** build time ≥ 60% of total · no week with two failed gates · cost under $5 total · every week has a review file and a commit.

---

## 6. Session log (optional but useful for the portfolio)

| Date | Session | Minutes | What moved | Blocked on |
|---|---|---|---|---|
| | | | | |

---

## 7. End-of-course evidence checklist (week 10)

- [ ] 9 weekly reviews in `notes/`, each with a teach-back
- [ ] 8 green week test suites (+ capstone)
- [ ] Flashcards imported: ≥ 140 cards reviewed at least twice
- [ ] Eval report with baseline, pass^k, judge agreement, failure taxonomy
- [ ] Capstone demo script runs offline; 5-minute recording exists
- [ ] `projects/portfolio/WRITEUP.md` complete
- [ ] Two deep-dive posts drafted
- [ ] One-page SendOS improvement proposal reviewed by a senior engineer
- [ ] All 30 interview questions answered aloud at least once
- [ ] Re-derivation exercises done from a blank file
