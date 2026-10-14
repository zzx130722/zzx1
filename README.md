# dev-basics · 开发环境搭建执行手册

任务一《开发环境搭建》的落地项目。当前状态：**基础环境已就绪，虚拟环境已建好并验证通过**。

---

## 一、环境现状体检结果

| 组件 | 状态 | 版本 / 路径 |
|---|---|---|
| 操作系统 | 已确认 | Windows 10 (19045) |
| Git | 已安装 | 2.55.0.windows.3，`C:\Program Files\Git` |
| Python | 已安装 | 3.13.3，`C:\Users\Administrator\AppData\Local\Programs\Python\Python313` |
| VS Code | 已安装 | 1.121.0（用户级），`code` 命令可用 |
| Node.js | 已安装 | v22.22.2 |
| 虚拟环境 | 已创建 | `.venv/`（Python 3.13.3） |
| pandas | 已安装 | 3.0.6（含 numpy 2.5.4） |
| VS Code 插件 | 已就绪 | 27 个，含 Jupyter / Ruff / Pylance / Black / GitLens |
| AI 编码插件 | 已就绪 | CodeGeeX + Copilot Chat（VS Code 内置，登录即用） |

> 结论：**任务一的环境部分已全部完成**，唯一剩余动作是登录 AI 助手账号。

---

## 二、⚠️ 多版本 Python 的坑（务必先看）

`where python` 在这台机器上会依次列出 **4 个** Python：

```
C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe   <-- WorkBuddy 内置运行时
C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe      <-- 你的项目基准（本环境用它建的）
C:\Users\Administrator\AppData\Local\Programs\Python\Python37\python.exe
C:\Users\Administrator\AppData\Local\Programs\Python\Python39\python.exe
```

**问题**：排第一的是工具内置运行时，直接敲 `python` 会命中它，而它不该承载你的项目环境（可能随工具升级被替换）。

**做法**：
- 建虚拟环境时用绝对路径指向 Python313（本项目已这样做）。
- 日常开发**不要**直接敲全局 `python`，先激活 `.venv`，让 `.venv` 的解释器接管。

---

## 三、虚拟环境的完整操作流程（Windows）

```bash
# 1. 进入项目
cd C:/Users/Administrator/WorkBuddy/2026-10-13-16-35-32/dev-basics

# 2. 激活（Git Bash）
source .venv/Scripts/activate
# PowerShell:  .venv\Scripts\Activate.ps1
# CMD:         .venv\Scripts\activate.bat

# 3. 验证已激活：命令行前缀应出现 (.venv)
which python        # 应指向 .venv/Scripts/python.exe

# 4. 装包（激活后可直接用 pip）
pip install -r requirements.txt

# 5. 退出
deactivate
```

**记牢三条铁律**：

1. **每个项目一个 venv**，不要把包装进全局 Python。
2. **`.venv/` 永不提交**（已写入 `.gitignore`）。
3. **装完包要更新 `requirements.txt`**：`pip freeze > requirements.txt`。

---

## 四、验收标准（跑通即毕业）

```bash
cd dev-basics
./.venv/Scripts/python.exe hello.py
```

期望输出：

```
环境自检
----------------------------------
Python 版本  : 3.13.3
解释器路径   : ...\dev-basics\.venv\Scripts\python.exe
是否在虚拟环境: 是
操作系统     : Windows 10
pandas 版本  : 3.0.6
----------------------------------
结论：环境正常，可以开始写代码了。
```

- [x] Python 可执行，版本 ≥ 3.11
- [x] venv 可创建、可激活，`sys.prefix != sys.base_prefix`
- [x] pip 能装包，`requirements.txt` 可复现依赖
- [x] VS Code 能识别 `.venv` 为解释器、补全与跳转正常
- [x] VS Code 插件补齐（Jupyter / Ruff 已装，共 27 个）
- [x] Notebook 内核 `ipykernel` 已装（任务三的 Pandas 练习前提）
- [ ] AI 助手登录账号后在编辑器内可用（需手动登录一次，无法自动完成）

---

## 五、VS Code 插件（安装状态与两种装法）

### 5.1 当前状态

**已全部就绪（27 个）**，关键插件：

| 插件 | ID | 用途 |
|---|---|---|
| Python | `ms-python.python` | 语言支持、运行调试 |
| Pylance | `ms-python.vscode-pylance` | 类型推断、智能补全 |
| Debugpy | `ms-python.debugpy` | 断点调试 |
| Black Formatter | `ms-python.black-formatter` | 保存自动格式化 |
| **Jupyter** | `ms-toolsai.jupyter` | 任务三的 Pandas notebook |
| **Ruff** | `charliermarsh.ruff` | 极快的 linter |
| GitLens | `eamodio.gitlens` | 任务二的 Git 可视化 |
| CodeGeeX | `aminer.codegeex` | AI 补全（可直用） |
| Copilot Chat | `github.copilot-chat` | VS Code 1.121 **内置**，登录即用 |

### 5.2 方法 A：图形界面（3 步）

1. 左侧活动栏点**扩展**图标（四个方块），或按 `Ctrl+Shift+X`
2. 搜索框输入插件名，例如 `jupyter`
3. 在结果里点**安装**（Install）；需要账号的插件装完会提示登录

### 5.3 方法 B：命令行（推荐，可批量、可写进脚本）

```bash
code --install-extension <插件ID>        # 安装
code --list-extensions                   # 列出已装
code --uninstall-extension <插件ID>      # 卸载
code --install-extension <插件ID> --force  # 强制更新到最新版
```

本项目实际使用的命令：

```bash
code --install-extension ms-toolsai.jupyter
code --install-extension charliermarsh.ruff
```

### 5.4 常见问题

- **搜索转圈 / 装不上**：国内网络访问插件市场常超时。可换镜像，或从
  `marketplace.visualstudio.com` 下载 `.vsix` 文件后离线安装：
  `code --install-extension 文件路径.vsix`
- **提示无法降级**：说明该插件是 VS Code 内置版，无需安装。`github.copilot-chat` 就是这种情况。
- **团队共享**：把插件 ID 写进 `.vscode/extensions.json`，队友打开项目会自动收到安装提示（本项目已配置）。

> AI 助手备选：不想用 Copilot 可装 **Continue**（`Continue.continue`）或 **Cline**（`saoudrizwan.claude-dev`），两者支持接自己的模型。

---

## 六、目录结构

```
dev-basics/
├── .git/                   # Git 仓库（已初始化，分支 main）
├── .venv/                  # 虚拟环境（已创建，不提交）
├── .vscode/
│   ├── settings.json       # 已锁定解释器为 .venv，保存自动格式化
│   └── extensions.json     # 推荐插件清单
├── .gitattributes          # 统一换行符为 LF
├── .gitignore              # 已包含 venv / 缓存 / 密钥 / Jupyter 检查点
├── hello.py                # 环境自检脚本
├── requirements.txt        # 依赖清单
├── GIT-WORKFLOW.md         # 任务二：Git 实操手册
├── PROMPT-GUIDE.md         # 任务四：Prompt 三原则 + 可复用模板
├── PROGRESS.md             # 学习进度看板（四任务状态 + 勾选清单）
└── README.md               # 本文件
```

后续任务三的产物建议放这里：`leetcode/`（3 个题解）+ `pandas/`（2 个 notebook）。

### 相关文档

- **任务一（本文件）**：环境搭建、多版本 Python 陷阱、插件安装、全量验收报告
- **[GIT-WORKFLOW.md](GIT-WORKFLOW.md)**：任务二 Git 实操手册——三区模型、规范提交、分支与 PR 流程、急救手册
- **[PROMPT-GUIDE.md](PROMPT-GUIDE.md)**：任务四 Prompt 三原则——上下文给足 / 任务拆小 / 约束明确，含填空模板与四个实战范例
- **[PROGRESS.md](PROGRESS.md)**：学习进度看板——四个任务的完成状态、逐项勾选清单与环境备忘

### Git 现状

仓库已推送到 GitHub：**[zzx130722/zzx1](https://github.com/zzx130722/zzx1)**，6 次提交全部同步。

远程 `origin` 曾临时指向本地裸仓库（`../local-remote/dev-basics.git`），用于在没有账号时练通 push / PR 全流程；现已切换为 GitHub 真实地址。切换方式见 GIT-WORKFLOW.md 第五节。

---

## 七、全量验收报告（2026-10-13 实测）

| # | 检查项 | 命令 | 结果 |
|---|---|---|---|
| 1 | Git | `git --version` | ✅ 2.55.0.windows.3 |
| 2 | Python | `python --version` | ✅ 3.13.3 |
| 3 | Node.js | `node --version` | ✅ v22.22.2 |
| 4 | VS Code | `code --version` | ✅ 1.121.0 |
| 5 | 虚拟环境 | `python hello.py` | ✅ in_venv = 是 |
| 6 | 依赖可用性 | `import pandas, numpy, ipykernel` | ✅ 3.0.6 / 2.5.4 / 7.4.0 |
| 7 | VS Code 插件 | `code --list-extensions` | ✅ 27 个 |
| 8 | Git 身份 | `git config --global user.name` | ✅ cuishiyong |
| 9 | AI 助手登录 | — | ⬜ 待手动登录 |

### 两个可选但推荐的 Git 配置

`git config --global` 目前只配了身份，下面两项**未设置**。它们不影响任务二能否跑通，但会影响提交的整洁度：

```bash
# 1. 新仓库默认分支用 main（避免默认 master 与 GitHub 不一致）
git config --global init.defaultBranch main

# 2. Windows 换行符处理：提交时把 CRLF 转成 LF，避免 diff 里满屏 ^M
git config --global core.autocrlf true
```

未设置 `core.autocrlf` 是 Windows 上提交历史出现"整文件改动"假象的最常见原因，建议在任务二开始前配好。
