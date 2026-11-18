# Week 4 · RAG 文档问答 Demo

> 对应任务卡「阶段二 · 工程内化 / 第 4 周：LLM 应用开发入门」。
> 模型：智谱 `glm-4-flash` + `embedding-3`，走 OpenAI 兼容接口，沿用第 2 周的 `week2-llm/.env`。
> 两个交付物：本目录的可运行 Demo，以及 `docs/ARCHITECTURE.md`（一页架构说明）。

## 三步跑起来

在 `dev-basics` 仓库根目录执行：

```powershell
.venv\Scripts\python.exe -X utf8 week4-rag\ask.py --rebuild
.venv\Scripts\python.exe -X utf8 week4-rag\ask.py "报销超过 5000 元要谁签字？"
.venv\Scripts\python.exe -X utf8 week4-rag\verify.py
```

`-X utf8` 不能省：Windows 控制台默认 GBK，脚本里 print 中文会乱码（不是代码错）。
`--rebuild` 只在**文档换过**时才需要跑，它会重新调 embedding 接口并写入 `data/index.json`。

不带问题参数就是连续问答模式，输入 `q` 退出：

```powershell
.venv\Scripts\python.exe -X utf8 week4-rag\ask.py
```

框架版（任务卡点名的 LangChain，安装了依赖才能跑）：

```powershell
.venv\Scripts\python.exe -X utf8 week4-rag\langchain_demo.py "一线城市住宿每晚上限是多少？"
```

## 可选：换成自己的团队文档（本周不必做）

> 2026-11-18 已确认：本周就沿用示例语料 `data/team-handbook.md` 交付，不替换真实文档。
> 下面三步只在以后真要换语料时才需要，跳过不影响本周验收。

1. 用真实内容替换 `data/team-handbook.md`，**保留 `## 小节标题` 这种二级标题**——程序靠它切分，标题还会作为答案来源。
2. 跑一次 `ask.py --rebuild` 重建索引。
3. 跑 `verify.py`，按里面的真实问题改写 `CASES`，然后**重新标定 `MIN_SCORE`**：看输出里"资料内的最低相似度"和"资料外的最高相似度"，阈值取两者中间。当前 0.55 只适用于这份示例语料。

## 换模型

改 `week2-llm/.env`（和 `week2-llm/client.py` 共用凭据，不另存一份 Key）：

| 变量 | 当前值 | 说明 |
|---|---|---|
| `LLM_API_KEY` | — | 智谱 Key，绝不写进代码；`.env` 已被 .gitignore 挡住 |
| `LLM_BASE_URL` | `https://open.bigmodel.cn/api/paas/v4` | 换 DeepSeek / 通义只需改这一行 |
| `LLM_MODEL` | `glm-4-flash` | 对话模型 |
| `LLM_EMBED_MODEL` | `embedding-3` | 可选，向量模型 |
| `LLM_EMBED_DIM` | `256` | 可选，向量维度 |
| `LLM_TEMPERATURE` | `0.2` | 可选，文档问答取低温 |

⚠️ 换厂商时要确认对方有 `/embeddings` 端点；没有的话检索层得换成本地 embedding 模型。

## 文件说明

| 文件 | 作用 |
|---|---|
| `config.py` | 所有可调参数集中在这里：切分大小、top-k、阈值、温度 |
| `rag.py` | 核心链路，六个步骤都是普通函数，逐行可读，`ask.py` 和 `verify.py` 共用 |
| `langchain_demo.py` | 同链路的 LangChain 版：框架接管切分 / Embeddings / ChatModel |
| `ask.py` | 命令行入口，打印命中片段、相似度和本次 token |
| `verify.py` | 验收：3 个资料内问题 + 2 个资料外问题，全绿才算过 |
| `data/team-handbook.md` | 示例语料（编的，非真实制度；已确认本周沿用） |
| `data/index.json` | 运行时生成的向量索引，**不提交**，由 `--rebuild` 产生 |
| `docs/ARCHITECTURE.md` | 交付物：一页架构说明 |

## 自检三问（本周唯一剩余项，合上代码能答出来才算过）

1. 为什么索引要落成 `index.json`，而不是每次提问都把文档重新向量化一遍？
2. `MIN_SCORE = 0.55` 是怎么定出来的？换一份文档还能直接沿用吗？
3. 检索不到时为什么直接返回固定话术、连模型都不调用？

## 常见坑

- **忘记 `--rebuild`**：换了文档却用旧索引，答案会答非所问。
- **阈值调太低**：资料外的问题也会检索到"看起来有点像"的片段，模型就开始硬编。用 `verify.py` 打印的分数分布定阈值。
- **`index.json` 别提交**：语料一变它就失效，提交进仓库只会制造不一致。
- 装 LangChain 依赖若被代理拦，换国内镜像：`pip install -i https://mirrors.aliyun.com/pypi/simple/ langchain-openai langchain-text-splitters`。
