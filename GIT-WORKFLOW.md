# Git 实操手册 · 从本地到 PR

任务二《Git 基础补课》的落地文档。**没有 GitHub 账号也能完成 90% 的内容**——本文用本地远程仓库跑通全流程，注册账号后只需换一个地址。

---

## 一、先建立心智模型：三个区

Git 里最容易搞混的不是命令，而是"我的改动现在在哪"。记住这条流水线：

```
工作区                暂存区                 本地仓库              远程仓库
(你正在编辑的文件)  →  (准备提交的快照)  →  (已提交的历史)  →  (origin)
       │                    │                    │                   │
   git add ────────→ ───────┘                    │                   │
                        git commit ─────────→ ──┘                   │
                                    git push ─────────────────→ ───┘
```

| 区 | 含义 | 对应命令 |
|---|---|---|
| 工作区 | 你打开、编辑的文件本身 | `git status` 看它的状态 |
| 暂存区 | 挑选出"这次要提交哪些改动" | `git add <文件>` |
| 本地仓库 | 提交后的历史，可回溯、可分支 | `git commit` |
| 远程仓库 | 备份与协作的公共副本 | `git push` / `git pull` |

> 一句话理解 `add`：它不是"保存"，而是"**把你选中的改动放进下一次提交的篮子**"。所以一次提交里可以只放一部分文件——这就是拆出干净提交的关键。

---

## 二、日常操作循环（90% 的时间只用这 6 条）

```bash
git status                    # 1. 看现在有什么改动（最高频命令）
git pull                      # 2. 动手前先同步远程，避免冲突
git switch -c feat/xxx        # 3. 开一个新分支干活
#   ...这里写代码...
git add <文件>                # 4. 挑选改动进暂存区
git commit -m "type: 描述"    # 5. 提交
git push                      # 6. 推到远程
```

**分支命令对照**（旧写法仍可用，但新写法语义更清晰）：

| 旧写法 | 新写法 | 说明 |
|---|---|---|
| `git checkout -b feat/x` | `git switch -c feat/x` | 新建并切换分支 |
| `git checkout main` | `git switch main` | 切换分支 |
| `git checkout -- 文件` | `git restore 文件` | 丢弃工作区改动 |

---

## 三、Commit Message 规范（Conventional Commits）

格式：

```
<类型>(<范围>): <简短描述>

<正文：为什么这么改，而不是改了什么>
```

### 类型表

| 类型 | 用途 | 示例 |
|---|---|---|
| `feat` | 新功能 | `feat(leetcode): 添加两数之和题解` |
| `fix` | 修 bug | `fix(pandas): 修复空值导致的分组报错` |
| `docs` | 只改文档 | `docs: 补充 venv 使用说明` |
| `refactor` | 重构，不改行为 | `refactor: 抽取重复的读取逻辑` |
| `chore` | 杂务、依赖、配置 | `chore: 升级 pandas 到 3.0` |
| `test` | 增删改测试 | `test: 补充边界用例` |
| `style` | 格式调整 | `style: 统一缩进为 4 空格` |

### 三条硬规则

1. **祈使句、现在时**：写"添加校验"，不写"添加了校验"或"修改了…"。
2. **标题 ≤ 50 字符**，结尾**不加句号**。
3. **一个提交只做一件事**。"顺便改了别的"是最常见的坏习惯，会让代码审查和回滚都变难。

### 反例对比

```
✗ update            ← 改了什么？不知道
✗ fix bug           ← 哪个 bug？
✗ 修改了一些东西，还加了新功能，顺便格式化  ← 三件事混在一起
✓ fix(pandas): 修复 CSV 空值导致的分组报错
✓ feat: 添加环境自检脚本与依赖清单
```

---

## 四、分支与 PR 流程

分支的本质：**在一条独立的线上改东西，改完再合并回去**。这样 `main` 永远是能用的。

标准流程（本项目已实测跑通）：

```bash
# 1. 从最新的 main 开分支
git switch main
git pull
git switch -c feat/git-workflow-guide

# 2. 在新分支上干活、提交
git add GIT-WORKFLOW.md
git commit -m "docs: 添加 Git 实操手册"

# 3. 推到远程（第一次推新分支要带 -u）
git push -u origin feat/git-workflow-guide

# 4. —— 这一步在 GitHub 上是「开 Pull Request」——
#    在网页上点 "New pull request"，选 base=main ← compare=feat/xxx
#    队友 review 后点 "Merge"，线上完成合并

# 5. 本地模拟合并（无 GitHub 时用这个）
git switch main
git merge --no-ff feat/git-workflow-guide

# 6. 推回远程并清理分支
git push
git branch -d feat/git-workflow-guide
```

### 为什么用 `--no-ff`

`--no-ff`（no fast-forward）会**强制保留一条合并记录**。好处是历史里能看清"这批改动来自哪个分支"，而不是被压成一条直线。团队项目普遍这么做。

---

## 五、拿到账号后：切换到真实远程仓库

无论是 GitHub 还是 Gitee（码云），步骤完全一样，**只需三条命令**：

```bash
# 1. 在网页上新建一个空仓库（不要勾选初始化 README），拿到地址
# 2. 把本地远程地址换成真实的
git remote set-url origin <你的仓库地址>

# 3. 推上去
git push -u origin main
```

以 Gitee 为例：

```bash
git remote set-url origin https://gitee.com/你的用户名/dev-basics.git
git push -u origin main
```

> 首次推送会要求输入用户名和密码（或 Personal Access Token）。
> GitHub 已于 2021 年停用密码推送，需在 Settings → Developer settings 生成 **Personal Access Token** 代替密码。
> Gitee 则可以直接用账号密码。

命令来源可以保留本地远程作为备份——用 `git remote -v` 查看，用 `git remote rename origin local` 给旧的重命名。

---

## 六、出错了怎么办（急救手册）

| 症状 | 命令 | 说明 |
|---|---|---|
| 改乱了某个文件，想还原 | `git restore 文件` | 丢弃工作区改动，**不可恢复** |
| `add` 错了，想移出暂存区 | `git restore --staged 文件` | 保留改动，只退出暂存区 |
| 提交信息写错了（还没 push） | `git commit --amend -m "新信息"` | 改写最后一次提交 |
| 提交漏了文件（还没 push） | `git add 漏掉的文件` → `git commit --amend --no-edit` | 补进上一次提交 |
| 想看某次提交改了什么 | `git show <commit-hash>` | 显示该次提交的完整 diff |
| 想看谁改的某一行 | `git blame 文件` | 逐行标注提交者与时间 |
| 合并冲突了 | 手动编辑冲突文件 → `git add 文件` → `git commit` | 冲突标记 `<<<<<<<` 要全部删掉 |
| 想撤销刚才的合并 | `git merge --abort` | 只在合并进行中可用 |
| 想看所有分支的图形历史 | `git log --graph --oneline --all --decorate` | 最直观的历史视图 |

> ⚠️ 一旦 push 到远程，`--amend` 和 `reset` 会影响他人，除非你明确知道后果，否则**用新的提交去修正**。

---

## 七、命令速查表

```bash
# 查看状态
git status                    # 当前改动概览
git log --oneline -10         # 最近 10 条提交
git diff                      # 工作区 vs 暂存区的具体改动
git diff --staged             # 暂存区 vs 上次提交

# 提交
git add <文件>                # 暂存指定文件
git add .                     # 暂存全部（注意别误加不想提交的）
git commit -m "msg"           # 提交
git commit -am "msg"          # 暂存已追踪文件并提交（不含新增文件）

# 分支
git branch                    # 列出本地分支
git switch -c <名字>          # 新建并切换
git switch <名字>             # 切换
git branch -d <名字>          # 删除已合并分支
git branch -D <名字>          # 强制删除

# 远程
git remote -v                 # 查看远程地址
git push -u origin <分支>     # 推送并建立追踪
git pull                      # 拉取并合并远程更新
git fetch                     # 只拉取不合并（更安全，可先看再决定）

# 撤销
git restore <文件>            # 丢弃工作区改动
git restore --staged <文件>   # 移出暂存区
git revert <commit>           # 生成一个"反向提交"来抵消某次提交（安全，适合已推送）
```

---

## 八、本项目的实际操作记录（已验证）

```bash
git init -b main                          # 初始化，主分支命名 main
# → .venv/ 被 .gitignore 正确拦截（git check-ignore 验证通过）

git add .gitattributes .gitignore .vscode
git commit -m "chore: 初始化项目骨架与忽略规则"

git add hello.py requirements.txt
git commit -m "feat: 添加环境自检脚本与依赖清单"

git add README.md
git commit -m "docs: 补充开发环境搭建执行手册"

git remote add origin <仓库地址>           # 先接本地裸仓库练手，后切换为 GitHub 真实地址
git push -u origin main                   # 首次推送，建立追踪关系
# → 会触发一次浏览器授权，成功后凭证存入 Windows 凭证管理器，之后无需重复登录
```

四个提交、四种类型，各自独立、语义清晰——这就是"规范提交"的样板。

> 最终远程地址：`https://github.com/zzx130722/zzx1.git`（实测推送成功，6 个提交全部同步）。
