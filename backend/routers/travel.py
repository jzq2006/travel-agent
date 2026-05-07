"""出行规划路由 — Agent 驱动的核心 API。

端点概览：
    POST /api/generate-plan        — Agent 生成完整出行方案（非流式，带记忆）
    POST /api/generate-plan/stream — Agent 生成出行方案（SSE 流式，带记忆）
    POST /api/chat                 — Agent 智能聊天（工具调用 + 三层记忆）
    POST /api/booking              — 创建预订
    GET  /api/bookings             — 查询当前用户的预订
    POST /api/newsletter/subscribe — 邮件订阅
    GET  /api/me                   — 当前用户信息
    GET  /api/preferences          — 获取用户偏好
    POST /api/preferences          — 保存用户偏好
    GET  /api/memory               — 查看当前用户的记忆内容
"""

import asyncio
import json
import re
import uuid

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from auth import require_login, get_current_user
from database import get_db, get_user_preferences, save_user_preferences
from models import (
    TravelPlanRequest, ChatRequest, BookingRequest, SubscribeRequest,
    UserPreferencesRequest,
)
from services.agent import get_travel_agent
from services.memory import get_memory_manager
from config import STYLE_MAP, LOW_BUDGET_THRESHOLD

router = APIRouter()


# ── Agent 出行方案生成（非流式） ──

@router.post("/api/generate-plan")
async def generate_travel_plan(request: TravelPlanRequest, user=Depends(require_login)):
    """Agent 自主编排工具调用，生成完整出行方案。

    记忆系统集成：
    - 加载用户长期记忆（偏好/画像）和历史方案，注入 Agent system prompt
    - 生成的方案自动保存到工作记忆（plan_history）
    """
    try:
        agent = get_travel_agent()
        style_text = STYLE_MAP.get(request.travelType, request.travelType)
        date_range = (
            f"{request.startDate}至{request.endDate}"
            if request.startDate and request.endDate else "未指定"
        )

        request_data = {
            "destination": request.destination,
            "duration": request.duration,
            "peopleCount": request.peopleCount,
            "budget": request.budget,
            "style_text": style_text,
            "selectedPreferences": request.selectedPreferences or [],
            "dietaryRequirements": request.dietaryRequirements,
            "desiredAttractions": request.desiredAttractions,
            "date_range": date_range,
            "remarks": request.remarks,
            "user_id": user["user_id"] if user else None,
        }

        result = await asyncio.to_thread(agent.generate_plan, request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {str(e)}")


# ── Agent 出行方案生成（SSE 流式） ──

@router.post("/api/generate-plan/stream")
async def generate_plan_stream(request: TravelPlanRequest, user=Depends(require_login)):
    """SSE 流式端点：实时推送 Agent 的思考过程和工具调用。"""
    agent = get_travel_agent()
    style_text = STYLE_MAP.get(request.travelType, request.travelType)
    date_range = (
        f"{request.startDate}至{request.endDate}"
        if request.startDate and request.endDate else "未指定"
    )

    request_data = {
        "destination": request.destination,
        "duration": request.duration,
        "peopleCount": request.peopleCount,
        "budget": request.budget,
        "style_text": style_text,
        "selectedPreferences": request.selectedPreferences or [],
        "dietaryRequirements": request.dietaryRequirements,
        "desiredAttractions": request.desiredAttractions,
        "date_range": date_range,
        "remarks": request.remarks,
        "user_id": user["user_id"] if user else None,
    }

    queue: asyncio.Queue = asyncio.Queue()

    async def event_stream():
        loop = asyncio.get_event_loop()
        agent_task = loop.run_in_executor(
            None, agent.generate_plan_stream, request_data, queue
        )

        done = False
        while not done:
            event = await asyncio.wait_for(queue.get(), timeout=120)
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            if event.get("type") in ("done", "final_answer") and queue.empty():
                try:
                    remaining = await asyncio.wait_for(queue.get(), timeout=5)
                    yield f"data: {json.dumps(remaining, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    pass
                done = True

        await agent_task

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Agent 智能聊天 ──

@router.post("/api/chat")
async def chat(request: ChatRequest, user=Depends(require_login)):
    """Agent 聊天模式，集成三层记忆。

    记忆流程：
    - 短期：从 DB 加载当前会话的历史对话 → 服务端管理，不依赖前端
    - 长期 + 工作：build_context() 注入 system prompt
    - 保存当前轮次到短期记忆
    - 自动从对话中提取事实到长期记忆
    """
    try:
        agent = get_travel_agent()
        user_id = user["user_id"] if user else None
        reply = await asyncio.to_thread(
            agent.chat,
            user_id,
            request.destination,
            request.message,
            request.sessionId or "",
            request.history,
        )
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code, detail=f"聊天服务失败: {str(e)}")


# ── 预订管理 ──

@router.post("/api/booking")
async def create_booking(request: BookingRequest, user=Depends(require_login)):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="姓名不能为空")
    if not re.match(r"^1[3-9]\d{9}$", request.phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    if not request.date:
        raise HTTPException(status_code=400, detail="请选择出行日期")

    booking_id = uuid.uuid4().hex[:8].upper()
    user_id = user["user_id"] if user else None

    with get_db() as conn:
        conn.execute(
            "INSERT INTO bookings (id,dest,name,phone,date,people,package,remark,user_id) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (booking_id, request.dest, request.name, request.phone,
             request.date, request.people, request.package, request.remark, user_id),
        )

    return {"success": True, "booking_id": booking_id}


@router.get("/api/bookings")
async def list_bookings(user=Depends(require_login)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC",
            (user["user_id"],),
        ).fetchall()
    return {"bookings": [dict(r) for r in rows]}


# ── 邮件订阅 ──

@router.post("/api/newsletter/subscribe")
async def subscribe(request: SubscribeRequest):
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", request.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM subscribers WHERE email=?", (request.email,)
        ).fetchone()
        if existing:
            return {"success": True, "message": "您已订阅过啦"}
        conn.execute("INSERT INTO subscribers (email) VALUES (?)", (request.email,))

    return {"success": True, "message": "订阅成功！"}


# ── 用户信息 ──

@router.get("/api/me")
async def me(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    return {"id": user["user_id"], "username": user["username"], "role": user["role"]}


# ── 用户偏好 ──

@router.get("/api/preferences")
async def get_preferences(user=Depends(require_login)):
    prefs = get_user_preferences(user["user_id"])
    if not prefs:
        return {
            "travel_style": "",
            "budget_level": "medium",
            "dietary_restrictions": "",
            "favorite_destinations": "",
            "notes": "",
        }
    return prefs


@router.post("/api/preferences")
async def save_preferences(
    request: UserPreferencesRequest, user=Depends(require_login)
):
    save_user_preferences(user["user_id"], request.model_dump())
    return {"success": True, "message": "偏好已保存"}


# ── 记忆查看（调试用） ──

@router.get("/api/memory")
async def view_memory(user=Depends(require_login)):
    """查看当前用户的全部记忆内容（短期 + 长期 + 工作）。"""
    memory = get_memory_manager()
    user_id = user["user_id"]

    facts = memory.get_user_facts_text(user_id)
    plans = memory.get_recent_plans_text(user_id)
    session_id = memory.get_session_id(user_id)
    conversation = memory.load_session_history(user_id, session_id, limit=10)

    return {
        "session_id": session_id,
        "short_term": [
            {"role": "user" if "HumanMessage" in type(m).__name__ else "assistant",
             "content": m.content[:200]}
            for m in conversation
        ],
        "long_term": facts,
        "working": plans,
    }
