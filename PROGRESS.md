# 学习进度

> 最后更新：2026-10-14 11:45
> 实际执行顺序已调整为 **① → ② → ④ → ③**（④ 是方法层，不依赖环境，却是 ③ 的效率前置）

## 总览

| 任务 | 状态 | 产出 |
|---|---|---|
| ① 开发环境搭建 | ✅ 完成 | `.venv/` + 全套配置，9 项实测通过 |
| ② Git 基础补课 | ✅ 完成 | **10 次规范提交**，全部已推送到 GitHub |
| ④ Prompt 基础三原则 | 🟡 已开始实战（见 PROMPT-LAB） | [PROMPT-GUIDE.md](PROMPT-GUIDE.md) + [PROMPT-LAB.md](PROMPT-LAB.md) |
| ③ AI 工具初体验 | 🟡 LeetCode 3 题已完成 | [leetcode/](leetcode/README.md)，待做 Pandas ×2 |

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

## 🟡 任务三：AI 工具初体验

**LeetCode 部分已完成**（3 题 / 25 个用例全部通过），Pandas 部分未开始。

- [x] `leetcode/` 三个题解文件（各含题目、思路、复杂度、边界用例与自测）
  - [x] Two Sum（哈希表）—— 最易错：`[3,3], target=6` 必须返回 `[0,1]`
  - [x] Valid Parentheses（栈）—— 最易错：`"([)]"` 数量对但顺序错
  - [x] Merge Two Sorted Lists（链表 / 双指针）—— 最易错：`[] + [0]`
- [x] `leetcode/run_all.py` 一键自测入口
- [x] `leetcode/LEETCODE-HOWTO.md` —— 怎么把题解提交到 LeetCode 网站
      （含可逐字粘贴的代码、七步操作、八种常见报错对照；粘贴版已按判题调用方式实测 20/20）
- [ ] **在 LeetCode 网站上实际提交通过一题**（拿到绿色「通过」）
- [ ] **验收（关键）**：不看代码，能用自己的话复述每道题的思路 + 说出最易错的边界用例
- [ ] `pandas/` 建两个 notebook
  - [ ] 读 CSV + `groupby` 聚合
  - [ ] 缺失值处理 + `merge` 合并

---

## 环境备忘

```bash
# 激活虚拟环境（Windows，Git Bash / VS Code 终端）
source .venv/Scripts/activate

# 运行自检脚本
python hello.py

# 一键跑三道 LeetCode 题解的自测
python leetcode/run_all.py
```

> ⚠️ 别直接用全局 `python`：PATH 首位是工具自带的运行时，会命中错误的解释器。

## Git 现状

- 远程：`https://github.com/zzx130722/zzx1.git`（分支 `main`）
- ✅ 提交身份已统一为 `zzx130722 <341903242+zzx130722@users.noreply.github.com>`（全局配置同步更新）
- ✅ **10 个提交全部在远程**，逐条核验 GitHub 上均归属 `zzx130722`
- 本地与远程完全同步（HEAD = `a42489d`），无 ahead / behind
- 工作区**完全干净**，无未提交改动
- 仓库文件 9 项（`.venv` 未被追踪，验证通过）
- 备份仍在：标签 `backup-before-rewrite`（重写前的 `5288f31`），确认无误后可删除

## 推送备忘（重要）

**推送必须用系统终端，不能用工具打开的 VS Code 集成终端。**

后者的环境变量里带着沙箱代理，访问 github.com 会报 `CONNECT tunnel failed, response 502`。
做法：`Win + R` → `powershell` → `cd` 到项目 → `git push`（凭证已缓存，不会再要求登录）。
