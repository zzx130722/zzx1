from typing import List


class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        # 左闭右开区间 [left, right)：当 left == right 时区间为空
        left, right = 0, len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                # 中间值太小，mid 和它左边全排除
                left = mid + 1
            else:
                # 中间值够大，mid 本身可能是答案，必须保留
                right = mid
        # 循环结束时 left == right，正是「第一个 >= target 的位置」
        # 若 target 比所有数都大，left 会自然停在 len(nums)，即插入到末尾
        return left
