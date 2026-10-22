"""重构版销售报表。

和 legacy_sales_report.py 的输出必须逐字节一致（在合法数据上）——
重构的定义就是「对外行为不变，内部结构改善」。
在脏数据上会**故意**不一致，因为原版有 3 个 bug，新版把它们修了，
差异逐条列在 REFACTOR-NOTES.md 里。
"""

from .errors import CsvFormatError, RowParseError, SalesReportError
from .loader import load_orders, dedupe_by_order_id
from .models import Order
from .report import render, summarize, format_amount

__all__ = [
    "CsvFormatError",
    "Order",
    "RowParseError",
    "SalesReportError",
    "dedupe_by_order_id",
    "format_amount",
    "load_orders",
    "render",
    "summarize",
]
