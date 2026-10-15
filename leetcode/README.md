# LeetCode 题解 · 6 题

> 任务三「AI 工具初体验」的第一部分。
> 四道简单题覆盖四种最基本的套路：**哈希表 / 栈 / 双指针 / 二分查找**；
> 另加一道困难题：**子数组不同元素数目的平方和**（树状数组 + 贡献转化）。

## 怎么运行

```bash
# 一键跑全部（推荐，在 dev-basics 目录下执行）
./.venv/Scripts/python.exe leetcode/run_all.py

# 或者单独跑某一题
./.venv/Scripts/python.exe leetcode/two_sum.py
```

本目录的题解是**练习版**：每个文件都能独立运行、自带自测用例，不依赖其他文件。
（要提交到 LeetCode 的版本在 `submit/`，两者入口格式不同，见下。）

### 想在 LeetCode 网站上跑？

**最快的方式**：打开 [`submit/`](submit/) 目录，里面**一个文件对应一道题**，
整文件复制 → 粘到 LeetCode → 提交，不用改任何东西。
（这些文件是按 LeetCode 的判题方式实测过的：`./.venv/Scripts/python.exe leetcode/verify_submit.py`
→ 49 项全通过，含六道题的方法签名核对。）

**想弄懂为什么不能直接粘 `leetcode/` 里的文件**，看 **[LEETCODE-HOWTO.md](LEETCODE-HOWTO.md)** ——
格式差异表、页面七步操作、常见报错对照，都写在里面。

### 想先弄懂题目本身？

两数之和有一份**可交互的图解页面**：**[two_sum_visual.html](two_sum_visual.html)** ——
点按钮就能看算法一轮一轮怎么走，还能切换「先查再存 / 先存再查」，
亲眼看到错误是怎么产生的。文字版详述在 **[two_sum_walkthrough.md](two_sum_walkthrough.md)**。

搜索插入位置同样有一份**可交互的二分图解**：**[search_insert_visual.html](search_insert_visual.html)** ——
一步一步看 left / right 怎么对半收缩，直观感受 O(log n)。文字版在
**[search_insert_walkthrough.md](search_insert_walkthrough.md)**。

## 题目一览

| 文件 | 题目 | 考点 | 时间 | 空间 |
|---|---|---|---|---|
| [two_sum.py](two_sum.py) | 1. 两数之和 | 哈希表、一次遍历 | O(n) | O(n) |
| [valid_parentheses.py](valid_parentheses.py) | 20. 有效的括号 | 栈、后进先出 | O(n) | O(n) |
| [merge_two_sorted_lists.py](merge_two_sorted_lists.py) | 21. 合并两个有序链表 | 双指针、哑节点 | O(m+n) | O(1) |
| [search_insert.py](search_insert.py) | 35. 搜索插入位置 | 二分查找、左闭右开 | O(log n) | O(1) |
| [submit/2913_...\_i.py](submit/2913_subarrays_distinct_sum_of_squares_i.py) | 2913. 子数组不同元素数目的平方和 I | 枚举 + 集合（**[讲解](subarrays_squares_walkthrough.md)**） | O(n²) | O(n) |
| [submit/2916_...\_ii.py](submit/2916_subarrays_distinct_sum_of_squares_ii.py) | 2916. 子数组不同元素数目的平方和 II | 树状数组、区间加 + 区间求和（**[讲解](subarrays_squares_walkthrough.md)**） | O(n log n) | O(n) |

> 后两题只有「提交版」（直接放在 `submit/`），没有 `leetcode/` 下的练习版 ——
> 因为当时的需求就是"给我能直接粘的代码"。教学材料改用
> **[subarrays_squares_walkthrough.md](subarrays_squares_walkthrough.md)**，里面把
> 「为什么 O(n²) 会超时 → 按右端点分组 → 平方和增量公式 → 两个树状数组」整条线推了一遍。

## 想交到 LeetCode 上？用 `submit/`

上面这四个文件是**练习版**，格式和 LeetCode 要求的不一样（入口是顶层函数、带 `main()`）。
[`submit/`](submit/) 里放着**提交版**，一个文件对应一道题，整文件复制就能用：

| 练习版（自己跑） | 提交版（交作业） | 方法名 |
|---|---|---|
| [two_sum.py](two_sum.py) | [submit/001_two_sum.py](submit/001_two_sum.py) | `twoSum` |
| [valid_parentheses.py](valid_parentheses.py) | [submit/020_valid_parentheses.py](submit/020_valid_parentheses.py) | `isValid` |
| [merge_two_sorted_lists.py](merge_two_sorted_lists.py) | [submit/021_merge_two_sorted_lists.py](submit/021_merge_two_sorted_lists.py) | `mergeTwoLists` |
| [search_insert.py](search_insert.py) | [submit/035_search_insert_position.py](submit/035_search_insert_position.py) | `searchInsert` |
| —（提交版直供） | [submit/2913_subarrays_distinct_sum_of_squares_i.py](submit/2913_subarrays_distinct_sum_of_squares_i.py) | `sumCounts` |
| —（提交版直供） | [submit/2916_subarrays_distinct_sum_of_squares_ii.py](submit/2916_subarrays_distinct_sum_of_squares_ii.py) | `sumCounts` |

提交版由 [verify_submit.py](verify_submit.py) 按 LeetCode 的判题方式校验（49 项全通过）：

```bash
./.venv/Scripts/python.exe leetcode/verify_submit.py
```

> 📖 两数之和另有一份**面向零基础**的逐行讲解：
> [two_sum_walkthrough.md](two_sum_walkthrough.md) ——
> 从"数组和下标是什么"讲起，两种解法各写一遍、每行都拆开解释，
> 附实测性能数据与三个新手常见坑。
>
> 📖 搜索插入位置也有：[search_insert_walkthrough.md](search_insert_walkthrough.md)
> —— 从"为什么不能一个个数"讲起，把二分的边界问题一次说清。

## 四个套路，各记一句话

**哈希表（Two Sum）** —— 暴力解法慢在"重复地找另一半"。用字典把"见过的数"存下来，
把 O(n) 的查找压成 O(1)。核心是**先查再存**，否则重复值会匹配到自己。

**栈（Valid Parentheses）** —— 括号的嵌套规则天然就是"后开的先关"，所以用后进先出。
栈空或栈顶类型不对就判负，遍历完栈必须为空。

**哑节点 + 双指针（Merge Two Sorted Lists）** —— 两个链表已有序，所以每次只要比较
两个头。哑节点用来消掉"结果链表还没有头节点"这个边界分支；
收尾时剩下的一段直接整段挂上，不用再逐个比。

**二分查找（Search Insert Position）** —— 数组有序就能每轮砍一半。
难点从来不是循环，而是**边界**：区间开闭、`<` 还是 `>=`、返回 left 还是 right。
本文用"左闭右开"模板，`while left < right` + `return left`，不用记等号。

**树状数组 + 贡献转化（平方和 II）** —— 直接枚举所有子数组是 O(n²)，n=10⁵ 要 166 秒。
换思路：**按右端点分组**，右端点每挪一格，只有一段 `A[l]` 会整体加 1；
而平方和的增量恰好是 `2·区间和 + 区间长度` —— 于是只要一个支持
"区间加 + 区间求和"的树状数组。**难点不在数据结构，在于想到"按右端点分组"。**

## 最容易写错的那个用例

每道题都有一个"看起来没问题但会挂"的用例，过关的关键就在这里：

| 题目 | 反例 | 为什么错 | 正确答案 |
|---|---|---|---|
| Two Sum | `nums=[3,3], target=6` | 先存后查会返回 `[0,0]`，同一个元素用了两次 | `[0,1]` |
| Valid Parentheses | `s="([)]"` | 数量都对得上，但顺序错了；只看数量会误判为有效 | `False` |
| Merge Two Sorted Lists | `l1=[], l2=[0]` | 忘记处理"一开始就有链表为空"，会崩或返回错 | `[0]` |
| Search Insert Position | `nums=[1,3,5,6], target=7` | 插在末尾时答案等于 `len(nums)`，写错边界会越界或返回 3 | `4` |
| 平方和 II | `nums=[1,2,1]` | `1` 出现两次；忘了"已出现过就不再增加计数"、或忘了更新 `last`，实测都会算成 `20` 而不是 `15` | `15` |

## 验收标准（重要）

**"测试通过"不等于"学会了"。** 这几道题的答案网上到处都有，
复制一份能跑的代码，对学习没有任何意义。真正的验收只有两条：

- [ ] 关掉代码，能用自己的话把每道题的**思路**讲一遍（不是背代码）
- [ ] 能说出每道题**最容易写错的那个边界用例**，以及为什么会错

讲得出来才算过。

## 关于"用 AI 写题解"这件事

这几份代码是 AI 写的，"AI 工具初体验"这一条任务也确实是要用 AI。
但用法有讲究——**你要做的是审稿人，不是收件箱**。至少做这三件事：

1. **先自己写**，卡住了再问 AI。全程被动接收，等于什么也没练到。
2. **追问"为什么"**——比如问：为什么这里必须用 `<=` 而不是 `<`？
   为什么哑节点能省掉一个 if 分支？为什么二分要写 `right = mid` 而不是 `mid - 1`？
3. **自己加一个测试用例**，尤其是那种"看起来不合法但边界很怪"的输入。
   跑一遍 `run_all.py` 会执行 35 个用例，其中 `([)]`、`[3,3]`、`[] + [0]`、
   `target=7`（插到末尾）这四个是最有价值的。

至于怎么问才能一次拿到能用的答案，见 [../PROMPT-GUIDE.md](../PROMPT-GUIDE.md)。
