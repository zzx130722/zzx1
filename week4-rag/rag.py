"""RAG 核心链路：加载 → 切分 → 向量化 → 检索 → 拼 Prompt → 生成。

刻意不引框架，六个步骤都是能单独调用的普通函数，方便逐行讲清楚
「RAG 到底做了什么」。框架等价实现见 langchain_demo.py。

两个设计决定值得记住：
1. 索引落盘缓存。文档向量化一次就够，每次提问只需把「问题」向量化，
   否则问 10 次就要为同一份文档付 10 次 embedding 的钱。
2. 检索不到就直接兜底，不调模型。相似度低于阈值时连生成请求都不发，
   既省 token，又从机制上保证不会对着空资料硬编答案。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import requests

from config import (
    API_KEY,
    BASE_URL,
    CHAT_MODEL,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_FILE,
    EMBED_DIM,
    EMBED_MODEL,
    INDEX_FILE,
    MIN_SCORE,
    TEMPERATURE,
    TOP_K,
)

SYSTEM_PROMPT = (
    "你是团队内部知识库助手，只依据【资料】里的内容回答问题。\n"
    "规则：\n"
    "1. 不得使用资料之外的知识，不推测、不补全；\n"
    "2. 资料里没有相关信息时，只回答「资料里没有提到，请咨询相关负责人」；\n"
    "3. 回答控制在 3 句以内，末尾用【来源：小节名称】标注依据，名称必须照抄资料里给出的标题；\n"
    "4. 资料里没有时只输出第 2 条那句话，不要标注来源。"
)

NO_ANSWER = "资料里没有提到，请咨询相关负责人"


def read_sections(path: Path) -> list[dict]:
    """按 Markdown 二级标题分节，返回 [{'title': 小节标题, 'text': 正文}]。

    一级标题和 > 引用块是文件说明，不进索引，否则会成为检索噪声。
    """
    text = path.read_text(encoding="utf-8-sig")
    sections: list[dict] = []
    title, buf = "概述", []
    for line in text.splitlines():
        if line.startswith("## "):
            if buf:
                sections.append({"title": title, "text": "\n".join(buf).strip()})
            title, buf = line[3:].strip(), []
        elif line.startswith("# ") or line.lstrip().startswith(">"):
            continue
        else:
            buf.append(line)
    if buf:
        sections.append({"title": title, "text": "\n".join(buf).strip()})
    return [s for s in sections if s["text"]]


def split_chunks(sections: list[dict], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """每节内按字符滑窗切块，相邻块重叠 overlap 个字符。

    为什么带 overlap：一句话正好卡在两块交界处时，任何一块都不完整，
    检索命中了也读不懂。重叠一点是最便宜的补救。
    """
    chunks: list[dict] = []
    for section in sections:
        text = section["text"]
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append({"title": section["title"], "text": piece})
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    """调智谱 embedding-3，把一批文本变成向量。单次最多 64 条。"""
    if not API_KEY:
        raise RuntimeError("没有找到 API key：请检查 week2-llm/.env 里的 LLM_API_KEY")
    result: list[list[float]] = []
    for i in range(0, len(texts), 64):
        batch = texts[i : i + 64]
        resp = requests.post(
            f"{BASE_URL}/embeddings",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": EMBED_MODEL, "input": batch, "dimensions": EMBED_DIM},
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"embedding 接口返回 {resp.status_code}：{resp.text[:200]}")
        data = resp.json()["data"]
        result.extend(d["embedding"] for d in sorted(data, key=lambda x: x["index"]))
    return result


def build_index(path: Path = DATA_FILE) -> int:
    """离线建索引：切分 → 向量化 → 归一化 → 存 JSON。返回片段数。"""
    chunks = split_chunks(read_sections(path))
    if not chunks:
        raise RuntimeError(f"{path} 里没有可索引的内容")
    matrix = np.asarray(embed([c["text"] for c in chunks]), dtype=float)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / np.maximum(norms, 1e-12)  # 预先归一化，检索时点积就是余弦相似度
    payload = {"chunks": chunks, "vectors": matrix.tolist()}
    INDEX_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1),
        encoding="utf-8",
        newline="\n",
    )
    return len(chunks)


def load_index() -> tuple[list[dict], np.ndarray]:
    if not INDEX_FILE.exists():
        raise RuntimeError("索引不存在，先跑：python -X utf8 ask.py --rebuild")
    data = json.loads(INDEX_FILE.read_text(encoding="utf-8-sig"))
    return data["chunks"], np.asarray(data["vectors"], dtype=float)


def retrieve(question: str, chunks: list[dict], matrix: np.ndarray,
             top_k: int = TOP_K, min_score: float = MIN_SCORE) -> list[dict]:
    """把问题向量化，和所有片段算余弦相似度，取过阈值的 top-k。"""
    q = np.asarray(embed([question])[0], dtype=float)
    q = q / max(float(np.linalg.norm(q)), 1e-12)
    scores = matrix @ q
    hits: list[dict] = []
    for i in np.argsort(-scores)[:top_k]:
        score = float(scores[i])
        if score < min_score:
            continue
        hits.append({"title": chunks[i]["title"], "text": chunks[i]["text"], "score": score})
    return hits


def generate(question: str, hits: list[dict]) -> tuple[str, dict]:
    """把命中片段拼进 user 消息，让模型照着答。"""
    context = "\n\n".join(
        f"[{i}] 小节「{h['title']}」\n{h['text']}" for i, h in enumerate(hits, 1)
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"【资料】\n{context}\n\n【问题】\n{question}"},
    ]
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": CHAT_MODEL, "messages": messages, "temperature": TEMPERATURE},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"chat 接口返回 {resp.status_code}：{resp.text[:200]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip(), data.get("usage", {})


def answer(question: str, chunks: list[dict] | None = None,
           matrix: np.ndarray | None = None) -> dict:
    """一次完整问答。返回 answer / hits / usage 三样，便于命令行和自测共用。"""
    if chunks is None or matrix is None:
        chunks, matrix = load_index()
    hits = retrieve(question, chunks, matrix)
    if not hits:
        return {"answer": NO_ANSWER, "hits": [], "usage": {}}
    text, usage = generate(question, hits)
    return {"answer": text, "hits": hits, "usage": usage}
