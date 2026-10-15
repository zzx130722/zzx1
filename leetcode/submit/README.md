# submit/ —— 可以直接粘到 LeetCode 的代码

这里每个文件都是**完整、可直接粘贴**的 LeetCode 提交版代码。
打开文件 → 全选 → 复制 → 粘到 LeetCode 代码框 → 提交。**不用改任何东西。**

| 文件 | 题目 | 方法名（不能改） | 题目地址 |
|---|---|---|---|
| [001_two_sum.py](001_two_sum.py) | 1. 两数之和 | `twoSum` | <https://leetcode.cn/problems/two-sum/> |
| [020_valid_parentheses.py](020_valid_parentheses.py) | 20. 有效的括号 | `isValid` | <https://leetcode.cn/problems/valid-parentheses/> |
| [021_merge_two_sorted_lists.py](021_merge_two_sorted_lists.py) | 21. 合并两个有序链表 | `mergeTwoLists` | <https://leetcode.cn/problems/merge-two-sorted-lists/> |
| [035_search_insert_position.py](035_search_insert_position.py) | 35. 搜索插入位置 | `searchInsert` | <https://leetcode.cn/problems/search-insert-position/> |
| [2913_subarrays_distinct_sum_of_squares_i.py](2913_subarrays_distinct_sum_of_squares_i.py) | 2913. 子数组不同元素数目的平方和 I（简单版，n ≤ 100） | `sumCounts` | <https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-i/> |
| [2916_subarrays_distinct_sum_of_squares_ii.py](2916_subarrays_distinct_sum_of_squares_ii.py) | 2916. 子数组不同元素数目的平方和 II（困难版，n ≤ 10⁵，要取模） | `sumCounts` | <https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-ii/> |

> ⚠️ **最后两题先认清自己在做哪一道。** 两道题的**题目描述和示例一模一样**，
> 区别只在数据范围和是否取模：I 是 `n ≤ 100`、不用取模（简单题）；
> II 是 `n ≤ 10⁵`、要对 `10⁹+7` 取模（困难题）。
> 拿 I 的暴力写法去交 II 会**超时**（实测 n=10⁵ 需约 166 秒）。
> 分不清就先交 I 的版本 —— 它的 `% MOD` 是无害的，小数据下答案不会超过模数。
> 两个文件的解法详见下方「平方和这两题」。

## 和 `leetcode/` 下同名题解的区别

| | `leetcode/*.py`（练习版） | `submit/*.py`（提交版） |
|---|---|---|
| 能本地跑 | ✅ 自己带 10 个用例 | ❌ 不带 `main()`，交给 LeetCode 测 |
| 能提交 | ❌ 格式不对 | ✅ 完全对应题目模板 |
| 入口 | 顶层函数 `search_insert` | `class Solution:` 里的 `searchInsert` |
| 用途 | 自己练、自己测 | 交作业 |

**一句话：想在本机跑就用 `leetcode/`，想交到网站就用 `submit/`。**

## 为什么不能直接粘 `leetcode/` 里的文件？

因为 LeetCode 判题的方式是**它来调用你的函数**，按固定名字找：

```python
Solution().searchInsert([1, 3, 5, 6], 5)
```

所以有三处必须对上，错一处就白交：

1. **外层必须有 `class Solution:`** —— LeetCode 只认这个名字的类
2. **方法名必须一字不差** —— `searchInsert` 不能写成 `search_insert` / `searchinsert`
3. **必须有 `self` 参数** —— 它是类的方法，不是普通函数

## 操作步骤（以第 35 题为例）

1. 浏览器打开 <https://leetcode.cn/problems/search-insert-position/>
2. 右上角**登录**（不登录也能写代码，但**提交必须登录**）
3. 代码框左上角语言下拉框选 **Python3**（别选成 Python，那是 Python 2）
4. **全选代码框里的内容删掉**（模板里已有几行，留着会和新代码重复）
5. 打开 `035_search_insert_position.py`，**全选 → 复制 → 粘贴**进去
6. 先点 **「运行」**：它会用题目里的示例跑一遍，能看到中间结果
   （这一步能跑通，说明格式没问题）
7. 再点 **「提交」**：这次会跑全部隐藏用例，通过就给你一个绿色的「通过」

> 「运行」和「提交」的区别：**运行**只跑你指定的那一个用例、给你看输出，用来调试；
> **提交**会跑几百个隐藏用例、只告诉你过没过，用来评分。所以**先运行、后提交**。

## 常见报错怎么改

| 报错 | 原因 | 怎么改 |
|---|---|---|
| `NameError: name 'Solution' is not defined` | 少了 `class Solution:` 那一行 | 检查最外层是不是 `class Solution:` |
| `AttributeError: 'Solution' object has no attribute 'searchInsert'` | 方法名拼错了 | 对照上表的「方法名（不能改）」列 |
| `NameError: name 'List' is not defined` | 少了导入 | 文件第一行的 `from typing import List` 要留着 |
| `IndentationError` / `TabError` | 粘贴时缩进乱了 | 清空代码框重新粘一次 |
| `TypeError: ... takes 2 positional arguments but 3 were given` | 方法忘了写 `self` | 第一个参数必须是 `self` |
| 显示「超出时间限制」（TLE） | 用了 O(n²) 暴力解法 | 第 35 题必须用二分，见下方说明 |

## 这些代码是怎么验过可以用的

`submit/` 里的文件没有 `main()`，所以**不能在本地直接运行**——
报错了你也不知道是原文有问题还是自己改坏了。

为了把这件事说死，仓库里配了一个校验脚本，它**模拟 LeetCode 的判题环境**：
只注入 LeetCode 会提供的名字（`List` / `Optional` / `ListNode`），
然后像判题机一样调用 `Solution().方法名(...)`，逐个用例比对结果，
最后再核对**方法名和参数名是否和题目要求一致**（这是最容易出错也最不好查的一项）。

```bash
# 在 dev-basics 目录下执行
./.venv/Scripts/python.exe leetcode/verify_submit.py
```

实测结果：**49 项全部通过**（六道题共 43 个用例 + 6 项方法签名核对）。
所以你粘上去之后如果报错，可以先跑一遍这个脚本 —— 脚本全过，
说明代码本身没问题，那就是粘贴或提交时的问题。

## 平方和这两题（2913 / 2916）

**I 的写法（O(n²)，适合 n ≤ 100）** —— 枚举起点 `i`，向右一格格扩展，
用集合记录见过哪些值，集合大小就是当前子数组的不同计数：

```python
for i in range(n):
    seen = set()
    for j in range(i, n):
        seen.add(nums[j])
        ans += len(seen) ** 2
```

**II 的写法（O(n log n)，n = 10⁵ 也过）** —— 核心是一次「贡献转化」：

固定右端点 `r`，设 `A[l]` = 子数组 `nums[l..r]` 的不同计数。
那么**「所有以 r 结尾的子数组的答案」恰好就是 `Σ A[l]²`**，
整个题就是把它对每个 `r` 累加起来。

当 `r` 从 `r-1` 推进到 `r`（新值 `v`，上一次出现在 `p`）时：

- `l` 在 `[p+1, r]`：这些子数组里 `v` 是**新面孔**，`A[l] += 1`
- `l` 在 `[0, p]`：`v` 早就出现过，`A[l]` **不变**

于是只需要支持「区间加 1」和「区间求和」——正好是**树状数组**的看家本领
（两个树状数组配合差分，就能做到区间加 + 区间求和）。

平方和怎么增量维护？每个 `A[l]` 加 1 时，`A[l]²` 增加 `2·A[l] + 1`，
所以区间整体加 1 后，平方和总共增加 `2·ΣA[l] + 区间长度`。
那个 `ΣA[l]` 就是上面的区间求和，一次查询搞定。

**想弄懂 II 为什么能这么推，可以看**：[subarrays_squares_walkthrough.md](../subarrays_squares_walkthrough.md)。

## 关于「必须 O(log n)」

第 35 题题目里明写着 **「请必须使用时间复杂度为 O(log n) 的算法」**。
用 `for` 循环一个个扫**也能通过**（测试数据不大），但不符合题目要求，
面试时会被判不合格 —— 所以这里给的是二分版本。

想弄懂二分为什么这么写、边界为什么容易错，看：
[search_insert_walkthrough.md](../search_insert_walkthrough.md)（文字逐行讲解）
和 [search_insert_visual.html](../search_insert_visual.html)（可点着走的图解）。
