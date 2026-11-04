"""LeetCode 35. 搜索插入位置（二分查找，左闭右开区间）。

关键细节：`>=` 里那个「等号」决定了 left 最后停在哪——
要找的是「第一个 >= target 的位置」；写成 `right = mid - 1`
等于把候选 mid 直接扔掉，nums = [1,3,5,6], target = 5 会错回 3。
"""


def search_insert(nums: list[int], target: int) -> int:
    """返回 target 在 nums 中的下标；不存在时返回它应插入的位置。"""
    # 左闭右开区间 [left, right)：一开始覆盖整个数组
    left, right = 0, len(nums)

    # 区间里还有元素就继续找
    while left < right:
        # 取中点（下取整）。Python 整数无上限，不用防溢出写法
        mid = (left + right) // 2

        if nums[mid] < target:
            # 中间值太小，答案只可能在右半边，且 mid 本身不可能是答案
            left = mid + 1
        else:
            # nums[mid] >= target：mid 本身有可能是答案，所以要保留它
            right = mid

    # 区间收缩到空时 left == right，正是「第一个 >= target 的位置」
    return left
