# 新的智能体工作流程

## 📋 工作流程说明

### 流程图

```
用户输入需求
    ↓
Generator 生成测试用例
    ↓
Reviewer 评审测试用例
    ↓
[等待用户反馈]
    ↓
    ├─ 用户同意 → Optimizer 给出最终优化方案 → 结束
    │
    ├─ 用户反馈（未指定智能体）→ Generator → Reviewer → [等待用户反馈]
    │
    └─ 用户反馈（@指定智能体）→ 指定的智能体回答 → [等待用户反馈]
```

## 🎯 详细流程

### 1. 初始流程

```
用户: "生成登录功能的测试用例"
    ↓
Generator: [生成测试用例]
    ↓
Reviewer: [评审测试用例，提出建议]
    ↓
[反馈对话框出现]
```

### 2. 用户同意

```
用户: 点击"同意"或输入"同意"
    ↓
Optimizer: [结合 Generator 和 Reviewer 的意见，给出最终优化的测试用例]
    ↓
结束（不再等待反馈）
```

### 3. 用户反馈（未指定智能体）

```
用户: "请添加边界测试用例"
    ↓
Generator: [根据反馈生成新的测试用例]
    ↓
Reviewer: [评审新的测试用例]
    ↓
[反馈对话框出现]
```

### 4. 用户反馈（指定智能体）

```
用户: "@TestCase_Generator 请添加异常处理测试"
    ↓
Generator: [只有 Generator 回答，添加异常处理测试]
    ↓
[反馈对话框出现]

或

用户: "@TestCase_Optimizer 请优化测试用例的可读性"
    ↓
Optimizer: [只有 Optimizer 回答，优化测试用例]
    ↓
[反馈对话框出现]
```

## 🔧 技术实现

### 1. 智能体初始化

**默认模式**（Generator → Reviewer）:
```python
team_service = TestCasesTeamAIService(settings)
await team_service.initialize()  # 包含 Generator 和 Reviewer
```

**指定单个智能体**:
```python
team_service = TestCasesTeamAIService(settings)
await team_service.initialize(specific_agent="TestCase_Generator")
# 或
await team_service.initialize(specific_agent="TestCase_Reviewer")
# 或
await team_service.initialize(specific_agent="TestCase_Optimizer")
```

### 2. 终止条件

```python
# Reviewer 完成后停止（等待用户反馈）
reviewer_termination = SourceMatchTermination(["TestCase_Reviewer"])

# Optimizer 完成后停止（最终回答，不等待反馈）
optimizer_termination = SourceMatchTermination(["TestCase_Optimizer"])
```

### 3. 反馈检测

```python
def _should_wait_for_feedback(self, agent_name: str) -> bool:
    # 只在 Reviewer 完成后等待反馈
    return agent_name == "TestCase_Reviewer"

def _is_final_answer(self, agent_name: str) -> bool:
    # Optimizer 的回答是最终回答
    return agent_name == "TestCase_Optimizer"
```

## 📊 示例对话

### 示例 1：用户同意

```
用户: 生成登录功能的测试用例

Generator: 
1. 测试用户名和密码正确的情况
2. 测试用户名错误的情况
3. 测试密码错误的情况

Reviewer:
建议添加：
- 空用户名/密码的测试
- SQL 注入测试
- 密码强度测试

[反馈对话框]

用户: 同意

Optimizer:
最终优化的测试用例：
1. 正常登录测试
   - 用户名和密码正确
2. 异常登录测试
   - 用户名错误
   - 密码错误
   - 空用户名
   - 空密码
3. 安全测试
   - SQL 注入测试
   - XSS 攻击测试
4. 密码强度测试
   - 弱密码
   - 强密码

[结束]
```

### 示例 2：用户反馈（未指定）

```
用户: 生成登录功能的测试用例

Generator: [生成测试用例]
Reviewer: [评审]

[反馈对话框]

用户: 请添加多次登录失败后锁定账户的测试

Generator: [添加账户锁定测试]
Reviewer: [评审新的测试用例]

[反馈对话框]

用户: 同意

Optimizer: [给出最终优化方案]

[结束]
```

### 示例 3：用户反馈（指定智能体）

```
用户: 生成登录功能的测试用例

Generator: [生成测试用例]
Reviewer: [评审]

[反馈对话框]

用户: @TestCase_Generator 请添加记住密码功能的测试

Generator: [只有 Generator 回答，添加记住密码测试]

[反馈对话框]

用户: @TestCase_Reviewer 请评审一下记住密码的安全性

Reviewer: [只有 Reviewer 回答，评审安全性]

[反馈对话框]

用户: 同意

Optimizer: [给出最终优化方案]

[结束]
```

## 🎨 前端显示

### Reviewer 完成后

```
┌─────────────────────────────────────────┐
│ 💬 测试用例评审员 已完成，请提供反馈      │
├─────────────────────────────────────────┤
│ • 直接点击"同意"，Optimizer 将给出最终方案 │
│ • 输入反馈内容，将重复 Generator → Reviewer 流程 │
│ • 使用 @智能体名称 指定特定智能体回答     │
│                                         │
│                        [✅ 同意]         │
└─────────────────────────────────────────┘
```

### 指定智能体完成后

```
┌─────────────────────────────────────────┐
│ 💬 测试用例生成器 已完成，请提供反馈      │
├─────────────────────────────────────────┤
│ • 直接点击"同意"，Optimizer 将给出最终方案 │
│ • 输入反馈内容继续对话                   │
│ • 使用 @智能体名称 指定其他智能体回答     │
│                                         │
│                        [✅ 同意]         │
└─────────────────────────────────────────┘
```

### Optimizer 完成后

```
✅ Optimizer 已给出最终优化方案，对话结束
```

## 🔄 与旧流程的区别

### 旧流程

```
Generator → Reviewer → Optimizer → [等待反馈]
    ↓
用户反馈 → Generator → Reviewer → Optimizer → [等待反馈]
```

**问题**：
- Optimizer 总是自动运行
- 用户无法控制何时获得最终方案
- 无法在 Reviewer 后直接提供反馈

### 新流程

```
Generator → Reviewer → [等待反馈]
    ↓
用户同意 → Optimizer → [结束]
    ↓
用户反馈 → Generator → Reviewer → [等待反馈]
```

**优势**：
- ✅ 用户可以在 Reviewer 后立即反馈
- ✅ 用户控制何时获得最终方案（点击"同意"）
- ✅ 支持多轮反馈和修改
- ✅ 支持指定特定智能体回答
- ✅ Optimizer 只在用户同意后运行一次

## 📝 修改的文件

1. **backend/services/ai_service.py**
   - 修改 `initialize()` 方法，支持 `specific_agent` 参数
   - 修改 `_create_team_agents()` 方法，根据参数创建不同的智能体组合
   - 修改终止条件，区分 Reviewer 和 Optimizer

2. **backend/services/team_stream_service.py**
   - 修改 `_should_wait_for_feedback()` 方法，只在 Reviewer 完成后等待
   - 添加 `_is_final_answer()` 方法，判断是否为最终回答
   - 修改流结束逻辑，区分不同的完成状态

3. **backend/api/routes.py**
   - 修改反馈处理逻辑，区分"同意"、"未指定智能体"、"指定智能体"三种情况
   - 在"同意"时，初始化只包含 Optimizer 的团队
   - 在"指定智能体"时，初始化只包含该智能体的团队
   - 在"未指定智能体"时，初始化包含 Generator 和 Reviewer 的团队

## 🧪 测试方法

### 测试场景 1：完整流程

1. 发送需求
2. 等待 Generator → Reviewer
3. 点击"同意"
4. 等待 Optimizer 给出最终方案
5. 验证对话结束

### 测试场景 2：多轮反馈

1. 发送需求
2. 等待 Generator → Reviewer
3. 输入反馈（不指定智能体）
4. 等待 Generator → Reviewer
5. 点击"同意"
6. 等待 Optimizer 给出最终方案

### 测试场景 3：指定智能体

1. 发送需求
2. 等待 Generator → Reviewer
3. 输入 "@TestCase_Generator 请添加..."
4. 等待 Generator 回答
5. 点击"同意"
6. 等待 Optimizer 给出最终方案

## 🎉 总结

新的工作流程更加灵活和可控：

✅ **用户主导**：用户决定何时获得最终方案  
✅ **灵活反馈**：支持多轮反馈和修改  
✅ **精准控制**：可以指定特定智能体回答  
✅ **清晰流程**：Generator → Reviewer → 反馈 → Optimizer  
✅ **高效协作**：避免不必要的智能体调用

