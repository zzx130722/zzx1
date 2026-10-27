# 学习进度

> 最后更新：2026-10-22 12:00
> 实际执行顺序已调整为 **① → ② → ④ → ③**（④ 是方法层，不依赖环境，却是 ③ 的效率前置）

## 总览

| 任务 | 状态 | 产出 |
|---|---|---|
| ① 开发环境搭建 | ✅ 完成 | `.venv/` + 全套配置，9 项实测通过 |
| ② Git 基础补课 | ✅ 完成 | **10 次规范提交**，全部已推送到 GitHub |
| ④ Prompt 基础三原则 | ✅ 完成（实验 3 可选未做） | [PROMPT-GUIDE.md](PROMPT-GUIDE.md) + [PROMPT-LAB.md](PROMPT-LAB.md)（2 次实战） |
| ③ AI 工具初体验 | ✅ **产出全部完成** | [leetcode/](leetcode/README.md) 8 题 + [pandas/](pandas/README.md) 2 个 notebook |
| ＋ 额外产出 | ✅ 完成 | **[AI-USAGE-NOTES.md](AI-USAGE-NOTES.md)**（怎么和 AI 协作）+ **[WORKBUDDY-NOTES.md](WORKBUDDY-NOTES.md)**（工具本身怎么用）+ **[MY-WORKBUDDY-NOTES.md](MY-WORKBUDDY-NOTES.md)**（我自己的第一人称复盘） |
| ▶ AI 编程进阶（4 条） | ✅ **完成，待自测** | **[ai-engineering/](ai-engineering/README.md)** 读代码 / 重构 / 调试 / pytest，四节都有可跑脚本 |
| ▶ 里程碑 1（3 道小题） | 🟡 **材料就位，代码待自己写** | **[ai-engineering/05-milestone/](ai-engineering/05-milestone/README.md)** 清洗 / 汇总 / 日志统计 + 17 项自动判分 |
| ▶ 下一阶段 | 🟡 **第 2 周代码备好，等 key** | **[week2-llm/](week2-llm/README.md)** 6 天任务全做成文件：curl/单次调用/封装/多轮 CLI，差注册 DeepSeek 填 `.env` | 计划全文：**[ai-plan/AI-LEARNING-PLAN.md](ai-plan/AI-LEARNING-PLAN.md)** + [进度看板](ai-plan/roadmap.html) |

---

## ✅ 任务一：开发环境搭建

- [x] Git 2.55.0 / Python 3.13.3 / Node v22.22.2 / VS Code 1.121.0 —— 均已就绪
- [x] 虚拟环境 `.venv`（用系统 Python 绝对路径创建，避开 PATH 首位的工具运行时）
- [x] 依赖：pandas 3.0.6、numpy 2.5.4、ipykernel 7.4.0
- [x] VS Code 插件 27 个（含 Jupyter、Ruff）
- [x] `.vscode/settings.json` 锁定解释器为 `.venv`
- [x] 自检脚本 `hello.py` 实测 `in_venv = 是`
- [ ] AI 助手登录账号（可选，用 WorkBuddy 本身即可跳过）

## ✅ 任务二：Git 基础补课

- [x] `.gitignore` 生效验证（`.venv` 被追踪文件数 = 0）
- [x] `.gitattributes` 统一换行符
- [x] 10 次规范提交（chore / feat / docs 三种类型 + 1 次 `--no-ff` 合并）
- [x] 走通 分支 → 提交 → 推送 → 合并 → 删分支 全流程
- [x] 推送到真实 GitHub：`https://github.com/zzx130722/zzx1`
- [x] 提交作者统一归属到自己的账号（重写历史 + 强推验证）
- [ ] 熟悉 `git blame` / `git revert`（可选进阶）

## 🟡 任务四：Prompt 基础三原则

内容已写成 [PROMPT-GUIDE.md](PROMPT-GUIDE.md)，并已在 [PROMPT-LAB.md](PROMPT-LAB.md) 里开始记录实战。

- [x] **实验 1**（2026-10-14）：把 Two Sum 题目原文直接当 prompt 丢过来
      → 8 个槽位只填了 1 个；但项目上下文自动补齐了 3 个，结果仍可用
- [x] **实验 2**（2026-10-14）：重写同一个需求，补上 3 个示例 + 目标 + 风格 → **4 / 8**
      → 发现新问题：**约束之间会打架**（"最简单的代码" vs "能过 LeetCode" 是两个方向）
- [ ] **实验 3**（可选）：试"先让 AI 列出各层次解法，再挑一个"的问法，看是否更省事
- [ ] 记住自检三问：它需要猜什么？这是一件事还是几件事？有没有说"不要什么"？
- [ ] 多一条自检：**我写的几条约束之间，彼此矛盾吗？**

全部记录见 [PROMPT-LAB.md](PROMPT-LAB.md)。

## ✅ 任务三：AI 工具初体验

**产出全部完成**：LeetCode 8 题 + pandas 2 个 notebook。剩下的是**验收动作**（见本节末尾）。

- [x] `leetcode/` 四个题解文件（各含题目、思路、复杂度、边界用例与自测）
  - [x] Two Sum（哈希表）—— 最易错：`[3,3], target=6` 必须返回 `[0,1]`
  - [x] Valid Parentheses（栈）—— 最易错：`"([)]"` 数量对但顺序错
  - [x] Merge Two Sorted Lists（链表 / 双指针）—— 最易错：`[] + [0]`
  - [x] Search Insert Position（二分查找）—— 最易错：`target=7` 要返回 `len(nums)`
- [x] `leetcode/run_all.py` 一键自测入口
- [x] `leetcode/LEETCODE-HOWTO.md` —— 怎么把题解提交到 LeetCode 网站
      （含格式差异表、七步操作、八种常见报错对照）
- [x] `leetcode/submit/` —— **八道题的可直接粘贴版**（一个文件一道题，整文件复制即可）
  - [x] 回文数（9）—— 只反转后一半数字；两个前置判断：负数、末位 0 但不是 0 本身
        （漏掉后者时 `10`/`100`/`1000` 都会误判为回文，但 `120` 反而对 —— 很难靠随手试发现）
  - [x] 子数组不同元素数目的平方和 I（2913，n ≤ 100，暴力 O(n²)）
  - [x] 子数组不同元素数目的平方和 II（2916，n ≤ 10⁵，树状数组 O(n log n) + 取模）
        —— **两题题目描述一字不差**，只有数据范围和取模不同；拿 I 去交 II 会 TLE（实测约 166s vs 0.58s）
  - [x] 组合两个表（175，SQL 题）—— **格式与算法题完全不同**：没有 `class Solution`、
        没有方法名，直接交一条查询语句；考点是 `LEFT JOIN`（没有地址的人也要保留）
- [x] `leetcode/verify_submit.py` —— 模拟 LeetCode 判题环境校验粘贴版，**64 项全通过**
- [x] `leetcode/verify_sql.py` —— 用 SQLite 实跑校验 SQL 版，**5 项全通过**
      （比对「行」与「列名」；附三种错误写法对照，确认检查真的有效）
- [x] 面向零基础的逐行讲解 + 可交互图解
  - [x] [two_sum_walkthrough.md](leetcode/two_sum_walkthrough.md) + [two_sum_visual.html](leetcode/two_sum_visual.html)
  - [x] [search_insert_walkthrough.md](leetcode/search_insert_walkthrough.md) + [search_insert_visual.html](leetcode/search_insert_visual.html)
  - [x] [subarrays_squares_walkthrough.md](leetcode/subarrays_squares_walkthrough.md)（平方和 II，含贡献转化推导）
- [ ] **在 LeetCode 网站上实际提交通过一题**（拿到绿色「通过」）—— 代码已备好，就差你点提交
- [ ] **验收（关键）**：不看代码，能用自己的话复述每道题的思路 + 说出最易错的边界用例
- [x] `pandas/` 建两个 notebook（2026-10-22 完成）
  - [x] [01_sales_groupby.ipynb](pandas/01_sales_groupby.ipynb) —— 读 CSV + `groupby` 聚合
        （含 BOM 编码坑、`to_datetime`、命名聚合、`reset_index`、多列分组、透视表）
  - [x] [02_missing_and_merge.ipynb](pandas/02_missing_and_merge.ipynb) —— 缺失值处理 + `merge` 合并
        （核心是 **merge 前查主键唯一性**：40 行订单 merge 后变 44 行，不去重金额会被算两遍）
  - [x] [pandas/make_data.py](pandas/make_data.py) —— 固定种子生成示例数据，重跑 MD5 一致
  - [x] 两个 notebook 已实际执行，**0 个错误单元格**（29 个代码格全部跑通）

### 任务三还差什么（三件都是"只能自己做"的）

| 待办 | 说明 |
|---|---|
| ⬜ 在 LeetCode 网站提交一次 | `submit/` 里 8 份代码都已备好，选最短的 SQL 题（3 行）最省事 |
| ⬜ 复述思路 | 不看代码，能讲清每道题为什么这么做、最易错哪个用例 |
| ⬜ 做完 pandas 两个 notebook 的「自己动手」 | 每个末尾有 2-3 个小任务，跑通不算完成，能答出来才算 |

---

## ▶ AI 编程进阶（4 条，10-22 新增）

> 入口：[ai-engineering/README.md](ai-engineering/README.md)
> 主线：**读懂别人的代码 → 改造自己的代码 → 出错时能定位 → 用测试钉住结论**

| 任务 | 状态 | 产出 | 一键验证 |
|---|---|---|---|
| ⑤ 读开源代码 + AI review | ✅ 完成 | `textwrap._wrap_chunks` 102 行逐段走查、7 个「问→猜→验」实验、7 条 review 意见裁决（2 听 / 4 错 / 1 看上下文） | `python -X utf8 ai-engineering/01-read-code/experiments.py` |
| ⑥ 重构简历项目代码 | ✅ 完成 | 70 行面条脚本 → 5 层包（models/errors/loader/report/cli）+ 类型注解 + `Decimal` + 自定义异常；**顺手找出 3 个真 bug** | `python -X utf8 check_equivalence.py`（在 02-refactor 目录） |
| ⑦ 造 bug 练定位 | ✅ 完成 | 5 关演练：可变默认参数 / 返回内部引用 / 整除丢零头 / try 范围过大 / 字符串排序 | `python -X utf8 drill.py`（03-debug-drill 目录） |
| ⑧ pytest + 人工把关 | ✅ 完成 | 12 条正式测试 + 5 条 `xfail(strict=True)` 契约测试 + 8 个 AI 测试里识别 4 个假绿 | `pytest ai-engineering/04-pytest -q` → 12 passed, 5 xfailed |

### 三条可复用的结论

1. **重构的第一步不是拆函数，是立安全网。** `check_equivalence.py` 先跑通"干净数据逐字节一致"，
   之后每改一处都跑它；干净数据都过不了的改动，没资格谈"重构"。
2. **数据静默缺失比程序崩溃危险。** 原版 `except: pass` 让 4 行数据只读到 1 条却一声不吭；
   正确做法是跳过坏行 + 打警告，而不是把错误变成 0。
3. **能说清"改坏什么会让它红"的测试才是测试。** 实测把 `format_amount` 改成 `return "WRONG"` 后，
   8 个 AI 测试里仍有 7 个绿着（`4 failed, 7 passed`）。

### 还差什么（只能自己做）

| 待办 | 说明 |
|---|---|
| ⬜ 03 的 5 关先写根因再看答案 | 跑 `drill.py` **不要**加 `--answers`，纸上写完再对 |
| ⬜ 04 的 4 个假绿自己指出来 | 读 `ai_tests_to_review.py`，判断完再看 `REVIEW-ANSWERS.md` |
| ⬜ 01 的作业：自己读 `csv.DictReader` | 三个问题在 `walkthrough_textwrap.md` 末尾 |
| ⬜ 02 若换成真实简历项目 | 把 `legacy_sales_report.py` 换成你的实训代码，其余流程原样套用 |

---

## ▶ 里程碑 1：三道小题，自己写（10-27 新增）

> 入口：[ai-engineering/05-milestone/README.md](ai-engineering/05-milestone/README.md)
> 对应学习计划第 2 周右列的最后一格：**给 3 个小任务，全程 AI 辅助独立完成，能逐行讲清逻辑**

| # | 题 | 输入 → 输出 | 考什么 |
|---|---|---|---|
| 1 | 脏 CSV 清洗 | `data/raw_orders.csv` → `out/t1_clean.csv` | 去重规则、金额去 `$`/千分位、两种日期格式、region 归一化 |
| 2 | 分组汇总 | 第 1 题的输出 → `out/t2_report.txt` | 分组、字母序、`TOTAL` 行的均值分母 |
| 3 | 日志按月统计 | `data/hits.log` → `out/t3_hits.tsv` | 正则取字段、月份映射、坏行计数 |

判分器 `grade.py` 逐项 PASS/FAIL（17 项），**只判对错，不给改法**：

```powershell
.venv\Scripts\python.exe -X utf8 ai-engineering\05-milestone\grade.py
```

- 判分器本身验过：正确产物 17/17 绿；把「保留旧订单 / region 没归一化 / North 总额少 100 /
  删掉 `#dropped` 行」四处改坏，四处都被抓到并指出第几条不一样
- ⚠️ `grade.py` 末尾 `EXPECTED_*` 就是答案，建议先自己写
- 状态：⬜ **代码待自己写**（材料已就位），三道都过之后还要过「六问自检」才算闭环

---

## 环境备忘

```bash
# 激活虚拟环境（Windows，Git Bash / VS Code 终端）
source .venv/Scripts/activate

# 运行自检脚本
python hello.py

# 一键跑四道简单题题解的自测
python leetcode/run_all.py

# 校验 submit/ 下的 Python 粘贴版（模拟 LeetCode 判题环境）
python leetcode/verify_submit.py

# 校验 submit/ 下的 SQL 粘贴版（SQLite 实跑）
python leetcode/verify_sql.py
```

> ⚠️ 别直接用全局 `python`：PATH 首位是工具自带的运行时，会命中错误的解释器。

## Git 现状

- 远程：`https://github.com/zzx130722/zzx1.git`（分支 `main`）
- ✅ 提交身份已统一为 `zzx130722 <341903242+zzx130722@users.noreply.github.com>`（全局配置同步更新）
- ✅ **10-22 11:00 核验：远程 `main` HEAD = `9376535`，与当时本地完全一致**
  （10-15 起累积的 35 个待推提交已全部推完，GitHub API 逐条核验通过）
- 之后本地又累积了 AI 编程进阶四节的产出，用系统终端推一次即可同步
- 仓库追踪文件 46 项（`.venv` 仍未追踪）
- 备份标签仍在：`backup-before-rewrite`（重写前的 `5288f31`），确认无误后可删除

## 推送备忘（重要）

**推送必须用系统终端，不能用工具打开的 VS Code 集成终端。**

后者的环境变量里带着沙箱代理，访问 github.com 会报 `CONNECT tunnel failed, response 502`。
做法：`Win + R` → `powershell` → 切到项目目录 → 执行两条命令：

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics
git push
```

（凭证已缓存，不会再要求登录。）推完可以再跑一次 `git status` 确认显示
`Your branch is up to date with 'origin/main'`。
