# 智能体反馈功能快速开始

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd /Users/darkringsystem/PycharmProjects/autogenTest
./start.sh
```

等待看到：
```
📄 Markdown 转换配置:
   使用 LLM: True
   ...

🚀 服务启动成功！
   访问地址: http://localhost:8000
   API 文档: http://localhost:8000/docs
```

### 2. 启动前端服务

打开新终端：
```bash
cd /Users/darkringsystem/PycharmProjects/autogenTest/frontend
npm run dev
```

等待看到：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. 打开浏览器

访问：http://localhost:5173/

## 📖 使用步骤

### 步骤 1：切换到智能体团队模式

1. 点击右上角的 **👥 团队** 按钮
2. 按钮变为绿色，表示已激活团队模式

### 步骤 2：发送测试需求

在输入框中输入：
```
生成一个登录功能的测试用例
```

点击发送或按 Enter。

### 步骤 3：观察智能体协作

你会看到：
```
🤖 测试用例生成器
   正在生成测试用例...
   [生成的测试用例内容]

🤖 测试用例评审员
   正在评审测试用例...
   [评审意见和建议]
```

### 步骤 4：反馈对话框出现

当评审员完成后，会出现反馈对话框：

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

### 步骤 5：选择操作

#### 选项 A：直接同意

点击 **✅ 同意** 按钮，对话结束。

#### 选项 B：提供反馈

在输入框中输入反馈，例如：
```
请添加更多边界测试用例
```

或者指定特定智能体：
```
@TestCase_Generator 请添加异常处理的测试用例
```

### 步骤 6：继续对话

如果提供了反馈，智能体会继续工作：
```
🤖 测试用例生成器
   正在根据反馈生成新的测试用例...
   [新的测试用例]

🤖 测试用例评审员
   正在评审新的测试用例...
   [新的评审意见]
```

再次出现反馈对话框，重复步骤 5。

## 🎯 示例对话

### 示例 1：正常流程

```
用户: 生成登录功能的测试用例

Generator: [生成测试用例]
Reviewer: [评审测试用例]

[反馈对话框出现]

用户: 点击"同意"

系统: 对话结束
```

### 示例 2：提供反馈

```
用户: 生成登录功能的测试用例

Generator: [生成测试用例]
Reviewer: [评审测试用例]

[反馈对话框出现]

用户: 请添加密码强度验证的测试用例

Generator: [添加新的测试用例]
Reviewer: [评审新的测试用例]

[反馈对话框出现]

用户: 点击"同意"

系统: 对话结束
```

### 示例 3：指定智能体

```
用户: 生成登录功能的测试用例

Generator: [生成测试用例]
Reviewer: [评审测试用例]

[反馈对话框出现]

用户: @TestCase_Optimizer 请优化测试用例的可读性

Optimizer: [优化测试用例]

[反馈对话框出现]

用户: 点击"同意"

系统: 对话结束
```

## 🔍 调试技巧

### 查看后端日志

后端终端会显示详细日志：
```
🆕 创建新对话 team_session_abc123
📝 继续对话 team_session_abc123，反馈: @TestCase_Generator 请添加边界测试
⏸️ 会话 team_session_abc123 等待用户反馈
✅ 会话 team_session_abc123 已完成
```

### 查看前端控制台

打开浏览器开发者工具（F12），查看控制台：
```
📝 Conversation ID: team_session_abc123
⏸️ 等待用户反馈，会话 ID: team_session_abc123
```

### 查看网络请求

在开发者工具的 Network 标签中：
1. 找到 `/api/team-chat/stream` 请求
2. 查看 Request Payload
3. 查看 Response Headers 中的 `X-Conversation-ID`

## ❓ 常见问题

### Q: 反馈对话框没有出现？

**可能原因**:
1. 没有切换到团队模式
2. 智能体还没有完成工作
3. 后端没有发送 `feedback_request` 消息

**解决方法**:
1. 确认右上角团队按钮是绿色
2. 等待智能体完成（看到"已完成"标记）
3. 查看后端日志是否有错误

### Q: 点击"同意"后没有反应？

**可能原因**:
1. 网络请求失败
2. 后端服务异常

**解决方法**:
1. 查看浏览器控制台是否有错误
2. 查看后端日志是否有异常
3. 检查网络连接

### Q: @ 智能体没有生效？

**可能原因**:
1. 智能体名称拼写错误
2. 没有使用完整名称

**解决方法**:
1. 使用完整名称：`@TestCase_Generator`
2. 注意大小写和下划线
3. 参考反馈对话框中的提示

### Q: 刷新页面后对话丢失？

**原因**: 前端状态存储在内存中，刷新会清空。

**解决方法**: 目前无法恢复，需要重新开始对话。

## 🧪 测试命令

### 测试后端 API

```bash
# 1. 新对话
curl -N http://localhost:8000/api/team-chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "生成登录测试用例"}'

# 2. 提供反馈（替换 conversation_id）
curl -N http://localhost:8000/api/team-chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请添加边界测试",
    "conversation_id": "team_session_xxx",
    "is_feedback": true
  }'

# 3. 同意结束
curl -N http://localhost:8000/api/team-chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "同意",
    "conversation_id": "team_session_xxx",
    "is_feedback": true
  }'
```

### 运行测试脚本

```bash
chmod +x test_feedback_flow.sh
./test_feedback_flow.sh
```

## 📚 相关文档

- [功能设计文档](./FEEDBACK_FEATURE.md)
- [使用指南](./FEEDBACK_USAGE.md)
- [实现总结](./FEEDBACK_IMPLEMENTATION_SUMMARY.md)
- [配置指南](./CONFIGURATION_GUIDE.md)

## 🎉 开始使用

现在你已经了解了如何使用智能体反馈功能！

1. 启动服务
2. 打开浏览器
3. 切换到团队模式
4. 发送测试需求
5. 提供反馈或同意

享受智能体协作的乐趣！🚀

