import sqlite3
from contextlib import contextmanager

import config
from auth import hash_password
import logging

logger = logging.getLogger("travel-agent")


@contextmanager
def get_db():
    """数据库连接上下文管理器，自动处理事务提交和连接关闭。"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化所有数据库表。"""
    with get_db() as conn:
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
                user_id INTEGER REFERENCES users(id),
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
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
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

            -- ── 记忆系统表 ──

            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                category TEXT NOT NULL,
                fact TEXT NOT NULL,
                source TEXT DEFAULT 'chat',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS plan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                destination TEXT NOT NULL,
                request_summary TEXT NOT NULL,
                plan_text TEXT NOT NULL,
                tools_called TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
        """)


def seed_admin():
    """创建默认管理员账户（仅首次运行时）。"""
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hash_password("admin123"), "admin"),
            )


# ── 用户偏好 ──

def get_user_preferences(user_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def save_user_preferences(user_id: int, prefs: dict) -> None:
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE user_preferences
                   SET travel_style=?, budget_level=?, dietary_restrictions=?,
                       favorite_destinations=?, notes=?,
                       updated_at=datetime('now','localtime')
                   WHERE user_id=?""",
                (prefs.get("travel_style", ""), prefs.get("budget_level", "medium"),
                 prefs.get("dietary_restrictions", ""), prefs.get("favorite_destinations", ""),
                 prefs.get("notes", ""), user_id),
            )
        else:
            conn.execute(
                """INSERT INTO user_preferences
                   (user_id, travel_style, budget_level, dietary_restrictions,
                    favorite_destinations, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, prefs.get("travel_style", ""), prefs.get("budget_level", "medium"),
                 prefs.get("dietary_restrictions", ""), prefs.get("favorite_destinations", ""),
                 prefs.get("notes", "")),
            )


# ── Agent 执行日志 ──

def log_agent_execution(
    user_id: int | None,
    task_type: str,
    input_summary: str,
    tools_called: list[str],
    final_answer: str,
    iterations: int,
    duration_ms: int,
):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO agent_logs
               (user_id, task_type, input_summary, tools_called, final_answer,
                iterations, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, task_type, input_summary,
             ",".join(tools_called), final_answer[:2000],
             iterations, duration_ms),
        )


# ── 短期记忆：会话历史 ──

def save_message(user_id: int, session_id: str, role: str, content: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO conversation_history (user_id, session_id, role, content) "
            "VALUES (?, ?, ?, ?)",
            (user_id, session_id, role, content[:5000]),
        )


def load_conversation(user_id: int, session_id: str, limit: int = 20) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT role, content FROM conversation_history
               WHERE user_id = ? AND session_id = ?
               ORDER BY id DESC LIMIT ?""",
            (user_id, session_id, limit),
        ).fetchall()
    return list(reversed([dict(r) for r in rows]))


def get_or_create_session(user_id: int, timeout_minutes: int = 30) -> str:
    """获取用户最近的会话ID，如果超过指定分钟无活动则创建新会话。"""
    with get_db() as conn:
        row = conn.execute(
            """SELECT session_id, created_at FROM conversation_history
               WHERE user_id = ?
               ORDER BY id DESC LIMIT 1""",
            (user_id,),
        ).fetchone()
        if row:
            # 检查最后活跃时间是否在超时窗口内
            inactive_rows = conn.execute(
                "SELECT 1 FROM conversation_history "
                "WHERE user_id = ? AND session_id = ? "
                "AND created_at > datetime('now', 'localtime', ?)",
                (user_id, row["session_id"], f"-{timeout_minutes} minutes"),
            ).fetchall()
            if inactive_rows:
                return row["session_id"]
    import uuid
    return uuid.uuid4().hex[:12]


# ── 长期记忆：用户画像 ──

def _normalize_fact(text: str) -> str:
    """归一化事实文本：去首尾标点和空格，统一句号，用于去重比较。"""
    return text.strip().rstrip("。！？，、；：").strip()


def save_user_facts(user_id: int, facts: list[dict]) -> None:
    """保存提取到的用户事实，自动去重（归一化后比较）。"""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT category, fact FROM user_memory WHERE user_id = ?", (user_id,)
        ).fetchall()
        existing_set = {(r["category"], _normalize_fact(r["fact"])) for r in existing}

        for fact_item in facts:
            key = (fact_item["category"], _normalize_fact(fact_item["fact"]))
            if key not in existing_set:
                conn.execute(
                    "INSERT INTO user_memory (user_id, category, fact, source) "
                    "VALUES (?, ?, ?, ?)",
                    (user_id, fact_item["category"], fact_item["fact"],
                     fact_item.get("source", "chat")),
                )
                existing_set.add(key)


def load_user_facts(user_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT category, fact FROM user_memory WHERE user_id = ? "
            "ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── 工作记忆：方案历史 ──

def save_plan(user_id: int, destination: str, request_summary: str,
              plan_text: str, tools_called: list[str]) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO plan_history
               (user_id, destination, request_summary, plan_text, tools_called)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, destination, request_summary[:300],
             plan_text[:5000], ",".join(tools_called)),
        )


def load_recent_plans(user_id: int, limit: int = 3) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT destination, request_summary, plan_text, created_at
               FROM plan_history WHERE user_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


# ── 记忆清理 ──

def cleanup_memory() -> dict:
    """清理过期的记忆数据，返回各表的清理数量。"""
    stats = {"conversation": 0, "facts": 0, "plans": 0, "logs": 0}

    with get_db() as conn:
        # 短期记忆：删除超过 N 天的对话
        stats["conversation"] = conn.execute(
            "DELETE FROM conversation_history "
            "WHERE created_at < datetime('now', 'localtime', ?)",
            (f"-{config.MEMORY_MAX_CONVERSATION_DAYS} days",),
        ).rowcount

        # 短期记忆：每个用户最多保留 N 条
        users = conn.execute("SELECT DISTINCT user_id FROM conversation_history").fetchall()
        for user in users:
            uid = user["user_id"]
            conn.execute(
                "DELETE FROM conversation_history WHERE id IN ("
                "  SELECT id FROM conversation_history "
                "  WHERE user_id = ? ORDER BY id DESC LIMIT -1 OFFSET ?"
                ")",
                (uid, config.MEMORY_MAX_CONVERSATION_PER_USER),
            )

        # 长期记忆：每个用户最多保留 N 条事实，超出按时间淘汰
        users = conn.execute("SELECT DISTINCT user_id FROM user_memory").fetchall()
        for user in users:
            uid = user["user_id"]
            deleted = conn.execute(
                "DELETE FROM user_memory WHERE id IN ("
                "  SELECT id FROM user_memory "
                "  WHERE user_id = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?"
                ")",
                (uid, config.MEMORY_MAX_FACTS_PER_USER),
            ).rowcount
            stats["facts"] += deleted

        # 工作记忆：每个用户最多保留 N 条方案
        users = conn.execute("SELECT DISTINCT user_id FROM plan_history").fetchall()
        for user in users:
            uid = user["user_id"]
            conn.execute(
                "DELETE FROM plan_history WHERE id IN ("
                "  SELECT id FROM plan_history "
                "  WHERE user_id = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?"
                ")",
                (uid, config.MEMORY_MAX_PLANS_PER_USER),
            )

        # Agent 日志：删除超过 N 天的
        stats["logs"] = conn.execute(
            "DELETE FROM agent_logs "
            "WHERE created_at < datetime('now', 'localtime', ?)",
            (f"-{config.MEMORY_MAX_LOG_DAYS} days",),
        ).rowcount

    logger.info(
        f"记忆清理完成: 对话={stats['conversation']}, "
        f"事实={stats['facts']}, 方案={stats['plans']}, 日志={stats['logs']}"
    )
    return stats
