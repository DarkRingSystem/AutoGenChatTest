
# Team Agent 业务沟通完整执行流程

## 📋 目录

1. [概述](#概述)
2. [场景一：首次对话](#场景一首次对话)
3. [场景二：用户同意方案](#场景二用户同意方案)
4. [场景三：用户提供反馈（无@提及）](#场景三用户提供反馈无提及)
5. [场景四：用户提供反馈（@特定智能体）](#场景四用户提供反馈特定智能体)
6. [场景五：用户提供反馈（@all）](#场景五用户提供反馈all)
7. [关键数据结构](#关键数据结构)
8. [核心服务类](#核心服务类)

---

## 概述

### 系统架构

```
┌─────────────┐         ┌─────────────┐         ┌─────────────────────┐
│   前端 UI   │ ◄─SSE─► │  后端 API   │ ◄────► │  AutoGen 智能体团队  │
│  (React)    │         │  (FastAPI)  │         │  (RoundRobinGroup)  │
└─────────────┘         └─────────────┘         └─────────────────────┘
      │                       │                           │
      │                       │                           │
      ▼                       ▼                           ▼
 用户交互层              路由 & 会话管理              智能体协作层
```

### 三个智能体角色

1. **TestCase_Generator** 🎯 - 测试用例生成专家
2. **TestCase_Reviewer** 🔍 - 测试用例评审专家
3. **TestCase_Optimizer** ⚡ - 测试用例优化专家

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

## 场景一：首次对话

### 用户操作
用户在前端输入："生成支付接口的测试用例"，点击发送。

### 1. 前端处理 (App.jsx)

#### 1.1 用户点击发送按钮
```javascript
// 文件: frontend/src/App.jsx, 行: ~180
const handleSend = async () => {
  if (!inputValue.trim() && uploadedFiles.length === 0) return;
  
  const userMessage = inputValue.trim();
  setInputValue('');
  
  // 调用流式聊天处理
  await handleStreamingChat(userMessage);
};
```

#### 1.2 准备请求数据
```javascript
// 文件: frontend/src/App.jsx, 行: ~200-240
const handleStreamingChat = async (userMessage, manualFeedback = null) => {
  // 获取文件 ID
  const fileIds = uploadedFiles.map(f => f.file_id);
  
  // 检查是否为反馈消息（首次对话为 false）
  let isFeedback = false;
  let conversationId = null;
  let targetAgent = null;
  
  // 添加用户消息到 UI
  const userMsg = {
    id: Date.now(),
    role: 'user',
    content: userMessage,
    timestamp: new Date().toISOString(),
    hasFiles: fileIds.length > 0,
    fileCount: fileIds.length,
  };
  setMessages(prev => [...prev, userMsg]);
  
  // 创建助手消息占位符
  const assistantMsg = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    streaming: true,
    isTeamMode: true,  // 团队模式
    agents: [],        // 智能体列表
  };
  setMessages(prev => [...prev, assistantMsg]);
```

#### 1.3 发送 HTTP 请求
```javascript
// 文件: frontend/src/App.jsx, 行: ~258-276
const endpoint = `${API_BASE_URL}/api/team-chat/stream`;

const response = await fetch(endpoint, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "生成支付接口的测试用例",
    file_ids: undefined,
    is_feedback: false,      // 首次对话
    conversation_id: null,   // 无会话 ID
    target_agent: null       // 无目标智能体
  }),
});
```

### 2. 后端处理 (routes.py)

#### 2.1 接收请求
```python
# 文件: backend/api/routes.py, 行: 245-261
@router.post("/api/team-chat/stream")
async def team_chat_stream(request: ChatRequest):
    """
    测试用例团队模式的流式聊天响应
    
    request.message = "生成支付接口的测试用例"
    request.is_feedback = False
    request.conversation_id = None
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
```

#### 2.2 导入服务
```python
# 文件: backend/api/routes.py, 行: 263-270
from services.ai_service import TestCasesTeamAIService
from services.team_stream_service import TeamStreamService
from services.team_session_service import get_team_session_service

# 获取会话服务（单例）
session_service = get_team_session_service()
```

#### 2.3 判断为新对话
```python
# 文件: backend/api/routes.py, 行: 277-399
if request.is_feedback and request.conversation_id:
    # 继续对话分支（跳过）
    pass
else:
    # ✅ 新对话分支（执行此分支）
    
    # 创建新会话
    conversation_id = session_service.create_session()
    # 返回: "team_session_a1b2c3d4e5f6g7h8"
    
    print(f"🆕 创建新对话 {conversation_id}")
```

#### 2.4 创建团队服务
```python
# 文件: backend/api/routes.py, 行: 387-392
# 创建团队服务实例
team_service = TestCasesTeamAIService(settings)
await team_service.initialize()  # 初始化 Generator + Reviewer

# 缓存团队实例（用于后续反馈）
_cache_team_service(conversation_id, team_service)
```

#### 2.5 添加用户消息到会话
```python
# 文件: backend/api/routes.py, 行: 394-397
# 添加用户消息到会话历史
session_service.add_message(
    conversation_id, 
    "user", 
    "生成支付接口的测试用例"
)

feedback_message = request.message
```

### 3. 团队服务初始化 (ai_service.py)

#### 3.1 初始化方法
```python
# 文件: backend/services/ai_service.py, 行: 163-200
async def initialize(self, specific_agent: Optional[str] = None):
    """
    specific_agent = None  # 首次对话，初始化所有智能体
    """
    # 验证配置
    self.settings.validate_config()
    
    # 创建模型客户端
    self.model_client = OpenAIChatCompletionClient(
        model=self.settings.model_name,
        api_key=self.settings.api_key,
        base_url=self.settings.base_url,
        model_info=model_info,
    )
    
    # 创建团队智能体
    self._create_team_agents(specific_agent=None)
    
    # 创建团队
    self._create_team()
```

#### 3.2 创建智能体
```python
# 文件: backend/services/ai_service.py, 行: 202-260
def _create_team_agents(self, specific_agent: Optional[str] = None):
    """
    specific_agent = None  # 创建 Generator + Reviewer
    """
    # 加载 Prompt
    test_generator_prompt = load_prompt(PromptNames.TEST_CASE_GENERATOR)
    test_reviewer_prompt = load_prompt(PromptNames.TEST_CASE_REVIEWER)
    test_optimizer_prompt = load_prompt(PromptNames.TEST_CASE_OPTIMIZER)
    
    # 创建三个智能体
    test_generator_agent = AssistantAgent(
        name="TestCase_Generator",
        model_client=self.model_client,
        system_message=test_generator_prompt,
    )
    
    test_reviewer_agent = AssistantAgent(
        name="TestCase_Reviewer",
        model_client=self.model_client,
        system_message=test_reviewer_prompt,
    )
    
    test_optimizer_agent = AssistantAgent(
        name="TestCase_Optimizer",
        model_client=self.model_client,
        system_message=test_optimizer_prompt,
    )
    
    # 根据 specific_agent 参数选择智能体
    if specific_agent == "TestCase_Generator":
        self.agents = [test_generator_agent]
    elif specific_agent == "TestCase_Reviewer":
        self.agents = [test_reviewer_agent]
    elif specific_agent == "TestCase_Optimizer":
        self.agents = [test_optimizer_agent]
    else:
        # ✅ 默认：Generator + Reviewer（不包含 Optimizer）
        self.agents = [test_generator_agent, test_reviewer_agent]
```

#### 3.3 创建团队
```python
# 文件: backend/services/ai_service.py, 行: 262-290
def _create_team(self):
    """创建 RoundRobinGroupChat 团队"""
    # 定义终止条件
    reviewer_termination = SourceMatchTermination(["TestCase_Reviewer"])
    optimizer_termination = SourceMatchTermination(["TestCase_Optimizer"])
    max_message_termination = MaxMessageTermination(max_messages=20)
    
    # 创建团队（轮询模式）
    self.team = RoundRobinGroupChat(
        participants=self.agents,  # [Generator, Reviewer]
        termination_condition=(
            reviewer_termination |      # Reviewer 完成后停止
            optimizer_termination |     # 或 Optimizer 完成后停止
            max_message_termination     # 或达到最大消息数
        ),
    )
    
    print(f"✅ 团队创建成功，包含智能体: {[agent.name for agent in self.agents]}")
```

### 4. 运行团队并流式返回 (routes.py)

#### 4.1 创建流式服务
```python
# 文件: backend/api/routes.py, 行: 401-420
# 创建流式处理服务
team_stream_service = TeamStreamService()

# 运行团队并获取事件流
event_stream = team_service.run_stream(feedback_message)
# feedback_message = "生成支付接口的测试用例"

# 处理事件流并生成 SSE 响应
sse_stream = team_stream_service.process_stream(
    event_stream, 
    feedback_message
)

# 返回 SSE 流式响应
return StreamingResponse(
    sse_stream,
    media_type="text/event-stream",
    headers={
        "X-Conversation-ID": conversation_id,  # 会话 ID
        "X-Team-Mode": "true",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
)
```

#### 4.2 团队运行流
```python
# 文件: backend/services/ai_service.py, 行: 310-320
async def run_stream(self, message: str):
    """运行团队（流式）"""
    if not self.team:
        raise RuntimeError("团队未初始化")
    
    # 调用 AutoGen 的 run_stream
    async for event in self.team.run_stream(task=message):
        yield event
```

### 5. 流式处理服务 (team_stream_service.py)

#### 5.1 处理事件流
```python
# 文件: backend/services/team_stream_service.py, 行: 30-100
async def process_stream(
    self,
    event_stream: AsyncGenerator[Any, None],
    user_message: str
) -> AsyncGenerator[str, None]:
    """处理团队事件流并生成 SSE 响应"""
    
    # 保存用户消息
    self.user_message = user_message
    
    # 发送初始状态
    yield self._create_status_message("团队协作中...")
    
    # 处理每个事件
    async for event in event_stream:
        # 解析事件
        event_dict = event.model_dump() if hasattr(event, 'model_dump') else {}
        
        # 获取智能体名称和内容
        agent_name = self._extract_agent_name(event_dict)
        content = self._extract_content(event_dict)
        
        if agent_name and content:
            # 新智能体开始回答
            if agent_name != self.current_agent:
                self.current_agent = agent_name
                self.agent_responses[agent_name] = ""
                
                # 发送智能体开始事件
                yield self._create_agent_start_message(agent_name)
            
            # 累积智能体回答
            self.agent_responses[agent_name] += content
            
            # 发送内容块
            yield self._create_content_message(agent_name, content)
```

#### 5.2 判断是否等待反馈
```python
# 文件: backend/services/team_stream_service.py, 行: 150-200
# 流结束后
if self.current_agent:
    # 发送智能体完成事件
    yield self._create_agent_end_message(self.current_agent)
    
    # 判断是否需要等待用户反馈
    if self._should_wait_for_feedback(self.current_agent):
        # ✅ Reviewer 完成，等待反馈
        self.waiting_for_feedback = True
        self.feedback_agent = self.current_agent
        
        # 发送反馈请求
        yield self._create_feedback_request_message(
            agent_name=self.current_agent,
            available_agents=[
                "TestCase_Generator",
                "TestCase_Reviewer",
                "TestCase_Optimizer"
            ]
        )
    elif self._is_final_answer(self.current_agent):
        # Optimizer 完成，这是最终答案
        yield self._create_final_answer_message()
```

#### 5.3 判断逻辑
```python
# 文件: backend/services/team_stream_service.py, 行: 250-270
def _should_wait_for_feedback(self, agent_name: str) -> bool:
    """判断是否需要等待用户反馈"""
    # 只有 Reviewer 完成后才等待反馈
    return agent_name == "TestCase_Reviewer"

def _is_final_answer(self, agent_name: str) -> bool:
    """判断是否为最终答案"""
    # 只有 Optimizer 的回答才是最终答案
    return agent_name == "TestCase_Optimizer"
```

### 6. 前端接收 SSE 流 (App.jsx)

#### 6.1 读取响应头
```javascript
// 文件: frontend/src/App.jsx, 行: 282-284
// 从响应头中获取 conversation_id
const responseConversationId = response.headers.get('X-Conversation-ID');
console.log('📨 responseConversationId:', responseConversationId);
// 输出: "team_session_a1b2c3d4e5f6g7h8"
```

#### 6.2 解析 SSE 事件
```javascript
// 文件: frontend/src/App.jsx, 行: 286-350
const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split('\n');
  buffer = lines.pop() || '';
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      // 处理不同类型的事件
      switch (data.type) {
        case 'agent_start':
          // 智能体开始回答
          handleAgentStart(data);
          break;
          
        case 'content':
          // 内容块
          handleContent(data);
          break;
          
        case 'agent_end':
          // 智能体完成
          handleAgentEnd(data);
          break;
          
        case 'feedback_request':
          // ✅ 反馈请求（Reviewer 完成）
          handleFeedbackRequest(data, responseConversationId);
          break;
          
        case 'final_answer':
          // 最终答案（Optimizer 完成）
          handleFinalAnswer(data);
          break;
      }
    }
  }
}
```

#### 6.3 处理反馈请求
```javascript
// 文件: frontend/src/App.jsx, 行: ~330-350
case 'feedback_request':
  console.log('📨 收到 feedback_request');
  console.log('📨 responseConversationId:', responseConversationId);
  
  // 更新消息，添加反馈请求标记
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
            conversationId: responseConversationId  // 保存会话 ID
          }
        : msg
    )
  );
  
  console.log('⏸️ 等待用户反馈，会话 ID:', responseConversationId);
  break;
```

### 7. 前端显示反馈对话框 (App.jsx)

```javascript
// 文件: frontend/src/App.jsx, 行: ~1050-1120
{msg.feedbackRequest && (
  <div className="feedback-dialog">
    <div className="feedback-header">
      <span className="feedback-icon">💬</span>
      <span className="feedback-title">
        {msg.feedbackRequest.agentName} 已完成，请提供反馈
      </span>
    </div>
    
    <div className="feedback-hint">
      <p>• 直接点击"同意"，Optimizer 将给出最终优化方案</p>
      <p>• 点击下方智能体标签，指定特定智能体回答</p>
      <p>• 点击"All"，重新运行 Generator → Reviewer 流程</p>
    </div>
    
    {/* 智能体标签选择器 */}
    <div className="agent-tags-container">
      <div className="agent-tags-label">选择智能体：</div>
      <div className="agent-tags">
        <button onClick={() => handleAgentTagClick('all')}>
          🔄 All
        </button>
        <button onClick={() => handleAgentTagClick('TestCase_Generator')}>
          🎯 Generator
        </button>
        <button onClick={() => handleAgentTagClick('TestCase_Reviewer')}>
          🔍 Reviewer
        </button>
        <button onClick={() => handleAgentTagClick('TestCase_Optimizer')}>
          ⚡ Optimizer
        </button>
      </div>
    </div>
    
    <div className="feedback-actions">
      <button onClick={() => handleApprove(msg.id)}>
        ✅ 同意
      </button>
    </div>
  </div>
)}
```

### 8. 执行流程总结

```
1. 用户输入 "生成支付接口的测试用例"
   ↓
2. 前端发送 POST /api/team-chat/stream
   {
     message: "生成支付接口的测试用例",
     is_feedback: false,
     conversation_id: null
   }
   ↓
3. 后端创建新会话 "team_session_xxx"
   ↓
4. 后端初始化团队服务（Generator + Reviewer）
   ↓
5. 后端运行团队，Generator 开始生成测试用例
   ↓
6. 前端接收 SSE 事件：
   - agent_start: TestCase_Generator
   - content: [生成的测试用例内容...]
   - agent_end: TestCase_Generator
   ↓
7. Reviewer 开始评审
   ↓
8. 前端接收 SSE 事件：
   - agent_start: TestCase_Reviewer
   - content: [评审意见...]
   - agent_end: TestCase_Reviewer
   ↓
9. 后端发送 feedback_request 事件
   ↓
10. 前端显示反馈对话框，等待用户操作
```

---

## 场景二：用户同意方案

### 用户操作
用户点击"同意"按钮。

### 1. 前端处理

#### 1.1 点击同意按钮
```javascript
// 文件: frontend/src/App.jsx, 行: ~480-495
const handleApprove = async (messageId) => {
  console.log('🟢 用户点击同意');
  
  // 找到待反馈的消息
  const message = messages.find(msg => msg.id === messageId);
  const conversationId = message.conversationId;
  
  console.log('🟢 会话 ID:', conversationId);
  
  // 调用流式聊天，传递手动反馈信息
  await handleStreamingChat('同意', {
    isFeedback: true,
    conversationId: conversationId,
    targetAgent: null  // 同意时不指定智能体
  });
};
```

#### 1.2 发送请求
```javascript
// 文件: frontend/src/App.jsx, 行: ~268-274
body: JSON.stringify({
  message: "同意",
  is_feedback: true,                    // ✅ 反馈消息
  conversation_id: "team_session_xxx",  // ✅ 会话 ID
  target_agent: null                    // ✅ 无目标智能体
}),
```

### 2. 后端处理

#### 2.1 判断为继续对话
```python
# 文件: backend/api/routes.py, 行: 278-286
if request.is_feedback and request.conversation_id:
    # ✅ 继续对话分支
    
    # 获取会话
    session = session_service.get_session(request.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    if not session.waiting_for_feedback:
        raise HTTPException(status_code=400, detail="当前会话不在等待反馈状态")
```

#### 2.2 判断用户同意
```python
# 文件: backend/api/routes.py, 行: 287-324
# 检查用户是否同意
is_user_approved = (
    not request.message.strip() or 
    "同意" in request.message or 
    "APPROVE" in request.message.upper()
)

if is_user_approved:
    # ✅ 用户同意分支
    
    conversation_id = request.conversation_id
    
    # 清理旧的团队实例
    old_team_service = _get_cached_team_service(conversation_id)
    if old_team_service:
        await old_team_service.cleanup()
        _remove_cached_team_service(conversation_id)
    
    # 添加用户同意到会话
    session_service.add_message(conversation_id, "user", "同意")
    
    # 获取对话历史
    history = session_service.get_conversation_history(conversation_id)
    # 返回: [
    #   {"role": "user", "content": "生成支付接口的测试用例"},
    #   {"role": "TestCase_Generator", "content": "[生成的测试用例]"},
    #   {"role": "TestCase_Reviewer", "content": "[评审意见]"},
    #   {"role": "user", "content": "同意"}
    # ]
```

#### 2.3 构建 Optimizer 消息
```python
# 文件: backend/api/routes.py, 行: 306-312
# 构建给 Optimizer 的消息
history_text = "\n\n".join([
    f"{'用户' if msg['role'] == 'user' else msg['role']}: {msg['content']}"
    for msg in history[:-1]  # 排除最后一条（"同意"）
])

optimizer_message = f"""对话历史：
{history_text}

用户已同意以上方案。请作为测试用例优化器，结合生成器和评审员的意见，给出最终优化的测试用例。"""
```

#### 2.4 创建只包含 Optimizer 的团队
```python
# 文件: backend/api/routes.py, 行: 314-324
# 创建新的团队实例（只包含 Optimizer）
team_service = TestCasesTeamAIService(settings)
await team_service.initialize(specific_agent="TestCase_Optimizer")
# 这次只初始化 Optimizer 智能体

# 缓存团队实例
_cache_team_service(conversation_id, team_service)

# 设置为最终回答模式
feedback_message = optimizer_message

print(f"✅ 用户同意，调用 Optimizer 给出最终回答")
```

### 3. Optimizer 运行

#### 3.1 团队初始化
```python
# 文件: backend/services/ai_service.py, 行: 202-260
def _create_team_agents(self, specific_agent: Optional[str] = None):
    """
    specific_agent = "TestCase_Optimizer"  # ✅ 只创建 Optimizer
    """
    # ... 创建三个智能体 ...
    
    if specific_agent == "TestCase_Optimizer":
        # ✅ 只包含 Optimizer
        self.agents = [test_optimizer_agent]
```

#### 3.2 Optimizer 生成最终答案
```python
# Optimizer 接收到的消息：
"""
对话历史：
用户: 生成支付接口的测试用例
TestCase_Generator: [生成的测试用例]
TestCase_Reviewer: [评审意见]

用户已同意以上方案。请作为测试用例优化器，结合生成器和评审员的意见，给出最终优化的测试用例。
"""

# Optimizer 根据历史生成最终优化的测试用例
```

### 4. 流式返回最终答案

#### 4.1 后端发送 SSE 事件
```python
# 文件: backend/services/team_stream_service.py, 行: ~150-200
# Optimizer 完成后
if self._is_final_answer(self.current_agent):
    # ✅ 这是最终答案
    yield self._create_final_answer_message()
```

#### 4.2 前端接收最终答案
```javascript
// 文件: frontend/src/App.jsx, 行: ~350-360
case 'final_answer':
  console.log('🎉 收到最终答案');
  
  // 更新消息，标记为完成
  setMessages(prev =>
    prev.map(msg =>
      msg.id === assistantMsgId
        ? { ...msg, streaming: false, isFinalAnswer: true }
        : msg
    )
  );
  break;
```

### 5. 执行流程总结

```
1. 用户点击"同意"按钮
   ↓
2. 前端发送 POST /api/team-chat/stream
   {
     message: "同意",
     is_feedback: true,
     conversation_id: "team_session_xxx"
   }
   ↓
3. 后端判断为用户同意
   ↓
4. 后端获取对话历史
   ↓
5. 后端构建 Optimizer 消息（包含完整历史）
   ↓
6. 后端创建只包含 Optimizer 的团队
   ↓
7. Optimizer 运行，生成最终优化的测试用例
   ↓
8. 前端接收 SSE 事件：
   - agent_start: TestCase_Optimizer
   - content: [最终优化的测试用例...]
   - agent_end: TestCase_Optimizer
   - final_answer: 标记为最终答案
   ↓
9. 对话结束
```

---

## 场景三：用户提供反馈（无@提及）

### 用户操作
用户在输入框输入："请添加边界测试用例"，点击发送。

### 1. 前端处理

#### 1.1 检测反馈消息
```javascript
// 文件: frontend/src/App.jsx, 行: ~212-218
// 自动检测反馈消息
const pendingFeedbackMessage = messages.find(msg => msg.feedbackRequest);
isFeedback = !!pendingFeedbackMessage;  // ✅ true
conversationId = pendingFeedbackMessage?.conversationId;  // ✅ "team_session_xxx"
targetAgent = isFeedback ? parseTargetAgent(userMessage) : null;  // ✅ null（无@提及）

console.log('🔵 自动检测反馈信息:', { isFeedback, conversationId, targetAgent });
```

#### 1.2 发送请求
```javascript
body: JSON.stringify({
  message: "请添加边界测试用例",
  is_feedback: true,                    // ✅ 反馈消息
  conversation_id: "team_session_xxx",  // ✅ 会话 ID
  target_agent: null                    // ✅ 无目标智能体
}),
```

### 2. 后端处理

#### 2.1 判断为用户反馈（无@提及）
```python
# 文件: backend/api/routes.py, 行: 327-378
else:
    # 用户提供了反馈（不是同意）
    
    conversation_id = request.conversation_id
    
    # 清理旧的团队实例
    old_team_service = _get_cached_team_service(conversation_id)
    if old_team_service:
        await old_team_service.cleanup()
        _remove_cached_team_service(conversation_id)
    
    # 添加用户反馈到会话
    session_service.add_message(conversation_id, "user", request.message)
    
    # 解析目标智能体
    target_agent = _parse_target_agent(request.message)
    # 返回: None（无@提及）
```

#### 2.2 构建反馈消息
```python
# 文件: backend/api/routes.py, 行: 343-378
# 获取对话历史
history = session_service.get_conversation_history(conversation_id)

# 构建包含历史的消息
history_text = "\n\n".join([
    f"{'用户' if msg['role'] == 'user' else msg['role']}: {msg['content']}"
    for msg in history[:-1]  # 排除最后一条（当前反馈）
])

if target_agent:
    # 有@提及（跳过）
    pass
else:
    # ✅ 无@提及，重复 Generator → Reviewer 流程
    
    feedback_message = f"""对话历史：
{history_text}

用户反馈: 请添加边界测试用例"""
    
    # 创建新的团队服务实例（Generator → Reviewer）
    team_service = TestCasesTeamAIService(settings)
    await team_service.initialize()  # 默认包含 Generator 和 Reviewer
    
    print(f"📝 继续对话 {conversation_id}，重复 Generator → Reviewer 流程")
```

### 3. 重新运行 Generator → Reviewer

流程与场景一相同，但消息包含完整的对话历史：

```
Generator 接收到的消息：
"""
对话历史：
用户: 生成支付接口的测试用例
TestCase_Generator: [第一次生成的测试用例]
TestCase_Reviewer: [第一次评审意见]

用户反馈: 请添加边界测试用例
"""

Generator 根据历史和反馈，重新生成测试用例
↓
Reviewer 评审新的测试用例
↓
再次等待用户反馈
```

---

## 场景四：用户提供反馈（@特定智能体）

### 用户操作
用户点击 Generator 标签，输入框显示："@TestCase_Generator 请添加性能测试"，点击发送。

### 1. 前端处理

#### 1.1 解析目标智能体
```javascript
// 文件: frontend/src/App.jsx, 行: ~150-165
const parseTargetAgent = (message) => {
  const match = message.match(/@(TestCase_\w+)/);
  if (match) {
    return match[1];  // ✅ "TestCase_Generator"
  }
  return null;
};

// 检测反馈消息
targetAgent = parseTargetAgent("@TestCase_Generator 请添加性能测试");
// 返回: "TestCase_Generator"
```

#### 1.2 发送请求
```javascript
body: JSON.stringify({
  message: "@TestCase_Generator 请添加性能测试",
  is_feedback: true,
  conversation_id: "team_session_xxx",
  target_agent: "TestCase_Generator"  // ✅ 指定智能体
}),
```

### 2. 后端处理

#### 2.1 解析目标智能体
```python
# 文件: backend/api/routes.py, 行: 340-369
# 解析目标智能体
target_agent = _parse_target_agent(request.message)
# 返回: "TestCase_Generator"

print(f"🎯 检测到目标智能体: {target_agent}")

# 构建反馈消息
if target_agent:
    # ✅ 用户指定了特定智能体
    
    feedback_message = f"""对话历史：
{history_text}

用户反馈（@{target_agent}）: @TestCase_Generator 请添加性能测试"""
    
    # 创建新的团队服务实例（只包含指定的智能体）
    team_service = TestCasesTeamAIService(settings)
    await team_service.initialize(specific_agent=target_agent)
    # 只初始化 Generator
    
    print(f"🎯 继续对话 {conversation_id}，指定智能体: {target_agent}")
```

### 3. 只运行 Generator

```python
# 团队初始化
def _create_team_agents(self, specific_agent="TestCase_Generator"):
    # ✅ 只包含 Generator
    self.agents = [test_generator_agent]

# Generator 接收到的消息：
"""
对话历史：
用户: 生成支付接口的测试用例
TestCase_Generator: [第一次生成的测试用例]
TestCase_Reviewer: [第一次评审意见]

用户反馈（@TestCase_Generator）: @TestCase_Generator 请添加性能测试
"""

# Generator 根据历史和反馈，生成包含性能测试的用例
```

### 4. 流式返回

```
前端接收 SSE 事件：
- agent_start: TestCase_Generator
- content: [包含性能测试的测试用例...]
- agent_end: TestCase_Generator
- feedback_request: 再次等待用户反馈
```

---

## 场景五：用户提供反馈（@all）

### 用户操作
用户点击 All 标签，输入框显示："@all 重新生成"，点击发送。

### 1. 前端处理

```javascript
// 解析目标智能体
targetAgent = parseTargetAgent("@all 重新生成");
// 返回: null（前端不解析 @all）

// 发送请求
body: JSON.stringify({
  message: "@all 重新生成",
  is_feedback: true,
  conversation_id: "team_session_xxx",
  target_agent: null
}),
```

### 2. 后端处理

#### 2.1 解析 @all
```python
# 文件: backend/api/routes.py, 行: 46-72
def _parse_target_agent(message: str) -> Optional[str]:
    """解析消息中的目标智能体"""
    
    # 先匹配 @all（不区分大小写）
    if re.search(r'@all\b', message, re.IGNORECASE):
        print(f"🔄 检测到 @all，将重新运行 Generator → Reviewer 流程")
        return "all"  # ✅ 返回 "all"
    
    # 匹配 @智能体名称
    match = re.search(r'@(TestCase_\w+)', message)
    if match:
        agent_name = match[1]
        print(f"🎯 检测到目标智能体: {agent_name}")
        return agent_name
    
    return None
```

#### 2.2 处理 @all
```python
# 文件: backend/api/routes.py, 行: 352-360
if target_agent == "all":
    # ✅ 用户选择 @all，重新运行 Generator → Reviewer 流程
    
    feedback_message = f"""对话历史：
{history_text}

用户反馈（@all）: @all 重新生成"""
    
    # 创建新的团队服务实例（Generator → Reviewer）
    team_service = TestCasesTeamAIService(settings)
    await team_service.initialize()  # 默认包含 Generator 和 Reviewer
    
    print(f"🔄 继续对话 {conversation_id}，@all 重新运行 Generator → Reviewer 流程")
```

### 3. 重新运行完整流程

与场景三相同，重新运行 Generator → Reviewer 流程。

---

## 关键数据结构

### 1. ChatRequest（请求模型）
```python
# 文件: backend/models.py
class ChatRequest(BaseModel):
    message: str                          # 用户消息
    file_ids: Optional[List[str]] = None  # 文件 ID 列表
    is_feedback: bool = False             # 是否为反馈消息
    conversation_id: Optional[str] = None # 会话 ID
    target_agent: Optional[str] = None    # 目标智能体
```

### 2. TeamSession（会话模型）
```python
# 文件: backend/services/team_session_service.py
@dataclass
class TeamSession:
    session_id: str                       # 会话 ID
    messages: List[TeamMessage]           # 消息列表
    waiting_for_feedback: bool            # 是否等待反馈
    last_agent: Optional[str]             # 最后一个智能体
    created_at: datetime                  # 创建时间
    updated_at: datetime                  # 更新时间
```

### 3. SSE 事件类型
```python
# 文件: backend/services/team_stream_service.py
SSE_EVENT_TYPES = {
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

## 核心服务类

### 1. TestCasesTeamAIService
- **职责**：管理智能体团队的生命周期
- **关键方法**：
  - `initialize(specific_agent)`: 初始化团队
  - `_create_team_agents(specific_agent)`: 创建智能体
  - `_create_team()`: 创建 RoundRobinGroupChat
  - `run_stream(message)`: 运行团队并返回事件流

### 2. TeamStreamService
- **职责**：处理团队事件流，生成 SSE 响应
- **关键方法**：
  - `process_stream(event_stream, user_message)`: 处理事件流
  - `_should_wait_for_feedback(agent_name)`: 判断是否等待反馈
  - `_is_final_answer(agent_name)`: 判断是否为最终答案
  - `_create_feedback_request_message()`: 创建反馈请求

### 3. TeamSessionService
- **职责**：管理会话历史和状态
- **关键方法**：
  - `create_session()`: 创建新会话
  - `get_session(session_id)`: 获取会话
  - `add_message(session_id, role, content)`: 添加消息
  - `get_conversation_history(session_id)`: 获取对话历史
  - `set_waiting_for_feedback(session_id, waiting)`: 设置等待反馈状态

---

## 总结

整个 Team Agent 业务沟通流程的核心要点：

1. **会话管理**：通过 `conversation_id` 维护对话上下文
2. **智能体协作**：Generator → Reviewer → Optimizer 的流水线
3. **反馈机制**：Reviewer 完成后等待用户反馈
4. **灵活控制**：支持同意、无@反馈、@特定智能体、@all 四种模式
5. **流式响应**：使用 SSE 实时推送智能体回答
6. **历史传递**：每次运行都包含完整的对话历史
7. **团队重建**：每次反馈都创建新的团队实例，确保状态清晰

这个设计既保证了智能体协作的灵活性，又给予用户充分的控制权，实现了人机协作的最佳实践。

---

## 附录 A：完整的代码调用链

### 场景一：首次对话的完整调用链

```
用户点击发送
  ↓
frontend/src/App.jsx:handleSend()
  ↓
frontend/src/App.jsx:handleStreamingChat(userMessage)
  ↓
fetch('http://localhost:8000/api/team-chat/stream', {
  method: 'POST',
  body: JSON.stringify({
    message: "生成支付接口的测试用例",
    is_feedback: false,
    conversation_id: null
  })
})
  ↓
backend/api/routes.py:team_chat_stream(request)
  ↓
backend/services/team_session_service.py:create_session()
  → 返回: "team_session_xxx"
  ↓
backend/services/ai_service.py:TestCasesTeamAIService.__init__(settings)
  ↓
backend/services/ai_service.py:TestCasesTeamAIService.initialize()
  ↓
backend/services/ai_service.py:_create_team_agents(specific_agent=None)
  → 创建: [Generator, Reviewer]
  ↓
backend/services/ai_service.py:_create_team()
  → 创建: RoundRobinGroupChat([Generator, Reviewer])
  ↓
backend/api/routes.py:_cache_team_service(conversation_id, team_service)
  ↓
backend/services/team_session_service.py:add_message(conversation_id, "user", message)
  ↓
backend/services/ai_service.py:run_stream(message)
  ↓
autogen_agentchat.teams.RoundRobinGroupChat:run_stream(task=message)
  → 生成事件流
  ↓
backend/services/team_stream_service.py:TeamStreamService.process_stream(event_stream, user_message)
  ↓
  ├─ Generator 开始
  │   ↓
  │   backend/services/team_stream_service.py:_create_agent_start_message("TestCase_Generator")
  │   → yield "data: {type: 'agent_start', agent_name: 'TestCase_Generator'}\n\n"
  │   ↓
  │   backend/services/team_stream_service.py:_create_content_message("TestCase_Generator", content)
  │   → yield "data: {type: 'content', agent_name: 'TestCase_Generator', content: '...'}\n\n"
  │   ↓
  │   backend/services/team_stream_service.py:_create_agent_end_message("TestCase_Generator")
  │   → yield "data: {type: 'agent_end', agent_name: 'TestCase_Generator'}\n\n"
  │
  ├─ Reviewer 开始
  │   ↓
  │   backend/services/team_stream_service.py:_create_agent_start_message("TestCase_Reviewer")
  │   → yield "data: {type: 'agent_start', agent_name: 'TestCase_Reviewer'}\n\n"
  │   ↓
  │   backend/services/team_stream_service.py:_create_content_message("TestCase_Reviewer", content)
  │   → yield "data: {type: 'content', agent_name: 'TestCase_Reviewer', content: '...'}\n\n"
  │   ↓
  │   backend/services/team_stream_service.py:_create_agent_end_message("TestCase_Reviewer")
  │   → yield "data: {type: 'agent_end', agent_name: 'TestCase_Reviewer'}\n\n"
  │
  └─ 判断是否等待反馈
      ↓
      backend/services/team_stream_service.py:_should_wait_for_feedback("TestCase_Reviewer")
      → 返回: True
      ↓
      backend/services/team_stream_service.py:_create_feedback_request_message()
      → yield "data: {type: 'feedback_request', agent_name: 'TestCase_Reviewer', available_agents: [...]}\n\n"
  ↓
backend/api/routes.py:StreamingResponse(sse_stream, headers={'X-Conversation-ID': conversation_id})
  ↓
前端接收 SSE 流
  ↓
frontend/src/App.jsx:response.headers.get('X-Conversation-ID')
  → 保存: conversationId = "team_session_xxx"
  ↓
frontend/src/App.jsx:reader.read()
  → 解析 SSE 事件
  ↓
  ├─ case 'agent_start': 创建智能体卡片
  ├─ case 'content': 累积内容
  ├─ case 'agent_end': 标记智能体完成
  └─ case 'feedback_request': 显示反馈对话框
      ↓
      setMessages(prev => prev.map(msg => ({
        ...msg,
        feedbackRequest: { agentName, availableAgents },
        conversationId: "team_session_xxx"
      })))
  ↓
前端渲染反馈对话框
  ↓
等待用户操作
```

---

## 附录 B：会话历史的演变

### 示例：完整对话的会话历史

```python
# 第一轮：用户首次提问
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例")
]

# Generator 回答后
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]")
]

# Reviewer 回答后
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]")
]

# 用户提供反馈
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]"),
    TeamMessage(role="user", content="请添加边界测试")
]

# Generator 重新生成
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]"),
    TeamMessage(role="user", content="请添加边界测试"),
    TeamMessage(role="TestCase_Generator", content="[包含边界测试的用例...]")
]

# Reviewer 重新评审
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]"),
    TeamMessage(role="user", content="请添加边界测试"),
    TeamMessage(role="TestCase_Generator", content="[包含边界测试的用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[新的评审意见...]")
]

# 用户同意
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]"),
    TeamMessage(role="user", content="请添加边界测试"),
    TeamMessage(role="TestCase_Generator", content="[包含边界测试的用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[新的评审意见...]"),
    TeamMessage(role="user", content="同意")
]

# Optimizer 给出最终答案
session.messages = [
    TeamMessage(role="user", content="生成支付接口的测试用例"),
    TeamMessage(role="TestCase_Generator", content="[生成的测试用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[评审意见...]"),
    TeamMessage(role="user", content="请添加边界测试"),
    TeamMessage(role="TestCase_Generator", content="[包含边界测试的用例...]"),
    TeamMessage(role="TestCase_Reviewer", content="[新的评审意见...]"),
    TeamMessage(role="user", content="同意"),
    TeamMessage(role="TestCase_Optimizer", content="[最终优化的测试用例...]")
]
```

---

## 附录 C：SSE 事件示例

### 完整的 SSE 事件流

```
# 1. 状态消息
data: {"type":"status","message":"团队协作中..."}

# 2. Generator 开始
data: {"type":"agent_start","agent_name":"TestCase_Generator","agent_role":"🎯 测试用例生成专家"}

# 3. Generator 内容（多次）
data: {"type":"content","agent_name":"TestCase_Generator","content":"## "}

data: {"type":"content","agent_name":"TestCase_Generator","content":"支付"}

data: {"type":"content","agent_name":"TestCase_Generator","content":"接口"}

data: {"type":"content","agent_name":"TestCase_Generator","content":"测试"}

data: {"type":"content","agent_name":"TestCase_Generator","content":"用例\n\n"}

data: {"type":"content","agent_name":"TestCase_Generator","content":"### 1. 正常支付流程\n"}

# ... 更多内容 ...

# 4. Generator 完成
data: {"type":"agent_end","agent_name":"TestCase_Generator"}

# 5. Reviewer 开始
data: {"type":"agent_start","agent_name":"TestCase_Reviewer","agent_role":"🔍 测试用例评审专家"}

# 6. Reviewer 内容（多次）
data: {"type":"content","agent_name":"TestCase_Reviewer","content":"## "}

data: {"type":"content","agent_name":"TestCase_Reviewer","content":"评审"}

data: {"type":"content","agent_name":"TestCase_Reviewer","content":"意见\n\n"}

# ... 更多内容 ...

# 7. Reviewer 完成
data: {"type":"agent_end","agent_name":"TestCase_Reviewer"}

# 8. 反馈请求
data: {"type":"feedback_request","agent_name":"TestCase_Reviewer","available_agents":["TestCase_Generator","TestCase_Reviewer","TestCase_Optimizer"],"message":"请提供反馈或点击同意"}

# 9. 完成
data: {"type":"done"}
```

---

## 附录 D：错误处理

### 常见错误和处理

#### 1. 会话不存在
```python
# 后端
if not session:
    raise HTTPException(status_code=404, detail="会话不存在")

# 前端
if (!response.ok) {
  if (response.status === 404) {
    message.error('会话已过期，请重新开始对话');
  }
}
```

#### 2. 会话不在等待反馈状态
```python
# 后端
if not session.waiting_for_feedback:
    raise HTTPException(status_code=400, detail="当前会话不在等待反馈状态")

# 前端
if (response.status === 400) {
  message.error('当前会话状态异常，请刷新页面');
}
```

#### 3. 流式传输中断
```javascript
// 前端
try {
  const { done, value } = await reader.read();
  if (done) break;
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('用户取消了请求');
  } else {
    console.error('流式传输错误:', error);
    message.error('连接中断，请重试');
  }
}
```

#### 4. 智能体运行超时
```python
# 后端
max_message_termination = MaxMessageTermination(max_messages=20)

# 如果达到最大消息数，团队会自动停止
# 前端会收到 done 事件
```

---

## 附录 E：性能优化

### 1. 团队实例缓存
```python
# 缓存团队实例，避免重复初始化
_team_service_cache: Dict[str, any] = {}

def _cache_team_service(conversation_id: str, team_service: any):
    _team_service_cache[conversation_id] = team_service

def _get_cached_team_service(conversation_id: str):
    return _team_service_cache.get(conversation_id)
```

### 2. 会话清理
```python
# 定期清理过期会话（可以添加定时任务）
def cleanup_expired_sessions(self, max_age_hours: int = 24):
    now = datetime.now()
    expired_sessions = [
        session_id
        for session_id, session in self.sessions.items()
        if (now - session.updated_at).total_seconds() > max_age_hours * 3600
    ]

    for session_id in expired_sessions:
        del self.sessions[session_id]
        _remove_cached_team_service(session_id)
```

### 3. 流式传输优化
```python
# 批量发送内容，减少网络开销
BATCH_SIZE = 10
content_buffer = []

for content_chunk in content_chunks:
    content_buffer.append(content_chunk)

    if len(content_buffer) >= BATCH_SIZE:
        yield self._create_content_message(
            agent_name,
            ''.join(content_buffer)
        )
        content_buffer = []
```

---

## 附录 F：调试技巧

### 1. 启用详细日志
```python
# 后端
import logging
logging.basicConfig(level=logging.DEBUG)

# 在关键位置添加日志
print(f"🔍 [DEBUG] 会话 ID: {conversation_id}")
print(f"🔍 [DEBUG] 是否反馈: {is_feedback}")
print(f"🔍 [DEBUG] 目标智能体: {target_agent}")
print(f"🔍 [DEBUG] 会话历史: {len(session.messages)} 条消息")
```

### 2. 前端调试
```javascript
// 启用详细日志
const DEBUG = true;

if (DEBUG) {
  console.log('🔍 [DEBUG] 发送请求:', {
    message: userMessage,
    is_feedback: isFeedback,
    conversation_id: conversationId,
    target_agent: targetAgent
  });
}

// 监控 SSE 事件
if (DEBUG) {
  console.log('📨 [SSE]', data.type, data);
}
```

### 3. 查看会话状态
```python
# 添加调试端点
@router.get("/api/debug/session/{session_id}")
async def debug_session(session_id: str):
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "session_id": session.session_id,
        "message_count": len(session.messages),
        "waiting_for_feedback": session.waiting_for_feedback,
        "last_agent": session.last_agent,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.messages
        ]
    }
```

---

## 附录 G：扩展建议

### 1. 添加更多智能体
```python
# 可以轻松添加新的智能体
security_tester_agent = AssistantAgent(
    name="Security_Tester",
    model_client=self.model_client,
    system_message=security_tester_prompt,
)

performance_tester_agent = AssistantAgent(
    name="Performance_Tester",
    model_client=self.model_client,
    system_message=performance_tester_prompt,
)

# 修改团队组成
self.agents = [
    test_generator_agent,
    test_reviewer_agent,
    security_tester_agent,
    performance_tester_agent,
    test_optimizer_agent
]
```

### 2. 支持并行执行
```python
# 使用 Swarm 模式替代 RoundRobin
from autogen_agentchat.teams import Swarm

self.team = Swarm(
    participants=self.agents,
    termination_condition=termination_condition,
)
```

### 3. 添加工具调用
```python
# 为智能体添加工具
from autogen_core.components.tools import FunctionTool

def run_test_case(test_code: str) -> str:
    """执行测试用例"""
    # 实际执行测试代码
    return "测试通过"

test_tool = FunctionTool(run_test_case, description="执行测试用例")

test_generator_agent = AssistantAgent(
    name="TestCase_Generator",
    model_client=self.model_client,
    system_message=test_generator_prompt,
    tools=[test_tool],  # 添加工具
)
```

### 4. 持久化会话
```python
# 使用数据库存储会话
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TeamSessionDB(Base):
    __tablename__ = 'team_sessions'

    session_id = Column(String, primary_key=True)
    messages = Column(Text)  # JSON 格式
    waiting_for_feedback = Column(Boolean)
    last_agent = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# 保存会话
def save_session(self, session: TeamSession):
    db_session = self.Session()
    db_session.add(TeamSessionDB(
        session_id=session.session_id,
        messages=json.dumps([msg.__dict__ for msg in session.messages]),
        waiting_for_feedback=session.waiting_for_feedback,
        last_agent=session.last_agent,
        created_at=session.created_at,
        updated_at=session.updated_at
    ))
    db_session.commit()
```

---

## 结语

这份文档详细描述了 Team Agent 业务沟通的完整执行流程，包括：

✅ **5 个完整场景**：首次对话、用户同意、无@反馈、@特定智能体、@all
✅ **完整的代码调用链**：从前端到后端的每一步
✅ **会话历史演变**：展示对话过程中数据的变化
✅ **SSE 事件示例**：实际的流式传输数据
✅ **错误处理**：常见错误和解决方案
✅ **性能优化**：缓存、清理、批量传输
✅ **调试技巧**：日志、监控、调试端点
✅ **扩展建议**：如何添加新功能

希望这份文档能帮助你深入理解整个系统的工作原理！🎉

