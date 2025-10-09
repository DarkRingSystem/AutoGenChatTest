# 文件上传功能使用指南

## 📋 功能概述

普通对话模式支持上传文件，AI 会自动读取文件内容并结合用户问题进行回答。

### 支持的文件类型

- **文档**: PDF, DOCX, TXT, MD
- **代码**: PY, JS, TS, JAVA, CPP, etc.
- **数据**: JSON, CSV, XML, YAML
- **其他**: 任何文本格式文件

---

## 🚀 使用流程

### 1. 上传文件

1. 进入**普通对话模式**
2. 点击输入框旁边的**📎 附件**按钮
3. 选择要上传的文件（支持多选）
4. 等待文件解析完成

### 2. 查看解析结果

上传后会显示文件列表：

```
✅ test.py (已解析)
✅ config.json (已解析)
❌ image.png (解析失败)
```

### 3. 发送问题

文件上传成功后，直接输入问题：

```
这段代码的作用是什么？
```

AI 会自动结合文件内容回答。

---

## 💡 使用示例

### 示例 1: 代码分析

**上传文件**: `calculator.py`

```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
```

**用户问题**: "这段代码有什么问题吗？如何改进？"

**AI 回答**: 
```
这段代码实现了基本的数学运算，整体结构清晰。以下是一些改进建议：

1. 添加类型注解
2. 添加文档字符串
3. 添加输入验证
4. 考虑除法运算的零除错误

改进后的代码：
...
```

---

### 示例 2: 配置文件分析

**上传文件**: `config.json`

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "123456"
  }
}
```

**用户问题**: "这个配置文件有什么安全问题？"

**AI 回答**:
```
这个配置文件存在以下安全问题：

1. 密码明文存储
2. 使用默认用户名 root
3. 使用弱密码 123456
4. 配置文件可能被提交到版本控制

建议：
- 使用环境变量存储敏感信息
- 使用强密码
- 添加 .gitignore
...
```

---

### 示例 3: 多文件分析

**上传文件**: 
- `main.py`
- `utils.py`
- `config.py`

**用户问题**: "分析这个项目的架构，有什么改进建议？"

**AI 回答**:
```
根据上传的文件，这是一个简单的 Python 项目：

架构分析：
1. main.py - 主入口文件
2. utils.py - 工具函数
3. config.py - 配置管理

改进建议：
1. 添加 __init__.py 使其成为包
2. 使用配置类而不是全局变量
3. 添加日志系统
4. 添加单元测试
...
```

---

## 🔍 后端实现原理

### 文件处理流程

```
1. 前端上传文件
   ↓
2. 后端接收并解析文件
   ↓
3. 转换为 Markdown 格式
   ↓
4. 存储到内存（file_storage）
   ↓
5. 返回 file_id 给前端
   ↓
6. 用户发送问题时携带 file_ids
   ↓
7. 后端从存储中获取文件内容
   ↓
8. 构建包含文件内容的提示词
   ↓
9. 发送给 AI 模型
```

### 提示词格式

后端会自动构建如下格式的提示词：

```
请结合以下文件内容和用户问题进行解答：

### 文件: test.py

```python
def hello():
    print('Hello, World!')
```

---

用户问题：这段代码的作用是什么？
```

---

## 🎯 最佳实践

### 1. 文件大小

- 建议单个文件 < 1MB
- 总文件数 < 10 个
- 过大的文件可能导致响应变慢

### 2. 文件内容

- 上传相关的文件
- 避免上传无关文件
- 代码文件建议包含注释

### 3. 提问技巧

**❌ 不好的问题**:
```
这是什么？
```

**✅ 好的问题**:
```
这段代码的时间复杂度是多少？如何优化？
```

**✅ 更好的问题**:
```
分析这段代码的性能瓶颈，并提供优化方案。
重点关注：
1. 时间复杂度
2. 空间复杂度
3. 可能的边界情况
```

### 4. 多轮对话

文件上传后会保持在会话中，可以进行多轮对话：

```
用户: 这段代码的作用是什么？
AI: [分析代码功能]

用户: 如何添加错误处理？
AI: [基于之前的代码提供建议]

用户: 写一个单元测试
AI: [基于代码生成测试]
```

---

## 🐛 常见问题

### Q1: 文件上传失败

**可能原因**:
- 文件格式不支持
- 文件损坏
- 文件过大

**解决方案**:
- 检查文件格式
- 尝试重新上传
- 减小文件大小

### Q2: AI 没有使用文件内容

**可能原因**:
- 文件解析失败
- 问题与文件无关

**解决方案**:
- 查看文件是否显示"已解析"
- 在问题中明确提到文件内容
- 例如："根据上传的代码..."

### Q3: 清空对话后文件还在吗？

**回答**: 
- 清空对话会清除消息历史
- 但文件仍在后端存储中（30分钟过期）
- 需要重新上传文件

### Q4: 切换模式后文件还在吗？

**回答**:
- 文件上传功能仅在普通对话模式可用
- 切换到其他模式后文件不可用
- 切换回普通对话模式需要重新上传

---

## 🔧 技术细节

### 前端实现

```javascript
// 上传文件
const formData = new FormData();
files.forEach(file => formData.append('files', file));

const response = await fetch('/api/parse-files', {
  method: 'POST',
  body: formData
});

const results = await response.json();
// results 包含 file_id 和解析结果
```

### 后端实现

```python
# 解析文件
from marker.convert import convert_single_pdf
from marker.models import load_all_models

# 转换为 Markdown
markdown = convert_single_pdf(file_path, models)

# 存储文件内容
file_storage[file_id] = {
    "filename": filename,
    "markdown": markdown,
    "metadata": metadata
}
```

### 构建上下文

```python
# api/utils.py
def build_message_with_file_context(message, file_ids):
    # 从存储中获取文件内容
    file_contexts = []
    for file_id in file_ids:
        file_data = file_storage[file_id]
        file_contexts.append(f"### 文件: {filename}\n\n{markdown}")
    
    # 构建完整提示词
    return f"""请结合以下文件内容和用户问题进行解答：
    
{context_text}

---

用户问题：{message}"""
```

---

## 📚 相关文档

- **API 文档**: `backend/api/routes.py` - `/api/parse-files` 端点
- **工具函数**: `backend/api/utils.py` - `build_message_with_file_context`
- **测试文件**: `backend/tests/test_file_context.py`

---

## ✅ 验收标准

- [ ] 可以上传单个文件
- [ ] 可以上传多个文件
- [ ] 文件解析成功显示 ✅
- [ ] 文件解析失败显示 ❌
- [ ] AI 回答包含文件内容
- [ ] 多轮对话保持文件上下文
- [ ] 清空对话后需要重新上传

---

## 🎉 总结

文件上传功能让 AI 能够：

1. ✅ 分析代码质量
2. ✅ 审查配置文件
3. ✅ 解释文档内容
4. ✅ 提供改进建议
5. ✅ 生成测试用例
6. ✅ 重构代码

充分利用这个功能，让 AI 成为你的代码审查助手！🚀

