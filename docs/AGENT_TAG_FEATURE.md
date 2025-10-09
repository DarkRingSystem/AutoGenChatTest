# 智能体标签选择功能

## 🎯 功能概述

在反馈对话框中添加了可点击的智能体标签，用户可以通过点击标签快速选择要回复的智能体，提升交互体验。

## ✨ 新功能

### 1. 可点击的智能体标签

在反馈对话框中，显示所有可用的智能体作为可点击的标签：

```
┌─────────────────────────────────────────┐
│ 💬 测试用例评审员 已完成，请提供反馈      │
├─────────────────────────────────────────┤
│ • 直接点击"同意"，Optimizer 将给出最终方案 │
│ • 点击下方智能体标签，指定特定智能体回答   │
│ • 点击"All"，重新运行 Generator → Reviewer │
│                                         │
│ 选择智能体：                             │
│ [🔄 All] [🎯 Generator] [🔍 Reviewer]   │
│ [⚡ Optimizer]                          │
│                                         │
│                        [✅ 同意]         │
└─────────────────────────────────────────┘
```

### 2. All 标签

- **功能**：重新运行 Generator → Reviewer 流程
- **图标**：🔄
- **颜色**：绿色渐变
- **用途**：当用户想要完整重新生成和评审测试用例时使用

### 3. 智能体标签

每个智能体都有独特的图标：
- **Generator** 🎯 - 生成器
- **Reviewer** 🔍 - 评审员
- **Optimizer** ⚡ - 优化器

### 4. 清除按钮

当用户点击了某个标签后，输入框中会自动添加 `@智能体名称`，此时会显示"清除"按钮：

```
[🔄 All] [🎯 Generator] [🔍 Reviewer] [⚡ Optimizer] [✖️ 清除]
```

点击"清除"按钮可以移除输入框中的 @ 提及。

## 🎨 交互逻辑

### 点击智能体标签

1. **首次点击**：
   ```
   输入框：空
   点击 [🎯 Generator]
   输入框：@TestCase_Generator 
   ```

2. **已有内容**：
   ```
   输入框：请添加边界测试
   点击 [🎯 Generator]
   输入框：@TestCase_Generator 请添加边界测试
   ```

3. **替换已有标签**：
   ```
   输入框：@TestCase_Reviewer 请优化
   点击 [🎯 Generator]
   输入框：@TestCase_Generator 请优化
   ```

### 点击 All 标签

```
输入框：空
点击 [🔄 All]
输入框：@all 
```

### 点击清除按钮

```
输入框：@TestCase_Generator 请添加测试
点击 [✖️ 清除]
输入框：请添加测试
```

## 🔧 技术实现

### 前端实现

#### 1. 智能体标签点击处理

```javascript
const handleAgentTagClick = (agentName) => {
  const currentInput = inputValue.trim();
  const hasAtMention = currentInput.match(/@(TestCase_\w+|all)/i);
  
  if (hasAtMention) {
    // 替换已有的 @ 提及
    const newInput = currentInput.replace(/@(TestCase_\w+|all)/i, `@${agentName}`);
    setInputValue(newInput);
  } else {
    // 添加到开头
    setInputValue(`@${agentName} ${currentInput}`);
  }
  
  message.success(`已选择 @${agentName}`);
};
```

#### 2. 清除 @ 提及

```javascript
const handleClearMention = () => {
  const currentInput = inputValue.trim();
  const newInput = currentInput.replace(/@(TestCase_\w+|all)\s*/i, '');
  setInputValue(newInput);
  message.success('已清除智能体选择');
};
```

#### 3. UI 渲染

```jsx
<div className="agent-tags-container">
  <div className="agent-tags-label">选择智能体：</div>
  <div className="agent-tags">
    {/* All 标签 */}
    <motion.button
      className="agent-tag agent-tag-all"
      onClick={() => handleAgentTagClick('all')}
    >
      <span className="agent-tag-icon">🔄</span>
      <span className="agent-tag-name">All</span>
    </motion.button>
    
    {/* 智能体标签 */}
    {availableAgents.map(agentName => (
      <motion.button
        className="agent-tag"
        onClick={() => handleAgentTagClick(agentName)}
      >
        <span className="agent-tag-icon">🎯</span>
        <span className="agent-tag-name">
          {agentName.replace('TestCase_', '')}
        </span>
      </motion.button>
    ))}
    
    {/* 清除按钮 */}
    {inputValue.match(/@(TestCase_\w+|all)/i) && (
      <motion.button
        className="agent-tag agent-tag-clear"
        onClick={handleClearMention}
      >
        <span className="agent-tag-icon">✖️</span>
        <span className="agent-tag-name">清除</span>
      </motion.button>
    )}
  </div>
</div>
```

### 后端实现

#### 1. 解析 @all

```python
def _parse_target_agent(message: str) -> Optional[str]:
    # 先匹配 @all（不区分大小写）
    if re.search(r'@all\b', message, re.IGNORECASE):
        print(f"🔄 检测到 @all，将重新运行 Generator → Reviewer 流程")
        return "all"
    
    # 匹配 @智能体名称
    match = re.search(r'@(TestCase_\w+)', message)
    if match:
        agent_name = match.group(1)
        print(f"🎯 检测到目标智能体: {agent_name}")
        return agent_name
    
    return None
```

#### 2. 处理 @all

```python
if target_agent == "all":
    # 用户选择 @all，重新运行 Generator → Reviewer 流程
    feedback_message = f"对话历史：\n{history_text}\n\n用户反馈（@all）: {request.message}"
    
    # 创建新的团队服务实例（Generator → Reviewer）
    team_service = TestCasesTeamAIService(settings)
    await team_service.initialize()  # 默认包含 Generator 和 Reviewer
    
    print(f"🔄 继续对话 {conversation_id}，@all 重新运行 Generator → Reviewer 流程")
elif target_agent:
    # 用户指定了特定智能体
    # ...
else:
    # 用户未指定智能体
    # ...
```

## 🎨 样式设计

### 智能体标签样式

```css
.agent-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInUp 0.3s ease;
}

.agent-tag:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
```

### All 标签特殊样式

```css
.agent-tag-all {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
  border-color: rgba(52, 211, 153, 0.3);
}

.agent-tag-all:hover {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.3) 0%, rgba(16, 185, 129, 0.3) 100%);
  border-color: rgba(52, 211, 153, 0.5);
  box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
}
```

### 清除按钮特殊样式

```css
.agent-tag-clear {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
  border-color: rgba(239, 68, 68, 0.3);
}

.agent-tag-clear:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(220, 38, 38, 0.3) 100%);
  border-color: rgba(239, 68, 68, 0.5);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}
```

## 📝 使用示例

### 示例 1：使用 All 重新生成

```
1. 用户发送："生成登录功能测试用例"
2. Generator → Reviewer 完成
3. 用户点击 [🔄 All]
4. 输入框显示：@all 
5. 用户输入：@all 请添加安全测试
6. 发送后，重新运行 Generator → Reviewer
```

### 示例 2：指定 Generator

```
1. 用户发送："生成登录功能测试用例"
2. Generator → Reviewer 完成
3. 用户点击 [🎯 Generator]
4. 输入框显示：@TestCase_Generator 
5. 用户输入：@TestCase_Generator 请添加边界测试
6. 发送后，只有 Generator 回答
```

### 示例 3：切换智能体

```
1. 用户点击 [🎯 Generator]
2. 输入框显示：@TestCase_Generator 
3. 用户改变主意，点击 [🔍 Reviewer]
4. 输入框显示：@TestCase_Reviewer （自动替换）
5. 用户输入：@TestCase_Reviewer 请评审安全性
6. 发送后，只有 Reviewer 回答
```

### 示例 4：清除选择

```
1. 用户点击 [🎯 Generator]
2. 输入框显示：@TestCase_Generator 
3. 用户点击 [✖️ 清除]
4. 输入框显示：（空）
5. 用户输入：请优化测试用例
6. 发送后，重新运行 Generator → Reviewer（默认行为）
```

## 🎉 优势

✅ **直观易用** - 可视化的标签选择，无需手动输入  
✅ **快速切换** - 点击即可切换智能体，自动替换  
✅ **防止错误** - 避免手动输入时的拼写错误  
✅ **视觉反馈** - 悬停和点击动画，清晰的交互反馈  
✅ **灵活控制** - 支持 All、特定智能体、清除等多种操作  
✅ **响应式设计** - 支持深色/浅色主题，适配不同屏幕

## 📝 修改的文件

1. **`frontend/src/App.jsx`**
   - 添加 `handleAgentTagClick()` 函数
   - 添加 `handleClearMention()` 函数
   - 修改反馈对话框 UI，添加智能体标签

2. **`frontend/src/App.css`**
   - 添加 `.agent-tags-container` 样式
   - 添加 `.agent-tag` 样式
   - 添加 `.agent-tag-all` 特殊样式
   - 添加 `.agent-tag-clear` 特殊样式
   - 添加 `fadeInUp` 动画

3. **`backend/api/routes.py`**
   - 修改 `_parse_target_agent()` 函数，支持 `@all`
   - 修改反馈处理逻辑，区分 `@all`、特定智能体、无指定三种情况

## 🧪 测试方法

1. 发送测试需求
2. 等待 Generator → Reviewer 完成
3. 查看反馈对话框中的智能体标签
4. 点击不同的标签，观察输入框变化
5. 点击"清除"按钮，验证清除功能
6. 发送反馈，验证后端正确处理

现在可以测试新功能了！🎉

