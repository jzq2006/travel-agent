# AI Travel Agent - 智能出行规划助手

基于 **ReAct Agent 模式** 的智能出行规划系统，大模型自主决策调用工具链（天气查询、景点搜索、路线规划、酒店推荐、地理编码），实现端到端的旅行方案生成。

## 架构亮点

- **ReAct Agent** — 大模型自主推理 + 行动循环，非硬编码 Prompt Chain
- **5 个 @tool 工具** — 天气 / 景点 / 路线 / 酒店 / 地理编码，LLM 自行决定调用顺序和次数
- **三层记忆系统** — 短期对话记忆 + 长期用户画像（LLM 自动提取事实）+ 工作记忆（历史规划）
- **SSE 流式输出** — 实时展示 Agent 推理过程、工具调用与结果
- **DeepSeek API** — OpenAI 兼容接口，支持 function calling

## 技术栈

| 层   | 技术                                    |
| ---- | --------------------------------------- |
| 后端 | FastAPI + LangChain + SQLite            |
| 前端 | Vue 3 + Vite + Axios                    |
| LLM  | DeepSeek Chat（OpenAI 兼容）            |
| 部署 | Docker Compose / start.bat 本地一键启动 |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）

### 配置

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入以下配置：
# DEEPSEEK_API_KEY=your_deepseek_api_key
# AMAP_API_KEY=your_amap_api_key
# JWT_SECRET=your_jwt_secret
```

### 一键启动（Windows）

双击 `start.bat` 或在项目根目录执行：

```bash
./start.bat
```

后端启动在 http://localhost:8000，前端启动在 http://localhost:5173。

### 手动启动

```bash
# 后端
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker compose up --build
```

前端通过 Nginx 反向代理访问后端，对外暴露 80 端口。

## 项目结构

```
travel-agent/
├── backend/
│   ├── main.py              # FastAPI 入口，lifespan + 中间件
│   ├── config.py            # 环境变量配置
│   ├── database.py          # SQLite 数据库管理 + 三层记忆存储
│   ├── models.py            # Pydantic 数据模型
│   ├── auth.py              # JWT 认证
│   ├── routers/
│   │   ├── travel.py        # 行程规划 / 聊天 / 预订 API
│   │   ├── auth.py          # 注册 / 登录 API
│   │   └── admin.py         # 管理后台 API
│   ├── services/
│   │   ├── agent.py         # ReAct Agent 核心（LangChain create_agent）
│   │   ├── tools.py         # 5 个 @tool 工具函数
│   │   ├── memory.py        # 三层记忆管理器
│   │   ├── llm.py           # LLM 初始化
│   │   ├── maps.py          # 高德地图 API 封装
│   │   └── weather.py       # 天气 API 封装
│   └── tests/               # 单元测试 + 集成测试
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主应用
│   │   ├── main.js          # 入口
│   │   ├── api/index.js     # Axios 实例 + 拦截器
│   │   └── components/      # Vue 组件
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
├── start.bat
└── .gitignore
```

## API 概览

| 方法   | 路径                      | 说明                   |
| ------ | ------------------------- | ---------------------- |
| POST   | /api/generate-plan/stream | SSE 流式生成出行方案   |
| POST   | /api/chat                 | Agent 聊天（带记忆）   |
| GET    | /api/preferences          | 获取用户偏好           |
| POST   | /api/preferences          | 设置用户偏好           |
| POST   | /api/booking              | 提交预订               |
| GET    | /api/bookings             | 查询我的预订           |
| POST   | /api/auth/register        | 注册                   |
| POST   | /api/auth/login           | 登录                   |
| GET    | /api/memory               | 查看三层记忆（调试）   |

## Agent 工具

| 工具                 | 功能                     |
| -------------------- | ------------------------ |
| query_weather        | 查询城市天气             |
| search_attractions   | 搜索景点和 POI           |
| plan_route           | 规划驾车/公交路线        |
| search_hotels_nearby | 搜索附近酒店             |
| geocode_address      | 地址转经纬度坐标         |

## License

MIT
