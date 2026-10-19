# Lab Notes — week NN

> Working notes, not a report. Keep this open in a second pane while you build. Fill it as you go; never reconstruct it afterwards. At the end of the week, the durable parts move into `notes/weekNN-review.md`.

## 1. Brief in one sentence

`labs/weekNN-<slug>/README.md` — what this week makes true in the codebase:

> ______

## 2. Failing tests = the specification

Read the tests **before** the brief. List them and what each one actually demands.

| Test | What it asserts (my words) | Status |
|---|---|---|
| `test_...` | | red |
| `test_...` | | red |

Command: `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux)

## 3. Plan before code (5 minutes, max)

- Files I expect to touch (only the owned module — see `docs/internals/SCAFFOLD-CONTRACT.md`):
  - ______
- Data structures / function signatures I will add: ______
- The one design decision that is hard to reverse: ______

## 4. Hypothesis log

> One line per attempt. Timestamp when you start. This log is how you get unstuck in 20 minutes.

| Time | Hypothesis | Test/command | Result | Kept? |
|---|---|---|---|---|
| | | | | |

## 5. Debugging notebook

For each non-obvious failure:

- **Symptom** (exact message, test name):
- **What I expected**:
- **What the trace/log actually shows**:
- **Narrowest reproduction**:
- **Root cause**:
- **Fix + test that would have caught it**:

## 6. Interface sketch

```
<draw the call path: entry → loop/provider → tool → result → trace>
```

Key invariants (things that must always be true):
1. ______
2. ______

## 7. Decisions made (promote real ones to an ADR)

| Decision | Alternatives considered | Why this one | Reversible? |
|---|---|---|---|
| | | | |

> If it would be expensive to reverse, copy it into `templates/adr.md` and save under `docs/decisions/` (or `notes/adr-*.md`).

## 8. SendOS bridge (3 questions from the brief)

Answer in your own words after reading the mapped C# files.

1. What matches?
2. What does SendOS add or do differently?
3. What would I change, and why?

Files read: ______

## 9. Stretch (only if the gate is already green)

- What I tried:
- Result / abandoned because:
- Worth keeping? yes / no

## 10. Reflection (3 questions — copy answers into the weekly review)

- **Conceptual:** what can I now explain that I could not on Monday?
- **Architectural:** what did this week's design make easy or hard?
- **Transfer:** what will I look for first the next time I read SendOS code?

## 11. Stuck log (20-minute rule)

| Time stuck | What I tried | Asked the tutor? (prompt used) | Answer that unlocked it |
|---|---|---|---|
| | | | |
