"""
LeetCode 35. 搜索插入位置（Search Insert Position）—— 难度：简单
https://leetcode.cn/problems/search-insert-position/

题目
----
给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。
如果目标值不存在于数组中，返回它将会被按顺序插入的位置。

请必须使用时间复杂度为 O(log n) 的算法。

示例：
    输入: nums = [1,3,5,6], target = 5   -> 输出: 2
    输入: nums = [1,3,5,6], target = 2   -> 输出: 1
    输入: nums = [1,3,5,6], target = 7   -> 输出: 4

--------------------------------------------------------------------------
思路：二分查找（折半查找）
--------------------------------------------------------------------------
题目里那句"必须 O(log n)"就是明示：不要从头到尾扫一遍。
数组已经排好序，所以可以每次砍掉一半——这就是二分。

把 left / right 想成一段"还可能有答案的区间"的两端。
每轮取中间位置 mid，只看 nums[mid] 和 target 谁大：

    nums[mid] < target  ->  答案一定在 mid 右边，把 left 提到 mid + 1
    nums[mid] >= target ->  答案一定在 mid 左边（含 mid），把 right 收到 mid

区间不断对半收缩，最后 left 停下的位置，就是答案。

关键细节：**`>=` 里的那个"等号"决定了 left 最后停在哪。**
因为我们要找的是"第一个 >= target 的位置"，也就是本题要的插入位置。
如果写成 `nums[mid] <= target` 才往右走（等于把"相等"划到了左边），
就变成在找"第一个 > target 的位置"了 —— 实测 nums = [1,3,5,6], target = 5 会返回 3，
而正确答案是 2。

另一个更常见的写法错误是把 `right = mid` 写成 `right = mid - 1`，
那等于把候选 mid 直接扔掉 —— 同样这条用例会返回 1，也是错的。
两种错误写法的实测输出，见 search_insert_walkthrough.md 的「坑 2」。

--------------------------------------------------------------------------
写法选择：左闭右开 [left, right)
--------------------------------------------------------------------------
本文件用的是"左闭右开"区间，即 left 能取到、right 取不到。
好处是边界干净、不用死记 `while left <= right` 里的等号：

    left, right = 0, len(nums)       # 区间是[0, len)，初始"整个数组"
    while left < right:              # 区间里还有元素
        mid = (left + right) // 2    # 下取整
        ...
    return left                      # 区间收缩到空，left == right 即答案

用示例 3（target = 7）走一遍，注意 right 始终等于 len(nums) = 4，最后停在 4：
    left=0, right=4, mid=2, nums[2]=5 < 7 -> left=3
    left=3, right=4, mid=3, nums[3]=6 < 7 -> left=4
    left=4, right=4 -> 循环结束，返回 4  (即"插在末尾")

--------------------------------------------------------------------------
复杂度
--------------------------------------------------------------------------
时间 O(log n)：每轮区间长度减半，n=10^9 也只要约 30 次比较。
空间 O(1)：只用了 left / right / mid 三个变量，没开额外数组。

对比暴力扫描的 O(n)，这正是题目要的"用有序换速度"。

--------------------------------------------------------------------------
边界用例（这比代码本身更重要）
--------------------------------------------------------------------------
1. [1,3,5,6], 5   -> 2   目标存在，且不在两端
2. [1,3,5,6], 2   -> 1   目标不存在，插在中间
3. [1,3,5,6], 7   -> 4   比所有元素都大 -> 插在末尾（最容易越界的一个）
4. [1,3,5,6], 0   -> 0   比所有元素都小 -> 插在开头
5. [1], 1         -> 0   单个元素且命中
6. [1], 0         -> 0   单个元素且偏小
7. [1], 2         -> 1   单个元素且偏大
8. [], 5          -> 0   空数组 -> 插在位置 0（代码不能崩）
"""


def search_insert(nums: list[int], target: int) -> int:
    """返回 target 在 nums 中的下标；不存在时返回它应插入的位置。"""
    # 左闭右开区间 [left, right)：一开始覆盖整个数组
    left, right = 0, len(nums)

    # 区间里还有元素就继续找
    while left < right:
        # 取中点（下取整）。写成 left + (right - left) // 2 可防整型溢出，
        # Python 整数无上限，所以这里直接 (left + right) // 2 就够。
        mid = (left + right) // 2

        if nums[mid] < target:
            # 中间值太小，答案只可能在右半边，且 mid 本身不可能是答案
            left = mid + 1
        else:
            # nums[mid] >= target：mid 本身有可能是答案，所以要保留它
            right = mid

    # 区间收缩到空时 left == right，正是"第一个 >= target 的位置"
    return left


def main() -> int:
    cases = [
        (([1, 3, 5, 6], 5), 2),
        (([1, 3, 5, 6], 2), 1),
        (([1, 3, 5, 6], 7), 4),
        (([1, 3, 5, 6], 0), 0),
        (([1], 1), 0),
        (([1], 0), 0),
        (([1], 2), 1),
        (([], 5), 0),
        (([1, 3, 5, 6], 3), 1),
        (([1, 3, 5, 6], 6), 3),
    ]

    passed = 0
    print("[4] 搜索插入位置 (Search Insert Position)")
    for (nums, target), expected in cases:
        actual = search_insert(nums, target)
        ok = actual == expected
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"    [{mark}] nums={nums} target={target} -> {actual}  期望 {expected}")

    total = len(cases)
    print(f"    通过 {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
