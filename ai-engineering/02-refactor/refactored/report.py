"""汇总与排版。纯函数，不碰文件、不打印 —— 这样才测得了。"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .models import Order


def format_amount(value: Decimal) -> str:
    """把 Decimal 排成和原版 `str(round(x, 2))` 完全一样的字符串。

    原版输出是 `2645.5` / `3509.0`（有 .0，但不补足两位）。
    重构不许改外部格式，所以这里刻意复现那个别扭的格式：
    先固定两位小数，再削掉尾随的 0，最后保证至少留一位小数。
    """
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if "." in text else text + ".0"


def summarize(orders: list[Order]) -> list[tuple[str, Decimal]]:
    """按区域求和，金额降序；金额相同时按区域名升序。

    排序**显式写出**两个键。原版是一趟手写冒泡，4 个区域就会排错 ——
    因为它只把最大的那个冒到第一位，其余位置靠运气。
    """
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for order in orders:
        totals[order.region] += order.amount
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def render(rows: list[tuple[str, Decimal]]) -> str:
    """拼成最终文本。返回值是字符串，不在里面 print —— 打印是 CLI 的事。"""
    lines = [f"{region} : {format_amount(amount)}" for region, amount in rows]
    total = sum((amount for _, amount in rows), Decimal("0"))
    lines.append(f"TOTAL : {format_amount(total)}")
    return "\n".join(lines) + "\n"
