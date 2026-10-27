"""配置中心：全项目只有这一个文件知道「服务在哪、用哪个模型」。

换厂商 = 只改 .env 里 LLM_BASE_URL 和 LLM_MODEL 两行（阶段验收原题），
本文件和 client.py 一行都不用动——前提是对方兼容 OpenAI 格式（国产主流厂商都兼容）。
"""
import os
from pathlib import Path


def load_env(path: Path) -> None:
    """把 .env 文件里的 KEY=VALUE 读进环境变量（一个够用的迷你版）。

    只做三件事：跳过空行和 # 注释、按第一个 = 切开、不覆盖已有的环境变量。
    真实项目一般用 python-dotenv 库，但手写一遍你就知道它没多神奇。
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_env(Path(__file__).parent / ".env")

# key 从环境变量来，绝不写死在代码里（写了并提交 = 被扫号盗刷）
API_KEY = os.environ.get("LLM_API_KEY", "")
# 换厂商时改 .env 里的这两行，比如通义千问：
#   LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
#   LLM_MODEL=qwen-plus
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
