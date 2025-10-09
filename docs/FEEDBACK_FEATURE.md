# 智能体反馈功能实现文档

## 功能概述

实现了智能体团队模式中的用户反馈功能，允许用户在 `TestCase_Reviewer` 或 `TestCase_Optimizer` 完成后提供反馈，并可以指定特定智能体继续对话。

## 工作流程

### 1. 初始对话
```
用户 → Generator → Reviewer → [等待反馈]
```

### 2. 用户反馈
- **同意/留空**: 结束对话
- **输入反馈**: 继续对话，可以 @ 指定智能体

### 3. 继续对话
```
用户反馈 → @指定智能体 → 智能体回答 → [等待反馈]
```

## 后端实现

### 1. 数据模型 (`backend/models.py`)

```python
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    file_ids: Optional[list[str]] = None
    is_feedback: bool = False  # 新增：标识是否为反馈消息
    target_agent: Optional[str] = None  # 新增：目标智能体

class SSEMessage(BaseModel):
    type: Literal[..., "feedback_request"]  # 新增类型
    available_agents: Optional[list[str]] = None  # 新增字段
```

### 2. 会话管理 (`backend/services/team_session_service.py`)

```python
class TeamSession:
    session_id: str
    messages: List[TeamMessage]
    waiting_for_feedback: bool  # 是否等待反馈
    last_agent: Optional[str]  # 最后回答的智能体

class TeamSessionService:
    def create_session() -> str
    def get_session(session_id) -> TeamSession
    def add_message(session_id, role, content)
    def set_waiting_for_feedback(session_id, waiting, last_agent)
```

### 3. 智能体服务 (`backend/services/ai_service.py`)

修改终止条件：
```python
# 当 Reviewer 或 Optimizer 完成后停止
feedback_termination = SourceMatchTermination([
    "TestCase_Reviewer", 
    "TestCase_Optimizer"
])
```

### 4. 流式服务 (`backend/services/team_stream_service.py`)

```python
def _should_wait_for_feedback(agent_name: str) -> bool:
    return agent_name in ["TestCase_Reviewer", "TestCase_Optimizer"]

def _create_feedback_request_message(agent_name: str) -> str:
    # 发送反馈请求，包含可用智能体列表
    pass
```

### 5. API 路由 (`backend/api/routes.py`)

```python
@router.post("/api/team-chat/stream")
async def team_chat_stream(request: ChatRequest):
    if request.is_feedback and request.conversation_id:
        # 继续对话模式
        - 从缓存中获取团队实例
        - 检查用户是否同意
        - 解析目标智能体
        - 继续运行团队
    else:
        # 新对话模式
        - 创建新会话
        - 创建新团队实例
        - 缓存团队实例
        - 运行团队
```

## 前端实现（待完成）

### 1. 处理反馈请求

```javascript
// 在 handleSendMessage 中检测是否有待反馈的消息
const pendingFeedbackMessage = messages.find(msg => msg.feedbackRequest);

if (pendingFeedbackMessage) {
  // 发送反馈
  const response = await fetch('/api/team-chat/stream', {
    method: 'POST',
    body: JSON.stringify({
      message: inputValue,
      conversation_id: pendingFeedbackMessage.conversationId,
      is_feedback: true,
      target_agent: parseTargetAgent(inputValue)
    })
  });
}
```

### 2. 解析 @ 提及

```javascript
function parseTargetAgent(message) {
  const match = message.match(/@(TestCase_\w+)/);
  return match ? match[1] : null;
}
```

### 3. 添加"同意"按钮

```jsx
{msg.feedbackRequest && (
  <div className="feedback-actions">
    <button onClick={() => handleApprove(msg.id)}>
      ✅ 同意
    </button>
  </div>
)}
```

## API 使用示例

### 1. 新对话

```bash
curl -X POST http://localhost:8000/api/team-chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "生成登录功能的测试用例"
  }'
```

响应：
```
data: {"type":"agent_start","agent_name":"TestCase_Generator",...}
data: {"type":"agent_message","content":"...",...}
data: {"type":"agent_done","agent_name":"TestCase_Generator",...}
data: {"type":"agent_start","agent_name":"TestCase_Reviewer",...}
data: {"type":"agent_message","content":"...",...}
data: {"type":"agent_done","agent_name":"TestCase_Reviewer",...}
data: {"type":"feedback_request","content":"请提供反馈","available_agents":[...],...}
data: [DONE]
```

### 2. 提供反馈

```bash
curl -X POST http://localhost:8000/api/team-chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@TestCase_Generator 请添加边界测试用例",
    "conversation_id": "team_session_abc123",
    "is_feedback": true
  }'
```

### 3. 同意并结束

```bash
curl -X POST http://localhost:8000/api/team-chat/stream \
  -H "Content-Type": application/json" \
  -d '{
    "message": "同意",
    "conversation_id": "team_session_abc123",
    "is_feedback": true
  }'
```

响应：
```
data: {"type":"done","content":"用户已同意，对话结束"}
data: [DONE]
```

## 测试场景

### 场景 1：正常反馈流程
1. 用户发送需求
2. Generator 生成测试用例
3. Reviewer 评审 → 等待反馈
4. 用户提供反馈
5. Generator 修改 → Reviewer 再次评审 → 等待反馈
6. 用户同意 → 结束

### 场景 2：指定智能体
1. 用户发送需求
2. Generator → Reviewer → 等待反馈
3. 用户输入 "@TestCase_Optimizer 请优化性能测试用例"
4. Optimizer 回答 → 等待反馈
5. 用户同意 → 结束

### 场景 3：直接同意
1. 用户发送需求
2. Generator → Reviewer → 等待反馈
3. 用户点击"同意"或输入"同意" → 结束

## 注意事项

1. **会话超时**: 团队实例缓存在内存中，需要定期清理过期会话
2. **并发问题**: 当前实现使用全局字典缓存，生产环境应使用 Redis
3. **错误处理**: 需要处理团队实例丢失、会话不存在等异常情况
4. **@ 语法**: 前端需要提供智能体名称的自动补全

## 下一步

1. ✅ 后端实现完成
2. ⏳ 前端实现待完成：
   - 检测待反馈消息
   - 发送反馈请求
   - 添加"同意"按钮
   - @ 智能体自动补全
   - 显示 conversation_id

