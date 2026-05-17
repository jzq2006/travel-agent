from fastapi import APIRouter, Depends

from auth import require_admin
from database import get_db, cleanup_memory

router = APIRouter()


@router.get("/api/admin/bookings")
async def admin_bookings(admin=Depends(require_admin)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
    return {"bookings": [dict(r) for r in rows]}


@router.get("/api/admin/subscribers")
async def admin_subscribers(admin=Depends(require_admin)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM subscribers ORDER BY subscribed_at DESC").fetchall()
    return {"subscribers": [dict(r) for r in rows]}


@router.get("/api/admin/users")
async def admin_users(admin=Depends(require_admin)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    return {"users": [dict(r) for r in rows]}


@router.get("/api/admin/agent-logs")
async def admin_agent_logs(admin=Depends(require_admin)):
    """查询 Agent 执行日志，用于监控和调试。"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    return {"logs": [dict(r) for r in rows]}


@router.post("/api/admin/cleanup")
async def admin_cleanup(admin=Depends(require_admin)):
    """手动触发记忆清理。"""
    stats = cleanup_memory()
    return {"success": True, "cleaned": stats}
