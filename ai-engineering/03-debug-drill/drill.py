"""调试演练：5 关，每关只看现象，先自己说根因。

跑法：
    ../../.venv/Scripts/python.exe -X utf8 drill.py            # 只看现象
    ../../.venv/Scripts/python.exe -X utf8 drill.py --answers  # 附一句话根因

规矩（很重要）：
    跑第一遍时**不要加 --answers**。每关读完，先在纸上写一句「我认为根因是……」，
    五关写完再翻答案。写不出来的，说明你还没真正定位，只是"感觉这里不对"。
"""

from __future__ import annotations

import sys

import buggy_app as app

ANSWERS = {
    1: "cart=[] 是默认参数，在函数**定义时**求值一次，之后每次调用共用同一个列表。",
    2: "get_items 返回的是内部列表本身（引用），调用方改了它，库存就真被改了。",
    3: "// 是整除，直接丢掉小数部分。137.5 // 3 = 45.0，剩下的 2.5 凭空消失。",
    4: "try 包住了整个 for 循环：第 2 行抛错后循环整体中断，后面两行根本没读；而 except: pass 把它藏了。",
    5: "sales 是字符串，sorted 按**字典序**比较，'9.5' > '10.0' 成立，所以顺序全错。",
}


def rule(title: str) -> None:
    print()
    print("─" * 66)
    print(title)
    print("─" * 66)


def level(no: int, phenomenon: str) -> None:
    print(f"\n>>> 现象：{phenomenon}")
    print(">>> 停 3 秒，先说根因，再往下看下一关。")


def main() -> int:
    show_answers = "--answers" in sys.argv

    print("调试演练 · 5 关")
    print("每关只给现象，不给原因。先在纸上写，五关写完再翻答案。")

    # ---------------------------------------------------------------- 1
    rule("第 1 关：购物车")
    first = app.add_to_cart("apple")
    print(f'第一次 add_to_cart("apple")  → {first}')
    second = app.add_to_cart("banana")
    print(f'第二次 add_to_cart("banana") → {second}')
    print('期望第二次是 ["banana"]')
    level(1, "第二次调用时，第一次放进去的 apple 还在")

    # ---------------------------------------------------------------- 2
    rule("第 2 关：库存清单")
    inventory = app.Inventory(["pen", "book"])
    print(f"初始库存：{inventory.get_items()}（共 {inventory.count()} 件）")
    borrowed = inventory.get_items()
    borrowed.append("eraser")
    print(f'外部对返回的列表 append("eraser") 之后：')
    print(f"  外部看到的：{borrowed}")
    print(f"  库存内部的：{inventory.get_items()}（共 {inventory.count()} 件）")
    print("期望：库存应该还是 2 件")
    level(2, "外部只是改了自己拿到的列表，库存内部却变了")

    # ---------------------------------------------------------------- 3
    rule("第 3 关：分账")
    total, people = 137.5, 3
    each = app.split_bill(total, people)
    print(f"账单 {total} 元，{people} 人分，每人 {each} 元")
    print(f"三人合计：{each * people} 元，账单是 {total} 元")
    print(f"按精确除法应该是：{total / people:.2f}")
    level(3, f"三人合计只有 {each * people} 元，少了 {total - each * people} 元")

    # ---------------------------------------------------------------- 4
    rule("第 4 关：读价目表（data/prices.csv 共 4 行）")
    prices = app.load_prices("data/prices.csv")
    print(f"读到的条数：{len(prices)}")
    print(f"内容：{prices}")
    print('期望：banana 那一行坏掉跳过，其余 3 个都在 {"apple": 3.5, "cherry": 12.0, "date": 7.25}')
    level(4, "4 行数据只读到 1 条，而且没有一点报错")

    # ---------------------------------------------------------------- 5
    rule("第 5 关：销量排行榜")
    rows = [
        {"name": "A", "sales": "9.5"},
        {"name": "B", "sales": "10.0"},
        {"name": "C", "sales": "8.0"},
        {"name": "D", "sales": "100.0"},
    ]
    print("原始数据（销量是字符串）：")
    for row in rows:
        print(f"  {row['name']}: {row['sales']}")
    picked = app.top_three(rows)
    print(f"top_three 选出：{[r['name'] for r in picked]}")
    print("期望：['D', 'B', 'A']（100.0 > 10.0 > 9.5）")
    level(5, "销量 100.0 的那个只排到第三")

    # ---------------------------------------------------------------- 收尾
    print()
    print("=" * 66)
    if not show_answers:
        print("五关都看完了。现在：")
        print("  1. 在纸上写下你认为的 5 个根因")
        print("  2. 再跑一次：python -X utf8 drill.py --answers")
        print("  3. 对答案，重点看你**说错的那一关**——那才是你真正的盲区")
        return 0

    print("参考答案（一句话根因）")
    print("=" * 66)
    for no in range(1, 6):
        print(f"\n第 {no} 关：{ANSWERS[no]}")
    print()
    print("更详细的复现步骤、修法、以及「怎么问 AI 才问得到根因」，见 ANSWER-KEY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
