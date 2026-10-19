# The Weekly Rhythm — how to spend 8–12 hours well

**Premise:** you have an internship, NUS coursework, and 8–12 hours a week for this. That is enough to finish nine weeks *if* the hours are structured, and not enough if they are not. This document is the operating method; [`CHECKPOINTS.md`](CHECKPOINTS.md) defines the finish line and [`LEARNING-PLAN.md`](LEARNING-PLAN.md) defines the content.

**The one rule:** never trade the gate for reading. A week with 6 hours and green tests beats a week with 12 hours and three unread papers.

---

## 1. Session architecture (the week has three kinds of session)

| Session | When (suggested) | Length | Purpose |
|---|---|---|---|
| **Build A** (Tue 20:00) | Mid-week | 90–120 min | Read failing tests + brief, then implement the smallest failing test |
| **Build B** (Thu 20:00) | Mid-week | 90–120 min | Finish implementation; make the lab artifact run end-to-end |
| **Deep session** (Sat 09:00–13:00) | Weekend | 3–4 h | Integration, theory + paper, SendOS bridge, weekly review |

That is 6–8 hours of protected time; stretch and busy weeks fill the remainder. Both weekday sessions are optional only in the "minimum viable week" (see §8); the Saturday review is never optional.

### Inside a 90-minute block

| Minutes | Activity | Notes |
|---|---|---|
| 0–5 | **Warm-up retrieval** | 5 flashcards from *previous* weeks, closed book. Do not open the laptop code first. |
| 5–10 | **Set the one target** | Write one sentence: "By the end of this block, this test passes / this artifact runs." |
| 10–70 | **Deep work** | Phone in another room, notifications off, one tab group. If stuck >20 min → §6. |
| 70–80 | **Break** | Walk, water, no screens. Breaks are part of the method, not a reward. |
| 80–90 | **Close-out log** | 3 lines in [`../../templates/lab-notes.md`](../../templates/lab-notes.md): what moved, what is next, what confused me. |

**Hard rule:** stop at the timer, not at "done". Stopping mid-problem with a written next step is what makes the next session start fast; finishing by pushing through to hour 3 makes the next session start exhausted.

---

## 2. Retrieval practice (the highest-leverage 10 minutes of your week)

Re-reading and highlight-feeling are the two most popular study techniques and among the least effective. Recalling from memory is what builds durable knowledge — the testing effect is one of the most replicated findings in learning science ([Roediger & Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/); [Dunlosky et al., 2013](https://journals.sagepub.com/doi/10.1177/1529100612453266) — the SAGE link may 403 automated fetches but works in a browser).

Three retrieval rituals, in order of value:

1. **Blank-page recall (weekly, 10 min):** close everything; write the week's mechanism from memory (the loop, the approval state machine, the compaction policy); then open your notes and diff. Gaps are your study list.
2. **Quiz + flashcards (weekly, 15 min):** take `docs/plan/quizzes/weekNN.md` closed book, then run the CSV in Anki. Score below 8/10 means the explain gate fails.
3. **Teach-back (weekly, 10 min):** 150 words, spoken aloud or written, with no notes. If you cannot, the week is not done — this is a gate condition, not a nicety.

**Anti-pattern:** opening the plan and re-reading the week's concepts. That is recognition, not recall, and it is why people "understand" a topic until they have to explain it.

---

## 3. Interleaving (mix, do not block)

Blocked practice (all of one topic, then all of another) feels smoother but transfers worse than interleaved practice. In practice:

- Start every Thursday session with 10 minutes of a **previous** week's quiz or 5 flashcards — mixing retrieval targets.
- In the Saturday session, alternate: 45 min build → 30 min theory → 30 min SendOS bridge. Alternating contexts forces you to re-load each mental model, which is the point.
- When studying evals, compare against security and context: "which of these three would catch a regression the other two miss?"
- Never interleave *new* topics in the same session — interleave review, keep new material blocked.

---

## 4. Spaced repetition schedule

| When | What | Time |
|---|---|---|
| Same day as the lab | Add the week's 5 cards (`docs/plan/flashcards/weekNN.csv`) | 5 min |
| Day 1 | Review new cards + the week's quiz wrong answers | 10 min |
| Day 3 | Review due cards; re-answer 3 wrong quiz questions | 10 min |
| Day 7 (Saturday) | Review due cards; pick 5 random cards from *older* weeks | 10 min |
| Day 21 | Same, plus a blank-page recall of that old week's mechanism | 15 min |

Use Anki (or any SRS) with the CSV import; tags are already `weekNN;topic`. **Never add a card you cannot answer in one sentence** — vague cards train vague recall. If a card is ambiguous, rewrite it.

---

## 5. Timeboxing rules

- **70/20/10.** 70% building, 20% reading, 10% reflection/writing. If reading exceeds 30% of the week's hours, cut it — the reading list is capped deliberately.
- **Read with a question.** Before opening a paper, write the question it must answer. If the paper does not answer it in 20 minutes, close it and note "later".
- **One new tool per week, maximum.** New library, new editor setup and new provider are three separate weeks of cognitive load.
- **Stop at the timer.** A planned 90-minute block that becomes 3 hours steals from the next two sessions.
- **Protect the Saturday block** as if it were a class. It is the only session long enough for integration, theory and the review.

---

## 6. The 20-minute unstuck rule

Stuck is normal; silent stuck is how self-study dies. When you notice you have been stuck for 20 minutes:

1. **Write the question down** in [`../../templates/lab-notes.md`](../../templates/lab-notes.md) §11: what you expected, what happened, what you tried.
2. **Shrink it:** reproduce the failure in the smallest possible test or script. 80% of "stuck" resolves here.
3. **Ask the AI tutor** with the template from START-HERE: week, test name, exact error, what you tried, and "give me a hint, not the answer". Good prompt example: *"Week 2, `test_agent_stops_on_max_steps` fails with `KeyError: 'tool_calls'`. I appended only the assistant content, not the tool_calls message. Hint?"*
4. **If still stuck after another 20 minutes**, ask for the minimal failing example and the concept, then implement it yourself. Save the answer as a flashcard.

**Never** spend 90 minutes on a library quirk. That is not productive struggle; it is a documentation problem, and the tutor is faster.

---

## 7. The weekly review ritual (Saturday, last 60 minutes)

1. Run the gate commands from [`CHECKPOINTS.md`](CHECKPOINTS.md); paste the summary into the review.
2. Fill [`../../templates/weekly-review.md`](../../templates/weekly-review.md) — especially the **failure log** and the **time audit**.
3. Write the 150-word teach-back with no notes.
4. Add 5 flashcards; import them.
5. Update [`PROGRESS.md`](PROGRESS.md): hours, gate status, "what I can now explain".
6. Put the next week's three sessions in the calendar before you close the laptop.
7. Commit: `git add -A && git commit -m "week NN: gate green + review"`.

The review is the only place where the week becomes evidence. Without it, week 9 arrives and you cannot write the portfolio post.

---

## 8. The minimum viable week (fallback)

When the internship explodes or coursework collides — one week in five, realistically — do not skip the week and do not pretend. Do the **minimum viable week** (4–5 hours):

1. **Session 1 (90 min):** read the brief + failing tests; implement the first failing test only.
2. **Session 2 (90 min):** finish until `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux) is green. Nothing else.
3. **Gate (60 min):** revise quiz ×10 + teach-back + 5 flashcards. Skip theory, paper, SendOS bridge, and stretch — but record them as debt in the review.
4. **Emergency 90-minute version** (if even that fails): run the week's tests, fix one test, write one flashcard, log the week as partial in `PROGRESS.md`. A partial week is data; a skipped week with no record is a hole.

**Never** skip the transfer stage for two weeks in a row — the SendOS bridge is the reason this curriculum exists. If you must choose, protect the bridge over the stretch.

---

## 9. Anti-patterns that will cost you the most time

| Anti-pattern | What it looks like | Replacement |
|---|---|---|
| Tutorial rabbit hole | "I'll just watch one more video on LangGraph" | The plan caps reading; frameworks arrive in weeks 6–9 as comparison |
| Note-taking as procrastination | Beautiful notes, no tests | Notes in the review only; code is the artefact |
| Framework shopping | Comparing 5 agent frameworks | Build the loop first; read frameworks after week 6 |
| Tool-hopping | New editor/model/db every week | One tool change per month, max |
| Cramming before the quiz | Re-reading for 40 minutes | 10 minutes of retrieval instead |
| Silent struggle | Stuck for an hour, no log, no question | 20-minute rule, written question, tutor |
| Perfecting the capstone | Polishing UI at 2 a.m. | Ship at 80%: demo + write-up + eval report |

---

## 10. What to measure each week (put it in PROGRESS.md)

- Hours actually spent (not planned).
- Day the week's tests went green (Saturday night is the target).
- Quiz score /10.
- Cards added and cards reviewed.
- One sentence: "I can now explain ______."
- Gate status: green / explain / transfer.

If two weeks in a row show <60% build time or a failing explain gate, stop and fix the method before continuing. The method is the intervention; more hours is usually the wrong fix.

---

## Sources

1. Roediger, H. L., & Karpicke, J. D. (2006). *Test-enhanced learning: Taking memory tests improves long-term retention.* Psychological Science, 17(3), 249–255. https://pubmed.ncbi.nlm.nih.gov/16507066/
2. Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). *Improving students' learning with effective learning techniques.* Psychological Science in the Public Interest, 14(1), 4–58. https://journals.sagepub.com/doi/10.1177/1529100612453266
3. Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). *Distributed practice in verbal recall tasks: A review and quantitative synthesis.* Psychological Bulletin, 132(3), 354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/
4. The Learning Scientists — accessible summaries of retrieval practice, spacing and interleaving: https://www.learningscientists.org/
