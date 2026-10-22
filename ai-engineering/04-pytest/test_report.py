"""对 refactored/report.py 的测试 —— 这是「写得对」的示范。

三个特征，值得对照着看：
  1. 每个测试只验证**一件事**，名字就是这句话（test_summarize_tie_breaks_by_region_name）
  2. 期望值**写死**在测试里，不调用被测试的代码去算（否则等于自己证明自己）
  3. 边界单独成测：空输入、同额并列、小数尾零
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from refactored.models import Order
from refactored.report import format_amount, render, summarize


def order(order_id: str, region: str, amount: str) -> Order:
    return Order(order_id=order_id, region=region, product="x", amount=Decimal(amount))


# ---------------------------------------------------------------- format_amount
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("2645.50"), "2645.5"),   # 尾随 0 要去掉，但保留一位小数
        (Decimal("3509.00"), "3509.0"),   # 整数也要留 .0
        (Decimal("0.00"), "0.0"),         # 零
        (Decimal("0.05"), "0.05"),        # 末尾是 5 不是 0，一个字都不该削
        (Decimal("10.10"), "10.1"),       # 只削末尾连续的 0
    ],
)
def test_format_amount(value: Decimal, expected: str) -> None:
    assert format_amount(value) == expected


# ---------------------------------------------------------------- summarize
def test_summarize_empty_input_returns_empty_list() -> None:
    assert summarize([]) == []


def test_summarize_single_region() -> None:
    rows = summarize([order("1", "East", "10.00"), order("2", "East", "5.50")])
    assert rows == [("East", Decimal("15.50"))]


def test_summarize_sorts_by_amount_descending() -> None:
    rows = summarize(
        [
            order("1", "South", "10.00"),
            order("2", "North", "30.00"),
            order("3", "East", "20.00"),
        ]
    )
    assert [region for region, _ in rows] == ["North", "East", "South"]


def test_summarize_tie_breaks_by_region_name() -> None:
    """金额相同时按区域名升序 —— 这一条不写死的话，排序结果依赖 dict 插入顺序。"""
    rows = summarize([order("1", "West", "10.00"), order("2", "East", "10.00")])
    assert [region for region, _ in rows] == ["East", "West"]


def test_summarize_uses_decimal_not_float() -> None:
    """钱的累加不能有二进制误差。0.1 + 0.2 用 float 是 0.30000000000000004。"""
    rows = summarize([order("1", "West", "0.10"), order("2", "West", "0.20")])
    assert rows == [("West", Decimal("0.30"))]
    assert rows[0][1] == Decimal("0.3")


# ---------------------------------------------------------------- render
def test_render_full_text_is_exact() -> None:
    text = render([("East", Decimal("2645.50")), ("North", Decimal("863.50"))])
    assert text == "East : 2645.5\nNorth : 863.5\nTOTAL : 3509.0\n"


def test_render_empty_still_prints_total() -> None:
    assert render([]) == "TOTAL : 0.0\n"
