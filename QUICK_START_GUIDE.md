# 快速开始指南

## 🚀 启动应用

### 1. 启动后端

```bash
cd backend
source venv/bin/activate
python main.py
```

**预期输出**:
```
╔══════════════════════════════════════════════════════════════╗
║                   AutoGen 聊天应用配置                        ║
╚══════════════════════════════════════════════════════════════╝

📋 应用信息
  • 标题: AutoGen 聊天 API
  • 版本: 1.0.0
  • 主机: 0.0.0.0
  • 端口: 8000

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v5.4.20  ready in 163 ms

➜  Local:   http://localhost:3001/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### 3. 访问应用

打开浏览器访问: **http://localhost:3001**

---

## 🎯 功能测试

### 测试 1: 首页导航

1. 访问 `http://localhost:3001`
2. 自动重定向到 `http://localhost:3001/home`
3. 看到 3 个模式选择卡片:
   - 普通对话模式
   - 测试用例智能体模式
   - UI 图片分析模式

**验证**:
- ✅ 页面标题: "AutoGen Chat - 选择模式"
- ✅ 矩阵雨背景动画
- ✅ 3 个模式卡片正常显示

### 测试 2: 普通对话模式

1. 点击"普通对话模式"卡片
2. 跳转到 `http://localhost:3001/chat/normal`
3. 看到聊天界面

**验证**:
- ✅ 页面标题: "AutoGen Chat - 普通对话"
- ✅ 顶部导航栏显示
- ✅ "普通对话"菜单项高亮
- ✅ 聊天界面正常显示

**测试对话**:
```
输入: 你好
预期: AI 回复问候语
```

**测试文件上传**:
1. 点击文件上传按钮
2. 选择一个文件（如 .py, .txt）
3. 等待文件解析完成
4. 输入: "这个文件的内容是什么？"
5. 预期: AI 基于文件内容回答

**测试会话复用**:
1. 发送消息: "我叫张三"
2. 发送消息: "我叫什么名字？"
3. 预期: AI 回答 "张三"

### 测试 3: 测试用例生成模式

1. 点击顶部导航 "测试用例"
2. 跳转到 `http://localhost:3001/chat/testcase`
3. 看到测试用例生成界面

**验证**:
- ✅ 页面标题: "AutoGen Chat - 测试用例生成"
- ✅ "测试用例"菜单项高亮
- ✅ 智能体协作界面显示

**测试生成**:
```
输入: 为用户登录功能生成测试用例
预期: 
  1. TestCase_Generator 开始生成
  2. TestCase_Reviewer 开始评审
  3. TestCase_Optimizer 开始优化
  4. 显示最终测试用例
```

**测试反馈**:
1. 等待生成完成
2. 输入: "@TestCase_Generator 请添加边界值测试"
3. 预期: Generator 响应并更新测试用例

### 测试 4: 图片分析模式

1. 点击顶部导航 "图片分析"
2. 跳转到 `http://localhost:3001/image-analysis`
3. 看到图片上传界面

**验证**:
- ✅ 页面标题: "AutoGen Chat - 图片分析"
- ✅ "图片分析"菜单项高亮
- ✅ 图片上传区域显示

**测试分析**:
1. 上传一张 UI 截图
2. 点击"开始分析"
3. 预期: 
   - UI_Expert 分析界面元素
   - Interaction_Analyst 分析交互流程
   - Test_Scenario_Expert 生成测试场景

### 测试 5: 路由功能

**直接访问**:
- 访问 `http://localhost:3001/chat/normal` ✅
- 访问 `http://localhost:3001/chat/testcase` ✅
- 访问 `http://localhost:3001/image-analysis` ✅

**浏览器导航**:
1. 从首页进入普通对话
2. 点击浏览器"后退"按钮
3. 预期: 返回首页 ✅
4. 点击浏览器"前进"按钮
5. 预期: 回到普通对话 ✅

**刷新页面**:
1. 在普通对话页面发送几条消息
2. 按 F5 刷新页面
3. 预期: 
   - 仍在普通对话页面 ✅
   - 会话 ID 保持不变 ✅
   - 可以继续对话 ✅

### 测试 6: 会话管理

**独立会话**:
1. 在普通对话发送: "我叫张三"
2. 切换到测试用例模式
3. 发送: "我叫什么名字？"
4. 预期: AI 不知道（因为是不同会话）✅

**会话持久化**:
1. 在普通对话发送: "记住：我的项目叫 AutoGen"
2. 刷新页面
3. 发送: "我的项目叫什么？"
4. 预期: AI 回答 "AutoGen" ✅

**清空会话**:
1. 点击"清空对话"按钮
2. 发送: "我的项目叫什么？"
3. 预期: AI 不知道（会话已重置）✅

---

## 🔍 后端 API 测试

### 健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "session_count": 0,
  "services": {
    "home": "active",
    "chat_normal": "active",
    "chat_testcase": "active",
    "image_analysis": "active",
    "files": "active"
  }
}
```

### 首页信息

```bash
curl http://localhost:8000/api/home/
```

**预期响应**:
```json
{
  "message": "AutoGen Chat Application",
  "version": "1.0.0",
  "modes": [
    {
      "id": "normal",
      "name": "普通对话",
      "description": "与 AI 进行自然对话，支持文件上传",
      "path": "/chat/normal",
      "icon": "message"
    },
    ...
  ]
}
```

### 普通对话

```bash
curl -X POST http://localhost:8000/api/chat/normal/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "conversation_id": null
  }'
```

**预期**: SSE 流式数据

### 测试用例生成

```bash
curl -X POST http://localhost:8000/api/chat/testcase/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "为登录功能生成测试用例",
    "conversation_id": null
  }'
```

**预期**: SSE 流式数据，包含智能体协作过程

---

## 📊 监控和调试

### 后端日志

**会话创建**:
```
📝 创建新会话: normal_abc123 (总会话数: 1)
```

**会话复用**:
```
♻️ 复用现有会话: normal_abc123
```

**智能体工作**:
```
🤖 [TestCase_Generator] 开始工作
💬 [TestCase_Generator] 生成测试用例...
✅ [TestCase_Generator] 完成
```

### 前端控制台

**路由导航**:
```
Navigation: /home -> /chat/normal
```

**会话管理**:
```
📂 恢复 normal 会话 ID: normal_abc123
💾 保存 normal 会话 ID: normal_abc123
```

**API 调用**:
```
🔵 发送消息: 你好
📝 Conversation ID: normal_abc123
```

---

## ⚠️ 常见问题

### 问题 1: 前端无法连接后端

**症状**: 前端显示网络错误

**解决**:
1. 检查后端是否启动: `http://localhost:8000/health`
2. 检查 CORS 配置
3. 检查环境变量 `VITE_API_URL`

### 问题 2: 会话 ID 丢失

**症状**: 刷新页面后 AI 忘记之前的对话

**解决**:
1. 检查浏览器控制台是否有错误
2. 检查 localStorage 是否被清除
3. 检查后端日志中的会话 ID

### 问题 3: 文件上传失败

**症状**: 文件上传后无法解析

**解决**:
1. 检查文件格式是否支持
2. 检查后端是否安装 marker-pdf
3. 查看后端日志中的错误信息

### 问题 4: 图片分析报错

**症状**: 上传图片后报错

**解决**:
1. 检查图片格式（支持 jpg, png）
2. 检查图片大小（建议 < 5MB）
3. 检查后端模型是否正确加载

---

## 📚 API 文档

访问 **http://localhost:8000/docs** 查看完整的 API 文档（Swagger UI）

---

## ✅ 验收清单

### 基础功能
- [ ] 后端正常启动（27 个路由）
- [ ] 前端正常启动
- [ ] 首页正常显示
- [ ] 3 个模式都能正常访问

### 路由功能
- [ ] URL 直接访问各功能
- [ ] 浏览器前进/后退正常
- [ ] 刷新页面保持状态
- [ ] 导航菜单高亮正确

### 对话功能
- [ ] 普通对话正常工作
- [ ] 测试用例生成正常工作
- [ ] 图片分析正常工作
- [ ] 文件上传正常工作

### 会话管理
- [ ] 会话 ID 正确保存
- [ ] 会话 ID 正确复用
- [ ] 不同模式会话独立
- [ ] 清空会话正常工作

### 用户体验
- [ ] 页面标题正确
- [ ] 主题切换正常
- [ ] 动画效果流畅
- [ ] 响应速度快

---

## 🎉 完成

如果所有测试都通过，恭喜！应用已经成功运行。

**下一步**:
- 查看 `ROUTING_IMPLEMENTATION_SUMMARY.md` 了解架构
- 查看 `BACKEND_ROUTES_GUIDE.md` 了解后端 API
- 查看 `FRONTEND_ROUTING_PLAN.md` 了解前端规划

