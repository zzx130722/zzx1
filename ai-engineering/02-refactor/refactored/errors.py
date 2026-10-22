"""异常层次。

为什么不用 `ValueError` 一个打天下：
调用方需要区分「文件格式错」（整份数据都别读了）和「某一行错」（跳过这行继续）。
一个异常类型做不到这件事，只能靠猜字符串。
"""

from __future__ import annotations


class SalesReportError(Exception):
    """本模块所有可预期错误的基类。调用方 catch 它就能兜住全部。"""


class CsvFormatError(SalesReportError):
    """文件层面的问题：表头不对、列数不对、文件不是一个 CSV。"""


class RowParseError(SalesReportError):
    """单行的问题。带上行号，否则用户根本不知道去文件里找哪一行。"""

    def __init__(self, line_no: int, reason: str) -> None:
        self.line_no = line_no
        self.reason = reason
        super().__init__(f"line {line_no}: {reason}")
