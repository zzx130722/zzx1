"""LeetCode 1 两数之和的测试用例（沿用原 two_sum.py main() 的用例表）。"""

import pytest

from devbasics.leetcode import two_sum


@pytest.mark.parametrize(
    ("nums", "target", "expected"),
    [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([3, 2, 4], 6, [1, 2]),
        ([3, 3], 6, [0, 1]),  # 重复值：验证「先查再存」的必要性
        ([-3, 4, 3, 90], 0, [0, 2]),  # 负数与正数相加得到 0
        ([0, 4, 3, 0], 0, [0, 3]),  # 两个 0 分处首尾
        ([2, 5, 5, 11], 10, [1, 2]),
    ],
)
def test_two_sum(nums, target, expected):
    assert two_sum(nums, target) == expected


def test_two_sum_no_solution_returns_empty():
    # 题目保证有解，但兜底分支不该崩
    assert two_sum([1, 2], 100) == []
