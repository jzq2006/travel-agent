"""测试配置 — 提供测试客户端和内存数据库。"""

import os
import sys
import sqlite3
import pytest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


@pytest.fixture
def test_db(tmp_path):
    """创建临时数据库用于测试。"""
    db_path = str(tmp_path / "test_travel.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            dest TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            people INTEGER DEFAULT 1,
            package TEXT,
            remark TEXT,
            user_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            travel_style TEXT DEFAULT '',
            budget_level TEXT DEFAULT 'medium',
            dietary_restrictions TEXT DEFAULT '',
            favorite_destinations TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_type TEXT NOT NULL,
            input_summary TEXT NOT NULL,
            tools_called TEXT DEFAULT '',
            final_answer TEXT DEFAULT '',
            iterations INTEGER DEFAULT 0,
            duration_ms INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
    """)
    conn.commit()
    conn.close()

    # 临时替换 DB_PATH
    import config
    original_db_path = config.DB_PATH
    config.DB_PATH = db_path

    yield db_path

    config.DB_PATH = original_db_path


@pytest.fixture
def client(test_db):
    """创建测试客户端。"""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """注册测试用户并返回 JWT token。"""
    resp = client.post("/api/register", json={
        "username": "testuser",
        "password": "test123456",
    })
    return resp.json()["token"]


@pytest.fixture
def auth_headers(auth_token):
    """返回带 Authorization 的请求头。"""
    return {"Authorization": f"Bearer {auth_token}"}
