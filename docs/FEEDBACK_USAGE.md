# 智能体反馈功能使用指南

## 功能概述

智能体反馈功能允许用户在 `TestCase_Reviewer` 或 `TestCase_Optimizer` 完成工作后，提供反馈并指定特定智能体继续对话，或者直接同意结束对话。

## 使用场景

### 场景 1：正常工作流程

1. **用户发送需求**
   ```
   用户: "生成登录功能的测试用例"
   ```

2. **智能体自动协作**
   ```
   Generator → 生成测试用例
   Reviewer → 评审测试用例
   [等待用户反馈]
   ```

3. **前端显示反馈对话框**
   - 显示提示信息
   - 显示可用智能体列表
   - 显示"同意"按钮

4. **用户选择操作**
   - **选项 A**: 点击"同意"按钮 → 结束对话
   - **选项 B**: 输入反馈内容 → 继续对话

### 场景 2：提供反馈并继续

用户输入反馈：
```
"请添加更多边界测试用例"
```

系统行为：
- Generator 继续工作（默认轮询顺序）
- 生成新的测试用例
- Reviewer 再次评审
- [再次等待用户反馈]

### 场景 3：指定智能体回答

用户输入反馈并 @ 提及智能体：
```
"@TestCase_Optimizer 请优化性能测试用例"
```

系统行为：
- Optimizer 接收反馈并工作
- 优化测试用例
- [等待用户反馈]

### 场景 4：直接同意

用户点击"同意"按钮或输入"同意"：
```
"同意"
```

系统行为：
- 结束对话
- 清理团队实例
- 显示"用户已同意，对话结束"

## 前端界面

### 反馈对话框

当智能体完成工作后，会在消息下方显示反馈对话框：

```
┌─────────────────────────────────────────┐
│ 💬 测试用例评审员 已完成，请提供反馈      │
├─────────────────────────────────────────┤
│ • 直接点击"同意"或留空发送，将结束智能体协作 │
│ • 输入反馈内容，可以使用 @智能体名称 指定回复的智能体 │
│ • 可用智能体：@TestCase_Generator, @TestCase_Reviewer, @TestCase_Optimizer │
│                                         │
│                        [✅ 同意]         │
└─────────────────────────────────────────┘
```

### @ 智能体语法

支持以下智能体名称：
- `@TestCase_Generator` - 测试用例生成器
- `@TestCase_Reviewer` - 测试用例评审员
- `@TestCase_Optimizer` - 测试用例优化器

示例：
```
@TestCase_Generator 请添加异常处理的测试用例
@TestCase_Reviewer 请重新评审边界条件
@TestCase_Optimizer 请优化测试用例的可读性
```

## API 使用

### 1. 新对话

**请求**:
```bash
POST /api/team-chat/stream
Content-Type: application/json

{
  "message": "生成登录功能的测试用例"
}
```

**响应**:
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

**响应头**:
```
X-Conversation-ID: team_session_abc123
```

### 2. 提供反馈

**请求**:
```bash
POST /api/team-chat/stream
Content-Type: application/json

{
  "message": "@TestCase_Generator 请添加边界测试用例",
  "conversation_id": "team_session_abc123",
  "is_feedback": true
}
```

**响应**:
```
data: {"type":"agent_start","agent_name":"TestCase_Generator",...}
data: {"type":"agent_message","content":"...",...}
...
```

### 3. 同意并结束

**请求**:
```bash
POST /api/team-chat/stream
Content-Type: application/json

{
  "message": "同意",
  "conversation_id": "team_session_abc123",
  "is_feedback": true
}
```

**响应**:
```
data: {"type":"done","content":"用户已同意，对话结束"}
data: [DONE]
```

## 技术实现

### 后端

1. **会话管理**: 使用 `TeamSessionService` 管理对话状态
2. **团队缓存**: 使用全局字典缓存团队实例
3. **终止条件**: 在 Reviewer/Optimizer 完成后停止
4. **反馈检测**: 检测 `is_feedback` 标志并恢复团队

### 前端

1. **反馈检测**: 检测消息中的 `feedbackRequest` 字段
2. **会话保持**: 保存 `conversationId` 并在反馈时发送
3. **@ 解析**: 使用正则表达式提取目标智能体
4. **UI 交互**: 显示反馈对话框和"同意"按钮

## 测试

### 使用测试脚本

```bash
./test_feedback_flow.sh
```

### 手动测试

1. 启动服务：
   ```bash
   ./start.sh
   ```

2. 打开前端：
   ```bash
   cd frontend
   npm run dev
   ```

3. 测试流程：
   - 切换到"智能体团队"模式
   - 发送测试需求
   - 等待反馈对话框出现
   - 尝试不同的反馈方式

## 注意事项

1. **会话超时**: 团队实例缓存在内存中，长时间不活动可能被清理
2. **并发限制**: 当前实现使用全局字典，不支持分布式部署
3. **错误恢复**: 如果团队实例丢失，需要重新开始对话
4. **@ 语法**: 必须使用完整的智能体名称，如 `@TestCase_Generator`

## 常见问题

### Q: 为什么我的反馈没有生效？

A: 检查以下几点：
- 是否在反馈对话框出现后发送的消息
- `conversation_id` 是否正确
- 是否设置了 `is_feedback: true`

### Q: 如何指定特定智能体回答？

A: 在消息中使用 @ 语法，例如：
```
@TestCase_Generator 请添加更多测试用例
```

### Q: 点击"同意"后还能继续对话吗？

A: 不能。点击"同意"会结束对话并清理团队实例。如果需要继续，请重新开始对话。

### Q: 支持多轮反馈吗？

A: 支持。每次智能体完成后都会等待反馈，可以进行多轮反馈直到用户同意。

## 未来改进

1. **会话持久化**: 使用 Redis 存储会话状态
2. **超时清理**: 自动清理过期的团队实例
3. **智能体选择器**: 提供下拉菜单选择智能体
4. **反馈历史**: 显示之前的反馈记录
5. **快捷回复**: 提供常用反馈模板

