"""LeetCode 1. 两数之和（哈希表 + 一次遍历）。

原文件 leetcode/two_sum.py 里有完整思路走查；本模块只保留函数。

核心记忆点：**先查、再存**。写成「先存再查」的话，
nums = [3, 3], target = 6 会让下标 0 和自己匹配，返回 [0, 0]。
"""


def two_sum(nums: list[int], target: int) -> list[int]:
    """返回 nums 中和为 target 的两个元素的下标；无解时返回空列表。"""
    seen: dict[int, int] = {}

    for i, n in enumerate(nums):
        complement = target - n

        # 先查：确认另一半是否已经出现过
        if complement in seen:
            return [seen[complement], i]

        # 再存：把自己登记进去，供后面的元素来匹配
        seen[n] = i

    return []
