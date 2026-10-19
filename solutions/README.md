# Solutions

Reference implementations, one directory per week, mirroring the repository root:

```
solutions/week01/agentlab/providers/openai_compat.py
solutions/week02/agentlab/loop/...
solutions/week06/agentlab/orchestrator/...
```

Apply a solution (it copies over your work — this is a last resort):

```powershell
# Windows (PowerShell)
.\tasks.ps1 solution 1
```

```bash
# macOS / Linux
./tasks.sh solution 1
```

## Policy: do not open these until your tests pass

The tests already tell you *what* to build. The solution tells you *how*, which is the part you are training. Use it in exactly three situations:

1. **You are green** — read it to compare designs, not to copy. Ask: what did I do that is more/less general? What invariant did I miss?
2. **You are stuck for more than 90 minutes** on the same failure, *and* you have written down your hypothesis. Read one function, close the file, finish yourself.
3. **You are reviewing** — e.g. before the capstone, or before a SendOS code review, to compare a miniature against the real thing.

## What solutions are not

- They are not the only correct answer. Agent design has many valid shapes; the tests encode the contract, not the design.
- They are not production code. They favour clarity and teaching over throughput, async, and framework conventions.
- They are not complete. Some labs have deliberate gaps marked in `NOTES.md` — those gaps are your stretch exercise.

## Solutions vs your code

Keep your implementation. After comparing, write five bullets in your weekly review:

- What design choice did I make that the reference did not? Is mine better for a reason?
- What did the reference handle that I missed? Was it tested, or accidental?
- Which invariant would I add to the test suite now?
