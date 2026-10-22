"""把 03-debug-drill 里的 5 个 bug，用测试固定下来。

写法是 `xfail(strict=True)`：**断言「正确的行为」**，但标记「当前会失败」。
   - 现在：5 个全部 xfail（预期内的失败），整个测试套件仍然是绿的
   - 修好某一条之后：那一条会变成 XPASS，而 strict=True 会让它**报 FAILED**

这就是它的价值：**修好了会提醒你，删掉这行 xfail 标记，把它变成真正的回归测试。**
普通 `xfail`（strict=False）做不到这件事——修好了它会一直绿，你就永远忘了它。

⚠️ 第 1 条会污染模块级的默认参数，所以每条测试开头都 reload 一次，
   保证跑的是「干净进程刚启动时」的行为。
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

import buggy_app

DATA = Path(__file__).resolve().parent.parent / "03-debug-drill" / "data" / "prices.csv"


@pytest.fixture(autouse=True)
def fresh_module():
    """每条测试前重载模块，重置默认参数和模块级状态。"""
    importlib.reload(buggy_app)
    yield


@pytest.mark.xfail(strict=True, reason="bug1: cart=[] 是可变默认参数，两次调用共用同一个列表")
def test_add_to_cart_does_not_leak_between_calls() -> None:
    assert buggy_app.add_to_cart("apple") == ["apple"]
    assert buggy_app.add_to_cart("banana") == ["banana"]


@pytest.mark.xfail(strict=True, reason="bug2: get_items 返回内部列表的引用，调用方一改就污染库存")
def test_get_items_returns_copy() -> None:
    inventory = buggy_app.Inventory(["pen", "book"])
    inventory.get_items().append("eraser")
    assert inventory.count() == 2


@pytest.mark.xfail(strict=True, reason="bug3: // 是整除，137.5 // 3 得 45.0，零头丢失")
def test_split_bill_keeps_cents() -> None:
    assert buggy_app.split_bill(137.5, 3) == pytest.approx(45.8333, abs=1e-3)


@pytest.mark.xfail(strict=True, reason="bug4: try 包住整个 for，一行坏数据让后面全部读不到")
def test_load_prices_skips_only_bad_line() -> None:
    prices = buggy_app.load_prices(str(DATA))
    assert set(prices) == {"apple", "cherry", "date"}


@pytest.mark.xfail(strict=True, reason="bug5: sales 是字符串，sorted 走字典序，'9.5' > '100.0'")
def test_top_three_compares_numerically() -> None:
    rows = [
        {"name": "A", "sales": "9.5"},
        {"name": "B", "sales": "10.0"},
        {"name": "C", "sales": "8.0"},
        {"name": "D", "sales": "100.0"},
    ]
    assert [row["name"] for row in buggy_app.top_three(rows)] == ["D", "B", "A"]
