"""LeetCode 20. 有效的括号（栈）。

括号的嵌套规则本身就是「后开的先关」，正是后进先出——所以用栈。

三个失败场景各对应一条判断：
1. "("  -> 遍历完栈没空       -> 有左括号没闭合
2. ")"  -> 遇到右括号时栈为空 -> 右括号多了
3. "(]" -> 栈顶和右括号不匹配 -> 类型对不上
"""


def is_valid(s: str) -> bool:
    """判断括号字符串是否有效。"""
    # 右括号 -> 它需要的左括号
    closer_to_opener = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []

    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in closer_to_opener:
            # 栈空（右括号多了）或栈顶对不上（类型/顺序错）都判负
            if not stack or stack.pop() != closer_to_opener[ch]:
                return False
        else:
            # 题目保证只含括号，这里对意外字符显式判负，避免静默放过
            return False

    # 全部闭合才算有效
    return not stack
