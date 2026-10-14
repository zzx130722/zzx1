# 学习进度

> 最后更新：2026-10-13 17:59
> 实际执行顺序已调整为 **① → ② → ④ → ③**（④ 是方法层，不依赖环境，却是 ③ 的效率前置）

## 总览

| 任务 | 状态 | 产出 |
|---|---|---|
| ① 开发环境搭建 | ✅ 完成 | `.venv/` + 全套配置，9 项实测通过 |
| ② Git 基础补课 | ✅ 完成 | 6 次规范提交，已推送到 GitHub |
| ④ Prompt 基础三原则 | 🟡 内容已产出，待实战 | [PROMPT-GUIDE.md](PROMPT-GUIDE.md) |
| ③ AI 工具初体验 | ⬜ 未开始 | 待建 `leetcode/` + `pandas/` |

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
- [x] 6 次规范提交（chore / feat / docs 三种类型 + 1 次 `--no-ff` 合并）
- [x] 走通 分支 → 提交 → 推送 → 合并 → 删分支 全流程
- [x] 推送到真实 GitHub：`https://github.com/zzx130722/zzx1`
- [ ] 熟悉 `git blame` / `git revert`（可选进阶）

## 🟡 任务四：Prompt 基础三原则

内容已写成 `PROMPT-GUIDE.md`，但**还没实际用过一次**——光看不算学会。

- [ ] 用文档里的填空模板，**自己写一个 prompt** 让我做 Two Sum
- [ ] 对比一下：笼统问法 vs 完整问法，AI 的回应差多少
- [ ] 记住自检三问：它需要猜什么？这是一件事还是几件事？有没有说"不要什么"？

## ⬜ 任务三：AI 工具初体验

- [ ] `leetcode/` 建三个题解文件
  - [ ] Two Sum（哈希表）
  - [ ] Valid Parentheses（栈）
  - [ ] Merge Two Sorted Lists（链表）
- [ ] `pandas/` 建两个 notebook
  - [ ] 读 CSV + `groupby` 聚合
  - [ ] 缺失值处理 + `merge` 合并
- [ ] **验收标准**：不看答案能自己讲出思路 + 说出边界用例（能讲出来才算过）

---

## 环境备忘

```bash
# 激活虚拟环境（Windows，Git Bash / VS Code 终端）
source .venv/Scripts/activate

# 运行自检脚本
python hello.py
```

> ⚠️ 别直接用全局 `python`：PATH 首位是工具自带的运行时，会命中错误的解释器。

## Git 现状

- 远程：`https://github.com/zzx130722/zzx1.git`（分支 `main`）
- ✅ 提交身份已统一为 `zzx130722 <341903242+zzx130722@users.noreply.github.com>`（全局配置同步更新）
- ✅ 6 个历史提交已重写作者（原先归属在 `cuishiyong` 账号下），**并已强推成功**，
  远程 6 个提交逐条核验均归属 `zzx130722`
- 本地与远程完全同步（HEAD = `3146028`）
- 备份仍在：标签 `backup-before-rewrite`（重写前的 `5288f31`），确认无误后可删除
- **待提交**：本文件、`PROMPT-GUIDE.md`、`README.md`、`GIT-WORKFLOW.md`、`.vscode/settings.json`
  → 计划并入任务三的提交
