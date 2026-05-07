"""LLM 初始化 — 提供底层 LLM 实例供 Agent 和其他模块使用。

注意：Agent 逻辑已移至 services/agent.py，本文件仅保留 LLM 实例化。
"""

from langchain_deepseek import ChatDeepSeek

from config import DEEPSEEK_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_TOKENS

if not DEEPSEEK_API_KEY:
    raise ValueError("请在 .env 文件中配置 DEEPSEEK_API_KEY")

llm = ChatDeepSeek(
    model=AGENT_MODEL,
    api_key=DEEPSEEK_API_KEY,
    temperature=AGENT_TEMPERATURE,
    max_tokens=AGENT_MAX_TOKENS,
)
