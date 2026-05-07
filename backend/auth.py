import hashlib
import secrets
import time

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import JWT_SECRET, JWT_EXPIRATION

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
    return f"{salt}:{h}"


def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":")
    return secrets.compare_digest(
        hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex(),
        h,
    )


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": int(time.time()) + JWT_EXPIRATION,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials:
        return None
    return decode_token(credentials.credentials)


async def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


async def require_login(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user
