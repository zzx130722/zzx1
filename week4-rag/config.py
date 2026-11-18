"""配置中心：换模型、换文档、调检索参数都只改这里或 .env。

密钥不另存一份，直接复用 week2-llm/.env（同一个智谱 Key）。
这样第 2 周的 client.py 和第 4 周的 RAG 用的是同一套凭据，不会两边不一致。
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
ENV_FILE = REPO / "week2-llm" / ".env"


def _load_env(path: Path) -> None:
    """迷你版 .env 读取器，和 week2-llm/config.py 同一套写法。

    utf-8-sig 是为了兼容 Windows 上带 BOM 的文本文件（本项目踩过这个坑）。
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env(ENV_FILE)

API_KEY = os.environ.get("LLM_API_KEY", "")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
CHAT_MODEL = os.environ.get("LLM_MODEL", "glm-4-flash")
EMBED_MODEL = os.environ.get("LLM_EMBED_MODEL", "embedding-3")
EMBED_DIM = int(os.environ.get("LLM_EMBED_DIM", "256"))
TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))

DATA_FILE = ROOT / "data" / "team-handbook.md"
INDEX_FILE = ROOT / "data" / "index.json"

CHUNK_SIZE = 220        # 每块最多多少字符；中文按字算，220 字约等于一小段
CHUNK_OVERLAP = 40      # 相邻块重叠，避免一句话被切成两半后语义丢失
TOP_K = 3               # 每次取最相关的 3 块塞进 Prompt
MIN_SCORE = 0.55        # 余弦相似度下限；低于它当作「资料里没有」，直接兜底
                        # 0.55 不是拍脑袋：verify.py 实测资料内最低 0.634、
                        # 资料外最高 0.489，取中间留余量。换语料后要重新标定。
