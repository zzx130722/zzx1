"""
验证 submit/ 下的「LeetCode 粘贴版」代码是否真的能被 LeetCode 跑通。

用法（在 dev-basics 目录下）：

    ./.venv/Scripts/python.exe leetcode/verify_submit.py

为什么需要这个脚本？
--------------------
submit/ 里的文件是**给 LeetCode 用的**，它们没有 main()、不能自己跑自己，
所以 run_all.py 覆盖不到它们。但它们又必须正确 —— 一旦错了，
你会在网站上收到一个看不懂的报错，还不知道是自己改坏了还是原文就有问题。

这个脚本的做法是**模拟 LeetCode 的判题环境**：
    1. 只注入 LeetCode 会提供的名字（List / Optional / ListNode）
    2. exec 执行代码文件（等价于你把代码粘进代码框）
    3. 像判题机一样调用 Solution().方法名(参数)
    4. 逐个用例比对返回值，并核对方法名与参数名是否和题目要求一致

最后一项（方法名核对）是本脚本最有价值的部分：
LeetCode 是**按名字**去找你的函数的，名字错一个字母就白交了。
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from typing import List, Optional

SUBMIT_DIR = Path(__file__).resolve().parent / "submit"


# LeetCode 会内置提供的链表节点类（第 21 题要用）
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def load(filename: str):
    """像 LeetCode 那样执行代码文件，返回里面的 Solution 类。"""
    namespace = {
        "List": List,
        "Optional": Optional,
        "ListNode": ListNode,
        "__name__": "solution",
    }
    source = (SUBMIT_DIR / filename).read_text(encoding="utf-8")
    exec(compile(source, filename, "exec"), namespace)
    return namespace["Solution"]


def to_array(head) -> list:
    """把链表转成 Python 列表，方便比对。"""
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def build(values: list):
    """把 Python 列表转成链表。"""
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def annotation_name(ann) -> str:
    """把类型注解规范化成可比较的短名字。"""
    if isinstance(ann, type):
        return ann.__name__
    return str(ann).replace("typing.", "").replace("__main__.", "")


class Runner:
    def __init__(self) -> None:
        self.results: list[bool] = []

    def check(self, label: str, actual, expected) -> None:
        ok = actual == expected
        self.results.append(ok)
        print(f"    [{'PASS' if ok else 'FAIL'}] {label} -> {actual}  期望 {expected}")

    def signature(self, filename: str, method_name: str, params: list[str], ret: str) -> None:
        solution = load(filename)
        method = getattr(solution, method_name, None)
        if method is None:
            print(f"    [FAIL] 类里找不到方法 {method_name}")
            self.results.append(False)
            return
        sig = inspect.signature(method)
        got_params = list(sig.parameters)
        got_ret = annotation_name(sig.return_annotation)
        ok = got_params == params and got_ret == ret
        self.results.append(ok)
        print(f"    [{'PASS' if ok else 'FAIL'}] Solution.{method_name}  "
              f"参数 {got_params}  返回 {got_ret}")


def main() -> int:
    runner = Runner()

    print("=" * 64)
    print("LeetCode 粘贴版实测（按判题调用方式 Solution().方法名(...)）")
    print("=" * 64)

    print("\n[1] 两数之和  Solution.twoSum")
    two_sum = load("001_two_sum.py")().twoSum
    for nums, target, expected in [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([3, 2, 4], 6, [1, 2]),
        ([3, 3], 6, [0, 1]),
        ([-3, 4, 3, 90], 0, [0, 2]),
        ([0, 4, 3, 0], 0, [0, 3]),
        ([2, 5, 5, 11], 10, [1, 2]),
    ]:
        runner.check(f"nums={nums} target={target}", two_sum(nums, target), expected)

    print("\n[2] 有效的括号  Solution.isValid")
    is_valid = load("020_valid_parentheses.py")().isValid
    for s, expected in [
        ("", True), ("()", True), ("()[]{}", True), ("([{}])", True), ("{[]}", True),
        ("([)]", False), ("(((", False), (")))", False), ("(", False), ("]", False),
    ]:
        runner.check(f's="{s}"', is_valid(s), expected)

    print("\n[3] 合并两个有序链表  Solution.mergeTwoLists")
    merge = load("021_merge_two_sorted_lists.py")().mergeTwoLists
    for a, b, expected in [
        ([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),
        ([], [], []),
        ([], [0], [0]),
        ([1], [], [1]),
        ([-5, 0, 3], [-2, 1, 9], [-5, -2, 0, 1, 3, 9]),
    ]:
        runner.check(f"{a} + {b}", to_array(merge(build(a), build(b))), expected)

    print("\n[4] 搜索插入位置  Solution.searchInsert")
    search_insert = load("035_search_insert_position.py")().searchInsert
    for nums, target, expected in [
        ([1, 3, 5, 6], 5, 2),   # 题目示例 1
        ([1, 3, 5, 6], 2, 1),   # 题目示例 2
        ([1, 3, 5, 6], 7, 4),   # 题目示例 3
        ([1, 3, 5, 6], 0, 0),
        ([1], 1, 0),
        ([1], 0, 0),
        ([1], 2, 1),
        ([], 5, 0),
        ([1, 3, 5, 6], 3, 1),
        ([1, 3, 5, 6], 6, 3),
    ]:
        runner.check(f"nums={nums} target={target}", search_insert(nums, target), expected)

    print("\n[5] 方法签名核对（LeetCode 靠名字来找你的函数）")
    runner.signature("001_two_sum.py", "twoSum", ["self", "nums", "target"], "List[int]")
    runner.signature("020_valid_parentheses.py", "isValid", ["self", "s"], "bool")
    runner.signature(
        "021_merge_two_sorted_lists.py", "mergeTwoLists",
        ["self", "list1", "list2"], "Optional[ListNode]",
    )
    runner.signature(
        "035_search_insert_position.py", "searchInsert",
        ["self", "nums", "target"], "int",
    )

    print("\n" + "-" * 64)
    passed = sum(runner.results)
    total = len(runner.results)
    print(f"共 {total} 项，通过 {passed} 项")
    if passed == total:
        print("全部通过 —— submit/ 下的文件可以整文件复制粘贴到 LeetCode。")
    else:
        print("存在失败项，先看上面的 FAIL 行。")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
