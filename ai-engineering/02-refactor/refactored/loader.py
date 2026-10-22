"""读取与清洗。所有跟 CSV 打交道的脏活都在这里，别的地方不碰文件。"""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .errors import CsvFormatError, RowParseError
from .models import Order

EXPECTED_HEADER = ["order_id", "region", "product", "amount"]
CENT = Decimal("0.01")


def parse_amount(raw: str, line_no: int) -> Decimal:
    """把 '1,234.50' / ' 45.5 ' / '' 变成 Decimal。

    原版这里是 `float(row[3])` + 裸 `except: pass`，于是：
      - '1,234.50' 解析失败 → 静默跳过；
      - 更糟的是 `amt` 定义在循环外，跳过之后它还是**上一行的金额**，
        这一行的销售额被记到当前区域头上。
    所以这里对三种情况分开处理：空 → 报错（交给调用方决定跳过还是中止）；
    带千分位 → 去掉逗号再解析；无法解析 → 报错并带行号。
    """
    text = raw.strip().replace(",", "")
    if not text:
        raise RowParseError(line_no, "amount is empty")
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise RowParseError(line_no, f"amount {raw!r} is not a number") from None
    if not value.is_finite():
        raise RowParseError(line_no, f"amount {raw!r} is not finite")
    return value.quantize(CENT)


def load_orders(path: str | Path, warnings: list[str]) -> list[Order]:
    """读 CSV，返回订单列表。

    坏行不抛异常，而是记进 `warnings` 并跳过 —— 这是业务上的选择：
    一份 3 万行的销售表，不该因为第 718 行少个逗号就整份作废。
    但**必须**报出来，不能像原版那样悄无声息。

    参数里传一个 list 来收集警告，是刻意的：返回值只有一个，调用方一眼看得出
    主数据是什么；警告是副作用，放在显式传入的容器里，比全局变量或 logging 更难被忽略。
    """
    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)

        header = next(reader, None)
        if header is None:
            raise CsvFormatError(f"{file_path}: file is empty")
        if [h.strip() for h in header] != EXPECTED_HEADER:
            raise CsvFormatError(
                f"{file_path}: expected header {EXPECTED_HEADER}, got {header}"
            )

        orders: list[Order] = []
        for line_no, row in enumerate(reader, start=2):
            if not row or all(cell.strip() == "" for cell in row):
                continue  # 空行直接跳过，不算错误
            if len(row) != len(EXPECTED_HEADER):
                warnings.append(
                    f"line {line_no}: expected {len(EXPECTED_HEADER)} columns, got {len(row)}; skipped"
                )
                continue
            try:
                amount = parse_amount(row[3], line_no)
                orders.append(
                    Order(
                        order_id=row[0].strip(),
                        region=row[1].strip(),
                        product=row[2].strip(),
                        amount=amount,
                    )
                )
            except RowParseError as exc:
                warnings.append(f"{exc}; skipped")  # RowParseError 自带行号
            except ValueError as exc:
                warnings.append(f"line {line_no}: {exc}; skipped")
    return orders


def dedupe_by_order_id(orders: list[Order], warnings: list[str]) -> list[Order]:
    """按 order_id 去重，保留第一次出现的那条。

    原版没有这一步，同一张订单在导出时出现两次就会把销售额算两遍。
    保留「第一条」而不是「最后一条」，是因为导出文件通常是追加写入的，
    先出现的才是原始记录。
    """
    seen: dict[str, Order] = {}
    for order in orders:
        if order.order_id in seen:
            warnings.append(f"duplicate order_id {order.order_id!r}; later copy ignored")
            continue
        seen[order.order_id] = order
    return list(seen.values())
