from typing import List


class Solution:
    def sumCounts(self, nums: List[int]) -> int:
        MOD = 10 ** 9 + 7
        n = len(nums)
        size = n + 2

        # A[l] = 以 l 为起点、以当前遍历到的下标 r 为终点的子数组的「不同计数」。
        # 下面用「差分 + 树状数组」维护 A，支持两种操作：
        #   区间加：A[l..r] 全部 +1
        #   区间求和：A[l] + ... + A[r]
        # 树状数组内部下标从 1 开始，所以整体右移一位；
        # d1 存差分 D，d2 存 j * D[j]，于是 A 的前缀和 = (x+1)*ΣD - Σ(j*D[j])。
        d1 = [0] * size
        d2 = [0] * size

        def range_add(l, r, v):
            i = l + 1
            while i < size:
                d1[i] += v
                d2[i] += v * l
                i += i & -i
            i = r + 2
            while i < size:
                d1[i] -= v
                d2[i] -= v * (r + 1)
                i += i & -i

        def prefix_A(x):
            """返回 A[0] + A[1] + ... + A[x]；x 为 -1 时返回 0。"""
            i = x + 1
            s1 = 0
            s2 = 0
            while i > 0:
                s1 += d1[i]
                s2 += d2[i]
                i -= i & -i
            return (x + 1) * s1 - s2

        last = {}      # 每个值上一次出现的下标
        ans = 0        # 所有子数组不同计数平方和（对 MOD 取余）
        total_sq = 0   # 当前状态下 Σ A[l]^2，即「以 r 结尾的答案」

        for r, v in enumerate(nums):
            p = last.get(v, -1)   # v 上一次出现的下标；首次出现记作 -1

            # nums[r] 只会让起点落在 [p+1, r] 的子数组多出一个不同值，
            # 这些位置的 A[l] 各 +1，平方和增加 Σ(2*A[l]+1) = 2*ΣA[l] + (r-p)
            span_sum = prefix_A(r) - prefix_A(p)
            total_sq = (total_sq + 2 * span_sum + (r - p)) % MOD
            ans = (ans + total_sq) % MOD

            range_add(p + 1, r, 1)
            last[v] = r

        return ans
