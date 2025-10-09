# 快速启动指南

## 🚀 启动服务

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动后端服务
python3 main.py
```

后端服务将在 `http://localhost:8000` 启动。

**验证后端是否启动成功**：
```bash
curl http://localhost:8000/health
```

应该返回类似：
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "session_count": 0
}
```

### 2. 启动前端服务

打开新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动前端服务
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

## 🖼️ 使用图片分析功能

1. **打开浏览器**
   - 访问 `http://localhost:5173`

2. **选择模式**
   - 在首页看到 3 个卡片（现在排列在一排）
   - 点击 **"UI 图片分析模式"** 卡片

3. **上传图片**
   - 方式一：点击 "上传图片文件" 按钮，选择本地图片
   - 方式二：在 "或者输入图片 URL" 输入框中输入图片 URL

4. **填写附加信息（可选）**
   - 图片所在页面 URL
   - 测试场景描述
   - 附加上下文信息

5. **开始分析**
   - 点击 **"开始分析"** 按钮
   - 实时查看三个智能体的分析过程：
     - 🎨 UI 专家
     - 🔄 交互分析师
     - 📋 测试场景专家

## ⚠️ 常见问题

### 问题 1：后端启动失败

**错误信息**：`ModuleNotFoundError: No module named 'autogen_agentchat'`

**解决方案**：
```bash
cd backend
pip install -r requirements.txt
```

### 问题 2：前端连接失败

**错误信息**：`Failed to fetch` 或 `ERR_CONNECTION_REFUSED`

**原因**：后端服务未启动

**解决方案**：
1. 确保后端服务已启动（参见上面的启动步骤）
2. 验证后端是否正常运行：
   ```bash
   curl http://localhost:8000/health
   ```

### 问题 3：LLM API 配置

**错误信息**：API key 相关错误

**解决方案**：
1. 检查 `backend/.env` 文件是否存在
2. 确保配置了正确的 API 密钥：
   ```env
   # DeepSeek API
   DEEPSEEK_API_KEY=your_api_key_here
   DEEPSEEK_BASE_URL=https://api.deepseek.com
   
   # 或者 OpenAI API
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

### 问题 4：前端卡片排列问题

**已修复**：现在 3 个卡片会排列在一排（在大屏幕上）

- 大屏幕（>1200px）：3 个卡片一排
- 中等屏幕（768px-1200px）：2 个卡片一排
- 小屏幕（<768px）：1 个卡片一排

## 📊 测试 API

### 使用测试脚本

```bash
cd backend/examples
python3 test_image_analyzer_api.py
```

### 使用 curl 测试

**测试健康检查**：
```bash
curl http://localhost:8000/health
```

**测试图片分析（使用 URL）**：
```bash
curl -X POST http://localhost:8000/api/image-analysis/stream \
  -F "image_url=https://example.com/screenshot.png" \
  -F "test_description=登录页面测试"
```

## 🎯 功能特点

### 三个专业智能体协作

1. **🎨 UI 专家**
   - 分析视觉元素和布局结构
   - 识别所有可见的 UI 元素
   - 评估设计规范

2. **🔄 交互分析师**
   - 分析交互行为和用户流程
   - 识别交互模式
   - 提供测试建议

3. **📋 测试场景专家**
   - 综合前两位专家的分析
   - 设计全面的测试场景
   - 提供自动化测试建议

### 并行处理架构

- UI 专家和交互分析师**并行执行**
- 测试场景专家综合两者结果
- 性能提升约 38%

### 实时流式输出

- 使用 SSE 技术
- 实时显示每个智能体的回复
- 支持 Markdown 格式渲染

## 📚 更多文档

- [前端使用指南](docs/IMAGE_ANALYZER_FRONTEND_GUIDE.md)
- [功能完成总结](docs/UI图片分析功能完成总结.md)
- [GraphFlow 实现](backend/examples/GRAPHFLOW_IMPLEMENTATION.md)
- [架构文档](backend/examples/ARCHITECTURE.md)

## 🎉 开始使用

现在你可以开始使用 UI 图片分析功能了！

1. 启动后端：`cd backend && python3 main.py`
2. 启动前端：`cd frontend && npm run dev`
3. 打开浏览器：`http://localhost:5173`
4. 选择 "UI 图片分析模式"
5. 上传图片并开始分析！

祝你使用愉快！🚀

