# Week 2 · 第一个会调大模型的 Python 项目

> 对应学习计划第 2 周（10/26 - 11/01）：「跑通最小的那条路」。
> 6 天任务拆成了 4 个文件，每个文件在哪个天、跑什么命令，见下面的表。

## 快速开始（3 步）

1. **拿 key**（对应周一）：浏览器打开 https://platform.deepseek.com → 注册 →
   左侧「API keys」→ 创建 → 复制那串 `sk-` 开头的 key（**只显示一次**）。
   新用户有免费额度，练完第 2 周花不了一块钱。
2. **配 key**：在 `week2-llm/` 目录里新建一个文本文件，改名成 `.env`，内容一行：

   ```
   LLM_API_KEY=sk-把你复制的key粘到这里
   ```

   `.env` 已被 .gitignore 挡住，**永远不会提交到 GitHub**（计划里的常见坑 #1）。
3. **跑**（在 `dev-basics` 目录下）：

   ```powershell
   .venv\Scripts\python.exe -X utf8 week2-llm\step1_single_call.py   # 周二：看到 JSON
   .venv\Scripts\python.exe -X utf8 week2-llm\chat_cli.py            # 周五六末：连续聊天
   ```

   如果中文输出乱码，`-X utf8` 参数别丢（Windows 控制台默认 GBK，不是代码错）。

## 文件对应计划哪一天

| 文件 | 对应 | 讲什么 |
|---|---|---|
| `config.py` | 周一 | 全项目只有它知道「服务在哪、用哪个模型」。**换厂商 = 改 `.env` 里两行**（阶段验收原题） |
| `step1_single_call.py` | 周二 | 发一次请求，把返回的原始 JSON 完整打出来看结构，再取出答案 |
| `client.py` | 周三 + 周四 | `chat(messages) -> str` 封装；system 角色在调用方传入，函数本身不关心 |
| `chat_cli.py` | 周五 + 周末 | 多轮对话 + `while True` 命令行循环，「它记得上一句」靠的是历史回传 |

## curl 版（周二任务的另一种做法）

想体验「不写 Python 也能调 API」，在 PowerShell 里跑（Windows 自带 `curl.exe`）：

```powershell
curl.exe https://api.deepseek.com/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer sk-你的key" `
  -d '{\"model\":\"deepseek-chat\",\"messages\":[{\"role\":\"system\",\"content\":\"你是有用的助手\"},{\"role\":\"user\",\"content\":\"你好\"}]}'
```

能看到一坨 JSON——`step1_single_call.py` 做的就是这件事，只是用 Python 把
「取答案」这步自动化了。

## 自检三问（合上代码能答出来才算过）

1. `messages` 里为什么要把 `assistant` 的历史回答也放回去？→ 模型没有记忆，
   每次请求都是独立的，它「记得上一句」是因为我们把整段历史重新发了一遍。
   不放回去的话，它每次都只看到你最新这一句。
2. 为什么 key 放 `.env` 而不是直接写进 `client.py`？→ 写进代码只要提交一次
   GitHub，扫号机器人几分钟内就会拿它盗刷。key 和代码分离，泄露面就小。
3. 换成通义千问要改几处？→ 只改 `.env` 里的 `LLM_BASE_URL` 和 `LLM_MODEL`
   两行，`client.py` 一行不动——因为大家都是 OpenAI 兼容格式。
