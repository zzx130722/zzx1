"""LeetCode 21 合并两个有序链表的测试用例。"""

import pytest

from devbasics.leetcode import ListNode, build, merge_two_lists, to_list


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ([], [], []),
        ([], [0], [0]),
        ([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),  # 有相等元素，交替推进
        ([5], [1, 2, 3], [1, 2, 3, 5]),  # 一边整体比另一边大
        ([1, 1, 1], [1, 1], [1, 1, 1, 1, 1]),  # 全部相等
        ([-10, -5, 0], [-8, -3], [-10, -8, -5, -3, 0]),  # 负数正常比较
        ([1, 2], [], [1, 2]),
    ],
)
def test_merge_two_lists(a, b, expected):
    assert to_list(merge_two_lists(build(a), build(b))) == expected


def test_merge_reuses_nodes_not_copies():
    # 额外验证空间复杂度 O(1)：合并后应复用原节点，而不是复制出新对象
    left, right = build([1, 3]), build([2, 4])
    ids_before = {id(left), id(right), id(left.next), id(right.next)}

    merged = merge_two_lists(left, right)
    ids_after = set()
    node = merged
    while node:
        ids_after.add(id(node))
        node = node.next

    assert ids_before <= ids_after


def test_list_node_defaults():
    node = ListNode()
    assert node.val == 0
    assert node.next is None
