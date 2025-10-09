# AutoGen 多模态 AI 智能体平台

<div align="center">

![AutoGen](https://img.shields.io/badge/AutoGen-0.7.5-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![React](https://img.shields.io/badge/React-18-blue)
![Ant Design](https://img.shields.io/badge/Ant%20Design-5-purple)

**一个功能强大的多模态 AI 智能体协作平台**

支持普通对话、测试用例生成、UI 图片分析等多种智能体协作模式

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [文档](#-文档)

</div>

---

## 📖 项目简介

这是一个基于 Microsoft AutoGen 0.7.5 框架构建的多模态 AI 智能体协作平台，提供三种专业的工作模式：

1. **普通对话模式** - 基础 AI 对话功能
2. **测试用例智能体团队** - 三个专业智能体协作生成、评审和优化测试用例
3. **UI 图片分析智能体团队** - 三个专业智能体协作分析 UI 截图并生成测试场景

## ✨ 功能特性

### 🎯 三种工作模式

#### 1️⃣ 普通对话模式
- 💬 基础 AI 对话功能
- 🔄 支持流式和非流式响应
- 📝 Markdown 渲染和代码高亮
- 💾 会话管理和历史记录

#### 2️⃣ 测试用例智能体团队
- 👥 **三个专业智能体协作**：
  - `TestCase_Generator` - 测试用例生成器
  - `TestCase_Reviewer` - 测试用例评审器
  - `TestCase_Optimizer` - 测试用例优化器
- 🔄 **GraphFlow 工作流** - 自动化的智能体协作流程
- 🎯 **智能路由** - 支持 `@智能体名称` 定向反馈
- 📊 **实时流式显示** - 每个智能体的工作过程实时展示
- 🎨 **可折叠智能体卡片** - 清晰的视觉层次

#### 3️⃣ UI 图片分析智能体团队
- 🖼️ **多种图片输入方式**：
  - 本地文件上传
  - 图片 URL
  - 网页 URL（自动截图）
- 👥 **三个专业智能体协作**：
  - `UI_Expert` - UI 元素分析专家
  - `Interaction_Analyst` - 交互流程分析师
  - `Test_Scenario_Expert` - 测试场景专家
- ⚡ **并行执行** - UI_Expert 和 Interaction_Analyst 并行分析
- 🎨 **智能展开** - 智能体按执行顺序自动展开
- 🛑 **停止控制** - 支持中途停止分析

### 🛠️ 技术特性

#### 后端
- 🚀 **FastAPI** - 高性能异步 Python Web 框架
- 🤖 **AutoGen 0.7.5** - 微软 AI 智能体框架
- 📡 **SSE 流式传输** - 实时服务器推送事件
- 🔄 **GraphFlow** - 有向图工作流引擎
- 💾 **会话管理** - 完整的会话隔离和管理
- 📝 **提示词系统** - 模块化的提示词管理
- 🎯 **多模型支持** - DeepSeek、UI-TARS、OpenAI 等

#### 前端
- ⚛️ **React 18** - 现代化 UI 框架
- 🎨 **Ant Design 5** - 企业级 UI 组件库
- 🌊 **Framer Motion** - 流畅的动画效果
- 🎭 **霓虹灯风格** - 赛博朋克主题设计
- 🌓 **深色/浅色主题** - 完整的主题切换支持
- 📱 **响应式设计** - 完美适配各种屏幕尺寸
- ⚡ **Vite** - 极速的开发和构建体验

## 🏗️ 项目架构

### 四层架构设计

本项目采用**分层智能体工厂架构**，具有高可维护性、高可扩展性和高可测试性：

```
┌─────────────────────────────────────────────────────────┐
│                    1️⃣ API 接口层                         │
│              (FastAPI Routes - routes.py)               │
│          接收前端请求，启动业务流程                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    2️⃣ 服务层                             │
│        (AIService, TestCasesTeamAIService)              │
│          业务流程编排，调用智能体工厂                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    3️⃣ 智能体工厂层                        │
│              (AgentFactory, AgentRegistry)              │
│      创建、注册、管理智能体，提供智能体缓存                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    4️⃣ 智能体层                           │
│    (ChatAgent, TestCaseTeamAgent, ImageAnalyzerTeam)    │
│          具体智能体实现，完成各自的业务逻辑                 │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
autogenTest/
├── backend/                          # FastAPI 后端
│   ├── agents/                       # 🤖 智能体层
│   │   ├── __init__.py               # 智能体注册
│   │   ├── base_agent.py             # 智能体基类
│   │   ├── factory.py                # 智能体工厂
│   │   ├── chat_agent.py             # 普通对话智能体
│   │   ├── testcase_team_agent.py    # 测试用例团队智能体
│   │   └── image_analyzer_team.py    # UI 图片分析团队智能体
│   ├── api/                          # 🌐 API 接口层
│   │   ├── __init__.py
│   │   └── routes.py                 # 所有 API 端点
│   ├── core/                         # 🔧 核心模块
│   │   ├── dependencies.py           # 依赖注入
│   │   └── llm_clients.py            # LLM 客户端管理
│   ├── services/                     # 📦 服务层
│   │   ├── ai_service.py             # AI 对话服务
│   │   ├── stream_service.py         # 流式服务
│   │   ├── session_service.py        # 会话管理服务
│   │   ├── team_stream_service.py    # 团队流式服务
│   │   └── image_analysis_stream_service.py  # 图片分析流式服务
│   ├── prompts/                      # 提示词文件
│   │   ├── prompt_loader.py          # 提示词加载器
│   │   ├── ui_expert.txt             # UI 专家提示词
│   │   ├── interaction_analyst.txt   # 交互分析师提示词
│   │   ├── test_scenario_expert.txt  # 测试场景专家提示词
│   │   ├── test_case_generator.txt   # 测试用例生成器提示词
│   │   ├── test_case_reviewer.txt    # 测试用例评审器提示词
│   │   └── test_case_optimizer.txt   # 测试用例优化器提示词
│   ├── tests/                        # 测试文件
│   │   ├── README.md
│   │   ├── test_uitars_auth.py
│   │   ├── test_uitars_vision.py
│   │   ├── test_graphflow.py
│   │   ├── test_image_analyzer.py
│   │   └── test_image_analyzer_api.py
│   ├── examples/                     # 示例代码
│   ├── main.py                       # FastAPI 主应用
│   ├── config.py                     # 配置管理
│   ├── models.py                     # 数据模型
│   └── requirements.txt              # Python 依赖
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── components/               # React 组件
│   │   │   ├── ModeSelector.jsx      # 模式选择器
│   │   │   ├── ImageAnalyzer.jsx     # 图片分析组件
│   │   │   ├── FileUpload.jsx        # 文件上传组件
│   │   │   ├── MatrixRain.jsx        # 矩阵雨背景
│   │   │   ├── CyberpunkRobot.jsx    # 赛博朋克机器人
│   │   │   ├── NeonRocket.jsx        # 霓虹火箭图标
│   │   │   ├── NeonTestTube.jsx      # 霓虹试管图标
│   │   │   └── NeonImageAnalyzer.jsx # 霓虹图片分析图标
│   │   ├── App.jsx                   # 主应用组件
│   │   ├── App.css                   # 全局样式
│   │   └── main.jsx                  # 入口文件
│   ├── index.html                    # HTML 模板
│   ├── vite.config.js                # Vite 配置
│   └── package.json                  # Node 依赖
│
├── tests/                            # 集成测试
│   ├── README.md
│   └── test_feedback_flow.sh
│
├── docs/                             # 文档目录
│   ├── prompts/                      # 提示词文档
│   ├── frontend/                     # 前端文档
│   ├── ARCHITECTURE.md               # 架构文档
│   ├── QUICK_START_IMAGE_ANALYZER.md # 图片分析快速开始
│   └── PROJECT_ORGANIZATION_SUMMARY.md  # 项目整理总结
│
├── start.sh                          # 启动脚本 (macOS/Linux)
├── start.bat                         # 启动脚本 (Windows)
├── ARCHITECTURE.md                   # 📐 架构设计文档
├── REFACTORING_SUMMARY.md            # 📝 重构总结文档
├── GIT_GUIDE.md                      # 📚 Git 使用指南
└── README.md                         # 本文件
```

### 架构特性

#### 🏭 智能体工厂模式

- **统一创建**: 通过工厂统一创建和管理所有智能体
- **类型注册**: 支持动态注册新的智能体类型
- **智能缓存**: 自动缓存智能体实例，提升性能
- **生命周期管理**: 统一的资源清理机制

#### 🧩 基类继承体系

- **BaseAgent**: 单智能体基类，定义通用接口
- **BaseTeamAgent**: 团队智能体基类，支持工作流编排
- **代码复用**: 减少重复代码，提高可维护性

#### 🔌 高可扩展性

添加新智能体只需三步：
1. 创建智能体类（继承基类）
2. 在 AgentType 中添加类型
3. 注册到工厂

#### 📊 工作流支持

- **RoundRobinGroupChat**: 轮询式团队协作（测试用例生成）
- **GraphFlow**: 有向图工作流（图片分析并行执行）
- **自定义终止条件**: 灵活的流程控制

详细架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)

## 🚀 快速开始

### 前置要求

- **Python 3.11+** 和 pip
- **Node.js 18+** 和 npm
- **API 密钥**：
  - DeepSeek API Key（用于文本模型）
  - 火山引擎 API Key（用于 UI-TARS 视觉模型）

### 方式一：使用启动脚本（推荐）

#### macOS/Linux
```bash
# 使用虚拟环境启动（推荐，本地开发默认使用）
./start.sh

# 或使用系统环境启动（如果已配置好依赖）
./start-simple.sh
```

#### Windows
```cmd
# 双击运行或命令行执行
start.bat
```

**启动脚本功能**：
- ✅ 自动检查并创建 Python 虚拟环境
- ✅ 自动检查并安装后端依赖
- ✅ 自动检查并安装前端依赖
- ✅ 自动检查 .env 配置文件
- ✅ 启动后端服务（端口 8000）
- ✅ 启动前端服务（端口 3000）
- ✅ 彩色输出，易于阅读
- ✅ Ctrl+C 自动清理进程

> 📖 **详细说明**：[启动脚本使用指南](docs/START_SCRIPTS.md)

### 方式二：手动启动

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 启动后端
python main.py
```

**环境变量配置示例**：
```env
# DeepSeek API（用于文本模型）
API_KEY=sk-your-deepseek-api-key
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com

# 火山引擎 API（用于 UI-TARS 视觉模型）
ARK_API_KEY=your-ark-api-key
UITARS_ENDPOINT_ID=your-uitars-endpoint-id

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

后端将在 `http://localhost:8000` 运行

#### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3001` 运行

### 访问应用

打开浏览器访问：**http://localhost:3001**

你将看到三个模式选择卡片：
1. 🚀 普通对话模式
2. 🧪 测试用例智能体团队
3. 🖼️ UI 图片分析智能体团队

## 📖 使用指南

### 模式一：普通对话模式

1. 在首页选择 **"普通对话模式"**
2. 输入你的问题或需求
3. AI 助手会实时流式回复
4. 支持 Markdown 格式和代码高亮

### 模式二：测试用例智能体团队

1. 在首页选择 **"测试用例智能体模式"**
2. 输入需求文档或功能描述
3. 三个智能体会依次工作：
   - **Generator** 生成测试用例
   - **Reviewer** 评审测试用例
   - **Optimizer** 优化测试用例
4. 查看每个智能体的工作过程和结果
5. 可以使用 `@智能体名称` 进行定向反馈

**反馈示例**：
```
@TestCase_Reviewer 请重点关注边界条件测试
@TestCase_Optimizer 请增加性能测试用例
@all 请重新生成更详细的测试用例
```

### 模式三：UI 图片分析智能体团队

1. 在首页选择 **"UI 图片分析模式"**
2. 选择图片输入方式：
   - **上传图片**：从本地上传 UI 截图
   - **图片 URL**：输入图片的直接链接
   - **网页 URL**：输入网页地址（自动截图）
3. （可选）添加测试描述和额外上下文
4. 点击 **"开始分析"**
5. 三个智能体会协作分析：
   - **UI_Expert** 分析 UI 元素和布局
   - **Interaction_Analyst** 分析交互流程
   - **Test_Scenario_Expert** 生成测试场景
6. 查看完整的分析报告和测试建议

## 🎯 API 端点

### 基础 API
- `GET /` - API 信息
- `GET /health` - 健康检查
- `GET /docs` - Swagger UI 文档
- `GET /redoc` - ReDoc 文档

### 普通对话 API
- `POST /api/chat/stream` - 流式聊天（SSE）
- `POST /api/chat` - 非流式聊天

### 会话管理 API
- `GET /api/sessions` - 列出所有会话
- `GET /api/sessions/{session_id}` - 获取会话信息
- `DELETE /api/sessions/{session_id}` - 删除会话

### 测试用例团队 API
- `POST /api/team-chat/stream` - 团队模式流式聊天（SSE）

### UI 图片分析 API
- `POST /api/image-analysis/stream` - 图片分析流式响应（SSE）
- `POST /api/image-analysis` - 图片分析非流式响应

### Markdown 转换 API
- `POST /api/convert/markdown` - 单文件转换
- `POST /api/convert/markdown/batch` - 批量文件转换
- `GET /api/convert/supported-formats` - 获取支持的格式

### SSE 事件类型

**普通对话模式**：
- `status` - 处理状态
- `chunk` - 流式文本块
- `done` - 完成
- `error` - 错误信息

**团队模式**：
- `agent_start` - 智能体开始工作
- `agent_message` - 智能体消息（增量）
- `agent_done` - 智能体完成
- `done` - 全部完成
- `token_usage` - Token 使用统计
- `error` - 错误信息

**图片分析模式**：
- `agent_start` - 智能体开始分析
- `agent_message` - 分析内容（增量）
- `agent_done` - 智能体完成
- `done` - 分析完成
- `token_usage` - Token 使用统计
- `error` - 错误信息

## 🎨 界面特性

### 模式选择页面
- 🎭 **赛博朋克风格** - 霓虹灯效果和矩阵雨背景
- 🎨 **三个模式卡片** - 每个卡片都有独特的霓虹灯图标动画
- 🌓 **主题切换** - 支持深色和浅色主题
- 📱 **响应式设计** - 自适应不同屏幕尺寸

### 智能体工作界面
- 💬 **智能体气泡** - 每个智能体有独立的消息气泡
- 🎯 **状态指示** - 实时显示智能体工作状态（分析中/完成）
- 📂 **可折叠卡片** - 点击展开/折叠智能体内容
- 🎨 **Markdown 渲染** - 完整的 Markdown 和代码高亮支持
- 📊 **Token 统计** - 显示每次分析的 Token 使用情况

### 图片分析界面
- 🖼️ **多种输入方式** - 上传、URL、网页截图
- 📝 **可选描述** - 添加测试描述和额外上下文
- 🎬 **智能展开** - 智能体按执行顺序自动展开
- 🛑 **停止控制** - 支持中途停止分析
- 📋 **结果展示** - 清晰的分析结果和测试建议

## 🛠️ 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | Latest | Web 框架 |
| **AutoGen** | 0.7.5 | AI 智能体框架 |
| **Pydantic** | Latest | 数据验证 |
| **Uvicorn** | Latest | ASGI 服务器 |
| **OpenAI SDK** | Latest | LLM 集成 |
| **Volcengine SDK** | Latest | 火山引擎 API |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 18 | UI 框架 |
| **Ant Design** | 5 | 组件库 |
| **Framer Motion** | Latest | 动画库 |
| **Vite** | Latest | 构建工具 |
| **Axios** | Latest | HTTP 客户端 |
| **React Markdown** | Latest | Markdown 渲染 |

### AI 模型
| 模型 | 提供商 | 用途 |
|------|--------|------|
| **deepseek-chat** | DeepSeek | 文本对话和生成 |
| **UI-TARS** | 火山引擎 | UI 图片分析 |
| **gpt-4o** | OpenAI | 可选的文本模型 |

## ⚙️ 配置说明

### 后端环境变量

创建 `backend/.env` 文件：

```env
# ==================== 基础配置 ====================
HOST=0.0.0.0
PORT=8000
DEBUG=false

# ==================== DeepSeek API ====================
# 用于文本对话和测试用例生成
API_KEY=sk-your-deepseek-api-key
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com

# ==================== 火山引擎 API ====================
# 用于 UI-TARS 视觉模型
ARK_API_KEY=your-ark-api-key
UITARS_ENDPOINT_ID=your-uitars-endpoint-id

# ==================== OpenAI API（可选）====================
# 如果要使用 OpenAI 模型
# API_KEY=sk-your-openai-api-key
# MODEL_NAME=gpt-4o-mini
# BASE_URL=https://api.openai.com/v1

# ==================== Markdown 转换配置 ====================
MARKDOWN_MAX_FILE_SIZE_MB=10
MARKDOWN_MAX_BATCH_FILES=10
MARKDOWN_USE_LLM=false
MARKDOWN_FORCE_OCR=false
MARKDOWN_DISABLE_IMAGE_EXTRACTION=false

# ==================== 会话管理配置 ====================
SESSION_TIMEOUT_MINUTES=30
MAX_SESSIONS=100
```

### 前端环境变量

创建 `frontend/.env` 文件（可选）：

```env
VITE_API_URL=http://localhost:8000
```

### 模型配置说明

#### DeepSeek 模型
- **用途**：普通对话、测试用例生成
- **优点**：性价比高、中文支持好
- **获取密钥**：https://platform.deepseek.com/

#### UI-TARS 模型
- **用途**：UI 图片分析
- **优点**：专门针对 UI 界面优化
- **获取密钥**：https://console.volcengine.com/

#### OpenAI 模型（可选）
- **用途**：可替代 DeepSeek 用于文本生成
- **优点**：功能强大、生态完善
- **获取密钥**：https://platform.openai.com/

## 🔧 开发指南

### 后端开发

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 启动开发服务器（自动重载）
python main.py

# 运行测试
python -m pytest tests/

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

### 前端开发

```bash
cd frontend

# 启动开发服务器（热模块替换）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### 添加新的智能体

1. 在 `backend/prompts/` 创建提示词文件
2. 在 `backend/agents/` 或 `backend/services/` 创建智能体类
3. 在 `backend/api/routes.py` 添加 API 端点
4. 在前端创建对应的 UI 组件

### 自定义提示词

编辑 `backend/prompts/` 目录下的 `.txt` 文件：

```
backend/prompts/
├── ui_expert.txt              # UI 专家提示词
├── interaction_analyst.txt    # 交互分析师提示词
├── test_scenario_expert.txt   # 测试场景专家提示词
├── test_case_generator.txt    # 测试用例生成器提示词
├── test_case_reviewer.txt     # 测试用例评审器提示词
└── test_case_optimizer.txt    # 测试用例优化器提示词
```

## 📦 生产部署

### 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 使用 Gunicorn 部署（推荐）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

```bash
cd frontend

# 构建生产版本
npm run build

# dist 目录包含静态文件，可以部署到：
# - Nginx
# - Apache
# - Vercel
# - Netlify
# - 任何静态文件托管服务
```

### Docker 部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🐛 故障排除

### 常见问题

#### 1. 后端启动失败

**问题**：`ModuleNotFoundError` 或导入错误
```bash
# 解决方案：确保虚拟环境已激活并安装所有依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**问题**：`API_KEY not configured`
```bash
# 解决方案：检查 .env 文件是否存在并配置正确
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

#### 2. UI-TARS 模型认证失败

**问题**：`401 Unauthorized` 或 `Authentication failed`
```bash
# 解决方案：
# 1. 检查 ARK_API_KEY 是否正确
# 2. 检查 UITARS_ENDPOINT_ID 是否正确
# 3. 确认火山引擎账户余额充足
# 4. 验证 API 密钥权限
```

#### 3. 前端无法连接后端

**问题**：`Network Error` 或 `Failed to fetch`
```bash
# 解决方案：
# 1. 确认后端已启动（http://localhost:8000）
# 2. 检查防火墙设置
# 3. 验证 CORS 配置
# 4. 检查前端 .env 中的 VITE_API_URL
```

#### 4. 图片分析失败

**问题**：图片上传后无响应或报错
```bash
# 解决方案：
# 1. 检查图片格式（支持 jpg, png, webp）
# 2. 确认图片大小不超过限制
# 3. 验证 UI-TARS API 配置
# 4. 查看后端日志获取详细错误信息
```

#### 5. 智能体响应缓慢

**问题**：智能体响应时间过长
```bash
# 解决方案：
# 1. 检查网络连接
# 2. 验证 API 服务状态
# 3. 考虑使用更快的模型
# 4. 检查系统资源使用情况
```

### 调试技巧

#### 查看后端日志
```bash
cd backend
python main.py
# 日志会实时输出到终端
```

#### 查看前端控制台
```
打开浏览器开发者工具（F12）
查看 Console 和 Network 标签
```

#### 测试 API 端点
```bash
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

## 📚 文档

### 项目文档
- [项目架构](docs/ARCHITECTURE.md)
- [UI 图片分析快速开始](docs/QUICK_START_IMAGE_ANALYZER.md)
- [项目整理总结](docs/PROJECT_ORGANIZATION_SUMMARY.md)
- [Backend 测试说明](backend/tests/README.md)
- [Frontend 文档](docs/frontend/README_FRONTEND.md)
- [Prompts 文档](docs/prompts/README_PROMPTS.md)

### 技术文档
- [AutoGen 官方文档](https://microsoft.github.io/autogen/stable/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [Ant Design 官方文档](https://ant.design/)
- [Framer Motion 官方文档](https://www.framer.com/motion/)

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- **Python**：遵循 PEP 8 规范
- **JavaScript**：遵循 ESLint 配置
- **提交信息**：使用清晰的提交信息

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

可自由用于个人或商业用途。

## 🙏 致谢

感谢以下开源项目和团队：

- **Microsoft AutoGen** - 强大的 AI 智能体框架
- **FastAPI** - 现代化的 Python Web 框架
- **Ant Design** - 优秀的 React UI 组件库
- **React** - 灵活的前端框架
- **Framer Motion** - 流畅的动画库
- **DeepSeek** - 高性价比的 AI 模型
- **火山引擎** - UI-TARS 视觉模型

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 发送邮件至：your-email@example.com

## 🌟 Star History

如果这个项目对你有帮助，请给它一个 ⭐️！

---

<div align="center">

**使用 ❤️ 和 AutoGen 0.7.5 构建**

Made with AutoGen • FastAPI • React • Ant Design

</div>

