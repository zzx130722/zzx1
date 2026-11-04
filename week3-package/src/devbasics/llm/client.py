"""chat(messages) -> str：把「调一次模型」封装成一个函数（week2-llm 收编版）。

与原版 week2-llm/client.py 的区别：
- 不再 import config.py，改为调用时从环境变量读取三个配置；
- 支持 keyword 参数覆盖，测试不用碰真实网络也能测配置逻辑。

环境变量（谁调用谁设置，包不管 .env 文件）：
- LLM_API_KEY   必填，缺失时直接报人话错误
- LLM_BASE_URL  缺省 DeepSeek，换厂商只改这一个变量
- LLM_MODEL     缺省 deepseek-chat
"""

import os

import requests

_DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
_DEFAULT_MODEL = "deepseek-chat"


def chat(
    messages: list,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    timeout: int = 30,
) -> str:
    """发一次对话请求，返回模型回答的纯文本。

    messages 是 OpenAI 兼容格式，第一条必须是 system 角色——
    这不是格式洁癖：放中间或漏掉，不同模型行为不一，排查很费劲。
    """
    key = api_key if api_key is not None else os.environ.get("LLM_API_KEY", "")
    url = f"{base_url or _DEFAULT_BASE_URL}/chat/completions"
    payload_model = model or _DEFAULT_MODEL

    if not key:
        raise RuntimeError(
            "没有找到 API key：请设置环境变量 LLM_API_KEY（或在调用时传入 api_key=...）"
        )
    if not messages or messages[0].get("role") != "system":
        raise ValueError("messages 的第一条必须是 system 角色")

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": payload_model, "messages": messages},
        timeout=timeout,
    )

    # 错误分类给最常见三种，翻译成人话，调用方只管 try/except RuntimeError
    if resp.status_code == 401:
        raise RuntimeError("401：key 不对或没填对，去平台重新复制")
    if resp.status_code == 429:
        raise RuntimeError("429：请求太快或额度不足，等几秒再试")
    if resp.status_code >= 500:
        raise RuntimeError(f"{resp.status_code}：服务端出错，稍后重试")
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]
