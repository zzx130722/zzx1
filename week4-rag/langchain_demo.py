"""同一条 RAG 链路的 LangChain 版（任务卡点名的框架）。

和 rag.py 对照着看，框架接管了三件事：
  RecursiveCharacterTextSplitter → 切分
  Embeddings 抽象基类           → 向量化（把智谱 embedding-3 包进去）
  ChatOpenAI                    → 生成（智谱兼容 OpenAI 格式，直接换 base_url）

检索仍手写 numpy 余弦：教学上故意留着，好让 top-k 和阈值怎么起作用看得见。
生产项目里这一步会换成向量库（Chroma / FAISS / pgvector）。

    python -X utf8 langchain_demo.py "一线城市住宿上限多少"
"""
from __future__ import annotations

import sys

import numpy as np
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

import rag
from config import (
    API_KEY,
    BASE_URL,
    CHAT_MODEL,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_FILE,
    MIN_SCORE,
    TEMPERATURE,
    TOP_K,
)


class ZhipuEmbeddings(Embeddings):
    """把智谱 embedding-3 包成 LangChain 认识的 Embeddings 组件。

    自己实现两个方法就够了：embed_documents 批量处理文档，
    embed_query 处理单个问题。底层仍复用 rag.embed，避免两套 HTTP 逻辑。
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return rag.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return rag.embed([text])[0]


def build():
    """用框架切分器重建内存索引（本文件是教学演示，不落盘缓存）。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks: list[dict] = []
    for section in rag.read_sections(DATA_FILE):
        for piece in splitter.split_text(section["text"]):
            chunks.append({"title": section["title"], "text": piece})
    embeddings = ZhipuEmbeddings()
    matrix = np.asarray(embeddings.embed_documents([c["text"] for c in chunks]), dtype=float)
    matrix = matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)
    return chunks, matrix, embeddings


def main() -> None:
    question = " ".join(sys.argv[1:]) or "报销超过 5000 元要谁签字？"
    chunks, matrix, embeddings = build()

    q = np.asarray(embeddings.embed_query(question), dtype=float)
    q = q / max(float(np.linalg.norm(q)), 1e-12)
    scores = matrix @ q
    hits = [
        (int(i), float(scores[i]))
        for i in np.argsort(-scores)[:TOP_K]
        if scores[i] >= MIN_SCORE
    ]

    print(f"LangChain 版：{len(chunks)} 个片段（RecursiveCharacterTextSplitter）")
    for rank, (i, score) in enumerate(hits, 1):
        print(f"  [{rank}] {chunks[i]['title']}  {score:.3f}")

    if not hits:
        print("回答：", rag.NO_ANSWER)
        return

    context = "\n\n".join(
        f"[{rank}] 小节「{chunks[i]['title']}」\n{chunks[i]['text']}"
        for rank, (i, _) in enumerate(hits, 1)
    )
    llm = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=CHAT_MODEL,
        temperature=TEMPERATURE,
        timeout=60,
        max_retries=1,
    )
    messages = [
        SystemMessage(content=rag.SYSTEM_PROMPT),
        HumanMessage(content=f"【资料】\n{context}\n\n【问题】\n{question}"),
    ]
    print("\n回答：", llm.invoke(messages).content)


if __name__ == "__main__":
    main()
