"""LLM 客户端子包：week2-llm/client.py 收编于此。

与原版的区别：config.py 被干掉了——key/base_url/model 改为
调用时从环境变量读取（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL）。
作为「包」被别人安装使用时，读写调用方目录下的 .env 文件是越权行为；
环境变量是进程级约定，谁调用谁负责设置。
"""

from devbasics.llm.client import chat

__all__ = ["chat"]
