# Team Agent 快速参考手册

## 📚 文档索引

- **完整执行流程**：[TEAM_AGENT_EXECUTION_FLOW.md](./TEAM_AGENT_EXECUTION_FLOW.md)
- **智能体标签功能**：[AGENT_TAG_FEATURE.md](./AGENT_TAG_FEATURE.md)
- **消息操作功能**：[MESSAGE_ACTIONS_FEATURE.md](./MESSAGE_ACTIONS_FEATURE.md)
- **Bug 修复记录**：[BUG_FIX_OPTIMIZER.md](./BUG_FIX_OPTIMIZER.md)

---

## 🎯 核心概念

### 三个智能体

| 智能体 | 图标 | 角色 | 职责 |
|--------|------|------|------|
| TestCase_Generator | 🎯 | 生成专家 | 根据需求生成测试用例 |
| TestCase_Reviewer | 🔍 | 评审专家 | 评审测试用例质量 |
| TestCase_Optimizer | ⚡ | 优化专家 | 给出最终优化方案 |

### 工作流程

```
用户输入 → Generator → Reviewer → [等待反馈]
                                        ↓
                        ┌───────────────┴───────────────┐
                        │                               │
                   用户同意                        用户反馈
                        │                               │
                        ▼                               ▼
                   Optimizer                    重新运行/指定智能体
                        │
                        ▼
                    最终答案
```

---

## 🔄 五种交互模式

### 1. 首次对话
```
用户 → "生成支付接口测试用例"
系统 → Generator 生成 → Reviewer 评审 → 等待反馈
```

### 2. 用户同意
```
用户 → 点击"同意"按钮
系统 → Optimizer 生成最终方案 → 对话结束
```

### 3. 用户反馈（无@）
```
用户 → "请添加边界测试"
系统 → Generator 重新生成 → Reviewer 重新评审 → 等待反馈
```

### 4. 用户反馈（@特定智能体）
```
用户 → "@TestCase_Generator 请添加性能测试"
系统 → 只运行 Generator → 等待反馈
```

### 5. 用户反馈（@all）
```
用户 → "@all 重新生成"
系统 → Generator 重新生成 → Reviewer 重新评审 → 等待反馈
```

---

## 📡 API 接口

### POST /api/team-chat/stream

#### 请求参数
```json
{
  "message": "用户消息",
  "is_feedback": false,           // 是否为反馈消息
  "conversation_id": null,        // 会话 ID（首次为 null）
  "target_agent": null,           // 目标智能体（可选）
  "file_ids": []                  // 文件 ID 列表（可选）
}
```

#### 响应头
```
X-Conversation-ID: team_session_xxx
X-Team-Mode: true
Content-Type: text/event-stream
```

#### SSE 事件类型
```javascript
{
  "status": "状态消息",
  "agent_start": "智能体开始",
  "content": "内容块",
  "agent_end": "智能体完成",
  "feedback_request": "反馈请求",
  "final_answer": "最终答案",
  "error": "错误",
  "done": "完成"
}
```

---

## 🗂️ 关键文件

### 前端
```
frontend/src/
├── App.jsx                    # 主应用组件
├── App.css                    # 样式文件
└── components/
    ├── ModeSelector.jsx       # 模式选择器
    └── FileUpload.jsx         # 文件上传
```

### 后端
```
backend/
├── main.py                    # 应用入口
├── api/
│   └── routes.py              # API 路由
├── services/
│   ├── ai_service.py          # AI 服务（团队管理）
│   ├── team_stream_service.py # 流式处理服务
│   └── team_session_service.py# 会话管理服务
├── models.py                  # 数据模型
└── prompts/
    └── test_case_prompts.py   # 智能体 Prompt
```

---

## 🔑 关键代码位置

### 1. 判断是否等待反馈
```python
# 文件: backend/services/team_stream_service.py, 行: ~250
def _should_wait_for_feedback(self, agent_name: str) -> bool:
    return agent_name == "TestCase_Reviewer"
```

### 2. 判断是否为最终答案
```python
# 文件: backend/services/team_stream_service.py, 行: ~260
def _is_final_answer(self, agent_name: str) -> bool:
    return agent_name == "TestCase_Optimizer"
```

### 3. 解析目标智能体
```python
# 文件: backend/api/routes.py, 行: ~46
def _parse_target_agent(message: str) -> Optional[str]:
    if re.search(r'@all\b', message, re.IGNORECASE):
        return "all"
    match = re.search(r'@(TestCase_\w+)', message)
    if match:
        return match[1]
    return None
```

### 4. 创建团队智能体
```python
# 文件: backend/services/ai_service.py, 行: ~202
def _create_team_agents(self, specific_agent: Optional[str] = None):
    if specific_agent == "TestCase_Generator":
        self.agents = [test_generator_agent]
    elif specific_agent == "TestCase_Reviewer":
        self.agents = [test_reviewer_agent]
    elif specific_agent == "TestCase_Optimizer":
        self.agents = [test_optimizer_agent]
    else:
        # 默认：Generator + Reviewer
        self.agents = [test_generator_agent, test_reviewer_agent]
```

### 5. 前端处理反馈请求
```javascript
// 文件: frontend/src/App.jsx, 行: ~330
case 'feedback_request':
  setMessages(prev =>
    prev.map(msg =>
      msg.id === assistantMsgId
        ? {
            ...msg,
            streaming: false,
            feedbackRequest: {
              agentName: data.agent_name,
              availableAgents: data.available_agents
            },
            conversationId: responseConversationId
          }
        : msg
    )
  );
  break;
```

---

## 🐛 常见问题

### 1. Optimizer 生成错误内容
**原因**：智能体回答未保存到会话历史  
**解决**：在流结束后保存所有智能体回答
```python
# 文件: backend/api/routes.py, 行: ~430
for agent_name, response in team_stream_service.agent_responses.items():
    if response:
        session_service.add_message(current_conversation_id, agent_name, response)
```

### 2. 前端无法读取 conversation_id
**原因**：CORS 未暴露自定义响应头  
**解决**：添加 `expose_headers` 配置
```python
# 文件: backend/main.py
app.add_middleware(
    CORSMiddleware,
    expose_headers=["X-Conversation-ID", "X-Team-Mode"],
)
```

### 3. 后端创建新会话而非继续
**原因**：前端未正确传递 `conversation_id`  
**解决**：从响应头读取并保存到消息对象
```javascript
const responseConversationId = response.headers.get('X-Conversation-ID');
setMessages(prev => prev.map(msg => ({
  ...msg,
  conversationId: responseConversationId
})));
```

---

## 📊 性能指标

### 典型响应时间
- **首次对话**：3-5 秒（Generator + Reviewer）
- **用户同意**：2-3 秒（Optimizer）
- **用户反馈**：3-5 秒（重新运行）

### 资源占用
- **内存**：每个会话约 1-2 MB
- **缓存**：团队实例约 5-10 MB
- **并发**：支持 100+ 并发会话

---

## 🔧 调试命令

### 查看会话状态
```bash
curl http://localhost:8000/api/sessions/team_session_xxx
```

### 查看所有会话
```bash
curl http://localhost:8000/api/sessions
```

### 删除会话
```bash
curl -X DELETE http://localhost:8000/api/sessions/team_session_xxx
```

### 查看后端日志
```bash
# 启动时启用详细日志
LOG_LEVEL=DEBUG python3 -m uvicorn main:app --reload
```

---

## 🎨 UI 组件

### 反馈对话框
```jsx
<div className="feedback-dialog">
  <div className="feedback-header">
    💬 {agentName} 已完成，请提供反馈
  </div>
  
  <div className="agent-tags-container">
    <button onClick={() => handleAgentTagClick('all')}>
      🔄 All
    </button>
    {availableAgents.map(agent => (
      <button onClick={() => handleAgentTagClick(agent)}>
        {getAgentIcon(agent)} {agent}
      </button>
    ))}
  </div>
  
  <button onClick={() => handleApprove(messageId)}>
    ✅ 同意
  </button>
</div>
```

### 消息操作按钮
```jsx
{/* 用户消息 */}
<div className="message-actions user-actions">
  <button onClick={() => handleResendMessage(msg.id)}>
    🔄 重新发送
  </button>
  <button onClick={() => handleEditMessage(msg.id)}>
    ✏️ 编辑
  </button>
</div>

{/* 智能体消息 */}
<div className="message-actions assistant-actions">
  <button onClick={() => handleCopyMessage(msg.id)}>
    📋 复制
  </button>
  <button onClick={() => handleSaveMessage(msg.id)}>
    💾 保存
  </button>
</div>
```

---

## 📝 配置文件

### 环境变量
```bash
# .env
API_KEY=your_api_key
BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

### 前端配置
```javascript
// frontend/.env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 快速启动

### 启动后端
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端
```bash
cd frontend
npm run dev
```

### 访问应用
```
前端: http://localhost:3001
后端: http://localhost:8000
API 文档: http://localhost:8000/docs
```

---

## 📚 扩展阅读

- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [SSE 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)

---

## 💡 最佳实践

1. **会话管理**：定期清理过期会话，避免内存泄漏
2. **错误处理**：捕获所有异常，提供友好的错误提示
3. **日志记录**：记录关键操作，便于调试和监控
4. **性能优化**：使用缓存减少重复初始化
5. **用户体验**：提供清晰的反馈和加载状态

---

## 🎉 总结

Team Agent 系统通过三个智能体的协作，实现了高质量的测试用例生成：

✅ **Generator** 负责生成  
✅ **Reviewer** 负责评审  
✅ **Optimizer** 负责优化  
✅ **用户** 全程参与决策  

这种人机协作的模式，既保证了输出质量，又给予用户充分的控制权！🚀

