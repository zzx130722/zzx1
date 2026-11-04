"""LeetCode 21. 合并两个有序链表（哑节点 + 双指针，归并的 merge 步）。

哑节点（dummy）的价值：省掉「第一个节点还没有头」的特殊分支。
循环结束时剩下那一段本身有序，直接整段挂上，不用再比较。
"""


class ListNode:
    """LeetCode 给定的单链表节点定义。"""

    def __init__(self, val: int = 0, next: "ListNode | None" = None):
        self.val = val
        self.next = next


def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    """合并两个升序链表，返回合并后的头节点。原地改指向，不新建节点。"""
    dummy = ListNode()  # 哑节点，避免「第一个节点」的特殊处理
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
