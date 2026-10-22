"""数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Order:
    """一条订单。

    - `frozen=True`：数据类一旦构造就不该被改。谁想改，请造一个新的。
      这条约束让「这个字段是谁改的」这类问题彻底消失。
    - `amount` 用 `Decimal` 而不是 `float`：钱不能有二进制误差。
      0.1 + 0.2 在 float 下是 0.30000000000000004，在 Decimal 下正好是 0.3。
    - `slots=True`：字段固定，拼错属性名会立刻 AttributeError，而不是悄悄造出一个新属性。
    """

    order_id: str
    region: str
    product: str
    amount: Decimal

    def __post_init__(self) -> None:
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if not self.region:
            raise ValueError(f"region must not be empty (order {self.order_id})")
        if self.amount < 0:
            raise ValueError(f"amount must be >= 0 (order {self.order_id}: {self.amount})")
