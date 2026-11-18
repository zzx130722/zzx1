"""命令行问答入口。

    python -X utf8 ask.py --rebuild          # 文档换过之后重建索引
    python -X utf8 ask.py "报销要什么材料"    # 问一句
    python -X utf8 ask.py                    # 进入连续问答，输入 q 退出

Windows 控制台默认 GBK，中文输出会乱码，所以 -X utf8 不能省。
"""
import sys

import rag


def show(question: str, chunks, matrix) -> None:
    result = rag.answer(question, chunks, matrix)
    print("\n" + "=" * 64)
    print("问题：", question)
    if result["hits"]:
        print("命中片段（按相似度排序）：")
        for i, hit in enumerate(result["hits"], 1):
            preview = hit["text"].replace("\n", " ")[:52]
            print(f"  [{i}] {hit['title']}  {hit['score']:.3f}  {preview}...")
    else:
        print("命中片段：无（低于相似度下限，直接兜底，不调用模型）")
    print("\n回答：", result["answer"])
    if result["usage"]:
        u = result["usage"]
        print(f"token：输入 {u.get('prompt_tokens')} / 输出 {u.get('completion_tokens')}")


def main() -> None:
    args = sys.argv[1:]
    if "--rebuild" in args:
        count = rag.build_index()
        print(f"索引已重建：{count} 个片段 → {rag.INDEX_FILE}")
        return

    chunks, matrix = rag.load_index()
    if args:
        show(" ".join(args), chunks, matrix)
        return

    print(f"已加载 {len(chunks)} 个片段。输入问题后回车，输入 q 退出。")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() == "q":
            break
        if question:
            show(question, chunks, matrix)


if __name__ == "__main__":
    main()
