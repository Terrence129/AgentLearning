# The Weekly Rhythm — how to spend 8–12 hours well

**每周节奏 — 如何用好 8–12 小时**

**Premise:** you have an internship, NUS coursework, and 8–12 hours a week for this. That is enough to finish nine weeks *if* the hours are structured, and not enough if they are not. This document is the operating method; [`CHECKPOINTS.md`](CHECKPOINTS.md) defines the finish line and [`LEARNING-PLAN.md`](LEARNING-PLAN.md) defines the content.

**前提：** 你有实习、NUS 的课程，每周还有 8–12 小时用于本课程。*如果*这些时间是有结构的，就足以完成九周的内容；如果没有结构，就不够。本文档是执行方法；[`CHECKPOINTS.md`](CHECKPOINTS.md) 定义了终点线，[`LEARNING-PLAN.md`](LEARNING-PLAN.md) 定义了内容。

**The one rule:** never trade the gate for reading. A week with 6 hours and green tests beats a week with 12 hours and three unread papers.

**唯一的规则：** 永远不要用阅读来换取关卡。一周投入 6 小时且测试通过（变绿），胜过投入 12 小时却留下三篇没读完的论文。

---

## 1. Session architecture (the week has three kinds of session)

**1. 会话结构（一周有三种会话）**

| Session<br>会话 | When (suggested)<br>时间（建议） | Length<br>时长 | Purpose<br>目的 |
|---|---|---|---|
| **Build A** (Tue 20:00)<br>**构建 A**（周二 20:00） | Mid-week<br>周中 | 90–120 min<br>90–120 分钟 | Read failing tests + brief, then implement the smallest failing test<br>阅读失败的测试 + 任务说明，然后实现最小的那个失败测试 |
| **Build B** (Thu 20:00)<br>**构建 B**（周四 20:00） | Mid-week<br>周中 | 90–120 min<br>90–120 分钟 | Finish implementation; make the lab artifact run end-to-end<br>完成实现；让实验（lab）产出物端到端跑通 |
| **Deep session** (Sat 09:00–13:00)<br>**深度会话**（周六 09:00–13:00） | Weekend<br>周末 | 3–4 h<br>3–4 小时 | Integration, theory + paper, SendOS bridge, weekly review<br>集成、理论 + 论文、SendOS 桥接、每周复盘 |

That is 6–8 hours of protected time; stretch and busy weeks fill the remainder. Both weekday sessions are optional only in the "minimum viable week" (see §8); the Saturday review is never optional.

这就是 6–8 小时受保护的时间；剩下的时间由拓展目标和忙碌周来填补。只有在「最低可行周」（参见 §8）中，两个工作日会话才是可选的；周六的复盘永远不是可选的。

### Inside a 90-minute block

**一个 90 分钟时间块的内部安排**

| Minutes<br>分钟 | Activity<br>活动 | Notes<br>说明 |
|---|---|---|
| 0–5 | **Warm-up retrieval**<br>**热身回忆** | 5 flashcards from *previous* weeks, closed book. Do not open the laptop code first.<br>闭卷做 5 张*之前*几周的闪卡。不要先打开电脑上的代码。 |
| 5–10 | **Set the one target**<br>**设定唯一目标** | Write one sentence: "By the end of this block, this test passes / this artifact runs."<br>写一句话：「在这个时间块结束时，这个测试通过 / 这个产出物能运行。」 |
| 10–70 | **Deep work**<br>**深度工作** | Phone in another room, notifications off, one tab group. If stuck >20 min → §6.<br>手机放到另一个房间，关闭通知，只开一个标签页组。如果卡住超过 20 分钟 → §6。 |
| 70–80 | **Break**<br>**休息** | Walk, water, no screens. Breaks are part of the method, not a reward.<br>走一走，喝点水，不看屏幕。休息是方法的一部分，而不是奖励。 |
| 80–90 | **Close-out log**<br>**收尾记录** | 3 lines in [`../../templates/lab-notes.md`](../../templates/lab-notes.md): what moved, what is next, what confused me.<br>在 [`../../templates/lab-notes.md`](../../templates/lab-notes.md) 中写 3 行：有什么进展、下一步是什么、什么让我困惑。 |

**Hard rule:** stop at the timer, not at "done". Stopping mid-problem with a written next step is what makes the next session start fast; finishing by pushing through to hour 3 makes the next session start exhausted.

**硬性规则：** 到点就停，而不是等到「做完」才停。在问题做到一半时停下并写下下一步，才能让下一次会话快速启动；硬撑到第 3 个小时才做完，会让下一次会话一开始就精疲力尽。

---

## 2. Retrieval practice (the highest-leverage 10 minutes of your week)

**2. 提取练习（你一周中杠杆最高的 10 分钟）**

Re-reading and highlight-feeling are the two most popular study techniques and among the least effective. Recalling from memory is what builds durable knowledge — the testing effect is one of the most replicated findings in learning science ([Roediger & Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/); [Dunlosky et al., 2013](https://journals.sagepub.com/doi/10.1177/1529100612453266) — the SAGE link may 403 automated fetches but works in a browser).

重读和「划重点的感觉」是最流行的两种学习技巧，却也是效果最差的之一。凭记忆回忆才能构建持久的知识——测试效应是学习科学中被重复验证最多的发现之一（[Roediger & Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/)；[Dunlosky et al., 2013](https://journals.sagepub.com/doi/10.1177/1529100612453266)——SAGE 的链接可能会对自动抓取返回 403，但在浏览器中可以正常打开）。

Three retrieval rituals, in order of value:

三种提取练习的固定流程，按价值排序：

1. **Blank-page recall (weekly, 10 min):** close everything; write the week's mechanism from memory (the loop, the approval state machine, the compaction policy); then open your notes and diff. Gaps are your study list.

   **白纸回忆（每周，10 分钟）：** 关掉一切；凭记忆写出本周的机制（循环、审批状态机、压缩（compaction）策略）；然后打开笔记做对比。差距就是你的学习清单。

2. **Quiz + flashcards (weekly, 15 min):** take `docs/plan/quizzes/weekNN.md` closed book, then run the CSV in Anki. Score below 8/10 means the explain gate fails.

   **测验 + 闪卡（每周，15 分钟）：** 闭卷完成 `docs/plan/quizzes/weekNN.md`，然后在 Anki 中过一遍 CSV。得分低于 8/10 就意味着讲解关卡未通过。

3. **Teach-back (weekly, 10 min):** 150 words, spoken aloud or written, with no notes. If you cannot, the week is not done — this is a gate condition, not a nicety.

   **复述讲解（teach-back）（每周，10 分钟）：** 150 词，大声说出来或写下来，不看笔记。如果做不到，这一周就没完成——这是关卡条件，而不是锦上添花。

**Anti-pattern:** opening the plan and re-reading the week's concepts. That is recognition, not recall, and it is why people "understand" a topic until they have to explain it.

**反模式：** 打开计划重读本周的概念。那是识别，不是回忆；这也正是为什么人们总觉得自己「理解」了某个主题，直到不得不讲解它的时候才露馅。

---

## 3. Interleaving (mix, do not block)

**3. 交错练习（混着练，不要分块）**

Blocked practice (all of one topic, then all of another) feels smoother but transfers worse than interleaved practice. In practice:

分块练习（先把一个主题全部练完，再练另一个）感觉更顺畅，但迁移效果比交错练习差。实际操作中：

- Start every Thursday session with 10 minutes of a **previous** week's quiz or 5 flashcards — mixing retrieval targets.

  每个周四的会话都先用 10 分钟做一份**之前**某周的测验或 5 张闪卡——混合提取的对象。

- In the Saturday session, alternate: 45 min build → 30 min theory → 30 min SendOS bridge. Alternating contexts forces you to re-load each mental model, which is the point.

  在周六的会话中交替进行：45 分钟构建 → 30 分钟理论 → 30 分钟 SendOS 桥接。交替切换情境会迫使你重新加载每个思维模型，而这正是目的所在。

- When studying evals, compare against security and context: "which of these three would catch a regression the other two miss?"

  学习评测（eval）时，与安全和上下文对照比较：「这三者中，哪一个能捕捉到另外两个漏掉的回归？」

- Never interleave *new* topics in the same session — interleave review, keep new material blocked.

  永远不要在同一个会话中交错*新*主题——交错的是复习，新材料要分块学习。

---

## 4. Spaced repetition schedule

**4. 间隔重复安排**

| When<br>时间 | What<br>内容 | Time<br>耗时 |
|---|---|---|
| Same day as the lab<br>做实验的当天 | Add the week's 5 cards (`docs/plan/flashcards/weekNN.csv`)<br>添加本周的 5 张卡片（`docs/plan/flashcards/weekNN.csv`） | 5 min<br>5 分钟 |
| Day 1<br>第 1 天 | Review new cards + the week's quiz wrong answers<br>复习新卡片 + 本周测验的错题 | 10 min<br>10 分钟 |
| Day 3<br>第 3 天 | Review due cards; re-answer 3 wrong quiz questions<br>复习到期的卡片；重新回答 3 道测验错题 | 10 min<br>10 分钟 |
| Day 7 (Saturday)<br>第 7 天（周六） | Review due cards; pick 5 random cards from *older* weeks<br>复习到期的卡片；从*更早*的几周中随机挑 5 张卡片 | 10 min<br>10 分钟 |
| Day 21<br>第 21 天 | Same, plus a blank-page recall of that old week's mechanism<br>同上，另加对那一周机制的白纸回忆 | 15 min<br>15 分钟 |

Use Anki (or any SRS) with the CSV import; tags are already `weekNN;topic`. **Never add a card you cannot answer in one sentence** — vague cards train vague recall. If a card is ambiguous, rewrite it.

使用 Anki（或任何间隔重复系统）导入 CSV；标签已经是 `weekNN;topic`。**永远不要添加一张你无法用一句话回答的卡片**——模糊的卡片只会训练出模糊的回忆。如果某张卡片有歧义，就重写它。

---

## 5. Timeboxing rules

**5. 时间盒规则**

- **70/20/10.** 70% building, 20% reading, 10% reflection/writing. If reading exceeds 30% of the week's hours, cut it — the reading list is capped deliberately.

  **70/20/10。** 70% 构建，20% 阅读，10% 反思/写作。如果阅读超过本周时间的 30%，就削减它——阅读清单是有意设上限的。

- **Read with a question.** Before opening a paper, write the question it must answer. If the paper does not answer it in 20 minutes, close it and note "later".

  **带着问题去读。** 打开一篇论文之前，先写下它必须回答的问题。如果 20 分钟内论文没有回答这个问题，就关掉它并记下「以后再看」。

- **One new tool per week, maximum.** New library, new editor setup and new provider are three separate weeks of cognitive load.

  **每周最多一个新工具。** 新的库、新的编辑器配置和新的模型提供商（provider），是三周各自独立的认知负担。

- **Stop at the timer.** A planned 90-minute block that becomes 3 hours steals from the next two sessions.

  **到点就停。** 一个计划 90 分钟的时间块变成 3 小时，就会偷走接下来两次会话的时间。

- **Protect the Saturday block** as if it were a class. It is the only session long enough for integration, theory and the review.

  **像对待一堂课一样保护好周六的时间块。** 它是唯一一个足够长、能容纳集成、理论和复盘的会话。

---

## 6. The 20-minute unstuck rule

**6. 20 分钟脱困规则**

Stuck is normal; silent stuck is how self-study dies. When you notice you have been stuck for 20 minutes:

卡住是正常的；默默地卡着，才是自学失败的方式。当你发现自己已经卡了 20 分钟：

1. **Write the question down** in [`../../templates/lab-notes.md`](../../templates/lab-notes.md) §11: what you expected, what happened, what you tried.

   **把问题写下来**，写在 [`../../templates/lab-notes.md`](../../templates/lab-notes.md) §11 中：你预期会发生什么、实际发生了什么、你尝试过什么。

2. **Shrink it:** reproduce the failure in the smallest possible test or script. 80% of "stuck" resolves here.

   **缩小问题：** 用尽可能小的测试或脚本复现这个失败。80% 的「卡住」会在这一步解决。

3. **Ask the AI tutor** with the template from START-HERE: week, test name, exact error, what you tried, and "give me a hint, not the answer". Good prompt example: *"Week 2, `test_agent_stops_on_max_steps` fails with `KeyError: 'tool_calls'`. I appended only the assistant content, not the tool_calls message. Hint?"*

   **向 AI 导师求助**，使用 START-HERE 中的模板：所在周、测试名、确切的错误、你尝试过什么，以及「给我一个提示，不要给答案」。好的提示词示例：*「第 2 周，`test_agent_stops_on_max_steps` 失败，报错 `KeyError: 'tool_calls'`。我只追加了 assistant 的内容，没有追加 tool_calls 消息。能给个提示吗？」*

4. **If still stuck after another 20 minutes**, ask for the minimal failing example and the concept, then implement it yourself. Save the answer as a flashcard.

   **如果又过了 20 分钟仍然卡住**，就索要最小的失败示例和相关概念，然后自己实现。把答案保存为一张闪卡。

**Never** spend 90 minutes on a library quirk. That is not productive struggle; it is a documentation problem, and the tutor is faster.

**永远不要**在某个库的怪异行为上花 90 分钟。那不是有益的挣扎，而是文档问题，问导师会更快。

---

## 7. The weekly review ritual (Saturday, last 60 minutes)

**7. 每周复盘流程（周六，最后 60 分钟）**

1. Run the gate commands from [`CHECKPOINTS.md`](CHECKPOINTS.md); paste the summary into the review.

   运行 [`CHECKPOINTS.md`](CHECKPOINTS.md) 中的关卡命令；把摘要粘贴到复盘中。

2. Fill [`../../templates/weekly-review.md`](../../templates/weekly-review.md) — especially the **failure log** and the **time audit**.

   填写 [`../../templates/weekly-review.md`](../../templates/weekly-review.md)——尤其是**失败日志**和**时间审计**。

3. Write the 150-word teach-back with no notes.

   不看笔记写出 150 词的复述讲解。

4. Add 5 flashcards; import them.

   添加 5 张闪卡；导入它们。

5. Update [`PROGRESS.md`](PROGRESS.md): hours, gate status, "what I can now explain".

   更新 [`PROGRESS.md`](PROGRESS.md)：小时数、关卡状态、「我现在能讲解什么」。

6. Put the next week's three sessions in the calendar before you close the laptop.

   在合上电脑之前，把下一周的三次会话放进日历。

7. Commit: `git add -A && git commit -m "week NN: gate green + review"`.

   提交：`git add -A && git commit -m "week NN: gate green + review"`。

The review is the only place where the week becomes evidence. Without it, week 9 arrives and you cannot write the portfolio post.

复盘是让这一周变成证据的唯一地方。没有它，等到第 9 周你就写不出作品集文章。

---

## 8. The minimum viable week (fallback)

**8. 最低可行周（兜底方案）**

When the internship explodes or coursework collides — one week in five, realistically — do not skip the week and do not pretend. Do the **minimum viable week** (4–5 hours):

当实习忙到爆炸或者课程撞车时——现实地说，大约每五周会有一周——不要跳过这一周，也不要假装。执行**最低可行周**（4–5 小时）：

1. **Session 1 (90 min):** read the brief + failing tests; implement the first failing test only.

   **会话 1（90 分钟）：** 阅读任务说明 + 失败的测试；只实现第一个失败测试。

2. **Session 2 (90 min):** finish until `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux) is green. Nothing else.

   **会话 2（90 分钟）：** 一直做到 `.\tasks.ps1 week NN`（Windows）/ `./tasks.sh week NN`（macOS/Linux）通过为止。不做别的。

3. **Gate (60 min):** revise quiz ×10 + teach-back + 5 flashcards. Skip theory, paper, SendOS bridge, and stretch — but record them as debt in the review.

   **关卡（60 分钟）：** 复习测验 ×10 + 复述讲解 + 5 张闪卡。跳过理论、论文、SendOS 桥接和拓展目标——但要在复盘中把它们记为债务。

4. **Emergency 90-minute version** (if even that fails): run the week's tests, fix one test, write one flashcard, log the week as partial in `PROGRESS.md`. A partial week is data; a skipped week with no record is a hole.

   **紧急 90 分钟版本**（如果连上面的都做不到）：运行本周的测试，修好一个测试，写一张闪卡，在 `PROGRESS.md` 中把这一周记为部分完成。部分完成的一周是数据；没有记录就跳过的一周是一个窟窿。

**Never** skip the transfer stage for two weeks in a row — the SendOS bridge is the reason this curriculum exists. If you must choose, protect the bridge over the stretch.

**永远不要**连续两周跳过迁移阶段——SendOS 桥接正是这门课程存在的理由。如果必须取舍，保住桥接，放弃拓展目标。

---

## 9. Anti-patterns that will cost you the most time

**9. 最耗费你时间的反模式**

| Anti-pattern<br>反模式 | What it looks like<br>表现 | Replacement<br>替代做法 |
|---|---|---|
| Tutorial rabbit hole<br>教程兔子洞 | "I'll just watch one more video on LangGraph"<br>「我就再看一个 LangGraph 的视频」 | The plan caps reading; frameworks arrive in weeks 6–9 as comparison<br>计划限制了阅读量；框架会在第 6–9 周作为对比出现 |
| Note-taking as procrastination<br>用记笔记来拖延 | Beautiful notes, no tests<br>笔记很漂亮，测试一个没有 | Notes in the review only; code is the artefact<br>笔记只写在复盘里；代码才是产出物 |
| Framework shopping<br>挑选框架 | Comparing 5 agent frameworks<br>比较 5 个 Agent 框架 | Build the loop first; read frameworks after week 6<br>先构建循环；第 6 周之后再读框架 |
| Tool-hopping<br>频繁换工具 | New editor/model/db every week<br>每周换一个新的编辑器/模型/数据库 | One tool change per month, max<br>每月最多换一次工具 |
| Cramming before the quiz<br>测验前临时抱佛脚 | Re-reading for 40 minutes<br>重读 40 分钟 | 10 minutes of retrieval instead<br>改为做 10 分钟的提取练习 |
| Silent struggle<br>默默挣扎 | Stuck for an hour, no log, no question<br>卡了一小时，没有记录，也没提问 | 20-minute rule, written question, tutor<br>20 分钟规则、写下问题、找导师 |
| Perfecting the capstone<br>把结业项目做到完美 | Polishing UI at 2 a.m.<br>凌晨 2 点还在打磨 UI | Ship at 80%: demo + write-up + eval report<br>做到 80% 就交付：演示 + 总结文章 + 评测报告 |

---

## 10. What to measure each week (put it in PROGRESS.md)

**10. 每周要度量什么（写进 PROGRESS.md）**

- Hours actually spent (not planned).

  实际花费的小时数（不是计划的）。

- Day the week's tests went green (Saturday night is the target).

  本周测试通过（变绿）的日期（目标是周六晚上）。

- Quiz score /10.

  测验得分 /10。

- Cards added and cards reviewed.

  添加的卡片数和复习的卡片数。

- One sentence: "I can now explain ______."

  一句话：「我现在能讲解 ______。」

- Gate status: green / explain / transfer.

  关卡状态：green（通过）/ explain（讲解）/ transfer（迁移）。

If two weeks in a row show <60% build time or a failing explain gate, stop and fix the method before continuing. The method is the intervention; more hours is usually the wrong fix.

如果连续两周的构建时间占比 <60%，或讲解关卡未通过，就停下来，先修正方法再继续。方法才是干预手段；投入更多时间通常是错误的解决办法。

---

## Sources

**参考文献**

1. Roediger, H. L., & Karpicke, J. D. (2006). *Test-enhanced learning: Taking memory tests improves long-term retention.* Psychological Science, 17(3), 249–255. https://pubmed.ncbi.nlm.nih.gov/16507066/

   《测试增强学习：参加记忆测试能提高长期保持》，发表于 Psychological Science 第 17 卷第 3 期，249–255 页。

2. Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). *Improving students' learning with effective learning techniques.* Psychological Science in the Public Interest, 14(1), 4–58. https://journals.sagepub.com/doi/10.1177/1529100612453266

   《用有效的学习技巧提升学生的学习效果》，发表于 Psychological Science in the Public Interest 第 14 卷第 1 期，4–58 页。

3. Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). *Distributed practice in verbal recall tasks: A review and quantitative synthesis.* Psychological Bulletin, 132(3), 354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/

   《言语回忆任务中的分散练习：综述与定量综合分析》，发表于 Psychological Bulletin 第 132 卷第 3 期，354–380 页。

4. The Learning Scientists — accessible summaries of retrieval practice, spacing and interleaving: https://www.learningscientists.org/

   The Learning Scientists——关于提取练习、间隔练习和交错练习的通俗易懂的总结：https://www.learningscientists.org/
