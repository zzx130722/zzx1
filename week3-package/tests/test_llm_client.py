"""LLM 客户端的测试用例。

只测「不发网络请求也能验证的逻辑」：配置缺失、参数校验。
真实调 API 属于集成测试，需要 key，不放进单元测试。
"""

import pytest

from devbasics.llm import chat

GOOD_MESSAGES = [
    {"role": "system", "content": "你是测试助手"},
    {"role": "user", "content": "你好"},
]


def test_chat_requires_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="LLM_API_KEY"):
        chat(GOOD_MESSAGES)


def test_chat_rejects_missing_system_role(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    with pytest.raises(ValueError, match="system"):
        chat([{"role": "user", "content": "你好"}])


def test_chat_rejects_empty_messages(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    with pytest.raises(ValueError, match="system"):
        chat([])
