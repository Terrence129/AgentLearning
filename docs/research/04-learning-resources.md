# 04 — Learning Resources: A Verified, Ranked Map for Agent Engineering

**Compiled:** 2026-10-18 · **Access date for every link:** 2026-10-18
**Audience:** senior full-stack engineer (Java / C# / React / AWS), minimal prior LLM-app experience, ~6 h/week alongside an internship and coursework, working on an enterprise .NET agent platform, Chinese speaker based in Singapore.
**Verification:** every item below was status-checked on 2026-10-18 (HTTP 200 unless flagged); the 15 highest-value links were additionally fetched with content read (`✅`; a few are JS-rendered shells where only existence/HTTP status could be confirmed). Items marked `⚠️` resolve only after a redirect; `❌` is dead; `🔒` is paywalled or bot-blocked. See §J for the full ledger.

## 2026 state of play (read this first, ~10 min)

Three shifts should shape what you learn. (1) **Harnesses beat frameworks**: the durable skill is owning the loop, context, state and tools — not memorising a framework's API. Anthropic's own engineers now write about *harnesses* as the unit of design and even ship a "meta-harness" ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), updated with a 2026 note; [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents), 2026-04-08). (2) **Context engineering is the craft**: compaction, note-taking, just-in-time retrieval and sub-agents ([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), 2025-09-29). (3) **MCP is infrastructure**: the spec is now versioned and dated ([MCP docs, spec 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)), and both .NET and Python SDKs are first-class, which matters directly for your platform.

For your situation the highest-leverage path is **Python to learn concepts → C#/.NET Agent Framework to ship**. Learn the concepts in Python first (sample density is 10× higher), then map them to [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) and the [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) — days of work, not months.

---

## A. Ten-week self-study track (~63 h core + ~8 h reading buffer)

Designed for **6 h/week** with one heavier capstone week. Weeks 4 and 9 are the flexible ones: split either across two weeks to stretch to 12 weeks, or drop Week 9 and merge 6+7 to compress to 8 weeks.

| Wk | Focus | Hrs | Concrete output (do, don't watch) | Primary sources |
|----|-------|-----|-----------------------------------|-----------------|
| 1 | Mental model + a loop from scratch | 6 | 80-line Python ReAct agent: raw chat-completions API, 3 tools, `while` loop, structured tool calls, max-iteration guard. No framework. | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents); [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html) |
| 2 | Tools, schemas, MCP | 6 | Wrap two internal APIs as tools; write descriptions to the "junior-dev docstring" standard; build a small MCP server and call it from Claude Desktop or VS Code. | [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents); [MCP docs](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro); [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) |
| 3 | Context engineering + retrieval | 7 | Agentic search over a repo/DB with `grep`/SQL tools instead of a vector DB; add a "just-in-time" file reader; measure tokens per task. | [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) |
| 4 | Evals + observability (**do not skip**) | 7 | 20-case golden set for week-1 agent, LLM-as-judge rubric, trace logging, pass-rate dashboard; fail-then-fix one regression. | [Hamel Husain — Your AI product needs evals](https://hamel.dev/blog/posts/evals/); [Inspect](https://inspect.aisi.org.uk/); [Langfuse](https://langfuse.com/) |
| 5 | Memory & long-horizon tasks | 6 | Add compaction + a `NOTES.md`/progress-file memory; run a 3-session task and show continuity after context reset. | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [MemGPT paper](https://arxiv.org/abs/2310.08560); [Letta docs](https://docs.letta.com/) |
| 6 | Multi-agent & orchestration | 6 | Orchestrator + 2 workers with a hard budget; compare against a single agent on the same eval set; write down where multi-agent lost. | [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system); [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| 7 | Coding & computer-use agents (security) | 6 | Read SWE-agent's ACI; run a coding agent in a throwaway container; demonstrate one prompt-injection attack and one mitigation (credential isolation, allow-list). | [SWE-agent](https://arxiv.org/abs/2405.15793); [SWE-agent repo](https://github.com/SWE-agent/SWE-agent); [OpenHands](https://github.com/All-Hands-AI/OpenHands) |
| 8 | Production hardening on .NET + AWS | 6 | Port week-1 agent to Microsoft Agent Framework (C#): middleware, telemetry, human approval gate, MCP hosted tool; plan AWS deployment surface. | [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview); [Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/); [.NET AI docs](https://learn.microsoft.com/en-us/dotnet/ai/) |
| 9 | Model layer: RL, fine-tuning, DSPy (optional) | 5 | One-page decision memo: when to fine-tune vs prompt vs nothing; run one DSPy or prompt-optimisation experiment. | [Agentic RL survey](https://arxiv.org/abs/2509.02547); [DSPy](https://github.com/stanfordnlp/dspy); [ACE paper](https://arxiv.org/abs/2510.04618) |
| 10 | Capstone + write-up | 8 | One agent that removes real drudgery from your internship (e.g. ticket triage, PR-review checklist); eval report + cost/latency numbers + a 1,000-word post. | Everything above; [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) ch. on agents/evals 🔒 |

**Pacing rules that matter more than the schedule:** cap passive video at 30% of each week; every week ends with a runnable artefact; keep a single `notes/` repo of traces and failures — that repo becomes your interview portfolio. If you fall behind, cut Week 9 first, then shrink Week 6; never cut Week 4 (evals are the actual job).

---

## B. Courses (ranked, with duration / cost / prerequisites)

| Course | Provider | Duration | Cost | Prereqs | Verdict | Link |
|--------|----------|----------|------|---------|---------|------|
| **Agentic AI** (Andrew Ng) | DeepLearning.AI | 9 h 55 m, intermediate | Free to audit; paid certificate/Pro | Confident Python | **Best single structured intro.** Modernised version of the old 4-course agent series; do the notebooks, skip the hype framing. | [Course](https://www.deeplearning.ai/courses/agentic-ai/) ⚠️ |
| **AI Agents Course** | Hugging Face | 4 units + final project, ~20–30 h (est.) | Free; optional certificate | Python + basic LLM concepts | **Best hands-on fundamentals.** Unit 1 implements the loop by hand; then smolagents / LlamaIndex / LangGraph. Do Units 1–2 + bonus evaluation unit. | [HF Agents Course](https://huggingface.co/learn/agents-course) ✅ |
| **MCP Course** | Hugging Face | ~6–10 h (est.) | Free | Python or TS | **Best free MCP end-to-end.** Pairs directly with the [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) for your platform work. | [HF MCP Course](https://huggingface.co/learn/mcp-course) |
| **AI Agents for Beginners** (18 lessons) | Microsoft | ~10–15 h | Free | Python or C# | Most enterprise-flavoured free curriculum; strong on tool use, agentic RAG, and MCP. Cherry-pick lessons 1–4, MCP, and multi-agent. | [Repo](https://github.com/microsoft/ai-agents-for-beginners) ✅ |
| **Microsoft Agent Framework docs + tutorials** | Microsoft Learn | Self-paced | Free | C#/.NET | **Required for your platform.** The official successor to Semantic Kernel + AutoGen, with workflows, middleware, telemetry, MCP, and Python/Go parity. Last updated 2026-08-25. | [Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) ✅ · [Tutorials](https://learn.microsoft.com/en-us/agent-framework/tutorials/overview) |
| **LLM Agents MOOC** (Dawn Song, UC Berkeley) | Berkeley RDI | 12 × ~2 h lectures + labs | Free (latest iteration Spring 2025; certificates closed) | Basic ML helps | Best research-grade survey, guest lectures from OpenAI/Anthropic/DeepMind/CMU. **Selective**: reasoning, tool use, SWE agents, evaluation. No newer cohort is published — the site redirects to Spring 2025. | [Spring 2025](https://llmagents-learning.org/sp25) · [Fall 2024 archive](https://llmagents-learning.org/f24) ✅ |
| **Claude Academy / Anthropic courses** | Anthropic | 1–5 h per course | Free | API basics | Vendor-authoritative and the most current material on Agent SDK, Claude Code, MCP and tool design. Start with the Agent SDK track. | [academy.claude.com](https://academy.claude.com) · [Agent SDK docs](https://platform.claude.com/docs/en/agent-sdk/overview) |
| **Introduction to LangGraph** | LangChain Academy | ~6–8 h | Free | Python | Only worth it if you choose LangGraph; best explanation of checkpointing/state graphs. Otherwise skip — the concepts are in the essays. | [Course](https://academy.langchain.com/courses/intro-to-langgraph) · [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| **Google Agent Development Kit (ADK)** | Google | Self-paced codelabs | Free | Python | Contrast framework; only if your team evaluates it. Good reference for tool/agent config in YAML-and-code style. | [ADK docs](https://google.github.io/adk-docs/) · [Repo](https://github.com/google/adk-python) |
| **COS 597R: Deep Dive into LLMs** | Princeton | Archived seminar | Free | Stronger math/ML | Optional, research-oriented, **not agent-specific**. Useful only for model-level intuition. | [Course site](https://princeton-cos597r.github.io/) |
| **CS 886: Multiagent Systems** | U. Waterloo | Archived seminar (Winter 2025) | Free | Classical MAS theory | Optional. Classical multi-agent foundations (coordination, game theory); does not cover LLM agents. | [Course site](https://cs.uwaterloo.ca/~klarson/teaching/W25-886/) |

**Note on .NET parity:** every course above is taught in Python, which is correct for learning. For your day job, the mapping to keep in mind is Agent Framework (`Microsoft.Agents.AI`) + `ModelContextProtocol` C# SDK + OpenTelemetry, and Anthropic's [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) if your platform is Claude-based.

---

## C. Canonical essays and blog posts (with dates and "why read it")

| Date | Piece | Author / org | Why read it | Link |
|------|-------|--------------|-------------|------|
| 2024-12-19 (2026 update note) | Building effective agents | Anthropic | The one essay that gives you the shared vocabulary: workflows vs agents, prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer, and ACI/tool-design appendix. | [Anthropic](https://www.anthropic.com/engineering/building-effective-agents) ✅ |
| 2025-09-29 | Effective context engineering for AI agents | Anthropic | Reframes prompting as attention-budget management; the clearest treatment of compaction, structured note-taking and sub-agent context isolation. | [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) ✅ |
| 2025-06 (approx.) | How we built our multi-agent research system | Anthropic | Rare honest production post: token economics, orchestrator-worker design, eval of a non-deterministic research agent, and where multi-agent fails. | [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 2025-09 | Writing effective tools for agents — with agents | Anthropic | Tool definitions are prompts: naming, token-efficient returns, error surfaces, and the write-tests-for-tools loop. Directly applicable to .NET tool plugins. | [Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) |
| 2025-11-26 | Effective harnesses for long-running agents | Anthropic | The best practical answer to "how do I make an agent work across many context windows": initializer agent, feature-list JSON, progress file, git as memory. | [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) ✅ |
| 2026-04-08 | Scaling Managed Agents: decoupling the brain from the hands | Anthropic | Most advanced 2026 architecture writing: session / harness / sandbox as interfaces, stateless harnesses, credential isolation from the sandbox. Read after Week 7. | [Anthropic](https://www.anthropic.com/engineering/managed-agents) ✅ |
| 2025 | A practical guide to building agents (PDF) | OpenAI | Vendor-neutral-ish playbook: single vs multi-agent, guardrails, human-in-the-loop gates, and a useful "when not to build an agent" section. PDF only. | [OpenAI guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) |
| 2025 | 12-Factor Agents | Dex Horthy / HumanLayer | The production checklist your enterprise reviewers will implicitly want: own your prompts, context window, control flow and state; tools as structured outputs; compact errors; small focused agents; stateless reducer. | [Repo](https://github.com/humanlayer/12-factor-agents) ✅ |
| 2025-01-07 | Agents | Chip Huyen | The sober systems view: agent taxonomy, planning/feedback/failure modes, cost and latency budgets. The antidote to demo-driven enthusiasm. | [Huyenchip.com](https://huyenchip.com/2025/01/07/agents.html) |
| 2023-06-23 | LLM Powered Autonomous Agents | Lilian Weng | Still the cleanest conceptual decomposition (planning, memory, tool use) and the origin of many interview questions. Read once, skim later. | [Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/) |
| 2024-03 | Your AI product needs evals | Hamel Husain | Turns "vibes" into unit tests: assertions, LLM-as-judge, trace review. The single highest-ROI post for a senior engineer entering this field. | [Hamel.dev](https://hamel.dev/blog/posts/evals/) |
| 2023-07 | Patterns for building LLM-based systems & products | Eugene Yan | RAG, guardrails, evaluation, cost/latency trade-offs in system-design vocabulary you already own. | [Eugeneyan.com](https://eugeneyan.com/writing/llm-patterns/) |
| 2025 | Agents tag / "agents are LLMs using tools in a loop" | Simon Willison | Sharp, sceptical, frequently updated; the best filter for hype. Start from the tag page rather than any single post. | [Tag page](https://simonwillison.net/tags/agents/) |
| 2025 | Code execution with MCP | Anthropic | 2025–2026 pattern: let the agent write code that calls MCP tools instead of piping every tool result through context. Big token savings; pairs with Week 3. | [Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp) |

---

## D. Papers (must-read vs optional)

| Paper | Year / venue | Status | One-line contribution | Link |
|-------|--------------|--------|-----------------------|------|
| ReAct: Synergizing Reasoning and Acting | 2022 / ICLR 2023 | **Must** | Interleaved thought→action→observation; the loop every agent still runs. | [arXiv 2210.03629](https://arxiv.org/abs/2210.03629) |
| Toolformer | 2023 / NeurIPS 2023 | Optional | Self-supervised teaching of API calls; historical origin of "tools as tokens". | [arXiv 2302.04761](https://arxiv.org/abs/2302.04761) |
| Reflexion | 2023 / NeurIPS 2023 | Optional | Verbal self-reflection as memory; explains why retry-with-critique works. | [arXiv 2303.11366](https://arxiv.org/abs/2303.11366) |
| MemGPT: LLMs as Operating Systems | 2023 | **Must** | Memory hierarchy + paging for context; the intellectual root of Letta and most "agent memory" products. | [arXiv 2310.08560](https://arxiv.org/abs/2310.08560) |
| Generative Agents | 2023 / UIST 2023 | Optional | Memory stream + reflection + planning; the simulation paper that popularised agent societies. | [arXiv 2304.03442](https://arxiv.org/abs/2304.03442) |
| AutoGen | 2023 | Optional | Multi-agent conversation as a programming model; useful history now that it merged into Agent Framework. | [arXiv 2308.08155](https://arxiv.org/abs/2308.08155) |
| ToolLLM | 2023 / ICLR 2024 | Optional | 16k real APIs + tool-retrieval; why tool selection degrades with large toolsets. | [arXiv 2307.16789](https://arxiv.org/abs/2307.16789) |
| SWE-agent (ACI) | 2024 / NeurIPS 2024 | **Must** | Agent-computer interface design changes benchmark scores more than model swaps — the core lesson for platform builders. | [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| AgentBench | 2023 / ICLR 2024 | Optional | First broad multi-environment agent benchmark; good failure taxonomy. | [arXiv 2308.03688](https://arxiv.org/abs/2308.03688) |
| GAIA | 2023 / ICLR 2024 | **Must** | Real assistant tasks that are easy for humans, hard for agents; the benchmark to quote when someone claims AGI. | [arXiv 2311.12983](https://arxiv.org/abs/2311.12983) |
| τ-bench (TAU-bench) | 2024 | **Must** | Tool-agent-user interaction with domain policies — the closest public analogue to enterprise support agents. | [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) |
| SWE-bench | 2023 / ICLR 2024 | **Must** | Real GitHub issues + tests; taught the field that verifiable tasks are where agents win. | [arXiv 2310.06770](https://arxiv.org/abs/2310.06770) |
| CodeAct | 2024 / ICML 2024 | Optional | Executable Python actions beat JSON tool calls on many agent tasks; justifies code-mode tools. | [arXiv 2402.01030](https://arxiv.org/abs/2402.01030) |
| Agentic Context Engineering (ACE) | 2025, ICLR 2026 | **Must** | Treat context as an evolving playbook; +10.6% on agents and +8.6% on finance over strong baselines, without labelled supervision. Updated v3, 2026-03. | [arXiv 2510.04618](https://arxiv.org/abs/2510.04618) ✅ |
| A Survey of Context Engineering for LLMs | 2025 | Optional (reference) | Taxonomy to look things up in rather than read end-to-end. | [arXiv 2507.13334](https://arxiv.org/abs/2507.13334) |
| The Landscape of Agentic RL for LLMs | 2025 | Optional | Where RL-for-agents stands; enough to talk to ML teams credibly. | [arXiv 2509.02547](https://arxiv.org/abs/2509.02547) |
| Mem0 | 2025 | Optional | Production memory extraction/consolidation with latency/cost numbers. | [arXiv 2504.19413](https://arxiv.org/abs/2504.19413) |
| A-MEM: Agentic Memory | 2025 | Optional | Zettelkasten-style linked memory notes; contrasts with flat vector memory. | [arXiv 2502.12110](https://arxiv.org/abs/2502.12110) |
| τ²-bench | 2025 | Optional | Dual-control conversational agents (both sides act); next-gen telecom-style domains. | [arXiv 2506.07982](https://arxiv.org/abs/2506.07982) |
| WebArena | 2023 | Optional | Reproducible web environments for agents; useful for eval design inspiration. | [arXiv 2307.13854](https://arxiv.org/abs/2307.13854) |
| OSWorld | 2024 | Optional | Real-OS computer-use benchmark; calibrates how far computer-use agents actually are. | [arXiv 2404.07972](https://arxiv.org/abs/2404.07972) |

**Reading strategy:** read the four *Must* papers from 2022–2024 in Week 1–2 (they are short), then SWE-agent + τ-bench in Week 4 when you build evals. ACE is the one 2025–2026 paper to read closely — it is the current best mental model for context.

---

## E. Codebases to read or run (what to look at inside)

| Repo | Lang | What to look at inside | How to use it | Link |
|------|------|------------------------|---------------|------|
| Anthropic Cookbook · `patterns/agents` | Python | Minimal implementations of prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer — a few files each. | **Read** in Week 1; copy the patterns into your own loop. | [Repo path](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) |
| OpenAI Cookbook | Python | Tool-calling recipes, structured outputs, evals notebooks. | **Run** selectively; ignore the product-launch notebooks. | [Repo](https://github.com/openai/openai-cookbook) |
| smolagents | Python | A ~1k-line agent core: `CodeAgent`, tool decorators, executor, memory. The best "read the whole thing" agent codebase. | **Read end-to-end** in Week 2. | [Repo](https://github.com/huggingface/smolagents) |
| 12-factor-agents | Python/TS | Reference implementations showing pause/resume, human-in-the-loop tool calls, and stateless reducers. | **Run** the human-approval example in Week 8. | [Repo](https://github.com/humanlayer/12-factor-agents) |
| MCP Python SDK + Servers | Python | Server primitives (tools/resources/prompts), transports, and reference servers (`filesystem`, `git`) as tool-design exemplars. | **Run** in Week 2; port one server to C#. | [SDK](https://github.com/modelcontextprotocol/python-sdk) · [Servers](https://github.com/modelcontextprotocol/servers) |
| MCP C# SDK | C# | Attribute-based tool declaration, DI integration, stdio/HTTP transports. | **Build** your enterprise server with it (Week 8). | [Repo](https://github.com/modelcontextprotocol/csharp-sdk) |
| Microsoft Agent Framework | C#/Python/Go | `AIAgent` abstraction, agent sessions, middleware/filters, workflows, MCP integration, harness agent. | **Port** your Week 1 agent in Week 8. | [Repo](https://github.com/microsoft/agent-framework) |
| SWE-agent | Python | ACI implementation: view/edit commands, search, guardrails, trajectory format. | **Read** `agent/` + config in Week 7. | [Repo](https://github.com/SWE-agent/SWE-agent) |
| OpenHands | Python | Event-stream architecture, runtime sandbox/container isolation, state management, delegation. | **Read** architecture docs, not the whole codebase. | [Repo](https://github.com/All-Hands-AI/OpenHands) · [Paper](https://arxiv.org/abs/2407.16741) |
| Aider | Python | Repo map (tree-sitter ranking), edit formats (whole-file vs diff), git integration. | **Read** the repo-map module — great lesson in context selection. | [Repo](https://github.com/Aider-AI/aider) |
| LangGraph | Python/TS | Graph state, checkpointing, interrupts, subgraphs. | **Read** only if you adopt it. | [Repo](https://github.com/langchain-ai/langgraph) · [Docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| OpenAI Agents SDK | Python | Minimal handoff/guardrail/tracing primitives; readable in an afternoon. | **Read** for API design taste. | [Repo](https://github.com/openai/openai-agents-python) |
| HelloAgents (中文) | Python | From-scratch framework written for teaching; mirrors the Hello-Agents book chapters. | **Run** alongside the Chinese course. | [Repo](https://github.com/jjyaoao/helloagents) |
| Inspect (UK AISI) | Python | Serious eval framework: datasets, solvers, scorers, log viewer. | **Adopt** for Week 4 evals if you want rigour. | [Docs](https://inspect.aisi.org.uk/) · [Repo](https://github.com/UKGovernmentBEIS/inspect_ai) |
| Langfuse / Phoenix | Python/TS | Tracing, sessions, prompt management, eval scores. | **Instrument** one agent; traces are your debugging superpower. | [Langfuse](https://langfuse.com/) · [Phoenix](https://github.com/Arize-ai/phoenix) |

**Anti-pattern to avoid:** cloning 5 agent frameworks and reading none. Read **smolagents** fully, ship on **Agent Framework**, pick **one** eval tool.

---

## F. Books, newsletters, podcasts, conferences, communities

**Books** (all optional; read 1, not 4)

| Book | Why / verdict | Link |
|------|---------------|------|
| ***AI Agents in Depth* / 《深入理解 AI Agent》** — 李博杰 (Bojie Li), v2.0 2026, Apache-2.0 | **Adopted as this repo's companion textbook.** Best free 2026 textbook: harness engineering, context engineering (KV cache, skills, compression), memory/RAG, tools/MCP, coding agents, interaction (voice/computer-use), evals (pass@k vs pass^k, failure attribution, significance), post-training, continual evolution, multi-agent taxonomy. **109 experiments** with ★ difficulty ratings. Chinese original; community EN translation. Not a replacement for the labs — see the gap table. | [Repo](https://github.com/bojieli/ai-agent-book) ✅ · [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md) |
| *AI Engineering* — Chip Huyen (O'Reilly, 2025) | Best systems-level book: evals, RAG, finetuning, cost/latency. Chapters 6–9 cover agents and evals. Paywalled. | [O'Reilly](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 🔒 |
| *Build a Large Language Model (From Scratch)* — S. Raschka (Manning, 2024) | Only if you want model internals; excellent but ~40 h — do it after the capstone, not before. | [Manning](https://www.manning.com/books/build-a-large-language-model-from-scratch) · [Repo](https://github.com/rasbt/LLMs-from-scratch) |
| *Hands-On Large Language Models* — Alammar & Grootendorst (O'Reilly, 2024) | Fast visual intuition for tokens/embeddings/attention; skippable if you already know transformers. | [Book site](https://www.llm-book.com/) |
| 《Hello-Agents》 (free PDF, Chinese) | The best free agent-engineering textbook in Chinese; see §G. | [Repo](https://github.com/datawhalechina/hello-agents) |

**Newsletters** (subscribe to 3 max): [Import AI](https://importai.substack.com/) (policy/research signal) · [The Batch](https://www.deeplearning.ai/the-batch/) (weekly industry) · [Latent Space](https://www.latent.space/) (AI-engineer practitioner) · [Interconnects](https://www.interconnects.ai/) (research analysis) · [Chip Huyen](https://newsletter.languagemodels.co/) · [One Useful Thing](https://www.oneusefulthing.org/) (adoption patterns) · [Simon Willison](https://simonwillison.net/) (tooling/scepticism) · [Hamel Husain](https://hamel.dev/) (evals).

**Podcasts:** [Latent Space](https://www.latent.space/) (best for agent engineers) · [The TWIML AI Podcast](https://twimlai.com/) (technical interviews) · [Cognitive Revolution](https://www.cognitiverevolution.ai/) (product/industry) · [No Priors](https://www.nopriors.com/) (leadership-level framing). Commute-sized: 1 episode/week, skip news roundups.

**Conferences:** [AI Engineer World's Fair](https://www.ai.engineer/worldsfair/2026/) ⚠️ (San Francisco Moscone, typically June — the practitioner conference; talks land on YouTube free) · [AI Engineer Summit](https://www.ai.engineer/summit) ⚠️ (NYC, autumn) · [Interrupt](https://interrupt.langchain.com/) (LangChain's agent conference; talks online) · [NeurIPS](https://neurips.cc/) · [ICLR](https://iclr.cc/) (2026 papers, e.g. ACE). For Singapore: [AI Singapore](https://www.aisingapore.org/) runs community/AI-certification programmes and local events — the cheapest local network. Timezone note: SF events are 15–16 h behind SGT; conference videos are the realistic option during term.

**Communities:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) (practical, noisy) · [Hugging Face Discord](https://huggingface.co/join/discord) (course help) · [LangChain Forum](https://forum.langchain.com/) (framework Q&A) · MCP [Discord](https://discord.gg/6CSzBmMkjX) (invite may expire; find it via the docs) · Datawhale reader groups via [Hello-Agents](https://github.com/datawhalechina/hello-agents).

---

## G. Chinese-language resources (中文资源)

| Resource | What it is | Why it's worth your time | Link |
|----------|-----------|--------------------------|------|
| **《深入理解 AI Agent：设计原理与工程实践》** | 李博杰著，v2.0（2026-09-23），Apache-2.0 开源，10 章正文 + 109 个带 ★ 难度评级的实验。中文是正本，英文等 15 种语言为社区翻译。 | **本仓库采用的配套教材。** 你读中文正本会比英文译本快；上下文工程（KV Cache、Skills、状态栏、压缩）、记忆/RAG、工具/MCP、Coding Agent、评估（pass@k vs pass^k、失败归因、统计显著性）、后训练、持续进化、多 Agent 协作全部覆盖。第 10 章的信息增益判据和六种失效模式尤其适合对照第 6 周；第 9 章是从轨迹中学习的理论版，正好补 SendOS 的 distillation 闭环。 | [Repo](https://github.com/bojieli/ai-agent-book) ✅ · [在线阅读](https://bojieli.github.io/ai-agent-book/astro/) · [章节映射](../books/ai-agents-in-depth/CHAPTER-MAP.md) |
| **Hello-Agents《从零开始构建智能体》** | Datawhale open book: 16 chapters from agent history → ReAct/Plan-and-Solve/Reflection implemented by hand → Context Engineering → MCP/A2A/ANP → Agentic-RL (SFT→GRPO) → evals → 3 capstones. Free PDF + online. | **Best Chinese resource, full stop.** Matches this track week-for-week; the Agentic-RL chapter is material no English course covers this hands-on. Mandarin-first means faster for you. | [Repo](https://github.com/datawhalechina/hello-agents) ✅ · [在线阅读](https://datawhalechina.github.io/hello-agents/) |
| **Agent-Learning-Hub** | Datawhale's 2026-updated agent learning roadmap (published May 2026). | Use it to sanity-check sequencing; it is more Chinese-ecosystem-oriented (Dify/Coze/domestic models). | [Repo](https://github.com/datawhalechina/Agent-Learning-Hub) |
| 李宏毅 (Hung-yi Lee) 生成式AI導論 | NTU lecture series (Traditional Chinese audio, slides). The 2024 edition remains the canonical GenAI course. | Best Chinese-language *lecture* explanation of how LLMs work; watch the transformer/agent lectures, skip the rest. | [GenAI 2024](https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring.php) · [ML 2025](https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php) |
| 宝玉 (baoyu.io) | Translations/annotations of Anthropic/OpenAI engineering posts and agent guides. | High-fidelity Chinese versions of exactly the essays in §C — good for a second pass or for sharing with teammates. | [baoyu.io](https://baoyu.io/) |
| Prompt Engineering Guide 中文版 | DAIR.AI guide, Chinese translation. | Quick reference for prompting techniques; do not read cover-to-cover. | [中文版](https://www.promptingguide.ai/zh) |
| 机器之心 / 量子位 | AI news and paper summaries in Chinese. | Fast scanning of 2026 releases; treat claims sceptically and follow the source link. | [机器之心](https://www.jiqizhixin.com/) · [量子位](https://www.qbitai.com/) |
| 扣子 Coze 文档 | ByteDance low-code agent platform docs. | Relevant if your enterprise also ships low-code agents; not a substitute for learning the loop. | [Docs](https://www.coze.cn/docs) |
| 阿里云百炼 Model Studio / 智谱 / Qwen | Domestic model-platform and agent docs. | Useful if your platform must support domestic models or data residency. | [百炼](https://help.aliyun.com/zh/model-studio/) · [智谱](https://docs.bigmodel.cn/) · [Qwen](https://qwen.readthedocs.io/) |
| 掘金 (juejin.cn) | Chinese dev blog platform. | Occasional excellent engineering post-mortems; quality varies wildly. Search by concrete error messages, not by "Agent 入门". | [juejin.cn](https://juejin.cn/) |

**Language strategy for Singapore:** read English primary sources (they are always first), use Chinese resources for reinforcement and for explaining concepts to Chinese-speaking stakeholders. Hello-Agents is the one Chinese resource worth going through systematically.

---

## H. If you only have 50 hours

| # | Block | Hrs | Why it made the cut | Source |
|---|-------|-----|---------------------|--------|
| 1 | Building effective agents + 12-Factor Agents | 3 | Shared vocabulary + production checklist | [Essay](https://www.anthropic.com/engineering/building-effective-agents) · [Repo](https://github.com/humanlayer/12-factor-agents) |
| 2 | Chip Huyen "Agents" + ReAct paper | 3 | Systems frame + the loop's origin | [Post](https://huyenchip.com/2025/01/07/agents.html) · [arXiv](https://arxiv.org/abs/2210.03629) |
| 3 | Build a ReAct loop from scratch (no framework) | 6 | Nothing teaches faster than owning the loop | [HF Agents Course §1](https://huggingface.co/learn/agents-course) |
| 4 | Tool design + MCP server (Python, then C#) | 7 | Directly reusable in your .NET platform | [Anthropic tools](https://www.anthropic.com/engineering/writing-tools-for-agents) · [MCP](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro) |
| 5 | Context engineering + compaction | 4 | The 2026 differentiating skill | [Essay](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| 6 | Evals: 20-case golden set + judge + traces | 8 | Everything else is guesswork without this | [Hamel](https://hamel.dev/blog/posts/evals/) · [Inspect](https://inspect.aisi.org.uk/) |
| 7 | Read smolagents end-to-end | 4 | Whole-agent comprehension in one repo | [Repo](https://github.com/huggingface/smolagents) |
| 8 | Multi-agent research system post + one experiment | 4 | Know when multi-agent pays and when it does not | [Post](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 9 | SWE-agent ACI + prompt-injection demo/mitigation | 5 | Security is the enterprise blocker | [Paper](https://arxiv.org/abs/2405.15793) · [Essay](https://www.anthropic.com/engineering/managed-agents) |
| 10 | Microsoft Agent Framework port + MCP C# SDK | 6 | Makes it your day job, not a hobby | [Docs](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) · [SDK](https://github.com/modelcontextprotocol/csharp-sdk) |
| **Total** | | **50** | | |

**Deliberately not in the 50:** fine-tuning/RL (Week 9), classical multi-agent theory, vector-database internals, computer-use, LangGraph mastery. Those are 2027 problems for you.

---

## I. Deliberately skipped hype (and why)

- **"Build 10 agents in 10 days" listicles and awesome-* aggregator repos.** Breadth without a loop, evals or failure analysis teaches nothing; they also rot within months. Skip.
- **Framework tourism (CrewAI / AutoGen / Swarm / Dify / n8n first).** OpenAI's [Swarm](https://github.com/openai/swarm) is explicitly an educational experiment superseded by the Agents SDK; AutoGen and Semantic Kernel have been folded into [Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview). Learning a framework's API before you know what the framework abstracts is backwards. Build the loop first.
- **Low-code platforms (Coze, Dify, n8n) as a learning path.** They are shipping tools for product teams, not concept-builders. Read the docs when your employer adopts one.
- **Prompt-engineering mega-courses and "secret prompt" content.** Diminishing returns; context engineering subsumes most of it.
- **Vector-database deep dives and "RAG from scratch" curricula.** For agents, agentic search (`grep`, SQL, file trees) often beats embeddings, and you can learn retrieval in a week. Defer.
- **Fine-tuning / pre-training courses as a first step.** Premature: 95% of production value in your platform comes from tools, context and evals. See Week 9 decision memo instead.
- **"Fully autonomous AI employee" / agent-marketplace-token content.** Unfalsifiable claims, no eval methodology. The [GAIA](https://arxiv.org/abs/2311.12983) and [τ-bench](https://arxiv.org/abs/2406.12045) numbers are the honest counterweight.
- **Computer-use as a first project.** Impressive demos, fragile and expensive in practice; read [OSWorld](https://arxiv.org/abs/2404.07972) before investing.
- **Paid "agent engineer bootcamps" and certifications.** The free vendor + Berkeley/HF material is better and more current; certificates carry little weight compared with a traced, evaluated capstone in your portfolio.
- **Benchmark-chasing (SWE-bench leaderboard drama).** Useful as context, not as a goal; your enterprise tasks are not public benchmarks.

---

## J. Link-verification ledger (2026-10-18)

**Method:** HTTP status checks against every cited URL; 15 highest-value pages fetched with content read (`✅`): Anthropic building-effective-agents, effective context engineering, managed agents, effective harnesses, 12-factor repo, HF Agents Course, Microsoft AI Agents for Beginners, Microsoft Agent Framework overview, Berkeley MOOC (F24 + root), DeepLearning.AI catalog, MCP docs (2026-07-28), Hello-Agents README, ACE paper, LangChain Academy (JS-rendered shell — existence only).

**Dead or changed (use the replacement, not the original):**

- `https://llmagents-learning.org/` → **redirects** to `/sp25` (Spring 2025). There is **no 2026 edition**; the Fall 2024 and Spring 2025 archives are the current content. Certificates are closed.
- `https://strandsagents.com/latest/` (linked from Anthropic's essay) → **404**; the project root [strandsagents.com](https://strandsagents.com/) resolves. Strands is Python/TypeScript-focused; I found no first-class .NET SDK, so verify before prioritising it.
- `https://simonwillison.net/2025/Sep/18/agents/` → request **failed/timed out** on 2026-10-18; the [agents tag page](https://simonwillison.net/tags/agents/) and blog root resolve normally, so treat the specific post URL as **uncertain** and navigate from the tag page.
- `https://github.com/langchain-ai/langgraph/tree/main/docs/docs/tutorials`, `https://github.com/openai/openai-cookbook/tree/main/examples/agents`, `https://github.com/letta-ai/letta-quickstart` → **404** (paths moved); replaced in this document with the [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview), [cookbook root](https://github.com/openai/openai-cookbook), [Letta docs](https://docs.letta.com/).
- `https://conf.langchain.com/` → **DNS/connection error**; the live conference site is [interrupt.langchain.com](https://interrupt.langchain.com/).
- `https://blog.google/technology/developers/introducing-agent-development-kit/` → error; use [ADK docs](https://google.github.io/adk-docs/) or the [repo](https://github.com/google/adk-python).
- `https://speech.ee.ntu.edu.tw/~hylee/genai/2025-spring.php` → **404**; Lee's GenAI course site only exists for 2024 (`/genai/2024-spring.php`); his 2025 course is the ML course at `/ml/2025-spring.php`.

**Paywalled or bot-blocked (real for humans, 403 to scripts):**

- [O'Reilly — AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 🔒 (subscription; check whether your university library — NUS/NTU — provides O'Reilly Learning access).
- `openai.com/index/*` pages (e.g. BrowseComp, Agents SDK announcement, new agent tools) → 403 to automated requests; read via search/Google cache or the [OpenAI docs](https://platform.openai.com/docs/guides/agents).
- `ruanyifeng.com` → 403 to bots; works in a browser (not cited above).
- [OpenAI practical guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) → **HTTP 200 but PDF**: my fetch tool cannot extract PDF text, so I verified existence/status only, not page content. Treat as *exists, unread*.

**Redirects to expect (`⚠️`, resolve in browser):** `deeplearning.ai/short-courses/` → `/courses`; `deeplearning.ai/courses/agentic-ai/` → 308 (canonical redirect); `ai.engineer/worldsfair/2026/` and `ai.engineer/summit` → 308; `anthropic.com/engineering/building-agents-with-the-claude-agent-sdk` and `.../claude-code-best-practices` → 308; `docs.bigmodel.cn` → 308; MCP docs unversioned URL → versioned `/docs/2026-07-28/`.

**Stability caveats:** `eugeneyan.com` root timed out (article URL 200s); Discord invites expire; 2027 conference dates are unpublished. Re-run this status check quarterly — roughly 10% of this list moves within a year, so treat it as dated **2026-10-18**.

---

### If you remember one thing

Read *Building effective agents*, *Effective context engineering*, Chip Huyen's *Agents*, *12-Factor Agents* and Hamel's evals post (≈4 h). Build a ReAct loop by hand (6 h), add tools + an MCP server (7 h), build a 20-case eval harness with traces (8 h), read `smolagents` end-to-end (4 h), then port it to [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) with the [C# MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) (6 h). That is the whole game; everything else here is depth, optional research, or Chinese-language reinforcement.
