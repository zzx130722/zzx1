# 怎么把这些题解放到 LeetCode 上跑

> 面向零基础读者。看完这一份，三道题都能自己提交通过。

---

## 一、先说最重要的：本地文件**不能直接粘**

`leetcode/` 下的三个 `.py` 文件是**本地练习版**——它们能独立运行、能自己测自己，
但 LeetCode 的代码框只认一种固定格式，两者有三处不一样：

| 对比项 | 我们的本地文件 | LeetCode 代码框要的 |
|---|---|---|
| **入口** | 顶层函数 `def two_sum(...)` | 必须包在 `class Solution:` 里 |
| **方法名** | `two_sum`（下划线） | `twoSum`（驼峰）—— **必须一字不差** |
| **类型提示** | `list[int]` | `List[int]`（需 `from typing import List`） |
| **`main()` 自测** | 有 | **删掉**，LeetCode 不会执行它 |
| **链表节点类** | 自己定义了 `ListNode` | **不要重复定义**，LeetCode 已内置 |

### 为什么方法名必须一致？

LeetCode 判题时是**它来调用你的函数**。它以固定名字去找：

```python
Solution().twoSum([2,7,11,15], 9)
```

所以如果你的方法叫 `two_sum`，它找不到目标，就会报错或判你"无返回值"。

### 为什么不能带 `main()`？

我们本地的 `main()` 是**自己测自己**用的（跑那 7 个用例）。
LeetCode 的流程是反过来的——**它用隐藏用例来测你**。留着 `main()` 不会报错，
但它是无效代码，交上去也不规范，建议删掉。

---

## 二、四道题的可直接粘贴代码

以下是**逐字对应 LeetCode 中文站 Python3 模板**的版本，可以直接全选粘贴。

### 题目 1：两数之和

题目地址：<https://leetcode.cn/problems/two-sum/>

```python
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}

        for i, n in enumerate(nums):
            need = target - n

            if need in seen:
                return [seen[need], i]

            seen[n] = i

        return []
```

### 题目 2：有效的括号

题目地址：<https://leetcode.cn/problems/valid-parentheses/>

```python
class Solution:
    def isValid(self, s: str) -> bool:
        closer_to_opener = {")": "(", "]": "[", "}": "{"}
        stack = []

        for ch in s:
            if ch in "([{":
                stack.append(ch)
            elif ch in closer_to_opener:
                if not stack or stack.pop() != closer_to_opener[ch]:
                    return False
            else:
                return False

        return not stack
```

### 题目 3：合并两个有序链表

题目地址：<https://leetcode.cn/problems/merge-two-sorted-lists/>

> ⚠️ 这题有个特殊之处：LeetCode 的模板里**已经在注释中给出了 `ListNode` 的定义**。
> 粘贴时**保留那一整段注释**（或删掉都行，LeetCode 会自动注入），
> 但**千万不要自己再写一个 `class ListNode`** —— 那样会和 LeetCode 注入了的类打架。

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
from typing import Optional


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        tail = dummy

        while list1 and list2:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next

        tail.next = list1 or list2

        return dummy.next
```

### 题目 4：搜索插入位置

题目地址：<https://leetcode.cn/problems/search-insert-position/>

> ⚠️ 这题题目里明写着 **「请必须使用时间复杂度为 O(log n) 的算法」**。
> 用 `for` 循环一个个扫是能通过的（测试数据不大），但不符合题目要求，
> 面试时也会被判不合格——一定要用二分。

```python
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        # 左闭右开区间 [left, right)：右边 left == right 时区间为空
        left, right = 0, len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                # 中间值太小，mid 和它左边全排除
                left = mid + 1
            else:
                # 中间值够大，mid 本身可能是答案，必须保留
                right = mid
        # 循环结束时 left == right，正是"第一个 >= target 的位置"
        # 若 target 比所有数都大，left 会自然停在 len(nums)，即插入到末尾
        return left
```

> 三个最容易踩的边界：`while left < right` 不能写成 `<=`；
> `right = mid` 不能写成 `mid - 1`；`target` 比所有数都大时答案等于 `len(nums)`。
> 详细推导见 [search_insert_walkthrough.md](search_insert_walkthrough.md)，
> 想看动态过程就打开 [search_insert_visual.html](search_insert_visual.html)。

---

## 三、页面上怎么操作（七步）

1. **打开题目页**。直接在浏览器输入上面给的地址，或在题库里搜题号。
2. **登录**。不登录也能写代码，但**提交必须登录**（用手机号或 GitHub 都行）。
3. **选语言**。代码框左上角有个语言下拉框，选 **Python3**（别选成 Python，
   那是 Python 2，语法有差异）。
4. **清空并粘贴**。在代码框里按 `Ctrl + A` 全选 → `Delete` 删除默认模板 →
   粘贴上面给的完整代码。
5. **先点「运行」**。它只跑**下方显示的测试用例**（一般就是题目里的示例），
   几秒后右下角会显示你的输出。这一步是"自查"。
6. **再点「提交」**。它跑**全部隐藏用例**（几百个，包含各种边界）。
   等待几秒，出现绿色的「通过」就说明对了。
7. **看结果**。通过后会显示「执行用时」和「内存消耗」，以及"击败了 xx% 的用户"。

> **「运行」和「提交」的区别**，是这两步最值得理解的地方：
> 「运行」= 用你指定的几个用例试跑，给你看中间结果，用来调试；
> 「提交」= 用全部隐藏用例判题，不给中间结果，只告诉你过没过。
> **日常习惯：先运行确认示例过，再提交。** 直接提交虽然也行，但错了就白等一次。

---

## 四、一个特别有用的技巧：把你自己的边界用例填进去

第 5 步的「测试用例」区域是**可编辑的**。这就是它最值钱的地方——
把我们在本地写的那些"刁钻用例"填进去，用「运行」验证：

| 题目 | 填什么 | 用来验证什么 |
|---|---|---|
| 两数之和 | `nums = [3,3], target = 6` | **"先查再存"是否写对了**（写反会输出 `[0,0]`） |
| 有效的括号 | `s = "([)]"` | 数量都对但顺序错 —— 最容易漏的一个 |
| 合并链表 | `list1 = [], list2 = [0]` | 一开始就有链表为空的情况 |

**这一步比"提交通过"更能说明你真的懂了。** 因为隐藏用例通过可能只是运气好，
而你自己设计的用例通过，说明你主动想到了那个坑。

---

## 五、常见报错对照表

| 报错 / 现象 | 原因 | 怎么改 |
|---|---|---|
| `NameError: name 'Solution' is not defined` | 忘了写 `class Solution:` 这一行 | 检查最外层是不是 `class Solution:` |
| `AttributeError: 'Solution' object has no attribute 'twoSum'` | 方法名拼错了 | 必须是 `twoSum` / `isValid` / `mergeTwoLists` / `searchInsert` |
| 提示「无返回值」或输出 `null` | 函数里没 `return`，或 `return` 在 `if` 里面漏了 | 检查每条分支都有返回值 |
| `IndentationError` / `TabError` | 粘贴时缩进乱了（Tab 和空格混用） | 全选删除后重新粘；粘贴时选"粘贴"而不是"粘贴并匹配样式" |
| `NameError: name 'List' is not defined` | 少了 `from typing import List` | 把第一行的导入补上 |
| `TypeError: ... takes 2 positional arguments but 3 were given` | 方法忘了写 `self` 参数 | 第一个参数必须是 `self` |
| 写着"解答错误"，但本地明明能跑 | **用错了方法名或漏了 `self`** —— 平台根本没调到你的代码 | 对照上面的报错表逐条查 |
| 显示"超出时间限制"（TLE） | 用了 O(n²) 的暴力解法 | 两数之和换哈希表版；搜索插入位置换二分的 `while` 版 |

---

## 六、你现在可以做的练习（建议按顺序）

1. **把四道题都提交一遍**，拿到四个绿色的「通过」。
2. **故意改坏一次**：把两数之和的"先查再存"改成"先存再查"，
   用 `[3,3]` 这个测试用例运行——看它真的输出 `[0,0]`。
   **看过一次错误，比看十遍正确更记得住。**
3. **再故意改坏一次（二分专用）**：把搜索插入位置的 `right = mid` 改成 `right = mid - 1`，
   跑一遍 `nums = [1,3,5,6], target = 5`——本地会看到返回 1 而不是 2。
   这一处是最经典的二分边界错误，亲手踩一次就再也忘不掉。
   （注意：这种错法在多数用例上仍然是"对的"，所以光试几个数发现不了，
   必须专门挑那个能把边界戳出来的用例。）
4. **提交记录会留在你的账号里**，形成一条成长轨迹。
   以后回看自己的代码，能明显看出进步。

> 最后提醒：**拿到绿色「通过」不等于学会。**
> 真正的验收标准还是那句老话——合上代码，你能不能把思路讲给别人听？
> 能不能说出"为什么这里必须 `<=` 不能 `<`"？
