"""Travel Agent 核心 — 基于 ReAct 模式的智能出行规划代理。

架构说明：
    用户请求 → Agent（LLM 作为"大脑"）
                  ├─ 自主决策：需要调用哪些工具、调用几次、用什么参数
                  ├─ 工具调用：query_weather / search_attractions / plan_route / ...
                  ├─ 观察结果：根据工具返回的实时数据调整策略
                  └─ 生成方案：综合所有信息输出完整出行计划

    与传统"硬编码流水线"的区别：
    - 旧方式：代码写死 → 先查天气 → 再查路线 → 塞进 prompt → 调一次 LLM
    - Agent方式：LLM 自己判断 → "下雨了？那我多搜几个室内景点" → 动态调整策略

技术实现：
    使用 LangChain 1.2+ 的 create_agent API（底层基于 LangGraph 状态图）。
    Agent 是一个 CompiledStateGraph，支持 invoke/stream/astream_events。
"""

import asyncio
import time

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage

from config import (
    DEEPSEEK_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE,
    AGENT_MAX_ITERATIONS, AGENT_MAX_TOKENS, LOW_BUDGET_THRESHOLD,
)
from services.tools import ALL_TOOLS
from services.llm import llm
from services.memory import get_memory_manager
from database import log_agent_execution

# ── Agent 系统提示词 ──

PLAN_SYSTEM_PROMPT = """你是一位专业的旅行规划师，拥有多种工具来获取实时信息。

## 你的能力
你可以调用以下工具来获取实时数据，帮助你制定更准确的出行方案：
- query_weather: 查询目的地天气预报
- search_attractions: 搜索景点、餐厅、博物馆等兴趣点
- plan_route: 规划两个地点之间的交通路线
- search_hotels_nearby: 搜索指定地点附近的酒店
- geocode_address: 查询地点的经纬度坐标

## 规划流程（请严格按照此流程执行）
1. **查询天气**：调用 query_weather 了解出行期间的天气情况
2. **根据天气调整策略**：
   - 如果有雨：主动搜索室内景点（博物馆、商场、美食街等）替代户外景点
   - 如果高温：推荐避暑地点和室内活动
3. **搜索兴趣点**：调用 search_attractions 搜索用户感兴趣的景点和餐厅
4. **规划路线**：调用 plan_route 查询关键景点之间的交通方式，优化游览顺序
5. **推荐住宿**：调用 search_hotels_nearby 搜索景点附近的高性价比住宿
6. **综合输出**：根据收集到的所有实时数据，生成完整的出行方案

## 输出要求
- 按【天】规划，每天按时段（上午→中午→下午→晚上）安排
- 每个地点包含：名称、地址、人均消费、推荐理由（贴合用户风格）
- 标注景点间的交通方式和大致耗时
- 详细的预算明细（餐饮、门票、交通、住宿）
- 每个景点附带1条避坑提醒
- 最后给出3个本地隐藏彩蛋玩法
- 语言亲切自然，像朋友推荐一样
- 如果天气有特殊情况，方案开头给出天气出行提示
- 方案必须一次性给出完整信息，不要以问句结尾（如"需要我帮您…？""要不要…？"），用户没有继续对话的入口

注意：务必实际调用工具获取实时数据，不要凭空编造天气、路线或酒店信息。

{memory_context}"""

CHAT_SYSTEM_PROMPT = """你是{destination}的智能旅行顾问，名字叫"小旅"。

你可以调用工具来获取实时信息（天气、景点、路线、酒店等），给出更准确的建议。
遇到关于天气、景点、交通、住宿的具体问题时，请主动调用工具查询。

回答要求：
1. 用亲切自然的语气，像朋友聊天一样
2. 回答要具体、实用，尽量引用工具返回的实时数据
3. 可以根据你的知识合理补充
4. 不要回答与旅行无关的问题
5. 不要以问句结尾（如"需要我帮您…？""要不要…？"），用户没有继续对话的入口，所有信息请一次性给全

{memory_context}"""


# ── TravelAgent 主类 ──

class TravelAgent:
    """出行规划 Agent，封装了旅行方案生成和智能聊天两个核心能力。

    内部使用 LangGraph 状态图实现 ReAct 循环：
    - model 节点：LLM 推理，决定下一步动作（调用工具 or 生成回答）
    - tools 节点：执行工具调用，返回结果给 model
    - 循环直到 LLM 认为信息充分，输出最终回答
    """

    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("请在 .env 文件中配置 DEEPSEEK_API_KEY")

        self.tools = ALL_TOOLS
        self.memory = get_memory_manager()

    def _get_plan_agent(self, memory_context: str = ""):
        """构建带记忆上下文的方案生成 Agent。"""
        system_prompt = PLAN_SYSTEM_PROMPT.format(
            memory_context=memory_context or "（暂无该用户的历史记忆）"
        )
        return create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )

    def _get_chat_agent(self, destination: str, memory_context: str = ""):
        """构建带记忆上下文的聊天 Agent。"""
        system_prompt = CHAT_SYSTEM_PROMPT.format(
            destination=destination,
            memory_context=memory_context or "（暂无该用户的历史记忆）"
        )
        return create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )

    def _format_plan_input(self, request_data: dict) -> str:
        """将前端请求参数转换为自然语言描述，供 Agent 理解用户需求。"""
        city = request_data["destination"]
        days = request_data["duration"]
        people = request_data["peopleCount"]
        budget = request_data["budget"]
        style = request_data.get("style_text", "")
        hobbies = "、".join(request_data.get("selectedPreferences", [])) or "无特殊偏好"
        dietary = request_data.get("dietaryRequirements", "") or "无特殊要求"
        attractions = request_data.get("desiredAttractions", "") or "无特殊要求"
        date_range = request_data.get("date_range", "未指定")
        remarks = request_data.get("remarks", "") or "无"

        per_day = budget / max(days, 1)
        budget_hint = ""
        if per_day < LOW_BUDGET_THRESHOLD:
            budget_hint = (
                "\n【注意】用户预算较为有限，请优先推荐免费/低价景点、"
                "平价餐馆、公共交通、经济型住宿等省钱玩法。"
            )

        return (
            f"请为用户规划一个{city}的出行方案：\n"
            f"- 出行天数：{days}天\n"
            f"- 出行人数：{people}人\n"
            f"- 总预算：{budget}元（约{per_day:.0f}元/天）\n"
            f"- 旅游风格：{style}\n"
            f"- 兴趣偏好：{hobbies}\n"
            f"- 饮食要求：{dietary}\n"
            f"- 想去的景点：{attractions}\n"
            f"- 出行时段：{date_range}\n"
            f"- 用户备注：{remarks}"
            f"{budget_hint}"
        )

    def _extract_tools_and_answer(self, messages: list) -> tuple[list[str], str, int]:
        """从 Agent 输出的消息列表中提取工具调用记录和最终回答。"""
        tools_called = []
        final_answer = ""
        iterations = 0

        for msg in messages:
            if isinstance(msg, AIMessage):
                tool_calls = getattr(msg, "tool_calls", [])
                if tool_calls:
                    iterations += 1
                    for tc in tool_calls:
                        tools_called.append(tc.get("name", ""))
                else:
                    final_answer = msg.content or ""

        return tools_called, final_answer, iterations

    def generate_plan(self, request_data: dict) -> dict:
        """生成出行方案（非流式），自动加载用户记忆上下文。

        记忆流程：
        1. build_context() 加载用户偏好 + 长期记忆 + 历史方案
        2. 注入到 Agent 的 system prompt
        3. Agent 根据记忆个性化生成方案
        4. 方案保存到 plan_history（工作记忆）
        """
        user_id = request_data.get("user_id")
        user_input = self._format_plan_input(request_data)

        # 加载记忆上下文
        memory_context = self.memory.build_context(user_id) if user_id else ""
        agent = self._get_plan_agent(memory_context)

        start_time = time.time()
        result = agent.invoke({"messages": [HumanMessage(content=user_input)]})

        duration_ms = int((time.time() - start_time) * 1000)
        messages = result.get("messages", [])
        tools_called, final_answer, iterations = self._extract_tools_and_answer(messages)

        log_agent_execution(
            user_id=user_id, task_type="plan",
            input_summary=user_input[:200],
            tools_called=tools_called,
            final_answer=final_answer[:2000],
            iterations=iterations, duration_ms=duration_ms,
        )

        # 保存到工作记忆
        if user_id:
            self.memory.save_plan_history(
                user_id=user_id,
                destination=request_data["destination"],
                request_summary=user_input[:300],
                plan_text=final_answer,
                tools_called=tools_called,
            )

        return {
            "plan": final_answer,
            "tools_called": tools_called,
            "iterations": iterations,
        }

    def generate_plan_stream(self, request_data: dict, queue: asyncio.Queue) -> dict:
        """生成出行方案（流式），自动加载用户记忆上下文。"""
        user_id = request_data.get("user_id")
        user_input = self._format_plan_input(request_data)

        memory_context = self.memory.build_context(user_id) if user_id else ""
        agent = self._get_plan_agent(memory_context)

        queue.put_nowait({"type": "agent_start", "message": "正在为您智能规划..."})

        start_time = time.time()
        all_tools_called: list[str] = []
        iterations = 0
        final_answer = ""

        for event in agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                if not isinstance(node_output, dict) or "messages" not in node_output:
                    continue

                for msg in node_output["messages"]:
                    if isinstance(msg, AIMessage):
                        tool_calls = getattr(msg, "tool_calls", [])
                        if tool_calls:
                            iterations += 1
                            for tc in tool_calls:
                                all_tools_called.append(tc.get("name", ""))
                                queue.put_nowait({
                                    "type": "tool_call",
                                    "tool": tc.get("name", ""),
                                    "args": tc.get("args", {}),
                                })
                        elif msg.content:
                            final_answer = msg.content
                    else:
                        content = str(msg.content)[:500] if hasattr(msg, "content") else ""
                        if content:
                            queue.put_nowait({
                                "type": "tool_result",
                                "result": content,
                            })

        duration_ms = int((time.time() - start_time) * 1000)

        queue.put_nowait({"type": "final_answer", "content": final_answer})

        log_agent_execution(
            user_id=user_id, task_type="plan_stream",
            input_summary=user_input[:200],
            tools_called=all_tools_called,
            final_answer=final_answer[:2000],
            iterations=iterations, duration_ms=duration_ms,
        )

        # 保存到工作记忆
        if user_id:
            self.memory.save_plan_history(
                user_id=user_id,
                destination=request_data["destination"],
                request_summary=user_input[:300],
                plan_text=final_answer,
                tools_called=all_tools_called,
            )

        queue.put_nowait({"type": "done", "duration_ms": duration_ms})

        return {
            "tools_called": all_tools_called,
            "iterations": iterations,
            "duration_ms": duration_ms,
        }

    def chat(self, user_id: int | None, destination: str,
             message: str, session_id: str = "",
             client_history: list[dict] | None = None) -> str:
        """智能聊天，集成完整的三层记忆。

        记忆流程：
        1. 短期记忆：从 DB 加载当前会话的历史对话
        2. 长期记忆 + 工作记忆：build_context() 注入 system prompt
        3. 保存当前轮次到短期记忆
        4. 异步提取用户事实到长期记忆
        """
        # 加载记忆上下文（长期 + 工作）
        memory_context = self.memory.build_context(user_id) if user_id else ""

        # 加载短期记忆：服务端会话历史
        sid = ""
        server_history = []
        if user_id:
            sid = self.memory.get_session_id(user_id, session_id)
            server_history = self.memory.load_session_history(user_id, sid)

        # 合并：服务端历史 + 前端传来的额外历史（兼容旧前端）
        chat_messages = list(server_history)
        if client_history:
            for msg in client_history:
                if msg.get("role") == "user":
                    chat_messages.append(HumanMessage(content=msg.get("text", "")))
                else:
                    chat_messages.append(AIMessage(content=msg.get("text", "")))

        chat_messages.append(HumanMessage(content=message))

        # 构建带记忆的 chat agent
        chat_agent = self._get_chat_agent(destination, memory_context)

        result = chat_agent.invoke({"messages": chat_messages})
        result_messages = result.get("messages", [])

        # 取最后一条 AIMessage
        reply = ""
        for m in reversed(result_messages):
            if isinstance(m, AIMessage) and m.content and not getattr(m, "tool_calls", []):
                reply = m.content
                break

        # 保存到短期记忆
        if user_id and sid:
            self.memory.save_user_message(user_id, sid, message)
            self.memory.save_assistant_message(user_id, sid, reply)

            # 异步提取长期记忆（不阻塞响应）
            try:
                self.memory.extract_facts(user_id, message, reply)
            except Exception:
                pass

        return reply


# ── 全局单例 ──

_agent_instance: TravelAgent | None = None


def get_travel_agent() -> TravelAgent:
    """获取 TravelAgent 全局单例（懒加载，首次调用时初始化）。"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TravelAgent()
    return _agent_instance
