"""库存与订单小工具。

⚠️ 这个文件里埋了 5 个 bug，全部通过了「看起来没问题」的检验：
   - 没有语法错误
   - 单跑一次大多数时候是对的
   - 单元测试如果只测 happy path，也全绿

你的任务是：跑 `drill.py`，看现象，自己说清每个 bug 的**根因**，
再让 AI 只说一句「是不是 XX 原因」，而不是问它「哪里有问题」。
"""

from __future__ import annotations

from typing import Any

DEFAULT_DISCOUNT = 0.1


# ---------------------------------------------------------------- 购物车
def add_to_cart(item: str, cart: list[str] = []) -> list[str]:
    """把商品加进购物车。"""
    cart.append(item)
    return cart


# ---------------------------------------------------------------- 库存
class Inventory:
    def __init__(self, items: list[str] | None = None) -> None:
        self._items = list(items or [])

    def get_items(self) -> list[str]:
        """给外面看的商品清单。"""
        return self._items

    def add(self, item: str) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)


# ---------------------------------------------------------------- 分账
def split_bill(total: float, people: int) -> float:
    """把账单平均分给若干人，返回每人应付多少。"""
    if people <= 0:
        raise ValueError("people must be positive")
    return total // people


# ---------------------------------------------------------------- 读价目表
def load_prices(path: str) -> dict[str, float]:
    """读 'name,price' 格式的价目表。坏行跳过。"""
    prices: dict[str, float] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                name, raw = line.strip().split(",")
                prices[name] = float(raw)
    except Exception:
        pass
    return prices


# ---------------------------------------------------------------- 排行榜
def top_three(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按销量取前三名。"""
    return sorted(rows, key=lambda row: row["sales"], reverse=True)[:3]
