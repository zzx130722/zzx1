"""
LeetCode 21. 合并两个有序链表（Merge Two Sorted Lists）—— 难度：简单
https://leetcode.cn/problems/merge-two-sorted-lists/

题目
----
将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的
所有节点组成的。

--------------------------------------------------------------------------
思路：哑节点 + 双指针
--------------------------------------------------------------------------
两个链表已经是升序的，所以答案的每一位只需要比较两个链表的"当前头节点"，
谁小谁先出队——这就是归并排序里 merge 那一步。

难点不在比较，而在"拼"：如果把新链表的头节点直接拿来操作，会遇到一个麻烦——
第一次插入时还没有头，得写一段特殊判断。为了避免这种边界分支，
引入一个**哑节点（dummy）**：

    dummy = ListNode()      # 占位用的假头，不存真实数据
    tail = dummy            # tail 始终指向结果链表的最后一个节点

循环里只做一件事：谁小接谁。结束后 dummy.next 就是真正的答案头部。

循环结束时必然有一个链表先空，剩下那一段**本身就是有序的**，
所以直接整段挂上去，不需要再逐个比较：

    tail.next = l1 or l2

（`or` 在这里恰好是"取非空的那个"：Python 里空链表是 None，为假值。）

--------------------------------------------------------------------------
复杂度
--------------------------------------------------------------------------
时间 O(m + n)：每个节点只被访问一次，m、n 分别是两个链表的长度。
空间 O(1)：只用了 dummy 和 tail 两个额外变量，节点是**原地改指向**，
            没有创建新节点。这一点容易被忽略——很多人会 new 一堆节点出来。

--------------------------------------------------------------------------
边界用例
--------------------------------------------------------------------------
1. [] + []                -> []            两边都空
2. [] + [0]               -> [0]           一边为空
3. [1,2,4] + [1,3,4]      -> [1,1,2,3,4,4] 有相等元素，交替推进
4. [5] + [1,2,3]          -> [1,2,3,5]     一边整体比另一边大
5. [1,1,1] + [1,1]        -> [1,1,1,1,1]   全部相等
6. [-10,-5,0] + [-8,-3]   -> 负数也要正常比较
7. [1,2] + []             -> [1,2]         第一个链表有、第二个为空
"""


class ListNode:
    """LeetCode 给定的单链表节点定义。"""

    def __init__(self, val: int = 0, next: "ListNode | None" = None):
        self.val = val
        self.next = next


def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    """合并两个升序链表，返回合并后的头节点。原地改指向，不新建节点。"""
    dummy = ListNode()  # 哑节点，避免"第一个节点"的特殊处理
    tail = dummy

    while l1 and l2:
        # 用 <= 而不是 <：相等时优先取 l1，保证合并是稳定的
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next

    # 剩下的一段本身有序，直接整体挂上
    tail.next = l1 or l2

    return dummy.next


def build(values: list[int]) -> ListNode | None:
    """用列表构造链表，方便测试。"""
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head: ListNode | None) -> list[int]:
    """把链表转回列表，方便断言。"""
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def main() -> int:
    cases = [
        ([], [], []),
        ([], [0], [0]),
        ([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),
        ([5], [1, 2, 3], [1, 2, 3, 5]),
        ([1, 1, 1], [1, 1], [1, 1, 1, 1, 1]),
        ([-10, -5, 0], [-8, -3], [-10, -8, -5, -3, 0]),
        ([1, 2], [], [1, 2]),
    ]

    passed = 0
    print("[3] 合并两个有序链表 (Merge Two Sorted Lists)")
    for a, b, expected in cases:
        actual = to_list(merge_two_lists(build(a), build(b)))
        ok = actual == expected
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"    [{mark}] {a} + {b} -> {actual}  期望 {expected}")

    # 额外验证空间复杂度 O(1)：合并后应复用原节点，而不是复制出新对象
    left, right = build([1, 3]), build([2, 4])
    ids_before = {id(left), id(right), id(left.next), id(right.next)}
    merged = merge_two_lists(left, right)
    ids_after = set()
    node = merged
    while node:
        ids_after.add(id(node))
        node = node.next
    reused = ids_before <= ids_after
    passed += reused
    print(f"    [{'PASS' if reused else 'FAIL'}] 原节点被复用而非复制（验证 O(1) 空间）")

    total = len(cases) + 1
    print(f"    通过 {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
