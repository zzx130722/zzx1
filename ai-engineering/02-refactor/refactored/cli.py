"""命令行入口。只负责参数解析、调用、打印、写文件 —— 不含计算逻辑。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import SalesReportError
from .loader import dedupe_by_order_id, load_orders
from .report import render, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="按区域汇总销售报表")
    parser.add_argument(
        "input",
        nargs="?",
        default="data/sales_clean.csv",
        help="输入 CSV（默认 data/sales_clean.csv）",
    )
    parser.add_argument(
        "--out",
        default="report_new.txt",
        help="报表输出路径（默认 report_new.txt）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    warnings: list[str] = []

    try:
        orders = load_orders(args.input, warnings)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 2
    except SalesReportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    orders = dedupe_by_order_id(orders, warnings)
    text = render(summarize(orders))

    for message in warnings:
        print(f"WARN: {message}", file=sys.stderr)

    print(text, end="")
    Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
