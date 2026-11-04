"""LeetCode 35 搜索插入位置的测试用例。"""

import pytest

from devbasics.leetcode import search_insert


@pytest.mark.parametrize(
    ("nums", "target", "expected"),
    [
        ([1, 3, 5, 6], 5, 2),  # 目标存在，且不在两端
        ([1, 3, 5, 6], 2, 1),  # 目标不存在，插在中间
        ([1, 3, 5, 6], 7, 4),  # 比所有元素都大 -> 插在末尾（最容易越界）
        ([1, 3, 5, 6], 0, 0),  # 比所有元素都小 -> 插在开头
        ([1], 1, 0),
        ([1], 0, 0),
        ([1], 2, 1),
        ([], 5, 0),  # 空数组不能崩
        ([1, 3, 5, 6], 3, 1),
        ([1, 3, 5, 6], 6, 3),
    ],
)
def test_search_insert(nums, target, expected):
    assert search_insert(nums, target) == expected
