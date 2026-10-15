"""
验证 submit/ 下的 SQL 题解（LeetCode 数据库题）。

用法（在 dev-basics 目录下）：

    ./.venv/Scripts/python.exe leetcode/verify_sql.py

为什么需要这个脚本？
--------------------
SQL 题和算法题完全不同：**没有 class Solution，没有函数签名**，
你交的就是一条查询语句，答案对不对完全取决于它跑出来的**行和列**。

LeetCode 上没法在本地试，写错了只会给一个"解答错误"。
所以这里用 Python 自带的 sqlite3 建好同样的表、灌入题目给的示例数据，
把 .sql 文件当成查询执行一遍，对比行与列名。

（SQLite 与 MySQL 在 LEFT JOIN / 列别名这些用法上行为一致，
本题涉及的语法是标准 SQL，用 SQLite 验证是可靠的。）
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

SUBMIT_DIR = Path(__file__).resolve().parent / "submit"

# 每道 SQL 题的：建表语句、示例数据、期望的列名、期望的行（顺序无关）
CASES: dict[str, dict] = {
    "175_combine_two_tables.sql": {
        "title": "175. 组合两个表",
        "ddl": [
            "CREATE TABLE Person (personId INT, lastName VARCHAR(255), firstName VARCHAR(255));",
            "CREATE TABLE Address (addressId INT, personId INT, city VARCHAR(255), state VARCHAR(255));",
        ],
        "data": [
            "INSERT INTO Person VALUES (1, 'Wang', 'Allen');",
            "INSERT INTO Person VALUES (2, 'Alice', 'Bob');",
            "INSERT INTO Address VALUES (1, 2, 'New York City', 'New York');",
            "INSERT INTO Address VALUES (2, 3, 'Leetcode', 'California');",
        ],
        "columns": ["firstName", "lastName", "city", "state"],
        "rows": [
            ("Allen", "Wang", None, None),
            ("Bob", "Alice", "New York City", "New York"),
        ],
    },
}


class Runner:
    def __init__(self) -> None:
        self.results: list[bool] = []

    def check(self, label: str, actual, expected) -> None:
        ok = actual == expected
        self.results.append(ok)
        print(f"    [{'PASS' if ok else 'FAIL'}] {label}")
        if not ok:
            print(f"           实际 {actual}")
            print(f"           期望 {expected}")


def run_sql(sql: str, case: dict) -> tuple[list[str], list[tuple]]:
    """在内存库里建表、灌数据，然后执行待测查询。"""
    conn = sqlite3.connect(":memory:")
    try:
        for stmt in case["ddl"] + case["data"]:
            conn.execute(stmt)
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description]
        # 题目说「任意顺序返回」，所以排序后再比
        rows = sorted(cur.fetchall(), key=lambda r: tuple(str(x) for x in r))
        return columns, rows
    finally:
        conn.close()


def main() -> int:
    runner = Runner()

    print("=" * 64)
    print("LeetCode SQL 提交版实测（SQLite 实跑，对比行与列名）")
    print("=" * 64)

    for filename, case in CASES.items():
        print(f"\n{case['title']}  ({filename})")
        path = SUBMIT_DIR / filename
        if not path.exists():
            print(f"    [FAIL] 找不到文件 {path}")
            runner.results.append(False)
            continue

        sql = path.read_text(encoding="utf-8")
        columns, rows = run_sql(sql, case)
        print(f"    查询返回 {len(rows)} 行，列名 {columns}")

        runner.check("列名与题目要求一致", columns, case["columns"])
        expected = sorted(case["rows"], key=lambda r: tuple(str(x) for x in r))
        runner.check("数据与期望一致", rows, expected)

    # 附：故意写错时能不能被查出来（证明上面那两项检查真的有效）
    print("\n[附] 常见错误写法对照（应全部被检出为「与期望不一致」）")
    case = CASES["175_combine_two_tables.sql"]
    wrong = {
        "用 INNER JOIN（没有地址的人被丢掉）": (
            "SELECT p.firstName, p.lastName, a.city, a.state FROM Person AS p "
            "JOIN Address AS a ON p.personId = a.personId;"
        ),
        "LEFT JOIN 但 ON 写成 addressId": (
            "SELECT p.firstName, p.lastName, a.city, a.state FROM Person AS p "
            "LEFT JOIN Address AS a ON p.personId = a.addressId;"
        ),
        "用 WHERE 代替 ON（等价于 INNER JOIN）": (
            "SELECT p.firstName, p.lastName, a.city, a.state FROM Person AS p, Address AS a "
            "WHERE p.personId = a.personId;"
        ),
    }
    for label, sql in wrong.items():
        _, rows = run_sql(sql, case)
        expected = sorted(case["rows"], key=lambda r: tuple(str(x) for x in r))
        # 这里期望的是"不一致"，所以取反
        runner.check(f"{label} -> 应被检出", rows != expected, True)

    print("\n" + "-" * 64)
    passed = sum(runner.results)
    total = len(runner.results)
    print(f"共 {total} 项，通过 {passed} 项")
    if passed == total:
        print("全部通过 —— submit/ 下的 SQL 可以整文件复制粘贴到 LeetCode。")
    else:
        print("存在失败项，先看上面的 FAIL 行。")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
