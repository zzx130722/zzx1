class Solution:
    def isValid(self, s: str) -> bool:
        # 右括号 -> 它需要的左括号
        closer_to_opener = {")": "(", "]": "[", "}": "{"}
        stack = []

        for ch in s:
            if ch in "([{":
                stack.append(ch)
            elif ch in closer_to_opener:
                # 栈空（右括号多了）或栈顶对不上（类型/顺序错）都判负
                if not stack or stack.pop() != closer_to_opener[ch]:
                    return False
            else:
                # 题目保证只含括号，这里对意外字符显式判负
                return False

        # 全部闭合才算有效
        return not stack
