"""这是一批「AI 生成、还没经过人工把关」的测试。

跑法（注意：文件名不是 test_ 开头，所以主测试套件不会收集它，必须显式指定）：

    ../../.venv/Scripts/python.exe -X utf8 -m pytest ai_tests_to_review.py -v

你会看到 **11 passed**（8 个测试函数，其中参数化了 4 条）。但其中 4 个**什么都没测**——
它们绿得很漂亮，却保护不了任何东西。

你的任务：跑之前先自己读一遍，标出你认为「假绿」的那几个，
再去看 REVIEW-ANSWERS.md 对答案。

判断只有一个标准：**把被测代码改坏，这个测试会不会红？**
不会红的，就是假绿。想不出来就真去改一改，跑一遍。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import refactored.report as report
from refactored.models import Order
from refactored.report import format_amount, render, summarize


def order(order_id: str, region: str, amount: str) -> Order:
    return Order(order_id=order_id, region=region, product="x", amount=Decimal(amount))


# ============================================================ 第 1 组：可疑
def test_render_returns_something() -> None:
    text = render([("East", Decimal("10.0"))])
    assert text is not None


def test_format_amount_handles_zero() -> None:
    try:
        assert format_amount(Decimal("0.00")) == "0"
    except AssertionError:
        pass


def test_summarize_groups_by_region(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(report, "summarize", lambda orders: [("Mock", Decimal("1"))])
    assert report.summarize([]) == [("Mock", Decimal("1"))]


def test_every_order_has_positive_amount() -> None:
    orders: list[Order] = []
    for item in orders:
        assert item.amount > 0


# ============================================================ 第 2 组：扎实
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("2645.50"), "2645.5"),
        (Decimal("3509.00"), "3509.0"),
        (Decimal("0.05"), "0.05"),
        (Decimal("10.10"), "10.1"),
    ],
)
def test_format_amount_edge_cases(value: Decimal, expected: str) -> None:
    assert format_amount(value) == expected


def test_summarize_empty_returns_empty() -> None:
    assert summarize([]) == []


def test_summarize_total_is_manually_computed() -> None:
    """期望值是手算的：10.00 + 5.50 = 15.50。"""
    rows = summarize([order("1", "East", "10.00"), order("2", "East", "5.50")])
    assert rows == [("East", Decimal("15.50"))]


def test_render_line_count_matches_regions() -> None:
    """2 个区域 → 2 行明细 + 1 行 TOTAL = 3 行。"""
    text = render([("East", Decimal("1.00")), ("North", Decimal("2.00"))])
    assert len(text.strip().splitlines()) == 3
