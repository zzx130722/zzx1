# AI 编程进阶：读代码 → 改代码 → 找 bug → 写测试

这是 4 条任务的落地，一条主线：

> **先看懂别人的代码（01）→ 再改造自己的代码（02）→ 当它出错时能定位（03）→ 最后用测试把结论钉住（04）**

四条不是并列的，是递进的。01 教你读，02 教你改，03 教你查，04 教你**防止再犯**。
跳过 01 直接做 02，你只会照抄；跳过 03 直接做 04，你写的测试抓不到真问题。

## 目录

| 目录 | 任务 | 产出 | 关键文件 |
|---|---|---|---|
| [`01-read-code/`](01-read-code/README.md) | 读开源代码 + AI review | 102 行标准库走查 + 7 个可跑实验 + review 裁决表 | `walkthrough_textwrap.md`、`review-drill.md` |
| [`02-refactor/`](02-refactor/REFACTOR-NOTES.md) | 重构简历项目代码 | 70 行面条代码 → 5 层包 + 等价性校验 + 3 个真 bug | `check_equivalence.py`、`REFACTOR-NOTES.md` |
| [`03-debug-drill/`](03-debug-drill/ANSWER-KEY.md) | 故意造 bug，用 AI 定位 | 5 关演练 + 答案册 + 提问话术对照 | `drill.py`、`ANSWER-KEY.md` |
| [`04-pytest/`](04-pytest/README.md) | pytest 入门 + 人工把关 | 12 条正式测试 + 4 个假绿测试的识别 | `test_report.py`、`REVIEW-ANSWERS.md` |
| [`05-milestone/`](05-milestone/README.md) | **里程碑 1：三道小题自己写** | 脏 CSV 清洗 / 分组汇总 / 日志统计 + 自动判分器（`grade.py`，逐项 PASS-FAIL） | `grade.py`、`data/raw_orders.csv` |

## 一键验证（四条全跑一遍）

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics

# 01 读代码：7 个实验全过
.venv\Scripts\python.exe -X utf8 ai-engineering\01-read-code\experiments.py

# 02 重构：干净数据行为不变 + 脏数据差异可解释
cd ai-engineering\02-refactor
..\..\.venv\Scripts\python.exe -X utf8 check_equivalence.py
cd ..\..

# 03 调试：5 关现象（加 --answers 看答案）
cd ai-engineering\03-debug-drill
..\..\.venv\Scripts\python.exe -X utf8 drill.py
cd ..\..

# 04 测试：12 passed, 5 xfailed
.venv\Scripts\python.exe -X utf8 -m pytest ai-engineering\04-pytest -q

# 05 里程碑：判分（三题都写完才可能全绿；先跑会看到三个「没找到产物」）
.venv\Scripts\python.exe -X utf8 ai-engineering\05-milestone\grade.py
```

## 每条任务的验收标准

**01 · 读代码**
能回答：`chunks.reverse()` 换成 `pop(0)` 会慢多少（数量级）？303 行的重算能不能删？`<=` 改成 `<` 会挂哪个用例？
标准不是"看懂了"，是**能预言改动的后果**。

**02 · 重构**
不看代码能说清：bug 1 为什么让 East 多出 1189.00？为什么 `sales_clean.csv` 只有两个区域？
把排序改成升序，`check_equivalence.py` 会在 A 段还是 B 段报红？
标准是**知道先立安全网、再动手**，而不是"会拆函数"。

**03 · 调试**
5 关的根因，**跑之前**先在纸上写出来。第 1 遍全部说对的概率不高 —— 说错的那一关才是盲区。
标准是能说出"什么条件下才暴露"，而不是"我知道这里不对"。

**04 · 测试**
不看 `REVIEW-ANSWERS.md`，指出 8 个测试里哪 4 个是假绿，并说清理由。
标准是**会否决一个测试**，而不是"会写 assert"。

## 和前面 4 步的关系

前面 ①→②→④→③ 解决的是"能不能上手"：环境、Git、怎么问 AI、跑通第一批代码。
这 4 条解决的是"代码能不能交出去"：可读、可改、可查、可测。

前一阶段的产出（`leetcode/`、`pandas/`）在这 4 条里被反复用到：
- 02 的靶子就是 pandas 那套"读 CSV → 汇总 → 出报表"的业务，只是写成了面条代码
- 03 的 5 个 bug，全在 `AI-USAGE-NOTES.md` 那 12 问的覆盖范围内
- 04 的测试对象就是 02 重构出来的模块 —— **上次重构留下的边界，这次用测试钉住**

## 一条贯穿始终的原则

四节里出现过同一个动作，四次：

| 场景 | 这个动作 |
|---|---|
| 01 review | 每条意见必须给出能复现的反例 |
| 02 重构 | 每次改动后跑等价性校验 |
| 03 调试 | 先说假设，再让 AI 否证 |
| 04 测试 | 把代码改坏，看测试红不红 |

**都是同一件事：不要相信"看起来对"，要设计一个能让它现原形的实验。**
AI 能给的是假设和候选项，判断永远在你这边 —— 而判断的依据，只能是你自己跑出来的那个结果。
