# Labs

**实验**

One lab per week. Each lab is a **build specification**, not a tutorial: a brief, failing tests that define done, a starter skeleton, and a reference solution you should not open until your tests pass.

每周一个实验（lab）。每个实验都是一份**构建规格说明**，而不是教程：一份简介、定义“完成”标准的失败测试、一个起始骨架，以及一份在你的测试通过之前不应打开的参考解答。

| Week<br>周 | Lab<br>实验 | Module you build<br>你要构建的模块 | Tests<br>测试 | Hours<br>小时 | Status<br>状态 |
|---|---|---|---|---|---|
| 1 | [Provider seam](week01-provider/README.md)<br>[provider 接缝](week01-provider/README.md) | `agentlab/providers/openai_compat.py` | `tests/week01` | 8–10 | scaffolded<br>已搭好脚手架 |
| 2 | [Agent loop](week02-agent-loop/README.md)<br>[Agent 循环](week02-agent-loop/README.md) | `agentlab/loop/`, `agentlab/tools/builtin.py` | `tests/week02` | 10–12 | scaffolded<br>已搭好脚手架 |
| 3 | [Structured output](week03-structured-output/README.md)<br>[结构化输出](week03-structured-output/README.md) | `agentlab/schemas/` | `tests/week03` | 8–10 | scaffolded<br>已搭好脚手架 |
| 4 | [Context & memory](week04-context-memory/README.md)<br>[上下文与记忆](week04-context-memory/README.md) | `agentlab/context/` | `tests/week04` | 10–12 | scaffolded<br>已搭好脚手架 |
| 5 | [MCP](week05-mcp/README.md) | `agentlab/mcp/` | `tests/week05` | 8–10 | scaffolded<br>已搭好脚手架 |
| 6 | [Squads & approval](week06-squads/README.md)<br>[小队与审批](week06-squads/README.md) | `agentlab/orchestrator/` | `tests/week06` | 10–12 | scaffolded<br>已搭好脚手架 |
| 7 | [Evals](week07-evals/README.md)<br>[评测](week07-evals/README.md) | `agentlab/evals/` | `tests/week07` | 8–10 | scaffolded<br>已搭好脚手架 |
| 8 | [Security & governance](week08-security/README.md)<br>[安全与治理](week08-security/README.md) | `agentlab/guard/` | `tests/week08` | 8–10 | scaffolded<br>已搭好脚手架 |
| 9 | [Capstone](week09-capstone/README.md)<br>[结业项目](week09-capstone/README.md) | `agentlab/capstone/`, `agentlab/web/` | `tests/week09` | 12–16 | scaffolded<br>已搭好脚手架 |

> Status is updated as the repo evolves. If a lab you need is still marked `scaffolded` and its tests are missing, ask the AI tutor to generate it — the [scaffold contract](../docs/internals/SCAFFOLD-CONTRACT.md) defines exactly what it must contain.
>
> 状态会随着仓库的演进而更新。如果你需要的某个实验仍被标记为 `scaffolded`，而它的测试却缺失，请让 AI 导师生成它——[脚手架契约](../docs/internals/SCAFFOLD-CONTRACT.md)明确规定了它必须包含的内容。

## The contract for every lab

**每个实验的约定**

1. Read the brief and the concept note before opening the tests.

   在打开测试之前，先阅读简介和概念笔记。

2. Run the tests; they are the specification.

   运行测试；它们就是规格说明。

3. Implement in the module named above.

   在上面列出的模块中实现。

4. Green &rarr; write the weekly review &rarr; add flashcards &rarr; update `docs/plan/PROGRESS.md`.

   测试通过（变绿）&rarr; 撰写每周回顾 &rarr; 添加闪卡 &rarr; 更新 `docs/plan/PROGRESS.md`。

5. Only then diff against `solutions/weekNN/`.

   只有在这之后，才与 `solutions/weekNN/` 做对比。

```powershell
# Windows (PowerShell)
.\tasks.ps1 week 1       # run that week's tests
.\tasks.ps1 labs         # all lab tests (mostly red until you build them)
```

```bash
# macOS / Linux
./tasks.sh week 1        # run that week's tests
./tasks.sh labs          # all lab tests (mostly red until you build them)
```

## Rules

**规则**

- **No live API calls in tests.** Every lab ships with deterministic mocks; live calls are for exploration and the manual artifact.

  **测试中不进行真实的 API 调用。** 每个实验都自带确定性的 mock；真实调用只用于探索和手动产出的成果。

- **One concept, one build.** If a lab starts needing three new ideas, it is a sign the design is wrong.

  **一个概念，一次构建。** 如果一个实验开始需要三个新的想法，那就说明设计有问题。

- **Stretch goals are optional.** The gate is the acceptance criteria, not the stretch.

  **拓展目标是可选的。** 关卡是验收标准，而不是拓展目标。
