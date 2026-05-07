import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM 配置 ──
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
AGENT_MODEL = os.getenv("AGENT_MODEL", "deepseek-chat")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "4096"))

# ── 认证配置 ──
JWT_SECRET = os.getenv("JWT_SECRET", "travel-agent-jwt-secret-key")
JWT_EXPIRATION = 24 * 60 * 60  # 24 hours

# ── 外部 API 密钥 ──
QWEATHER_KEY = os.getenv("QWEATHER_KEY", "")
AMAP_KEY = os.getenv("AMAP_KEY", "")

# ── 数据库 ──
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel.db")

# ── 业务常量 ──
LOW_BUDGET_THRESHOLD = 800

STYLE_MAP = {
    "adventure": "探险之旅",
    "relaxation": "休闲度假",
    "culture": "文化体验",
    "nature": "自然风光",
    "food": "美食之旅",
    "romantic": "浪漫之旅",
    "family": "亲子游",
}

# ── CORS ──
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
