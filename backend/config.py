import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM 配置 ──
# 兼容所有 OpenAI 接口协议的模型服务商：
#   DeepSeek:   LLM_BASE_URL=https://api.deepseek.com/v1
#   智谱 GLM:   LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
#   月之暗面:    LLM_BASE_URL=https://api.moonshot.cn/v1
#   通义千问:    LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
#   OpenAI:     LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
AGENT_MODEL = os.getenv("AGENT_MODEL", "deepseek-chat")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "4096"))

# ── 认证配置 ──
JWT_SECRET = os.getenv("JWT_SECRET", "travel-agent-jwt-secret-key")
JWT_EXPIRATION = 24 * 60 * 60  # 24 hours

# ── 外部 API 密钥 ──
AMAP_KEY = os.getenv("AMAP_KEY", "")

# ── 数据库 ──
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel.db")

# ── 业务常量 ──
LOW_BUDGET_THRESHOLD = 800

# ── 记忆清理阈值 ──
MEMORY_MAX_CONVERSATION_DAYS = int(os.getenv("MEMORY_MAX_CONVERSATION_DAYS", "30"))
MEMORY_MAX_CONVERSATION_PER_USER = int(os.getenv("MEMORY_MAX_CONVERSATION_PER_USER", "500"))
MEMORY_MAX_FACTS_PER_USER = int(os.getenv("MEMORY_MAX_FACTS_PER_USER", "50"))
MEMORY_MAX_PLANS_PER_USER = int(os.getenv("MEMORY_MAX_PLANS_PER_USER", "20"))
MEMORY_MAX_LOG_DAYS = int(os.getenv("MEMORY_MAX_LOG_DAYS", "90"))

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
