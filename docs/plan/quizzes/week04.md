# Week 4 Quiz — Context Engineering and Memory

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** "Context rot" means:

- A) Old messages are deleted by the provider
- B) Recall/accuracy degrades as context length grows, even within the advertised window
- C) Cached prompts expire
- D) The model forgets its system prompt after 10 turns

**Q2.** What is the correct ordering of context priority classes (highest first)?

- A) Recent turns > observations > task state > pinned constraints
- B) Pinned constraints > task state > recent turns > observations > history
- C) Observations > history > task state > pinned constraints
- D) All classes are equal; drop the oldest

**Q3.** Compaction is best described as:

- A) Deleting the system prompt to save tokens
- B) Summarising old turns into a bounded carry-forward note and continuing from it
- C) Increasing the context window via a bigger model
- D) Moving messages to a vector database

**Q4.** Which memory type stores "customer X is on plan Y, verified on 2026-08-01"?

- A) Working memory
- B) Episodic memory
- C) Semantic memory with provenance
- D) Prompt cache

**Q5.** For a code repository, which retrieval strategy is often better than embeddings?

- A) Larger context windows
- B) Agentic search with `grep`/`glob`/file trees
- C) Fine-tuning on the repo
- D) Compaction

**Q6.** What is a "retention test"?

- A) A test that the vector store persists across restarts
- B) A test asserting that pinned constraints survive compaction at a target rate
- C) A test that the model retains its API key
- D) A latency benchmark for retrieval

## Part B — Short answer (3 questions)

**Q7.** Design the retention test for the week-4 lab: what do you pin, what do you measure, and what threshold do you assert?

**Q8.** Give one case where adding memory makes the system **worse**, and explain the mechanism.

**Q9.** Why do sub-agents help with context limits even though each sub-agent may read far more tokens than the lead agent?

## Part C — Spot the bug (1 question)

**Q10.** This compactor runs when the token estimate exceeds the budget. Identify **three** defects.

```python
def compact(messages, budget):
    if estimate_tokens(messages) > budget:
        summary = provider.complete(
            [{"role": "user", "content": "Summarize this conversation: " + str(messages)}]
        ).content
        return [{"role": "system", "content": summary}]
    return messages
```

---

## Answers and explanations

**Q1 — B.** Attention degrades before the hard limit is reached — the "attention budget" is finite. Bigger windows reduce but do not remove the effect.

**Q2 — B.** Pinned constraints (safety, task definition, approvals) outrank everything; task state next; recent turns and observations are cheap to regenerate. Dropping the oldest is a heuristic, not a policy.

**Q3 — B.** Compaction distils the window into a bounded note that preserves decisions, open problems and constraints, then restarts from it. It is lossy by design and must be tested.

**Q4 — C.** Facts with provenance are semantic memory; "what happened in run 12" is episodic; the scratchpad is working memory.

**Q5 — B.** Files are structured knowledge; path names, directories and `grep` give fresh, cheap, explainable retrieval without index staleness.

**Q6 — B.** It converts "seems to remember" into a measured guarantee — the lab requires ≥ 90% of pinned constraints surviving.

**Q7 — model answer.** Pin a set of constraints (e.g. "write actions require approval", "budget is $0.20", "output is a Decision union") and a task-state tuple (current goal, open subgoal, key ids). Run the long task through at least one compaction, then assert that every pinned item is still present (verbatim or semantically) in the post-compaction context, and that the task still completes. Threshold: ≥ 90% of pinned items retained, and 100% of safety-critical constraints.

**Q8 — model answer.** Long-lived memory of stale facts: a remembered preference or price from months ago is retrieved with high similarity and overrides fresher evidence, so the agent acts on outdated information. The mechanism is retrieval confidence without freshness/provenance weighting. Also: memory that leaks across tenants is a security failure, not a quality one.

**Q9 — model answer.** The lead agent's window stays small: sub-agents absorb the large exploratory reads and return condensed artifacts (often 1–2k tokens). Total tokens consumed may rise, but the lead's context stays clean and its attention budget is spent on synthesis rather than on raw data.

**Q10 — model answer.** (1) It drops the system prompt and all pinned constraints/approval state — the run loses its safety and task definition. (2) It serialises the whole conversation with `str(messages)` (huge, and usually non-JSON-safe) instead of a structured, bounded summary of what matters. (3) There is no bounded output, no retention check, and no trigger for pruning stale tool outputs; also no cost accounting for the compaction call itself. A correct version preserves pinned items explicitly, summarises with a structured prompt, bounds the summary length, and asserts retention.
