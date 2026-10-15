from typing import List


class Solution:
    def sumCounts(self, nums: List[int]) -> int:
        MOD = 10 ** 9 + 7
        n = len(nums)
        ans = 0
        # 枚举每个起点 i，向右一格一格扩展 j，用集合维护不同值的个数
        for i in range(n):
            seen = set()
            for j in range(i, n):
                seen.add(nums[j])       # 新元素可能已存在，也可能第一次出现
                ans += len(seen) ** 2   # 当前子数组的不同计数，平方后累加
        return ans % MOD
