"""LLM 初始化 — 基于 OpenAI 兼容协议，支持多家模型服务商。

支持的服务商（均兼容 OpenAI 接口协议）：
    DeepSeek / 智谱 GLM / 月之暗面 / 通义千问 / OpenAI
    只需配置 LLM_BASE_URL + LLM_API_KEY + AGENT_MODEL 即可切换。
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage
from typing import Literal
from collections.abc import Mapping
from typing import Any

from config import LLM_API_KEY, LLM_BASE_URL, AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_TOKENS

if not LLM_API_KEY:
    raise ValueError("请在 .env 文件中配置 LLM_API_KEY（或 DEEPSEEK_API_KEY）")


# ── Monkey-patch: 兼容 DeepSeek reasoning_content ──
# DeepSeek 思考模式返回 reasoning_content，要求后续请求原样传回。
# langchain-openai 没有处理这个字段，这里补上。
# 对其他模型（智谱、通义、月之暗面等）无影响。

import langchain_openai.chat_models.base as _base

_orig_to_msg = _base._convert_dict_to_message
_orig_to_dict = _base._convert_message_to_dict


def _patched_to_msg(_dict: Mapping[str, Any]) -> BaseMessage:
    msg = _orig_to_msg(_dict)
    if isinstance(msg, AIMessage) and "reasoning_content" in _dict:
        msg.additional_kwargs["reasoning_content"] = _dict["reasoning_content"]
    return msg


def _patched_to_dict(
    message: BaseMessage,
    api: Literal["chat/completions", "responses"] = "chat/completions",
) -> dict:
    d = _orig_to_dict(message, api=api)
    if isinstance(message, AIMessage) and "reasoning_content" in message.additional_kwargs:
        d["reasoning_content"] = message.additional_kwargs["reasoning_content"]
    return d


_base._convert_dict_to_message = _patched_to_msg
_base._convert_message_to_dict = _patched_to_dict


llm = ChatOpenAI(
    model=AGENT_MODEL,
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    temperature=AGENT_TEMPERATURE,
    max_tokens=AGENT_MAX_TOKENS,
)
