# EXPLAIN · 每项配置为什么这么配

> 验收要求：AI 帮配置，但你必须能解释。本文按「如果有人问你为什么」的口径写。

## 1. 项目结构

### 为什么用 src/tests/docs 分层？

| 层 | 放什么 | 为什么单独放 |
|---|---|---|
| `src/devbasics/` | 包本体 | 只有这层会被安装。它是「产品」 |
| `tests/` | pytest 测试 | 不随包发布。它是「质检」 |
| `docs/` | 讲解文档 | 不参与运行。它是「说明书」 |

**src 布局 vs 扁平布局**：扁平布局（包目录直接在仓库根）有个经典坑——
你在仓库根跑 `python`，`import devbasics` 会命中当前目录的源码，
**根本没测到安装后的包**；打包配置写错（比如漏了某个子包）本地永远发现不了。
src 布局下 `import devbasics` 只有安装后才可能成功，测试测的就是用户装到的东西。

### 为什么配 pyproject.toml？

它是 PEP 518 定下的标准：**一个文件声明项目的一切**——叫什么、依赖谁、
用什么后端打包、black/ruff 怎么配。老一代的 `setup.py` / `setup.cfg` / `requirements.txt`
三件套正在被它统一。关键两段：

- `[build-system]`：声明用 setuptools 打包。打包工具本身也是依赖，也要声明
- `[tool.setuptools.packages.find] where = ["src"]`：告诉打包工具去 src/ 找包。
  这行没写对，`pip install` 装出来就是个空包

### 虚拟环境

沿用仓库根的 `.venv`（任务一建的）。包以**可编辑模式**安装：
`pip install -e "week3-package[dev]"`。
`-e` 的意思是在 site-packages 里放一个**指回源码目录的链接**而不是复制——
你改了 src 下的代码，import 立刻生效，不用重装。`[dev]` 表示顺带装上
`[project.optional-dependencies]` 里的 dev 组工具（pytest/black/ruff/pre-commit）。

## 2. 质量工具链

### black（格式化器，只管「怎么写」）

- 行宽 **88**：black 默认值。别改成 79（PEP 8 老标准）或 120——改了就失去
  black「全社区一个格式、零争论」的意义
- 只负责格式，**不做逻辑检查**。它改你的代码永远不改变行为
- 配置写在 `[tool.black]`，不建 `.black` 文件

### ruff（linter，只管「写得对不对」）

一个 Rust 写的极快 linter，替代 flake8 + isort + 一堆插件的组合。
`[tool.ruff.lint] select` 里每组代码的含义：

| 代码 | 来源 | 抓什么 |
|---|---|---|
| E / W | pycodestyle | 风格（行太长、多余空格） |
| F | pyflakes | 真问题：未使用的 import/变量、未定义的名字 |
| I | isort | import 排序（标准库/三方/本地分组） |
| B | flake8-bugbear | 常见 bug 模式（比如可变默认参数） |
| UP | pyupgrade | 过时写法升级（如 `typing.List` → `list`） |

**black 和 ruff 为什么不打架**：分工明确——black 管格式，ruff 的 E 类检查
在 black 格式化后自然通过；ruff 不做格式化（那条产品线叫 ruff format，我们没启用）。

### pre-commit（提交前自动跑上面两个）

原理：`pre-commit install` 往 `.git/hooks/pre-commit` 写一个脚本，
每次 `git commit` 时先执行 `.pre-commit-config.yaml` 里列的钩子，任何一项失败就**中止提交**。

配置里每个钩子三要素：

```yaml
repo: https://github.com/psf/black   # 钩子代码从哪拉（pre-commit 会建独立虚拟环境装它）
rev: 26.10.1                         # 锁定版本——不锁的话哪天钩子升级，提交会莫名挂掉
hooks: [{id: black}]                 # 跑它仓库里的哪个钩子
```

三个钩子的分工：`ruff`（只 lint，带 `--fix` 能自动修一部分）、`black`（格式）、
`pre-commit-hooks` 仓库里的 `end-of-file-fixer` / `trailing-whitespace`（文件末尾换行、行尾空白——防两类最无意义的 diff）。

**作用域为什么只圈 `week3-package/`**：配置里一行 `files: ^week3-package/`，
钩子就只检查新包。旧目录（week2-llm、pandas 等）写于工具链建立之前，
ruff 按新标准会报 81 个历史风格问题——工具链刚上就大规模重写旧代码，
diff 会大到没法 review，这是工程上的大忌。等以后想把某个旧目录收编进包时，
修一个、放行一个（删掉 files 前缀或改正则）。

**失败时怎么办**：black/自动修复类钩子会直接改文件 → 重新 `git add` 再 commit 一次即可；
ruff 报的真问题 → 改代码。第一次跑会下载钩子，慢是正常的。

## 3. 收编时的两个设计决定

1. **题解只收函数、不收 `main()` 自测**：原文件里的自测循环是脚本思维；
   包里测试统一由 pytest 承担（tests/ 目录），用例一个不少，只是换成了参数化写法。
2. **LLM 客户端砍掉 config.py、改读环境变量**：原版 config.py 在 import 时读
   `week2-llm/.env`——脚本这样没问题，但「包」是装到别人机器上用的，
   包的代码去读写**调用方当前目录**的 .env 是越权行为。
   改成调用时读环境变量（谁调用谁设置），并支持 keyword 参数覆盖，测试可以不碰网络。

## 一句话版本（面试口径）

> src 布局保证测试测的是装出来的包；pyproject.toml 一个文件管元数据、依赖和工具配置；
> black 管格式（88 列默认值）、ruff 管 lint（E/F/W/I/B/UP）、pre-commit 把它们挂在
> git commit 上，rev 锁死版本保证团队里所有人钩子行为一致。
