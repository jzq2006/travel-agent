# AI Travel Agent - 智能出行规划助手

基于 **ReAct Agent 模式** 的全栈智能出行规划系统。大模型自主推理并编排工具调用链（天气查询、景点搜索、路线规划、酒店推荐、地理编码），生成个性化旅行方案。支持行程追问、SSE 流式推理展示、三层记忆系统和完整的用户管理体系。

## 核心架构

```
用户请求 → Agent（LLM 作为"大脑"）
              ├─ 自主决策：需要调用哪些工具、调用几次、用什么参数
              ├─ 工具调用：query_weather / search_attractions / plan_route / ...
              ├─ 观察结果：根据工具返回的实时数据动态调整策略
              └─ 生成方案：综合所有信息输出完整出行计划
```

与传统硬编码流水线的区别：不是代码写死"先查天气 → 再查路线 → 调 LLM"，而是 LLM 自己判断——"下雨了？那我多搜几个室内景点"——动态调整规划策略。

## 项目亮点

### Agent 架构

- **ReAct Agent（推理 + 行动循环）** — 基于 LangChain `create_agent` 构建 LangGraph 状态图，LLM 自主编排工具调用顺序和次数
- **Prompt 角色分离** — 三套 system prompt 塑造三个 Agent 角色：行程规划师、目的地顾问"小旅"、行程追问助手。共用同一个 LLM + 工具集，通过 prompt 切换行为
- **5 个 @tool 工具** — 天气 / 景点 / 路线 / 酒店 / 地理编码，Agent 根据用户需求自主选择调用

### 三层记忆系统

- **短期记忆** — `conversation_history` 表存储当前会话对话，30 分钟不活跃自动创建新会话
- **长期记忆** — `user_memory` 表存储用户画像，每轮对话后用独立 LLM 调用（temperature=0）自动提取结构化事实，归一化去重，跨会话保留
- **工作记忆** — `plan_history` 表存储历史方案摘要，Agent 可参考已生成方案避免重复推荐
- **自动清理** — 启动时按"定量 + 定时"策略自动清理过期数据，所有阈值通过环境变量配置

### 工程实践

- **SSE 流式输出** — 方案生成和行程追问均采用 Server-Sent Events 实时推送 Agent 推理过程、工具调用与最终结果
- **API 速率限制** — 基于滑动窗口的内存限流，方案生成 5次/分钟，聊天 15次/分钟，防止 LLM token 滥用
- **外部 API 容错** — 高德地图 API 调用统一封装重试层（指数退避，最多 2 次），最终失败返回降级值而非崩溃 Agent
- **JWT 认证** — PBKDF2-SHA256 密码哈希 + JWT Token，FastAPI 依赖注入实现 user/admin 权限分层

### 前端交互

- **实时推理展示** — 暗色终端风格面板实时展示 Agent 调用了什么工具、传了什么参数、返回了什么数据
- **行程追问** — 方案生成后自动弹出追问窗口，用户可针对方案继续提问或要求调整，Agent 参考完整方案作答
- **10 座城市目的地详情** — 北京、上海、成都、杭州、西安、丽江、桂林、三亚、张家界、青岛，含景点、美食、文化、套餐、穿搭建议
- **AI 目的地顾问** — 每个目的地嵌入"小旅"聊天助手，支持工具调用获取实时数据

## 技术栈

| 层   | 技术                                    |
| ---- | --------------------------------------- |
| 后端 | FastAPI + LangChain + SQLite            |
| 前端 | Vue 3 + Vite + Axios                    |
| LLM  | 多模型支持（DeepSeek / 智谱 / 月之暗面 / 通义千问 / OpenAI） |
| 外部 API | 高德地图（地理编码 / POI / 路线 / 天气） |
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
# LLM_API_KEY=your_api_key              # 模型 API Key
# LLM_BASE_URL=https://api.deepseek.com/v1  # 模型接口地址（见下方支持的模型）
# AGENT_MODEL=deepseek-chat             # 模型名称
# AMAP_KEY=your_amap_api_key            # 高德地图 API Key
# JWT_SECRET=your_jwt_secret            # JWT 密钥
```

#### 支持的模型服务商

只需修改 `LLM_BASE_URL` + `AGENT_MODEL` 即可切换：

| 服务商 | LLM_BASE_URL | AGENT_MODEL |
|--------|-------------|-------------|
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| 智谱 GLM | https://open.bigmodel.cn/api/paas/v4 | glm-4-flash |
| 月之暗面 | https://api.moonshot.cn/v1 | moonshot-v1-8k |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo |
| OpenAI | https://api.openai.com/v1 | gpt-4o-mini |

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
│   ├── config.py            # 环境变量配置 + 记忆清理阈值
│   ├── database.py          # SQLite 数据库 + 三层记忆存储 + 自动清理
│   ├── models.py            # Pydantic 数据模型
│   ├── auth.py              # JWT 认证 + PBKDF2 密码哈希
│   ├── routers/
│   │   ├── travel.py        # 行程规划 / 聊天 / 追问 / 预订 API（含限流）
│   │   ├── auth.py          # 注册 / 登录 API
│   │   └── admin.py         # 管理后台 API + 记忆清理
│   ├── services/
│   │   ├── agent.py         # ReAct Agent 核心（规划 / 聊天 / 追问三个角色）
│   │   ├── tools.py         # 5 个 @tool 工具函数
│   │   ├── memory.py        # 三层记忆管理器
│   │   ├── rate_limiter.py  # 滑动窗口速率限制器
│   │   ├── api_client.py    # 外部 API 重试 + 降级封装
│   │   ├── llm.py           # LLM 初始化
│   │   ├── maps.py          # 高德地图 API 封装
│   │   └── weather.py       # 天气 API 封装
│   └── tests/               # 单元测试 + 集成测试
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主应用
│   │   ├── main.js          # 入口
│   │   ├── api/index.js     # Axios 实例 + JWT 拦截器
│   │   └── components/      # Vue 组件
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
├── start.bat
└── .gitignore
```

## API 概览

### Agent 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/generate-plan/stream | SSE 流式生成出行方案（含限流） |
| POST | /api/generate-plan | 非流式生成出行方案（含限流） |
| POST | /api/chat | Agent 目的地聊天（含限流 + 三层记忆） |
| POST | /api/chat/plan | SSE 流式行程追问（含限流 + 方案上下文） |

### 业务接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/preferences | 获取用户偏好 |
| POST | /api/preferences | 设置用户偏好 |
| POST | /api/booking | 提交预订 |
| GET | /api/bookings | 查询我的预订 |
| POST | /api/newsletter/subscribe | 邮件订阅 |

### 认证与管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/register | 用户注册 |
| POST | /api/login | 用户登录 |
| GET | /api/me | 当前用户信息 |
| GET | /api/admin/bookings | 全部预订（管理员） |
| GET | /api/admin/users | 全部用户（管理员） |
| GET | /api/admin/agent-logs | Agent 执行日志（管理员） |
| POST | /api/admin/cleanup | 手动触发记忆清理（管理员） |
| GET | /api/memory | 查看三层记忆（调试） |

## Agent 工具

| 工具 | 功能 | 数据源 |
|------|------|--------|
| query_weather | 查询城市 7 天天气预报 | 高德天气 API |
| search_attractions | 搜索景点、餐厅、博物馆等 POI | 高德 POI 搜索 |
| plan_route | 规划驾车 / 公交路线 | 高德路线规划 |
| search_hotels_nearby | 搜索指定位置附近酒店 | 高德周边搜索 |
| geocode_address | 地址转经纬度坐标 | 高德地理编码 |

## 记忆清理配置

通过环境变量配置清理阈值，无需改代码：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| MEMORY_MAX_CONVERSATION_DAYS | 30 | 短期对话保留天数 |
| MEMORY_MAX_CONVERSATION_PER_USER | 500 | 每人最大对话条数 |
| MEMORY_MAX_FACTS_PER_USER | 50 | 每人最大事实条数 |
| MEMORY_MAX_PLANS_PER_USER | 20 | 每人最大方案条数 |
| MEMORY_MAX_LOG_DAYS | 90 | Agent 日志保留天数 |

## License

MIT
