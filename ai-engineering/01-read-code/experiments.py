"""textwrap._wrap_chunks 阅读实验：用运行结果验证你对源码的理解。

运行（注意要带 -X utf8，否则 Windows 控制台可能把中文输出变成乱码）：

    .venv/Scripts/python.exe -X utf8 ai-engineering/01-read-code/experiments.py

每个实验都是同样的三段：**问 → 猜 → 验**。
「猜」那一步必须自己做一次，否则读了等于没读 —— 阅读源码最容易犯的错，
是看到注释就以为懂了，等真改起来才发现理解反了。

所有结论都用 assert 固化，改错任何一条都会当场报错。
"""

from __future__ import annotations

import textwrap
import time


def title(no: int, question: str) -> None:
    print(f"\n{'=' * 68}")
    print(f"实验 {no}：{question}")
    print("=" * 68)


# ---------------------------------------------------------------- 实验 1
def exp1_chunks_shape() -> None:
    title(1, "传进 _wrap_chunks 的 chunks 长什么样？")
    print("先猜：'aa   bb cc' 会被切成几块？空白算不算一块？")

    wrapper = textwrap.TextWrapper(width=10)
    chunks = wrapper._split_chunks("aa   bb cc")
    print("实际：", chunks)
    print("带引号看清空白：", [repr(c) for c in chunks])

    # 结论：chunk 是「词」或「一整段连续空白」，空白本身也是独立的 chunk。
    # 这就是 docstring 里那句 "each chunk is either all whitespace or a word"。
    assert chunks == ["aa", "   ", "bb", " ", "cc"]


# ---------------------------------------------------------------- 实验 2
def exp2_reverse_for_pop() -> None:
    title(2, "为什么第 264 行要 chunks.reverse()？")
    print("先猜：正序从头部取元素，和倒序从尾部取，差别在哪？")

    def pop_tail(n: int) -> None:
        a = list(range(n))
        while a:
            a.pop()          # O(1)

    def pop_head(n: int) -> None:
        a = list(range(n))
        while a:
            a.pop(0)         # O(n)：每次都要把后面全部元素前移

    n = 50_000
    t1 = time.perf_counter()
    pop_tail(n)
    t_tail = time.perf_counter() - t1

    t2 = time.perf_counter()
    pop_head(n)
    t_head = time.perf_counter() - t2

    print(f"pop()    从尾部取 {n} 次：{t_tail:.4f}s")
    print(f"pop(0)   从头部取 {n} 次：{t_head:.4f}s")
    print(f"慢 {t_head / t_tail:.0f} 倍")
    print("（这个倍率每次跑都不一样，量级才是有意义的信息）")

    # 倒序之后，pop() 取出来的仍然是原来的第一个元素 —— 顺序没变，只是取的位置变了。
    lst = ["a", "b", "c"]
    lst.reverse()
    out = []
    while lst:
        out.append(lst.pop())
    assert out == ["a", "b", "c"]


# ---------------------------------------------------------------- 实验 3
def exp3_drop_whitespace() -> None:
    title(3, "drop_whitespace 到底删哪些空白？")
    print("先猜：'   aa bb   ' 宽 3，首尾的空白会被删，中间那格空格呢？")

    print("默认 True ：", textwrap.wrap("   aa bb   ", width=3))
    print("False     ：", textwrap.wrap("   aa bb   ", width=3, drop_whitespace=False))
    print("只看中间：'aa bb' 宽 3 →", textwrap.wrap("aa bb", width=3))
    print("对照      ：'aa bb' 宽 3 →", textwrap.wrap("aa bb", width=3, drop_whitespace=False))

    # 结论：只删**行首和行尾**的空白（第 284、306 行两处），
    # 中间的空格属于两个词之间的分隔，会留在上一行末尾。
    assert textwrap.wrap("   aa bb   ", width=3) == ["aa", "bb"]
    assert textwrap.wrap("aa bb", width=3, drop_whitespace=False) == ["aa ", "bb"]


# ---------------------------------------------------------------- 实验 4
def exp4_long_word() -> None:
    title(4, "单词比整行还长时会怎样？")
    print("先猜：'abcdefghijklmno' 宽 5，出来是几行？")

    print("默认            ：", textwrap.wrap("abcdefghijklmno", width=5))
    print("break_long_words=False：", textwrap.wrap("abcdefghijklmno", width=5, break_long_words=False))
    print("混合：'aaaaaaa bb' 宽 6 →", textwrap.wrap("aaaaaaa bb", width=6))
    print("      break=False      →", textwrap.wrap("aaaaaaa bb", width=6, break_long_words=False))

    # 第 301 行那个判断，就是「这个词塞不进当前行」和「这个词塞不进任何行」的分界。
    # 后者才交给 _handle_long_word 去硬切。
    assert textwrap.wrap("abcdefghijklmno", width=5) == ["abcde", "fghij", "klmno"]
    assert textwrap.wrap("abcdefghijklmno", width=5, break_long_words=False) == ["abcdefghijklmno"]


# ---------------------------------------------------------------- 实验 5
def exp5_max_lines_placeholder() -> None:
    title(5, "max_lines 和 placeholder 是怎么收尾的？")
    print("先猜：'aa bb cc dd ee' 宽 6，max_lines=2，placeholder='...'，第二行是什么？")

    print("max_lines=2 ：", textwrap.wrap("aa bb cc dd ee", width=6, max_lines=2, placeholder="..."))
    print("max_lines=3 ：", textwrap.wrap("aa bb cc dd ee", width=6, max_lines=3, placeholder="..."))
    print("正好放得下  ：", textwrap.wrap("aa bb cc dd", width=6, max_lines=2, placeholder="..."))
    print("placeholder 换短：", textwrap.wrap("aa bb cc dd ee", width=6, max_lines=2, placeholder=">"))

    # 注意第 311-316 行那个三重条件：不是「超过 max_lines 就截断」这么简单。
    # 最后一行如果刚好放得下（len(lines)+1 < max_lines 不成立但内容已结束），
    # 它仍然会原样输出，不会硬塞一个 placeholder。
    assert textwrap.wrap("aa bb cc dd ee", width=6, max_lines=2, placeholder="...") == ["aa bb", "cc..."]
    assert textwrap.wrap("aa bb cc dd", width=6, max_lines=2, placeholder="...") == ["aa bb", "cc dd"]


# ---------------------------------------------------------------- 实验 6
def exp6_two_value_errors() -> None:
    title(6, "哪儿会抛 ValueError？")
    print("先猜：宽 0 会抛错吗？placeholder 比整行还宽呢？")

    for kwargs, label in [
        ({"width": 0}, "width=0"),
        ({"width": 4, "max_lines": 1, "placeholder": "[long place]"}, "placeholder 太长"),
    ]:
        try:
            textwrap.wrap("aa", **kwargs)
        except ValueError as exc:
            print(f"{label:<22} → ValueError: {exc}")
        else:
            raise AssertionError(f"{label} 本该抛错却没有")

    # 这两处对应第 252 行和第 259 行 —— 参数校验放在函数最前面，
    # 后面的逻辑就可以假定「宽度是正的、placeholder 放得下」，不用层层防御。
    print("\n结论：前置校验的意义是让主体逻辑少写 if。")


# ---------------------------------------------------------------- 实验 7
def exp7_shorten_is_thin() -> None:
    title(7, "shorten() 凭什么只有 3 行？")
    print("先猜：shorten('Hello  world!', width=11) 结果是什么？12 呢？")

    print("width=11 →", repr(textwrap.shorten("Hello  world!", width=11)))
    print("width=12 →", repr(textwrap.shorten("Hello  world!", width=12)))

    # shorten 自己不做任何排版，它把三件事丢给别人：
    #   1. ' '.join(text.strip().split()) 先把所有空白压成一个空格
    #   2. TextWrapper(max_lines=1) 只允许一行
    #   3. fill() → _wrap_chunks() 做真正的切分
    # 这就是「薄封装」的典型长相：上层只负责调配参数。
    assert textwrap.shorten("Hello  world!", width=11) == "Hello [...]"
    assert textwrap.shorten("Hello  world!", width=12) == "Hello world!"


def main() -> None:
    print("textwrap.TextWrapper._wrap_chunks —— Python 3.13 标准库，第 238-339 行，共 102 行")
    print("下面 7 个实验对应走查文档里的 7 段。先自己猜，再往下看输出。")

    exp1_chunks_shape()
    exp2_reverse_for_pop()
    exp3_drop_whitespace()
    exp4_long_word()
    exp5_max_lines_placeholder()
    exp6_two_value_errors()
    exp7_shorten_is_thin()

    print(f"\n{'=' * 68}")
    print("7 个实验全部通过。如果你有哪一节的『猜』和『验』不一样，")
    print("回到 walkthrough_textwrap.md 对应那段重读一遍 —— 那才是你真正没懂的地方。")


if __name__ == "__main__":
    main()
