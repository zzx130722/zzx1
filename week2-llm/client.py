"""chat(messages) -> str：把「调一次模型」封装成一个函数。

周三的任务是封装，周四的 system 角色其实已经在 messages 里体现——
调用方想让它扮演什么角色，就自己传什么 system，本函数不掺和。

设计要点：
- 只依赖 config 的三个常量，别的什么都不想知道；
- 返回纯字符串，调用方不用再碰 JSON；
- 错误在这里翻译成人话，调用方只管 try/except RuntimeError。
"""
import requests

from config import API_KEY, BASE_URL, MODEL

# messages 的形状（这是 OpenAI 兼容格式的通用约定）：
# [
#     {"role": "system",    "content": "设定角色和规则"},     # 第一条必须是 system
#     {"role": "user",      "content": "用户说的话"},
#     {"role": "assistant", "content": "模型之前的回答"},     # 多轮时把历史放回来
#     {"role": "user",      "content": "用户的下一句"},
# ]


def chat(messages: list) -> str:
    """发一次对话请求，返回模型回答的纯文本。"""
    if not API_KEY:
        raise RuntimeError("没有找到 API key：请在 week2-llm/.env 里填 LLM_API_KEY=...（见 README）")
    if not messages or messages[0].get("role") != "system":
        # 不是格式洁癖：system 放第一条是所有厂商共同的行为约定，
        # 放中间或漏掉，行为在不同模型上表现不一，排查起来很费劲
        raise ValueError("messages 的第一条必须是 system 角色")

    url = f"{BASE_URL}/chat/completions"
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": MODEL, "messages": messages},
        timeout=30,
    )

    # 错误分类先给最常见三种（第 3 周会补重试和完整分类，这里先能看懂就行）
    if resp.status_code == 401:
        raise RuntimeError("401：key 不对或没填对，去平台重新复制")
    if resp.status_code == 429:
        raise RuntimeError("429：请求太快或额度不足，等几秒再试")
    if resp.status_code >= 500:
        raise RuntimeError(f"{resp.status_code}：服务端出错，稍后重试")
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]
