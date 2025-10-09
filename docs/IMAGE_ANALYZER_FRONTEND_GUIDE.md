# UI 图片分析功能 - 前端使用指南

## 📋 概述

UI 图片分析功能已成功集成到前端应用中，用户可以通过图形界面上传 UI 截图，由 3 个专业智能体协作分析并生成测试场景。

## 🎯 功能特点

### 三个专业智能体协作

1. **🎨 UI 专家 (UI_Expert)**
   - 分析界面的视觉元素和布局结构
   - 识别所有可见的 UI 元素
   - 评估设计规范和一致性

2. **🔄 交互分析师 (Interaction_Analyst)**
   - 分析用户界面的交互行为
   - 识别用户操作流程
   - 评估交互模式和反馈机制

3. **📋 测试场景专家 (Test_Scenario_Expert)**
   - 综合前两位专家的分析结果
   - 设计全面的测试场景和测试用例
   - 提供自动化测试建议

### 并行处理架构

- UI 专家和交互分析师**并行执行**，提高分析效率
- 测试场景专家等待两位专家完成后，综合分析结果
- 使用 GraphFlow 实现智能体工作流编排

## 🚀 快速开始

### 1. 启动服务

#### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

#### 启动前端服务

```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

### 2. 使用图片分析功能

1. **选择模式**
   - 打开浏览器访问 `http://localhost:5173`
   - 在模式选择页面，点击 **"UI 图片分析模式"** 卡片

2. **上传图片**
   - 方式一：点击 "上传图片文件" 按钮，选择本地图片
   - 方式二：在 "或者输入图片 URL" 输入框中输入图片 URL

3. **填写附加信息（可选）**
   - **图片所在页面 URL**：图片对应的网页地址
   - **测试场景描述**：描述需要测试的场景
   - **附加上下文信息**：其他需要智能体关注的信息

4. **开始分析**
   - 点击 **"开始分析"** 按钮
   - 系统将实时显示每个智能体的分析过程
   - 分析完成后，可以查看完整的分析结果

5. **查看结果**
   - 每个智能体的分析结果会以卡片形式展示
   - 支持 Markdown 格式渲染
   - 可以滚动查看完整内容

## 📡 API 接口

### 流式分析接口

**端点**: `POST /api/image-analysis/stream`

**请求参数** (FormData):
- `image` (可选): 上传的图片文件
- `image_url` (可选): 图片 URL
- `session_id` (可选): 会话 ID
- `web_url` (可选): 图片所在页面的 URL
- `test_description` (可选): 测试场景描述
- `additional_context` (可选): 附加上下文信息
- `target_url` (可选): 目标页面 URL

**响应**: Server-Sent Events (SSE) 流

**事件类型**:
```json
{
  "type": "status",
  "content": "图片分析团队协作中..."
}

{
  "type": "agent_start",
  "agent_name": "UI_Expert",
  "agent_role": "🎨 UI 专家",
  "content": "🎨 UI 专家 开始分析..."
}

{
  "type": "agent_message",
  "agent_name": "UI_Expert",
  "agent_role": "🎨 UI 专家",
  "content": "### 页面概览\n- 页面类型：登录页..."
}

{
  "type": "agent_done",
  "agent_name": "UI_Expert",
  "agent_role": "🎨 UI 专家",
  "content": "🎨 UI 专家 分析完成"
}

{
  "type": "done",
  "content": "图片分析完成"
}

{
  "type": "token_usage",
  "content": "总计使用 1234 tokens",
  "token_usage": {
    "total_tokens": 1234,
    "message_count": 6
  }
}
```

### 非流式分析接口

**端点**: `POST /api/image-analysis`

**请求参数**: 同流式接口

**响应**:
```json
{
  "session_id": "img_abc123",
  "ui_analysis": ["UI 专家的分析结果..."],
  "interaction_analysis": ["交互分析师的分析结果..."],
  "test_scenarios": ["测试场景专家的分析结果..."],
  "chat_history": [
    {
      "source": "user",
      "content": "请分析这个登录页面"
    },
    {
      "source": "UI_Expert",
      "content": "这是一个标准的登录页面..."
    }
  ],
  "summary": "该登录页面包含标准的用户名密码输入框...",
  "status": "success"
}
```

## 🎨 前端组件

### ImageAnalyzer 组件

**位置**: `frontend/src/components/ImageAnalyzer.jsx`

**主要功能**:
- 图片上传和 URL 输入
- 附加信息表单
- SSE 流式事件处理
- 智能体消息实时显示
- Markdown 内容渲染

**样式文件**: `frontend/src/components/ImageAnalyzer.css`

### 集成到 App.jsx

在 `App.jsx` 中添加了新的模式分支：

```jsx
{selectedMode === 'image-analyzer' ? (
  <div className={`app-container ${isDark ? 'dark' : 'light'}`}>
    <ImageAnalyzer isDark={isDark} />
  </div>
) : (
  // 其他模式...
)}
```

## 🔧 技术实现

### 后端架构

1. **API 路由** (`backend/api/routes.py`)
   - `/api/image-analysis/stream` - 流式分析
   - `/api/image-analysis` - 非流式分析

2. **图片分析团队** (`backend/examples/image_analyzer.py`)
   - `ImageAnalyzerTeam` 类
   - GraphFlow 工作流编排
   - 并行智能体执行

3. **流式服务** (`backend/services/image_analysis_stream_service.py`)
   - `ImageAnalysisStreamService` 类
   - SSE 事件生成
   - 智能体消息处理

4. **提示词** (`backend/prompts/`)
   - `ui_expert.txt` - UI 专家系统提示词
   - `interaction_analyst.txt` - 交互分析师系统提示词
   - `test_scenario_expert.txt` - 测试场景专家系统提示词

### 前端架构

1. **模式选择** (`ModeSelector.jsx`)
   - 添加了 "UI 图片分析模式" 选项

2. **图片分析组件** (`ImageAnalyzer.jsx`)
   - 图片上传处理
   - SSE 流式事件接收
   - 智能体消息渲染

3. **样式设计** (`ImageAnalyzer.css`)
   - 深色/浅色主题支持
   - 响应式布局
   - 智能体消息卡片样式

## 📝 使用示例

### 示例 1：分析登录页面

1. 上传登录页面截图
2. 填写信息：
   - 页面 URL: `https://example.com/login`
   - 测试描述: `用户登录功能测试`
   - 附加信息: `需要重点关注表单验证`
3. 点击 "开始分析"
4. 查看三个智能体的分析结果

### 示例 2：使用图片 URL

1. 输入图片 URL: `https://example.com/screenshot.png`
2. 填写测试描述: `购物车页面 UI 测试`
3. 点击 "开始分析"
4. 实时查看分析过程

## 🐛 故障排除

### 问题 1：图片上传失败

**可能原因**:
- 图片格式不支持
- 图片文件过大

**解决方案**:
- 确保图片格式为 PNG、JPG、JPEG 等常见格式
- 压缩图片大小

### 问题 2：分析超时

**可能原因**:
- 网络连接问题
- 后端服务未启动
- LLM API 响应慢

**解决方案**:
- 检查网络连接
- 确认后端服务正常运行
- 检查 LLM API 配置

### 问题 3：智能体消息不显示

**可能原因**:
- SSE 连接中断
- 前端事件处理错误

**解决方案**:
- 刷新页面重试
- 检查浏览器控制台错误信息
- 确认后端 SSE 流正常

## 📚 相关文档

- [GraphFlow 实现说明](../backend/examples/GRAPHFLOW_IMPLEMENTATION.md)
- [图片分析器架构](../backend/examples/ARCHITECTURE.md)
- [快速开始指南](../backend/examples/QUICK_START_IMAGE_ANALYZER.md)
- [详细文档](../backend/examples/README_IMAGE_ANALYZER.md)

## 🎉 总结

UI 图片分析功能已完全集成到前端应用中，提供了：

✅ 直观的图形界面
✅ 实时的分析过程展示
✅ 三个专业智能体协作
✅ 并行处理提高效率
✅ 完整的测试场景生成

现在可以开始使用这个强大的 UI 分析工具了！

