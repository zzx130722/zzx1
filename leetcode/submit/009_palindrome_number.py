class Solution:
    def isPalindrome(self, x: int) -> bool:
        # 负数一定不是回文（前面多一个负号）
        # 末位是 0 但本身不是 0 的数也一定不是（回文的首位不可能是 0）
        if x < 0 or (x % 10 == 0 and x != 0):
            return False

        # 只反转后一半数字，避免整数溢出（其他语言需要注意，Python 无所谓）
        reversed_half = 0
        while x > reversed_half:
            reversed_half = reversed_half * 10 + x % 10
            x //= 10

        # 偶数位：两边完全相等，如 1221 -> x=12, reversed_half=12
        # 奇数位：中间那位不影响回文，去掉它再比，如 12321 -> x=12, reversed_half=123
        return x == reversed_half or x == reversed_half // 10
