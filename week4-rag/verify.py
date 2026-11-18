"""验收脚本：资料内的问题要答对，资料外的问题必须承认不知道。

    python -X utf8 verify.py

第 4 周交付物「可运行 RAG Demo」的验收点就在这里：
能引用原文、能对资料外的问题说不知道。全绿才算跑通。
"""
import sys

import rag
from config import MIN_SCORE

CASES = [
    ("报销单超过 5000 元需要谁额外签字？", "in", "部门负责人"),
    ("一线城市住宿每晚上限是多少？", "in", "600"),
    ("单个 PR 建议不超过多少行？", "in", "400"),
    ("公司年会是哪天举行？", "out", ""),
    ("食堂几点开始供餐？", "out", ""),
]

NO_ANSWER_KEY = "资料里没有提到"


def main() -> int:
    chunks, matrix = rag.load_index()
    print(f"索引片段数：{len(chunks)}　相似度下限：{MIN_SCORE}\n")
    failed = 0
    for question, kind, keyword in CASES:
        result = rag.answer(question, chunks, matrix)
        top = result["hits"][0]["score"] if result["hits"] else 0.0
        if kind == "in":
            ok = bool(result["hits"]) and keyword in result["answer"] and NO_ANSWER_KEY not in result["answer"]
            expect = f"命中片段且回答含「{keyword}」"
        else:
            ok = not result["hits"] and NO_ANSWER_KEY in result["answer"]
            expect = "无命中片段且明确说资料里没有"
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {question}")
        print(f"       期望：{expect}")
        print(f"       实际：最高相似度 {top:.3f}，命中 {len(result['hits'])} 块，回答「{result['answer'][:60]}」")
    print(f"\n结果：{len(CASES) - failed}/{len(CASES)} 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
