# Solutions

**参考解答**

Reference implementations, one directory per week, mirroring the repository root:

参考实现，每周一个目录，目录结构与仓库根目录保持一致：

```
solutions/week01/agentlab/providers/openai_compat.py
solutions/week02/agentlab/loop/...
solutions/week06/agentlab/orchestrator/...
```

Apply a solution (it copies over your work — this is a last resort):

应用一份参考解答（它会覆盖你的工作——这是最后手段）：

```powershell
# Windows (PowerShell)
.\tasks.ps1 solution 1
```

```bash
# macOS / Linux
./tasks.sh solution 1
```

## Policy: do not open these until your tests pass

**策略：在你的测试通过之前不要打开它们**

The tests already tell you *what* to build. The solution tells you *how*, which is the part you are training. Use it in exactly three situations:

测试已经告诉你要构建*什么*。参考解答告诉你*怎么*构建，而这恰恰是你正在训练的部分。只在以下三种情况下使用它：

1. **You are green** — read it to compare designs, not to copy. Ask: what did I do that is more/less general? What invariant did I miss?

   **你的测试已通过（变绿）**——阅读它是为了对比设计，而不是照抄。问自己：我做的哪些地方更通用/更不通用？我漏掉了哪个不变量？

2. **You are stuck for more than 90 minutes** on the same failure, *and* you have written down your hypothesis. Read one function, close the file, finish yourself.

   **你在同一个失败上卡住超过 90 分钟**，*并且*你已经写下了自己的假设。读一个函数，关掉文件，自己完成剩下的部分。

3. **You are reviewing** — e.g. before the capstone, or before a SendOS code review, to compare a miniature against the real thing.

   **你在做复习回顾**——例如在结业项目（capstone）之前，或在 SendOS 代码评审之前，用缩微版与真实系统做对比。

## What solutions are not

**参考解答不是什么**

- They are not the only correct answer. Agent design has many valid shapes; the tests encode the contract, not the design.

  它们不是唯一正确的答案。Agent 设计有许多合理的形态；测试编码的是契约，而不是设计。

- They are not production code. They favour clarity and teaching over throughput, async, and framework conventions.

  它们不是生产代码。它们优先考虑清晰度和教学，而非吞吐量、异步和框架惯例。

- They are not complete. Some labs have deliberate gaps marked in `NOTES.md` — those gaps are your stretch exercise.

  它们并不完整。有些实验（lab）在 `NOTES.md` 中标注了刻意留下的空缺——这些空缺就是你的拓展练习。

## Solutions vs your code

**参考解答与你的代码**

Keep your implementation. After comparing, write five bullets in your weekly review:

保留你自己的实现。对比之后，在你的每周回顾中写下五条要点：

- What design choice did I make that the reference did not? Is mine better for a reason?

  我做了哪些参考实现没有做的设计选择？我的选择是否有理由更好？

- What did the reference handle that I missed? Was it tested, or accidental?

  参考实现处理了哪些我漏掉的情况？那是被测试覆盖的，还是偶然为之？

- Which invariant would I add to the test suite now?

  我现在会把哪个不变量加入测试套件？
