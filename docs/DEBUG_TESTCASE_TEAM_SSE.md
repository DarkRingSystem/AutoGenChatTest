# 测试用例智能体团队 SSE 流式传输调试指南

## 🎯 问题描述

**现象**：后端接口在输出流式响应，但前端停止继续显示

**场景**：
- 用户在"测试用例智能体团队"页面提交需求
- @TestCase_Generator 开始输出
- 前端显示一段时间后停止更新
- 后端日志显示仍在发送数据

## 🔍 调试步骤

### 1. 检查后端日志

后端已添加详细的调试日志，查看以下信息：

**事件接收日志**：
```
📨 Event #1: type=TextMessage, source=TestCase_Generator
📨 Event #2: type=ModelClientStreamingChunkEvent, source=TestCase_Generator
```

**SSE 发送日志**：
```
   ✅ Yielding TextMessage SSE for TestCase_Generator
   ✅ Yielding StreamingChunk SSE for TestCase_Generator
   📤 Sending StreamingChunk for TestCase_Generator, chunk_len=50, total_len=1500
```

**流结束日志**：
```
🔍 Stream ended. Current agent: TestCase_Generator
⏸️ Waiting for feedback from TestCase_Generator
📊 Sending token statistics
🏁 Sending [DONE] signal
```

**异常日志**：
```
❌ Error in process_stream: [error message]
[stack trace]
```

### 2. 检查前端日志

前端已添加详细的调试日志，打开浏览器开发者工具（F12），查看：

**SSE 接收日志**：
```
📦 Received 5 lines from SSE stream
📨 Parsed SSE event: agent_start TestCase_Generator
📨 Parsed SSE event: agent_message TestCase_Generator
```

**智能体状态日志**：
```
🚀 Agent started: TestCase_Generator (🎯 测试用例生成专家)
📝 Agent message: TestCase_Generator, content_len=50
   ✅ Updated TestCase_Generator content, new_len=1500
✅ Agent done: TestCase_Generator
```

**流结束日志**：
```
✅ SSE stream reader done
🏁 Received [DONE] signal
```

**异常日志**：
```
⚠️ Agent TestCase_Generator not found in agents list
❌ Error parsing SSE event: [error message]
```

### 3. 检查网络请求

在浏览器开发者工具的 **Network** 标签：

1. 找到 `/api/team-chat/stream` 请求
2. 查看状态：
   - ✅ `200 OK` - 正常
   - ❌ `cancelled` - 连接被取消
   - ❌ `failed` - 网络错误
3. 查看 **Response** 标签：
   - 是否还在接收数据？
   - 最后一条数据是什么？
4. 查看 **Timing** 标签：
   - 请求持续时间
   - 是否超时？

## 🐛 常见问题和解决方案

### 问题 1: 前端停止接收 SSE 事件

**现象**：
- 后端日志显示持续发送事件
- 前端日志显示某个时间点后不再接收

**可能原因**：
1. **浏览器连接超时**
   - 默认 SSE 连接有超时限制
   - 长时间无数据可能导致断开

2. **网络代理问题**
   - 某些代理会缓冲 SSE 响应
   - 导致数据延迟或丢失

3. **浏览器内存限制**
   - 消息内容过大
   - 浏览器限制单个响应大小

**解决方案**：
```python
# backend/services/team_stream_service.py
# 添加心跳机制
async def process_stream(self, event_stream, user_message):
    last_event_time = time.time()
    
    async for event in event_stream:
        # 处理事件...
        last_event_time = time.time()
        
        # 每 30 秒发送心跳
        if time.time() - last_event_time > 30:
            yield "data: {\"type\": \"heartbeat\"}\n\n"
            last_event_time = time.time()
```

### 问题 2: 智能体消息未找到

**现象**：
```
⚠️ Agent TestCase_Generator not found in agents list
```

**可能原因**：
- `agent_start` 事件未正确处理
- 智能体名称不匹配
- 事件顺序错误

**解决方案**：
1. 确认 `agent_start` 事件在 `agent_message` 之前发送
2. 检查智能体名称是否一致
3. 查看后端日志确认事件顺序

### 问题 3: JSON 解析错误

**现象**：
```
❌ Error parsing SSE event: Unexpected token
```

**可能原因**：
- SSE 数据被截断
- 数据格式不正确
- 特殊字符未转义

**解决方案**：
```python
# backend/models.py
def to_sse_format(self) -> str:
    """转换为 SSE 格式"""
    import json
    # 确保 JSON 正确转义
    data = json.dumps(self.dict(), ensure_ascii=False)
    return f"data: {data}\n\n"
```

### 问题 4: 状态更新不触发渲染

**现象**：
- 前端接收到事件
- 但界面不更新

**可能原因**：
- React 状态更新问题
- 引用相等性问题
- useEffect 依赖问题

**解决方案**：
```javascript
// 使用函数式更新
setMessages(prev =>
  prev.map(msg => {
    if (msg.id === assistantMsgId && msg.agents) {
      // 创建新数组，确保引用变化
      const updatedAgents = [...msg.agents];
      const agentIndex = updatedAgents.findIndex(a => a.name === parsed.agent_name);
      if (agentIndex !== -1) {
        // 创建新对象
        updatedAgents[agentIndex] = {
          ...updatedAgents[agentIndex],
          content: updatedAgents[agentIndex].content + parsed.content
        };
      }
      return { ...msg, agents: updatedAgents };
    }
    return msg;
  })
);
```

### 问题 5: 后端事件流提前结束

**现象**：
```
🔍 Stream ended. Current agent: TestCase_Generator
```

**可能原因**：
- AutoGen 事件流异常结束
- 智能体抛出异常
- 模型 API 错误

**解决方案**：
1. 查看后端完整日志
2. 检查是否有异常堆栈
3. 检查模型 API 调用是否成功

## 📊 性能监控

### 监控指标

1. **事件数量**
   - 后端发送的事件总数
   - 前端接收的事件总数
   - 是否一致？

2. **消息长度**
   - 每个智能体的消息长度
   - 是否超过限制？

3. **处理时间**
   - 从开始到结束的总时间
   - 是否超时？

4. **内存使用**
   - 浏览器内存占用
   - 是否持续增长？

### 监控代码

**后端**：
```python
# 在 process_stream 中添加
event_count = 0
start_time = time.time()

async for event in event_stream:
    event_count += 1
    # 处理事件...

end_time = time.time()
print(f"📊 Total events: {event_count}, duration: {end_time - start_time:.2f}s")
```

**前端**：
```javascript
// 在 SSE 处理循环中添加
let eventCount = 0;
const startTime = Date.now();

while (true) {
  const { done, value } = await reader.read();
  if (done) {
    const duration = (Date.now() - startTime) / 1000;
    console.log(`📊 Total events: ${eventCount}, duration: ${duration.toFixed(2)}s`);
    break;
  }
  eventCount++;
  // 处理数据...
}
```

## 🧪 测试步骤

### 1. 基础测试

1. 打开浏览器开发者工具（F12）
2. 切换到"测试用例智能体团队"模式
3. 输入简单需求："生成登录功能的测试用例"
4. 观察日志输出

**预期结果**：
- ✅ 后端持续输出事件日志
- ✅ 前端持续接收并显示消息
- ✅ 最终收到 `[DONE]` 信号

### 2. 长文本测试

1. 输入复杂需求，要求生成大量测试用例
2. 观察长时间运行的情况
3. 检查是否有中断

**预期结果**：
- ✅ 长时间运行不中断
- ✅ 消息持续更新
- ✅ 无内存泄漏

### 3. 反馈测试

1. 输入需求并等待 TestCase_Generator 完成
2. 观察是否收到反馈请求
3. 提供反馈并观察后续流程

**预期结果**：
- ✅ 收到反馈请求
- ✅ 反馈输入框显示
- ✅ 提交反馈后继续处理

## 🔧 快速修复清单

- [ ] 检查后端日志，确认事件正常发送
- [ ] 检查前端日志，确认事件正常接收
- [ ] 检查网络请求状态
- [ ] 检查智能体名称是否一致
- [ ] 检查事件顺序是否正确
- [ ] 检查 JSON 格式是否正确
- [ ] 检查是否有异常堆栈
- [ ] 检查浏览器控制台是否有错误
- [ ] 尝试刷新页面重新测试
- [ ] 尝试使用不同浏览器测试

## 📚 相关文档

- [DEBUG_SSE_ISSUE.md](DEBUG_SSE_ISSUE.md) - 图片分析 SSE 调试指南
- [README.md](../README.md) - 项目总览
- [QUICK_START.md](QUICK_START.md) - 快速开始指南

## 🆘 获取帮助

如果问题仍然存在，请提供以下信息：

1. **后端日志**：
   - 完整的事件日志
   - 异常堆栈（如果有）

2. **前端日志**：
   - 浏览器控制台完整日志
   - 最后接收的事件

3. **网络信息**：
   - Network 标签的请求详情
   - 请求状态和响应

4. **复现步骤**：
   - 输入的需求内容
   - 停止显示的时间点
   - 是否可以稳定复现

---

**祝调试顺利！** 🎉

