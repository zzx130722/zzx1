"""
一键运行 leetcode/ 下全部题解的自测。

用法（在 dev-basics 目录下）：

    ./.venv/Scripts/python.exe leetcode/run_all.py

每个题解文件都能**单独运行**（`.venv/Scripts/python leetcode/two_sum.py`），
这个脚本只是把它们串起来跑一遍，最后给一个总览。之所以选择"子进程"而不是
"import 调用"，是为了保证每个题解文件都可以独立复制到 LeetCode 上去提交，
不依赖这个目录里的其他文件。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# 顺序 = 建议的刷题顺序：哈希表 -> 栈 -> 链表 -> 二分
SOLUTIONS = [
    ("two_sum.py", "两数之和", "哈希表"),
    ("valid_parentheses.py", "有效的括号", "栈"),
    ("merge_two_sorted_lists.py", "合并两个有序链表", "链表 / 双指针"),
    ("search_insert.py", "搜索插入位置", "二分查找"),
]


def main() -> int:
    here = Path(__file__).resolve().parent
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    print("=" * 62)
    print(f"LeetCode 简单题自测   解释器 {sys.version.split()[0]}")
    print("=" * 62)

    results: list[tuple[str, str, bool]] = []

    for filename, title, tag in SOLUTIONS:
        path = here / filename
        if not path.exists():
            print(f"\n!! 文件缺失：{filename}")
            results.append((title, tag, False))
            continue

        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=str(here),
        )

        print()
        print(proc.stdout.rstrip())
        if proc.returncode != 0 and proc.stderr.strip():
            print(proc.stderr.rstrip())

        results.append((title, tag, proc.returncode == 0))

    # 总览表
    print()
    print("-" * 62)
    passed = sum(1 for _, _, ok in results if ok)
    for title, tag, ok in results:
        print(f"  [{'通过' if ok else '失败'}] {title:<12} 考点：{tag}")
    print("-" * 62)
    print(f"共 {len(results)} 题，通过 {passed} 题")

    if passed == len(results):
        print()
        print("全部通过。")
        print("但别急着往下走——验收标准不是「能跑」，而是：")
        print("  1. 关掉代码，你能用自己的话复述每道题的思路吗？")
        print("  2. 你能说出每道题最容易写错的那一个边界用例吗？")
    else:
        print()
        print("有题目未通过，先看上面的 FAIL 行。")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
