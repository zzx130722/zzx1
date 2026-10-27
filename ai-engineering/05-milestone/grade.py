#!/usr/bin/env python
"""里程碑 1 的自动判分器 —— 三题各一个检查函数。

用法（在 dev-basics 目录下）:
    .venv\\Scripts\\python.exe -X utf8 ai-engineering\\05-milestone\\grade.py

它会读 out/ 下的三个产物，逐项告诉你对不对。
退出码 0 = 三题全过；1 = 还有没过的。

⚠️ 文件末尾的 EXPECTED 里就是完整答案。
   建议：先自己写，卡住了再往下看；直接抄的话，这个练习对你的价值是 0。
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / "out"

T1_HEADER = ["order_id", "customer_id", "region", "order_date", "amount", "channel"]
REGIONS = {"North", "South", "East", "West", "UNKNOWN"}


def _result(ok: bool, label: str, detail: str = "") -> tuple[bool, str, str]:
    return ok, label, detail


def check_t1() -> list[tuple[bool, str, str]]:
    path = OUT / "t1_clean.csv"
    if not path.exists():
        return [_result(False, "产物存在", f"没找到 {path.name}，先用清洗脚本生成它")]

    text = path.read_text(encoding="utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return [_result(False, "非空", "文件是空的")]

    out = []
    header = [c.strip() for c in rows[0]]
    out.append(_result(header == T1_HEADER, "表头", f"期望 {T1_HEADER}，实际 {header}"))

    body = rows[1:]
    out.append(_result(len(body) == len(EXPECTED_T1), "行数",
                       f"期望 {len(EXPECTED_T1)} 行，实际 {len(body)} 行"
                       "（想想：14 行原始数据，重复 2 处、缺金额 2 处，各剩多少）"))

    ids = [r[0].strip() for r in body]
    out.append(_result(len(ids) == len(set(ids)), "order_id 无重复", f"重复的 id: {sorted({i for i in ids if ids.count(i) > 1})}"))
    out.append(_result(ids == sorted(ids), "按 order_id 升序", "行的顺序不对"))

    bad_region = [r[2] for r in body if r[2].strip() not in REGIONS]
    out.append(_result(not bad_region, "region 归一化", f"这些值不在 {sorted(REGIONS)} 里: {sorted(set(bad_region))[:5]}"))

    bad_date = [r[3] for r in body if not _is_ymd(r[3].strip())]
    out.append(_result(not bad_date, "日期统一 YYYY-MM-DD", f"格式不对: {bad_date[:3]}"))

    bad_amt = [r[4] for r in body if not _is_2dp(r[4].strip())]
    out.append(_result(not bad_amt, "金额两位小数", f"这些不是 2 位小数: {bad_amt[:3]}"))

    actual = [",".join(c.strip() for c in r) for r in body]
    expected = [",".join(r) for r in EXPECTED_T1]
    if actual != expected:
        diff = _first_diff(actual, expected)
        out.append(_result(False, "逐行内容", diff))
    else:
        out.append(_result(True, "逐行内容", f"{len(expected)} 行全部一致"))
    return out


def check_t2() -> list[tuple[bool, str, str]]:
    path = OUT / "t2_report.txt"
    if not path.exists():
        return [_result(False, "产物存在", f"没找到 {path.name}")]

    lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    out = []
    parsed = []
    for ln in lines:
        parts = ln.split("\t")
        if len(parts) != 4:
            out.append(_result(False, "格式", f"这行不是 4 个制表符分隔的字段: {ln!r}"))
            return out
        parsed.append(parts)

    out.append(_result(len(parsed) == len(EXPECTED_T2), "行数",
                       f"期望 {len(EXPECTED_T2)} 行（5 个 region + TOTAL），实际 {len(parsed)} 行"))

    names = [p[0] for p in parsed]
    out.append(_result(names == [p[0] for p in EXPECTED_T2], "region 顺序与 TOTAL 末行",
                       f"实际顺序 {names}"))

    ok_num = True
    detail = []
    for got, exp in zip(parsed, EXPECTED_T2):
        for idx, label in ((1, "单数"), (2, "总额"), (3, "均值")):
            if idx == 1:
                same = got[idx].strip() == exp[idx]
            else:
                same = _close(got[idx], exp[idx])
            if not same:
                ok_num = False
                detail.append(f"{got[0]} 的{label}: 得到 {got[idx]}，应为 {exp[idx]}")
    out.append(_result(ok_num, "每个数字", "；".join(detail[:4]) if detail else "5 行数字全部对得上（容差 0.005）"))
    return out


def check_t3() -> list[tuple[bool, str, str]]:
    path = OUT / "t3_hits.tsv"
    if not path.exists():
        return [_result(False, "产物存在", f"没找到 {path.name}")]

    lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    data = [ln for ln in lines if not ln.startswith("#")]
    tail = [ln for ln in lines if ln.startswith("#")]

    out = []
    parsed = [ln.split("\t") for ln in data]
    bad = [p for p in parsed if len(p) != 3]
    out.append(_result(not bad, "格式", f"这些行不是 3 个制表符字段: {bad[:2]}"))
    if bad:
        return out

    keys = [(p[0], p[1]) for p in parsed]
    out.append(_result(len(keys) == len(EXPECTED_T3), "行数", f"期望 {len(EXPECTED_T3)} 行，实际 {len(keys)} 行"))
    out.append(_result(keys == sorted(keys), "按 (月份, url) 升序", "排序不对"))
    out.append(_result(keys == [tuple(e[:2]) for e in EXPECTED_T3], "每个 (月份, url) 组合",
                       _first_diff([f"{k[0]}/{k[1]}" for k in keys], [f"{e[0]}/{e[1]}" for e in EXPECTED_T3])))
    counts = [p[2] for p in parsed]
    out.append(_result(counts == [e[2] for e in EXPECTED_T3], "每个计数",
                       _first_diff(counts, [e[2] for e in EXPECTED_T3])))
    out.append(_result(tail == [f"#dropped\t{EXPECTED_DROPPED}"], "末尾 #dropped 行",
                       f"期望 ['#dropped\\t{EXPECTED_DROPPED}']（那两行解析不出来的日志），实际 {tail}"))
    return out


def _is_ymd(s: str) -> bool:
    if len(s) != 10 or s[4] != "-" or s[7] != "-":
        return False
    try:
        y, m, d = s.split("-")
        return 1 <= int(m) <= 12 and 1 <= int(d) <= 31 and len(y) == 4
    except ValueError:
        return False


def _is_2dp(s: str) -> bool:
    if "." not in s:
        return False
    head, tail = s.split(".")
    return len(tail) == 2 and head.lstrip("-").isdigit() and tail.isdigit()


def _close(a: str, b: str) -> bool:
    try:
        return abs(float(a) - float(b)) < 0.005
    except ValueError:
        return False


def _first_diff(actual: list[str], expected: list[str]) -> str:
    for i, (a, e) in enumerate(zip(actual, expected)):
        if a != e:
            return f"第 {i + 1} 条不一样：得到 {a!r}，应为 {e!r}"
    if len(actual) != len(expected):
        return f"条数不一样：得到 {len(actual)}，应为 {len(expected)}"
    return "一致"


def main() -> int:
    tasks = [("第 1 题 清洗 raw_orders.csv", check_t1()),
             ("第 2 题 按 region 汇总", check_t2()),
             ("第 3 题 日志按月统计", check_t3())]

    all_ok = True
    for name, results in tasks:
        ok_count = sum(1 for ok, _, _ in results if ok)
        head = "PASS" if ok_count == len(results) else "FAIL"
        print(f"\n[{head}] {name}   {ok_count}/{len(results)} 项通过")
        for ok, label, detail in results:
            # 只在失败时打印 detail：通过时那些「期望 X 实际 Y」的提示会自相矛盾
            mark = "  ok  " if ok else "  ×   "
            print(f"{mark}{label:22} {detail if not ok else ''}".rstrip())
        if ok_count != len(results):
            all_ok = False

    print()
    if all_ok:
        print("三题全过。接下来做一件事：不看自己的代码，逐行讲清每行的作用 —— 讲不清的部分就是还没真懂。")
    else:
        print("还没全过。先看最上面第一个 × 那项，别一次改三处。")
    return 0 if all_ok else 1


# ============ 以下就是答案，先别往下看 ============

EXPECTED_T1 = [
    ["1001", "C-07", "North", "2026-01-05", "120.00", "web"],
    ["1002", "C-03", "North", "2026-01-09", "1340.50", "web"],
    ["1003", "C-11", "South", "2026-01-11", "88.80", "app"],
    ["1004", "C-02", "UNKNOWN", "2026-01-12", "45.00", "web"],
    ["1005", "C-09", "West", "2026-01-15", "300.00", "store"],
    ["1006", "C-04", "West", "2026-01-18", "72.25", "app"],
    ["1007", "C-15", "South", "2026-02-02", "2000.00", "store"],
    ["1008", "C-06", "North", "2026-02-05", "15.50", "web"],
    ["1009", "C-01", "East", "2026-02-09", "0.00", "web"],
    ["1011", "C-08", "North", "2026-02-20", "64.40", "web"],
    ["1012", "C-05", "West", "2026-02-21", "410.00", "store"],
]

EXPECTED_T2 = [
    ["East", "1", "0.00", "0.00"],
    ["North", "4", "1540.40", "385.10"],
    ["South", "2", "2088.80", "1044.40"],
    ["UNKNOWN", "1", "45.00", "45.00"],
    ["West", "3", "782.25", "260.75"],
    ["TOTAL", "11", "4456.45", "405.13"],
]

EXPECTED_T3 = [
    ["2026-01", "/blog/mapreduce", "1"],
    ["2026-01", "/index.html", "2"],
    ["2026-01", "/pricing", "1"],
    ["2026-02", "/api/hits", "1"],
    ["2026-02", "/blog/mapreduce", "1"],
    ["2026-02", "/index.html", "1"],
    ["2026-03", "/index.html", "2"],
    ["2026-03", "/pricing", "1"],
]
EXPECTED_DROPPED = 2


if __name__ == "__main__":
    raise SystemExit(main())
