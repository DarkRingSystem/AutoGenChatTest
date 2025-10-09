# AutoGen 聊天后端

基于 FastAPI 的后端，集成 AutoGen 0.7.5 并支持 SSE 流式传输。

## 功能特性

- 🚀 FastAPI 框架，高性能
- 🤖 AutoGen 0.7.5 集成，提供 AI 智能体能力
- 📡 服务器推送事件（SSE）实现实时流式传输
- 🔄 同时支持流式和非流式端点
- 🛡️ 已启用 CORS 跨域支持

## 设置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 创建 `.env` 文件：
```bash
cp .env.example .env
```

3. 编辑 `.env` 并配置 API 密钥：

**使用 DeepSeek（推荐，性价比高）：**
```env
API_KEY=sk-your-deepseek-api-key
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com
```

**或使用 OpenAI：**
```env
API_KEY=sk-your-openai-api-key
MODEL_NAME=gpt-4o-mini
BASE_URL=https://api.openai.com/v1
```

## 运行

启动服务器：
```bash
python main.py
```

或直接使用 uvicorn：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 将在 `http://localhost:8000` 上运行

## API 端点

### GET /
根端点，返回 API 信息

### GET /health
健康检查端点

### POST /api/chat/stream
使用 SSE 的流式聊天端点

请求体：
```json
{
  "message": "你好，你好吗？",
  "conversation_id": "可选的会话ID"
}
```

响应：SSE 事件流，包含以下事件：
- `status`: 当前处理状态
- `chunk`: 流式文本块
- `message`: 完整消息
- `tool_call`: 工具调用信息
- `tool_result`: 工具执行结果
- `done`: 流完成
- `error`: 错误信息

### POST /api/chat
非流式聊天端点

请求体：
```json
{
  "message": "你好，你好吗？",
  "conversation_id": "可选的会话ID"
}
```

响应：
```json
{
  "message": "我很好，谢谢！",
  "conversation_id": "可选的会话ID",
  "status": "success"
}
```

## 文档

交互式 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 支持的模型

### DeepSeek（推荐）
- **模型**：`deepseek-chat`
- **优势**：
  - 💰 性价比极高（比 GPT-4 便宜 90%+）
  - 🚀 响应速度快
  - 🇨🇳 中文能力强
  - 📊 上下文长度：32K tokens
- **获取 API Key**：访问 [DeepSeek 平台](https://platform.deepseek.com/)
- **定价**：
  - 输入：¥1/百万 tokens
  - 输出：¥2/百万 tokens

### OpenAI
- **模型**：`gpt-4o-mini`、`gpt-4o`、`gpt-4`
- **优势**：
  - 🎯 性能强大
  - 🌍 多语言支持
  - 🔧 生态完善
- **获取 API Key**：访问 [OpenAI 平台](https://platform.openai.com/)

### 其他兼容服务
本项目支持任何兼容 OpenAI API 格式的服务，包括：
- Azure OpenAI
- 本地部署的模型（如 Ollama、LM Studio）
- 其他第三方 API 服务

只需在 `.env` 中配置相应的 `BASE_URL` 即可。

## 环境变量说明

| 变量 | 描述 | 默认值 | 必需 |
|------|------|--------|------|
| `API_KEY` | API 密钥 | - | ✅ 是 |
| `MODEL_NAME` | 模型名称 | `deepseek-chat` | ❌ 否 |
| `BASE_URL` | API 基础 URL | `https://api.deepseek.com` | ❌ 否 |
| `HOST` | 服务器主机 | `0.0.0.0` | ❌ 否 |
| `PORT` | 服务器端口 | `8000` | ❌ 否 |

## 故障排除

### 智能体未初始化
- 检查 `.env` 中是否设置了 `API_KEY`
- 验证 API 密钥是否有效
- 确认 `BASE_URL` 配置正确

### 连接超时或失败
- 检查网络连接
- 验证 `BASE_URL` 是否可访问
- 确认 API 服务是否正常运行

### 模型不存在错误
- 确认 `MODEL_NAME` 拼写正确
- 检查该模型是否在你的 API 账户中可用
- DeepSeek 使用 `deepseek-chat`
- OpenAI 使用 `gpt-4o-mini` 或其他可用模型

