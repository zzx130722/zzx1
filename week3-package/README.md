# week3-package · 规范化 Python 包（devbasics）

第 3 周任务产出：把阶段一的练习收编成一个符合工程规范的 Python 包。

## 项目结构（src / tests / docs 三层）

```
week3-package/
├── pyproject.toml          # 项目元数据 + 依赖 + black/ruff 配置，一个文件管全部
├── README.md
├── docs/
│   └── EXPLAIN.md          # 每项配置为什么这么配（讲解文档，验收用）
├── src/
│   └── devbasics/          # 包本体——只有这一层会被安装、被别人 import
│       ├── __init__.py
│       ├── leetcode/       # 阶段一 leetcode/ 的 4 个题解
│       └── llm/            # 阶段一 week2-llm 的 chat 客户端
└── tests/                  # pytest 测试，只在这里 import 包，不参与安装
```

**为什么源码放 `src/` 而不是仓库根**：src 布局强迫你「装了才能 import」，
测试跑的一定是安装后的包，而不是恰好因为在当前目录才 import 成功的本地文件——
这类「本地能跑、装完就坏」的 bug，扁平布局要等别人装了才发现。

## 收编了什么

| 来源 | 去处 | 改动 |
|---|---|---|
| `leetcode/two_sum.py` 等 4 个题解 | `src/devbasics/leetcode/` | 只收算法函数，`main()` 自测改由 pytest 承担；完整思路走查仍在原文件 |
| `week2-llm/client.py` | `src/devbasics/llm/client.py` | **config.py 被干掉**，key/base_url/model 改为调用时读环境变量（包不该去读写调用方目录的 .env） |

## 怎么跑（在仓库根目录）

```powershell
# 1. 装包（可编辑模式）+ 开发工具，用仓库已有的 .venv
.venv\Scripts\pip.exe install -e "week3-package[dev]"

# 2. 跑测试
.venv\Scripts\python.exe -m pytest week3-package\tests -v

# 3. 质量检查
.venv\Scripts\ruff.exe check week3-package
.venv\Scripts\black.exe --check week3-package

# 4. pre-commit（首次要先 install，之后每次 git commit 自动跑）
.venv\Scripts\pre-commit.exe install
.venv\Scripts\pre-commit.exe run --all-files
```

## 使用示例

```python
from devbasics.leetcode import two_sum, search_insert, is_valid
from devbasics.llm import chat

two_sum([2, 7, 11, 15], 9)   # [0, 1]
search_insert([1, 3, 5, 6], 5)  # 2

# 需要环境变量 LLM_API_KEY（可选 LLM_BASE_URL / LLM_MODEL）
chat([{"role": "system", "content": "你是助手"}, {"role": "user", "content": "你好"}])
```
