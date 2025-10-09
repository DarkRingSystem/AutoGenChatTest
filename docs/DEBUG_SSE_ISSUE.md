# SSE 流式传输问题调试指南

## 🐛 问题描述

**现象**：后端还在输出流式内容，但前端停止继续显示

**可能原因**：
1. 前端 SSE 连接断开
2. JavaScript 错误导致事件处理停止
3. 浏览器内存限制
4. React 状态更新问题
5. 网络超时

## 🔍 调试步骤

### 1. 检查浏览器控制台

打开浏览器开发者工具（F12），查看：

#### Console 标签
查找以下日志：
- ✅ `📨 SSE Event:` - 确认是否还在接收事件
- ✅ `📝 更新 XXX 的消息` - 确认是否在更新消息
- ❌ `❌ 解析 SSE 事件失败` - JSON 解析错误
- ❌ `⚠️ 未找到 XXX 的任何消息` - 消息查找失败
- ❌ `❌ 分析失败` - 请求失败

#### Network 标签
1. 找到 `/api/image-analysis/stream` 请求
2. 查看状态：
   - ✅ `200 OK` - 正常
   - ❌ `500 Internal Server Error` - 后端错误
   - ❌ `cancelled` - 连接被取消
3. 查看 Response：
   - 是否还在接收数据
   - 最后一条数据是什么

### 2. 检查后端日志

查看后端终端输出：
- 是否还在发送事件
- 是否有错误信息
- 最后发送的事件类型

### 3. 常见问题和解决方案

#### 问题 1: JSON 解析错误

**现象**：
```
❌ 解析 SSE 事件失败: SyntaxError: Unexpected token
   原始数据: {...
```

**原因**：
- SSE 数据被截断
- 数据格式不正确

**解决方案**：
检查后端发送的数据格式是否正确：
```python
# 正确格式
yield f"data: {json.dumps(event_dict)}\n\n"

# 错误格式（缺少 \n\n）
yield f"data: {json.dumps(event_dict)}\n"
```

#### 问题 2: 消息查找失败

**现象**：
```
⚠️ 未找到 UI_Expert 的任何消息，创建新消息
```

**原因**：
- `agent_start` 事件未正确处理
- `canDisplayRef` 状态不正确

**解决方案**：
1. 确认 `agent_start` 事件在 `agent_message` 之前发送
2. 检查 `canDisplayRef.current` 的值

#### 问题 3: React 状态更新停止

**现象**：
- 控制台显示收到事件
- 但界面不更新

**原因**：
- `setAgentMessages` 没有触发重新渲染
- 状态更新被批处理延迟

**解决方案**：
```javascript
// 使用函数式更新确保获取最新状态
setAgentMessages(prev => {
  const newMessages = [...prev];  // 创建新数组
  // ... 修改 newMessages
  return newMessages;  // 返回新数组
});
```

#### 问题 4: 浏览器内存限制

**现象**：
- 长时间运行后停止更新
- 浏览器变慢

**原因**：
- 消息内容过大
- 频繁的状态更新

**解决方案**：
1. 限制消息长度
2. 使用虚拟滚动
3. 定期清理旧消息

#### 问题 5: 网络超时

**现象**：
- Network 标签显示请求 `cancelled`
- 控制台无错误

**原因**：
- 浏览器或代理超时
- 服务器超时

**解决方案**：
1. 增加服务器超时时间：
```python
# uvicorn
uvicorn.run(app, timeout_keep_alive=300)

# gunicorn
gunicorn --timeout 300
```

2. 发送心跳保持连接：
```python
# 每 30 秒发送一次心跳
yield "data: {\"type\": \"heartbeat\"}\n\n"
```

### 4. 调试技巧

#### 技巧 1: 监控事件流

在浏览器控制台运行：
```javascript
// 监控所有 SSE 事件
const originalLog = console.log;
console.log = function(...args) {
  if (args[0]?.includes?.('SSE Event')) {
    originalLog.apply(console, ['🔍', new Date().toISOString(), ...args]);
  } else {
    originalLog.apply(console, args);
  }
};
```

#### 技巧 2: 检查状态

在浏览器控制台运行：
```javascript
// 检查当前消息数量
console.log('消息数量:', document.querySelectorAll('.agent-section').length);

// 检查最后一条消息
const lastMessage = document.querySelector('.agent-section:last-child');
console.log('最后一条消息:', lastMessage?.textContent?.slice(0, 100));
```

#### 技巧 3: 手动触发更新

在浏览器控制台运行：
```javascript
// 强制滚动到底部
window.scrollTo(0, document.body.scrollHeight);
```

### 5. 修复后的代码改进

#### 改进 1: 增强错误日志

```javascript
// 在 SSE 处理循环中
try {
  const event = JSON.parse(data);
  console.log('📨 SSE Event:', event.type, event.agent_name || '');
  handleSSEEvent(event);
} catch (e) {
  console.error('❌ 解析 SSE 事件失败:', e);
  console.error('   原始数据:', data);
}
```

#### 改进 2: 添加连接状态监控

```javascript
// 在 while 循环中
if (done) {
  console.log('✅ SSE 流读取完成');
  break;
}
```

#### 改进 3: 详细的消息更新日志

```javascript
console.log(`📨 收到 ${msgAgentName} 的消息，长度: ${content?.length || 0}`);
console.log(`📝 更新 ${msgAgentName} 的消息，内容长度: ${content?.length || 0}`);
```

## 🧪 测试步骤

### 测试 1: 基本功能测试

1. 上传一张简单的图片
2. 观察控制台日志
3. 确认所有智能体的消息都正常显示

### 测试 2: 长内容测试

1. 上传一张复杂的 UI 截图
2. 观察是否能完整显示所有内容
3. 检查是否有性能问题

### 测试 3: 网络稳定性测试

1. 开启网络限速（Chrome DevTools -> Network -> Throttling）
2. 测试在慢速网络下是否正常
3. 检查是否有超时问题

### 测试 4: 并发测试

1. 快速连续发起多次分析
2. 观察是否有状态混乱
3. 检查是否有内存泄漏

## 📊 性能监控

### 监控指标

1. **消息接收速率**
   - 每秒接收的事件数
   - 是否有延迟

2. **状态更新频率**
   - `setAgentMessages` 调用次数
   - 是否过于频繁

3. **内存使用**
   - 浏览器内存占用
   - 是否持续增长

4. **渲染性能**
   - FPS（帧率）
   - 是否有卡顿

### 性能优化建议

1. **减少状态更新频率**
```javascript
// 使用防抖
const debouncedUpdate = debounce((content) => {
  setAgentMessages(prev => {
    // ... 更新逻辑
  });
}, 100);
```

2. **使用 React.memo 优化渲染**
```javascript
const AgentMessage = React.memo(({ message }) => {
  // ... 组件逻辑
});
```

3. **虚拟滚动**
```javascript
import { FixedSizeList } from 'react-window';
```

## 🔧 快速修复清单

- [ ] 检查浏览器控制台是否有错误
- [ ] 检查 Network 标签中的请求状态
- [ ] 检查后端日志是否正常
- [ ] 确认 SSE 数据格式正确
- [ ] 确认 React 状态更新正常
- [ ] 检查是否有内存泄漏
- [ ] 测试网络稳定性
- [ ] 检查浏览器兼容性

## 📚 相关文档

- [SSE 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [React 状态更新](https://react.dev/learn/state-as-a-snapshot)
- [浏览器性能分析](https://developer.chrome.com/docs/devtools/performance/)

---

**如果问题仍然存在，请提供以下信息**：
1. 浏览器控制台的完整日志
2. Network 标签的请求详情
3. 后端日志
4. 问题复现步骤

