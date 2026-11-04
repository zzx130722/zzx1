"""LeetCode 20 有效的括号的测试用例。"""

import pytest

from devbasics.leetcode import is_valid


@pytest.mark.parametrize(
    ("s", "expected"),
    [
        ("", True),  # 空字符串视为有效
        ("()", True),
        ("()[]{}", True),  # 多组并列，不嵌套
        ("([{}])", True),  # 多层嵌套
        ("([)]", False),  # 顺序错了——最容易漏的一个
        ("(((", False),  # 只有左括号
        (")))", False),  # 只有右括号
        ("(", False),
        ("]", False),
        ("{[]}", True),
    ],
)
def test_is_valid(s, expected):
    assert is_valid(s) == expected


def test_is_valid_rejects_unexpected_char():
    # 意外字符显式判负，不静默放过
    assert is_valid("(a)") is False
