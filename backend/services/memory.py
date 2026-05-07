"""Agent 记忆系统 — 三层记忆架构。

┌─────────────────────────────────────────────────────┐
│                    用户请求                          │
│                       │                              │
│                       ▼                              │
│  ┌─────────────────────────────────────────────┐    │
│  │         记忆管理器 (MemoryManager)           │    │
│  │                                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │ 短期记忆  │  │ 长期记忆  │  │ 工作记忆  │  │    │
│  │  │          │  │          │  │          │  │    │
│  │  │ 当前会话  │  │ 用户画像  │  │ 方案历史  │  │    │
│  │  │ 对话历史  │  │ 自动提取  │  │ 参考复用  │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  │    │
│  │       │              │             │         │    │
│  │       └──────────────┼─────────────┘         │    │
│  │                      ▼                        │    │
│  │            build_context() → 注入 prompt      │    │
│  └─────────────────────────────────────────────┘    │
│                       │                              │
│                       ▼                              │
│                   Travel Agent                       │
└─────────────────────────────────────────────────────┘

三层记忆说明：

1. 短期记忆（Short-term）
   - 存储：conversation_history 表
   - 内容：当前会话的用户/AI 对话记录
   - 生命周期：一次会话（可跨多个请求，服务端管理）
   - 作用：Agent 理解当前对话上下文

2. 长期记忆（Long-term）
   - 存储：user_memory 表
   - 内容：从历史对话中自动提取的用户偏好/画像
   - 生命周期：永久，跨所有会话
   - 作用：Agent 个性化推荐（"你之前说过不吃辣"）

3. 工作记忆（Working）
   - 存储：plan_history 表
   - 内容：为用户生成过的出行方案摘要
   - 生命周期：永久，跨所有会话
   - 作用：Agent 避免重复推荐、参考历史方案
"""

import json

from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage

from config import DEEPSEEK_API_KEY, AGENT_MODEL
from database import (
    save_message, load_conversation, get_or_create_session,
    save_user_facts, load_user_facts,
    save_plan, load_recent_plans,
    get_user_preferences,
)

# ── 事实提取提示词 ──

FACT_EXTRACTION_PROMPT = """你是一个信息提取器。从以下用户与AI旅行顾问的对话中，提取用户的旅行偏好和关键个人信息。

只提取用户明确提到的信息，不要推测。每条事实用一句话概括。

将信息分类为以下类别之一：
- preference: 旅行风格偏好（如喜欢自然风光、不喜欢人多的地方）
- dietary: 饮食要求（如不吃辣、素食、对海鲜过敏）
- budget: 预算习惯（如预算有限、愿意花大钱住好酒店）
- destination: 去过或想去的目的地
- companion: 出行同伴信息（如带小孩、情侣出行、独自旅行）
- general: 其他有用的旅行相关信息

用户说：{user_message}
AI回复：{ai_message}

请输出JSON格式（不要输出其他内容）：
{{"facts": [{{"category": "类别", "fact": "具体事实"}}]}}

如果没有新的有用信息，返回：{{"facts": []}}"""


class MemoryManager:
    """三层记忆管理器，负责记忆的读写和上下文构建。"""

    def __init__(self):
        # 用一个轻量 LLM 实例做事实提取（temperature=0，低 token）
        self._extractor_llm = ChatDeepSeek(
            model=AGENT_MODEL,
            api_key=DEEPSEEK_API_KEY,
            temperature=0,
            max_tokens=500,
        )

    # ── 短期记忆：会话历史 ──

    def get_session_id(self, user_id: int, client_session_id: str = "") -> str:
        """获取会话ID：前端传了就用前端的，否则取最近会话或新建。"""
        if client_session_id:
            return client_session_id
        return get_or_create_session(user_id)

    def load_session_history(self, user_id: int, session_id: str,
                             limit: int = 20) -> list:
        """从数据库加载当前会话的对话历史，转为 LangChain 消息对象。"""
        rows = load_conversation(user_id, session_id, limit)
        messages = []
        for row in rows:
            if row["role"] == "user":
                messages.append(HumanMessage(content=row["content"]))
            else:
                messages.append(AIMessage(content=row["content"]))
        return messages

    def save_user_message(self, user_id: int, session_id: str, content: str):
        save_message(user_id, session_id, "user", content)

    def save_assistant_message(self, user_id: int, session_id: str, content: str):
        save_message(user_id, session_id, "assistant", content)

    # ── 长期记忆：用户画像 ──

    def get_user_facts_text(self, user_id: int) -> str:
        """将用户的所有长期记忆格式化为文本，供注入 prompt。"""
        facts = load_user_facts(user_id)
        if not facts:
            return ""

        # 按类别分组
        grouped: dict[str, list[str]] = {}
        for f in facts:
            grouped.setdefault(f["category"], []).append(f["fact"])

        category_names = {
            "preference": "旅行偏好",
            "dietary": "饮食要求",
            "budget": "预算习惯",
            "destination": "去过/想去的目的地",
            "companion": "出行同伴",
            "general": "其他信息",
        }

        lines = []
        for cat, items in grouped.items():
            label = category_names.get(cat, cat)
            lines.append(f"- {label}：" + "；".join(items))

        return "\n".join(lines)

    def extract_facts(self, user_id: int, user_message: str, ai_message: str):
        """用 LLM 从对话中自动提取用户事实，存入长期记忆。

        这个方法会在 Agent 回复之后异步调用，不影响响应速度。
        """
        prompt = FACT_EXTRACTION_PROMPT.format(
            user_message=user_message[:1000],
            ai_message=ai_message[:1000],
        )

        try:
            response = self._extractor_llm.invoke([HumanMessage(content=prompt)])
            text = response.content.strip()

            # 提取 JSON 部分
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            facts = data.get("facts", [])

            if facts:
                save_user_facts(user_id, facts)

        except (json.JSONDecodeError, Exception):
            pass  # 提取失败不影响主流程

    # ── 工作记忆：方案历史 ──

    def get_recent_plans_text(self, user_id: int, limit: int = 3) -> str:
        """将用户的历史方案格式化为摘要文本。"""
        plans = load_recent_plans(user_id, limit)
        if not plans:
            return ""

        lines = []
        for i, plan in enumerate(plans, 1):
            lines.append(
                f"{i}. {plan['destination']}（{plan['created_at']}）"
                f"— {plan['request_summary']}"
            )

        return "\n".join(lines)

    def save_plan_history(self, user_id: int, destination: str,
                          request_summary: str, plan_text: str,
                          tools_called: list[str]):
        save_plan(user_id, destination, request_summary, plan_text, tools_called)

    # ── 综合上下文构建 ──

    def build_context(self, user_id: int) -> str:
        """构建 Agent 记忆上下文，注入到 system prompt 中。

        包含：用户偏好表单 + 长期记忆事实 + 历史方案摘要
        """
        sections = []

        # 1. 用户手动设置的偏好
        prefs = get_user_preferences(user_id)
        if prefs:
            pref_lines = []
            if prefs.get("travel_style"):
                pref_lines.append(f"旅行风格：{prefs['travel_style']}")
            if prefs.get("budget_level") and prefs["budget_level"] != "medium":
                pref_lines.append(f"预算级别：{prefs['budget_level']}")
            if prefs.get("dietary_restrictions"):
                pref_lines.append(f"饮食限制：{prefs['dietary_restrictions']}")
            if prefs.get("favorite_destinations"):
                pref_lines.append(f"喜欢的目的地：{prefs['favorite_destinations']}")
            if prefs.get("notes"):
                pref_lines.append(f"备注：{prefs['notes']}")
            if pref_lines:
                sections.append("用户设置的偏好：\n" + "\n".join(f"- {l}" for l in pref_lines))

        # 2. 自动提取的长期记忆
        facts_text = self.get_user_facts_text(user_id)
        if facts_text:
            sections.append("从历史对话中了解到的用户信息：\n" + facts_text)

        # 3. 历史方案
        plans_text = self.get_recent_plans_text(user_id)
        if plans_text:
            sections.append(
                "为该用户生成过的历史方案（避免重复推荐，可以在此基础上深化）：\n"
                + plans_text
            )

        if not sections:
            return ""

        return (
            "## 关于这位用户（记忆系统自动提供）\n\n"
            + "\n\n".join(sections)
            + "\n\n请在规划时参考以上信息，让方案更贴合这位用户。"
        )


# ── 全局单例 ──

_memory_instance: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = MemoryManager()
    return _memory_instance
