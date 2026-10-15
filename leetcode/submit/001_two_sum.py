from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}  # 数值 -> 下标

        for i, n in enumerate(nums):
            need = target - n

            # 先查：另一半出现过就直接返回
            if need in seen:
                return [seen[need], i]

            # 再存：把自己登记进去，供后面的元素匹配
            seen[n] = i

        return []
