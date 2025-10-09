# 消息操作功能

## 🎯 功能概述

为用户消息和智能体消息添加了便捷的操作按钮，提升用户体验和工作效率。

## ✨ 新功能

### 1. 用户消息操作（左侧按钮）

#### 🔄 重新发送
- **功能**：一键重新发送用户消息
- **图标**：<RedoOutlined />
- **位置**：用户消息气泡左侧
- **用途**：快速重试相同的问题，无需重新输入

#### ✏️ 编辑消息
- **功能**：编辑已发送的消息并重新发送
- **图标**：<EditOutlined />
- **位置**：用户消息气泡左侧
- **用途**：修改问题后重新提问

**编辑模式**：
- 点击编辑按钮后，消息内容变为可编辑的文本框
- 提供"保存并发送"和"取消"两个按钮
- 保存后自动重新发送修改后的消息

### 2. 智能体消息操作（右侧按钮）

#### 📋 复制内容
- **功能**：一键复制智能体回答到剪贴板
- **图标**：<CopyOutlined />
- **位置**：智能体消息气泡右侧
- **用途**：快速复制回答内容到其他地方使用

**复制逻辑**：
- **普通模式**：复制单个 AI 回答
- **团队模式**：复制所有智能体的回答，格式化为 Markdown

#### 💾 保存为 Markdown
- **功能**：将智能体回答保存为 .md 文件
- **图标**：<SaveOutlined />
- **位置**：智能体消息气泡右侧
- **用途**：永久保存重要的回答内容

**保存格式**：
- **普通模式**：`ai-response-YYYY-MM-DD-HH-MM-SS.md`
- **团队模式**：`testcase-team-YYYY-MM-DD-HH-MM-SS.md`
- 包含生成时间和完整的 Markdown 格式

## 🎨 UI 设计

### 按钮布局

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  [🔄] [✏️]  👤 用户消息气泡                      │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                                                 │
│              🤖 智能体消息气泡  [📋] [💾]        │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 交互效果

1. **悬停显示**：鼠标悬停在消息上时，操作按钮淡入显示
2. **悬停放大**：鼠标悬停在按钮上时，按钮放大 1.1 倍
3. **点击缩小**：点击按钮时，按钮缩小到 0.9 倍
4. **毛玻璃效果**：按钮背景使用毛玻璃效果（backdrop-filter）
5. **渐变高亮**：悬停时显示紫色渐变高亮

### 编辑模式 UI

```
┌─────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────┐ │
│ │ 可编辑的文本框                               │ │
│ │ 用户可以修改消息内容                         │ │
│ │                                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│              [✅ 保存并发送] [❌ 取消]           │
└─────────────────────────────────────────────────┘
```

## 🔧 技术实现

### 1. 重新发送消息

```javascript
const handleResendMessage = async (messageId) => {
  const msg = messages.find(m => m.id === messageId);
  if (!msg || msg.role !== 'user') return;
  
  console.log('🔄 重新发送消息:', msg.content);
  await handleStreamingChat(msg.content);
  message.success('消息已重新发送');
};
```

### 2. 编辑消息

```javascript
// 开始编辑
const handleEditMessage = (messageId) => {
  const msg = messages.find(m => m.id === messageId);
  if (!msg || msg.role !== 'user') return;
  
  setEditingMessageId(messageId);
  setEditingContent(msg.content);
};

// 保存编辑
const handleSaveEdit = async (messageId) => {
  if (!editingContent.trim()) {
    message.warning('消息内容不能为空');
    return;
  }

  // 更新消息内容
  setMessages(prev =>
    prev.map(msg =>
      msg.id === messageId ? { ...msg, content: editingContent } : msg
    )
  );

  // 重新发送
  await handleStreamingChat(editingContent);
  
  // 清除编辑状态
  setEditingMessageId(null);
  setEditingContent('');
  message.success('消息已更新并重新发送');
};

// 取消编辑
const handleCancelEdit = () => {
  setEditingMessageId(null);
  setEditingContent('');
  message.info('已取消编辑');
};
```

### 3. 复制消息

```javascript
const handleCopyMessage = async (messageId) => {
  const msg = messages.find(m => m.id === messageId);
  if (!msg || msg.role !== 'assistant') return;

  try {
    let textToCopy = '';
    
    if (msg.isTeamMode && msg.agents) {
      // 团队模式：复制所有智能体的回答
      textToCopy = msg.agents
        .map(agent => `## ${agent.name}\n\n${agent.content}`)
        .join('\n\n---\n\n');
    } else {
      // 普通模式：复制单个回答
      textToCopy = msg.content;
    }

    await navigator.clipboard.writeText(textToCopy);
    message.success('已复制到剪贴板');
  } catch (err) {
    console.error('复制失败:', err);
    message.error('复制失败');
  }
};
```

### 4. 保存为 Markdown

```javascript
const handleSaveMessage = (messageId) => {
  const msg = messages.find(m => m.id === messageId);
  if (!msg || msg.role !== 'assistant') return;

  try {
    let markdownContent = '';
    let filename = '';

    if (msg.isTeamMode && msg.agents) {
      // 团队模式
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      filename = `testcase-team-${timestamp}.md`;
      
      markdownContent = `# 测试用例智能体团队回答\n\n`;
      markdownContent += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
      markdownContent += `---\n\n`;
      
      msg.agents.forEach(agent => {
        markdownContent += `## ${agent.name}\n\n`;
        markdownContent += `${agent.content}\n\n`;
        markdownContent += `---\n\n`;
      });
    } else {
      // 普通模式
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      filename = `ai-response-${timestamp}.md`;
      
      markdownContent = `# AI 回答\n\n`;
      markdownContent += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
      markdownContent += `---\n\n`;
      markdownContent += msg.content;
    }

    // 创建 Blob 并下载
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    message.success(`已保存为 ${filename}`);
  } catch (err) {
    console.error('保存失败:', err);
    message.error('保存失败');
  }
};
```

## 🎨 CSS 样式

### 操作按钮容器

```css
.message-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  align-self: flex-start;
  margin-top: 8px;
}

.message-wrapper:hover .message-actions {
  opacity: 1;
}
```

### 操作按钮

```css
.action-button {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.action-button:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
  color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
```

### 编辑文本框

```css
.edit-message-textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  resize: vertical;
  transition: all 0.3s ease;
}

.edit-message-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
```

## 📝 使用示例

### 示例 1：重新发送消息

```
1. 用户发送："生成登录测试用例"
2. AI 回答完成
3. 用户悬停在自己的消息上
4. 点击 [🔄] 按钮
5. 系统自动重新发送相同的消息
```

### 示例 2：编辑并重新发送

```
1. 用户发送："生成登录测试用例"
2. AI 回答完成
3. 用户悬停在自己的消息上
4. 点击 [✏️] 按钮
5. 消息变为可编辑状态
6. 用户修改为："生成登录和注册测试用例"
7. 点击 [✅ 保存并发送]
8. 系统发送修改后的消息
```

### 示例 3：复制 AI 回答

```
1. AI 回答完成
2. 用户悬停在 AI 消息上
3. 点击 [📋] 按钮
4. 内容已复制到剪贴板
5. 用户可以粘贴到其他地方使用
```

### 示例 4：保存为 Markdown

```
1. AI 回答完成
2. 用户悬停在 AI 消息上
3. 点击 [💾] 按钮
4. 浏览器自动下载 .md 文件
5. 文件名：ai-response-2025-10-06-14-30-25.md
```

## 🎉 优势

✅ **提升效率** - 无需重新输入，一键重发或编辑  
✅ **便捷复制** - 快速复制 AI 回答到其他地方  
✅ **永久保存** - 将重要回答保存为 Markdown 文件  
✅ **优雅交互** - 悬停显示，不占用空间  
✅ **视觉反馈** - 动画效果，清晰的操作反馈  
✅ **主题适配** - 支持深色/浅色主题  
✅ **团队模式** - 智能处理团队模式的多智能体回答

## 📝 修改的文件

1. **`frontend/src/App.jsx`**
   - 添加 `editingMessageId` 和 `editingContent` 状态
   - 添加 `handleResendMessage()` 函数
   - 添加 `handleEditMessage()` 函数
   - 添加 `handleSaveEdit()` 函数
   - 添加 `handleCancelEdit()` 函数
   - 添加 `handleCopyMessage()` 函数
   - 添加 `handleSaveMessage()` 函数
   - 修改消息渲染，添加操作按钮
   - 添加编辑模式 UI

2. **`frontend/src/App.css`**
   - 添加 `.message-actions` 样式
   - 添加 `.action-button` 样式
   - 添加 `.edit-message-container` 样式
   - 添加 `.edit-message-textarea` 样式
   - 添加 `.edit-action-button` 样式
   - 添加悬停和动画效果

## 🧪 测试方法

1. **刷新浏览器**（Cmd+Shift+R）
2. 发送一条消息
3. 等待 AI 回答
4. **悬停在用户消息上**，查看左侧操作按钮
5. **悬停在 AI 消息上**，查看右侧操作按钮
6. 测试各个功能：
   - 点击 [🔄] 重新发送
   - 点击 [✏️] 编辑消息
   - 点击 [📋] 复制内容
   - 点击 [💾] 保存文件

现在可以测试新功能了！🎉

