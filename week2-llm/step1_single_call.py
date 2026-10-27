"""第一次真正调大模型 API：先看原始 JSON，再学怎么把答案取出来。

跑法（在 dev-basics 目录下）：
    .venv\\Scripts\\python.exe -X utf8 week2-llm\\step1_single_call.py
"""
import json

import requests

from config import API_KEY, BASE_URL, MODEL


def main() -> None:
    if not API_KEY:
        raise RuntimeError(
            "没有找到 API key。请先做 README 的第 1-2 步："
            "注册 DeepSeek 拿 key，然后在 week2-llm/.env 里写 LLM_API_KEY=sk-..."
        )

    # 注意 URL 的拼法：OpenAI 兼容格式一律是 base_url + /chat/completions
    url = f"{BASE_URL}/chat/completions"
    body = {
        "model": MODEL,
        # messages 是一个列表，顺序就是「对话的剧本」。第一句必须是 system。
        "messages": [
            {"role": "system", "content": "你是一个耐心的编程助教，用中文回答，保持简短。"},
            {"role": "user", "content": "用一句话说明什么是 API"},
        ],
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    print(f"POST {url}")
    print(f"model = {MODEL}")
    resp = requests.post(url, headers=headers, json=body, timeout=30)

    # 先看状态码再看内容：2xx 才算成功
    print(f"HTTP 状态码 = {resp.status_code}")
    if resp.status_code == 401:
        raise RuntimeError("401：key 不对。去平台重新复制一遍，确认 .env 里没有多余空格")
    if resp.status_code == 429:
        raise RuntimeError("429：请求太快或额度用完，等几秒再试")
    if resp.status_code >= 500:
        raise RuntimeError(f"{resp.status_code}：服务端开小差了，稍后重试")
    resp.raise_for_status()

    # 第一步：把整个 JSON 打出来，亲眼看一遍结构（周二的任务就是这行）
    print("\n===== 原始 JSON =====")
    print(json.dumps(resp.json(), ensure_ascii=False, indent=2))

    # 第二步：按结构把答案挖出来。答案固定住在 choices[0].message.content
    reply = resp.json()["choices"][0]["message"]["content"]
    print("\n===== 取出的回答 =====")
    print(reply)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        # 把报错翻译成人话直接打印，不甩一脸 traceback
        print(f"\n[出错了] {e}")
