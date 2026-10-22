"""对 refactored 的 loader / models / cli 的测试 —— 同样是「写得对」的示范。

这份文件有三个新东西，test_report.py 里没出现过：

  1. `tmp_path` fixture：pytest 送你一个每次都全新的临时目录，
     不用自己造临时文件、也不用担心测试之间互相污染。
  2. `capsys` fixture：抓 stdout / stderr，验证「程序打印了什么」。
  3. 直接调 `cli.main([...])` 测命令行入口——不用起子进程，
     返回值就是退出码，断言比 subprocess 快一个量级。

这些都是 AI 生成后由人把关保留下来的：初版 AI 把「文件不存在」
写成 `pytest.raises(FileNotFoundError)` 包住 `cli.main`，
但 main 内部已经 catch 了这个异常并 return 2——
那样写测试永远等不到异常，直接 FAIL。把关时要跑一遍才知道。
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal
from pathlib import Path

import pytest

from refactored.cli import build_parser, main
from refactored.errors import CsvFormatError, RowParseError, SalesReportError
from refactored.loader import dedupe_by_order_id, load_orders, parse_amount
from refactored.models import Order

HEADER = "order_id,region,product,amount"


def write_csv(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8", newline="\n")
    return str(path)


# ---------------------------------------------------------------- parse_amount
def test_parse_amount_strips_thousands_separator() -> None:
    assert parse_amount("1,234.50", 2) == Decimal("1234.50")


def test_parse_amount_strips_whitespace() -> None:
    assert parse_amount(" 45.5 ", 2) == Decimal("45.50")


@pytest.mark.parametrize("raw", ["", "   "])
def test_parse_amount_empty_raises(raw: str) -> None:
    with pytest.raises(RowParseError) as excinfo:
        parse_amount(raw, 7)
    assert excinfo.value.line_no == 7  # 行号必须带上，否则用户找不到行


def test_parse_amount_not_a_number_raises() -> None:
    with pytest.raises(RowParseError):
        parse_amount("abc", 2)


def test_parse_amount_nan_raises() -> None:
    """Decimal('NaN') 能构造成功但不 is_finite()，必须单独拦。"""
    with pytest.raises(RowParseError):
        parse_amount("NaN", 2)


# ---------------------------------------------------------------- load_orders
def test_load_orders_happy_path(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path / "ok.csv",
        HEADER + "\n1,East,apple,10.00\n2,West,pear,3.50\n",
    )
    warnings: list[str] = []
    orders = load_orders(path, warnings)
    assert len(orders) == 2
    assert orders[0].region == "East"
    assert orders[1].amount == Decimal("3.50")
    assert warnings == []  # 干净数据不该有任何警告


def test_load_orders_empty_file_raises(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "empty.csv", "")
    with pytest.raises(CsvFormatError):
        load_orders(path, [])


def test_load_orders_wrong_header_raises(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "bad_header.csv", "id,region,product,amount\n")
    with pytest.raises(CsvFormatError):
        load_orders(path, [])


def test_load_orders_skips_blank_line_silently(tmp_path: Path) -> None:
    """空行不是错误，跳过即可，也不该出现在警告里。"""
    path = write_csv(tmp_path / "blank.csv", HEADER + "\n\n1,East,x,1.00\n")
    warnings: list[str] = []
    assert len(load_orders(path, warnings)) == 1
    assert warnings == []


def test_load_orders_bad_row_becomes_warning(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path / "bad_row.csv",
        HEADER + "\n1,East,x,10.00\n2,West,y,abc\n",
    )
    warnings: list[str] = []
    orders = load_orders(path, warnings)
    assert len(orders) == 1  # 好行照常返回
    assert len(warnings) == 1 and "line 3" in warnings[0]  # 坏行报行号


def test_load_orders_short_row_becomes_warning(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "short.csv", HEADER + "\n1,East\n")
    warnings: list[str] = []
    orders = load_orders(path, warnings)
    assert orders == []
    assert len(warnings) == 1 and "columns" in warnings[0]


def test_load_orders_handles_utf8_bom(tmp_path: Path) -> None:
    """Excel 导出的 CSV 几乎必带 BOM。encoding='utf-8-sig' 是为此。"""
    path = tmp_path / "bom.csv"
    path.write_bytes(b"\xef\xbb\xbf" + (HEADER + "\n1,East,x,1.00\n").encode("utf-8"))
    warnings: list[str] = []
    orders = load_orders(str(path), warnings)
    assert orders[0].order_id == "1"  # 若没处理 BOM，这里会是 '\ufeff1'


def test_load_orders_negative_amount_becomes_warning(tmp_path: Path) -> None:
    """amount 解析得出来但 Order 构造失败（负数）→ ValueError 兜底，记警告。"""
    path = write_csv(tmp_path / "neg.csv", HEADER + "\n1,East,x,-5.00\n")
    warnings: list[str] = []
    assert load_orders(path, warnings) == []
    assert len(warnings) == 1 and "amount" in warnings[0]


# ---------------------------------------------------------------- dedupe
def test_dedupe_keeps_first_and_warns() -> None:
    o1 = Order("A", "East", "x", Decimal("1.00"))
    o2 = Order("A", "East", "x", Decimal("9.99"))  # 同单号，后出现的丢弃
    o3 = Order("B", "West", "x", Decimal("2.00"))
    warnings: list[str] = []
    kept = dedupe_by_order_id([o1, o2, o3], warnings)
    assert [o.amount for o in kept] == [Decimal("1.00"), Decimal("2.00")]
    assert len(warnings) == 1 and "duplicate" in warnings[0]


# ---------------------------------------------------------------- models
def test_order_rejects_empty_region() -> None:
    with pytest.raises(ValueError, match="region"):
        Order("1", "", "x", Decimal("1.00"))


def test_order_is_frozen() -> None:
    """frozen=True 的意义：谁改字段谁当场爆炸，而不是悄悄改成功。"""
    order = Order("1", "East", "x", Decimal("1.00"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        order.amount = Decimal("2.00")  # type: ignore[misc]


def test_errors_share_base_class() -> None:
    """调用方 catch SalesReportError 一个就能兜住两种错——这是分层的意义。"""
    assert issubclass(CsvFormatError, SalesReportError)
    assert issubclass(RowParseError, SalesReportError)


# ---------------------------------------------------------------- cli
def test_cli_end_to_end_writes_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = write_csv(
        tmp_path / "in.csv",
        HEADER + "\n1,East,apple,10.00\n2,East,pear,5.00\n3,West,x,1.00\n",
    )
    out_path = tmp_path / "out.txt"
    code = main([csv_path, "--out", str(out_path)])
    assert code == 0
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("TOTAL : 16.0\n")
    assert capsys.readouterr().out == text  # 屏幕上打印的与写文件的一致


def test_cli_missing_file_returns_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main([str(tmp_path / "nope.csv"), "--out", str(tmp_path / "o.txt")])
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_cli_bad_header_returns_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """SalesReportError 走另一个分支，退出码同样是 2——但错误信息不同。"""
    csv_path = write_csv(tmp_path / "bad.csv", "id,region,product,amount\n")
    code = main([csv_path, "--out", str(tmp_path / "o.txt")])
    assert code == 2
    assert "expected header" in capsys.readouterr().err


def test_build_parser_defaults() -> None:
    args = build_parser().parse_args([])
    assert args.input == "data/sales_clean.csv"
    assert args.out == "report_new.txt"
