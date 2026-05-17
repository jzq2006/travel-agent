"""LLM 初始化 — 基于 OpenAI 兼容协议，支持多家模型服务商。

支持的服务商（均兼容 OpenAI 接口协议）：
    DeepSeek / 智谱 GLM / 月之暗面 / 通义千问 / OpenAI
    只需配置 LLM_BASE_URL + LLM_API_KEY + AGENT_MODEL 即可切换。
"""

from langchain_openai import ChatOpenAI

from config import LLM_API_KEY, LLM_BASE_URL, AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_TOKENS

if not LLM_API_KEY:
    raise ValueError("请在 .env 文件中配置 LLM_API_KEY（或 DEEPSEEK_API_KEY）")

llm = ChatOpenAI(
    model=AGENT_MODEL,
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    temperature=AGENT_TEMPERATURE,
    max_tokens=AGENT_MAX_TOKENS,
)
