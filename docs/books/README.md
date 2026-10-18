# Bookshelf

Companion books that support the curriculum. A book is **reference material**, not a track: the labs and tests in this repo remain the source of truth for what you can do.

| Book | Edition | Verdict | Role in this repo |
|---|---|---|---|
| [*AI Agents in Depth: Design Principles and Engineering Practice*](ai-agents-in-depth/README.md) — Bojie Li (李博杰) | v2.0, 2026-09-23 · EN + 中文 | **Highly useful — adopt as the companion textbook** | Deep theory + 109 runnable experiments that complement the labs. Mapped week-by-week in [CHAPTER-MAP.md](ai-agents-in-depth/CHAPTER-MAP.md). |
| *AI Engineering* — Chip Huyen | 2025 | Useful, paywalled | Systems-level context; chapters 6–9 overlap weeks 3–9. Listed in [research 04 §F](../research/04-learning-resources.md). |
| 《Hello-Agents》 (Datawhale) | 2026, free | Useful, Chinese-first | Alternative hands-on track; see [research 04 §G](../research/04-learning-resources.md). Not integrated (overlaps this repo's labs). |

## Policy

- **Books are optional and time-boxed.** Every reading assignment in the plan is capped; a book must never displace a lab.
- **PDFs are kept locally, not committed.** Book binaries are large and independently versioned. They are git-ignored under `docs/books/**/*.pdf`; the official download links live in each book's README.
- **One book at a time.** Reading four books in parallel is the most common form of productive procrastination.
- **Books are versioned artifacts.** Record the edition you read; when a book and a primary source disagree, prefer the primary source and note it.

## Adding a book

Create `docs/books/<slug>/` with:

1. `README.md` — metadata, verdict, strengths, gaps, how to use, official link.
2. `CHAPTER-MAP.md` — chapter → week/lab mapping, reading paths, selected exercises.
3. The local file(s), which stay git-ignored.

Then link it from the root [README](../../README.md) and from [docs/research/04-learning-resources.md](../research/04-learning-resources.md).
