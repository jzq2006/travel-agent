from fastapi import APIRouter, HTTPException

from auth import verify_password, hash_password, create_token
from database import get_db
from models import LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/api/login")
async def login(request: LoginRequest):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=?", (request.username,)
        ).fetchone()
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(user["id"], user["username"], user["role"])
    return {
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
    }


@router.post("/api/register")
async def register(request: RegisterRequest):
    if len(request.username) < 2 or len(request.username) > 20:
        raise HTTPException(status_code=400, detail="用户名长度需在2-20之间")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username=?", (request.username,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")

        pw = hash_password(request.password)
        cursor = conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (request.username, pw, "user"),
        )
        user_id = cursor.lastrowid

    token = create_token(user_id, request.username, "user")
    return {
        "token": token,
        "user": {"id": user_id, "username": request.username, "role": "user"},
    }
