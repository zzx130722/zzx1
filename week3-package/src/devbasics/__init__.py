"""devbasics：阶段一练习收编成的规范化 Python 包。

两个子包：
- devbasics.leetcode —— 4 道 LeetCode 题解
- devbasics.llm      —— OpenAI 兼容格式的对话客户端（week2-llm 收编）
"""

from devbasics import leetcode, llm

__all__ = ["leetcode", "llm"]
__version__ = "0.1.0"
