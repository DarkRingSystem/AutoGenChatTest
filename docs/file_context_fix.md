# 文件上下文传递问题修复文档

## 问题描述

在测试用例模式中，用户上传的文件（通过 Markdown 转换 API 解析）没有被正确传递到大模型的上下文中。

### 问题表现

1. 用户上传文件并解析成功，获得 `file_id`
2. 用户在测试用例生成请求中传递 `file_ids` 参数
3. 但大模型生成测试用例时，没有看到文件内容，导致生成的测试用例与文件内容无关

## 根本原因

在 `backend/api/routes.py` 文件中，`_build_message_with_file_context` 函数调用了一个**不存在的函数** `get_file_storage()`，导致无法获取已存储的文件内容。

### 问题代码位置

**文件**: `backend/api/routes.py`

**第 94 行** (修复前):
```python
def _build_message_with_file_context(message: str, file_ids: Optional[list[str]]) -> str:
    if not file_ids or len(file_ids) == 0:
        return message

    # 获取文件存储
    file_storage = get_file_storage()  # ❌ 这个函数不存在！
    
    # ... 后续代码
```

### 文件存储机制

文件存储使用全局变量 `file_storage`（第 23 行定义）：

```python
# 文件内容存储（简单的内存存储，生产环境应使用数据库或缓存）
file_storage = {}
```

文件上传后，在第 814 行存储：

```python
file_storage[file_id] = {
    "filename": result.get("filename", "unknown"),
    "markdown": result.get("markdown", ""),
    "metadata": result.get("metadata", {})
}
```

## 修复方案

### 1. 添加 `get_file_storage()` 函数

在 `backend/api/routes.py` 中添加函数定义：

```python
def get_file_storage() -> Dict:
    """
    获取文件存储
    
    返回:
        文件存储字典
    """
    global file_storage
    return file_storage
```

### 2. 修复 `_build_message_with_file_context` 函数

更新函数实现，添加调试日志：

```python
def _build_message_with_file_context(message: str, file_ids: Optional[list[str]]) -> str:
    """构建包含文件上下文的消息"""
    if not file_ids or len(file_ids) == 0:
        return message

    # 获取文件存储
    storage = get_file_storage()  # ✅ 现在可以正常工作

    # 获取文件内容
    file_contexts = []
    for file_id in file_ids:
        if file_id in storage:
            file_data = storage[file_id]
            filename = file_data.get("filename", "unknown")
            markdown = file_data.get("markdown", "")

            if markdown:
                file_contexts.append(f"### 文件: {filename}\n\n{markdown}")
                print(f"📄 添加文件上下文: {filename} (长度: {len(markdown)} 字符)")
            else:
                print(f"⚠️ 文件 {filename} 没有 markdown 内容")
        else:
            print(f"⚠️ 文件 ID {file_id} 不存在于存储中")

    if not file_contexts:
        print(f"⚠️ 没有找到任何文件上下文，file_ids: {file_ids}")
        return message

    # 构建完整消息
    context_text = "\n\n---\n\n".join(file_contexts)
    full_message = f"""请结合以下文件内容和用户问题进行解答：

{context_text}

---

用户问题：{message}"""

    print(f"✅ 成功构建包含 {len(file_contexts)} 个文件的上下文消息")
    return full_message
```

### 3. 修复调用位置

在第 500-501 行，将调用从 `utils.py` 改为直接调用本地函数：

**修复前**:
```python
from .utils import build_message_with_file_context
message_with_context = build_message_with_file_context(feedback_message, request.file_ids)
```

**修复后**:
```python
print(f"📋 构建消息上下文，file_ids: {request.file_ids}")
message_with_context = _build_message_with_file_context(feedback_message, request.file_ids)
```

### 4. 更新 `backend/api/utils.py`

同步更新 `utils.py` 中的实现，使其调用 `routes.py` 中的 `get_file_storage()`：

```python
def build_message_with_file_context(message: str, file_ids: Optional[List[str]] = None) -> str:
    """
    构建包含文件上下文的消息
    
    Note:
        此函数已弃用，请使用 routes.py 中的 _build_message_with_file_context
        保留此函数仅为向后兼容
    """
    if not file_ids:
        return message
    
    # 导入 routes 中的实现
    from .routes import get_file_storage
    
    # ... 实现逻辑
```

### 5. 添加文件存储日志

在文件存储时添加日志（第 814 行）：

```python
filename = result.get("filename", "unknown")
markdown = result.get("markdown", "")
file_storage[file_id] = {
    "filename": filename,
    "markdown": markdown,
    "metadata": result.get("metadata", {})
}
print(f"💾 存储文件: {filename} (ID: {file_id}, Markdown长度: {len(markdown)} 字符)")
```

## 测试验证

创建了测试文件 `backend/tests/test_file_context.py`，包含以下测试用例：

1. ✅ **文件存储功能测试** - 验证文件可以正确存储和检索
2. ✅ **构建包含文件上下文的消息** - 验证文件内容正确添加到消息中
3. ✅ **空文件 ID 列表** - 验证空列表时返回原始消息
4. ✅ **不存在的文件 ID** - 验证不存在的文件 ID 时返回原始消息

所有测试通过！

## 使用流程

### 1. 上传并解析文件

```bash
curl -X POST "http://localhost:8000/api/convert/markdown/batch" \
  -F "files=@需求文档.pdf" \
  -F "files=@设计文档.pdf" \
  -F "use_llm=false"
```

响应示例：
```json
{
  "total": 2,
  "success_count": 2,
  "failed_count": 0,
  "results": [
    {
      "success": true,
      "file_id": "abc123",
      "filename": "需求文档.pdf",
      "markdown": "# 需求文档内容..."
    },
    {
      "success": true,
      "file_id": "def456",
      "filename": "设计文档.pdf",
      "markdown": "# 设计文档内容..."
    }
  ]
}
```

### 2. 使用文件 ID 生成测试用例

```bash
curl -X POST "http://localhost:8000/api/team/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请根据需求文档和设计文档，生成登录功能的测试用例",
    "file_ids": ["abc123", "def456"]
  }'
```

### 3. 大模型接收到的上下文

```
请结合以下文件内容和用户问题进行解答：

### 文件: 需求文档.pdf

# 需求文档内容...

---

### 文件: 设计文档.pdf

# 设计文档内容...

---

用户问题：请根据需求文档和设计文档，生成登录功能的测试用例
```

## 调试日志

修复后，系统会输出以下调试日志：

```
💾 存储文件: 需求文档.pdf (ID: abc123, Markdown长度: 1234 字符)
💾 存储文件: 设计文档.pdf (ID: def456, Markdown长度: 2345 字符)
📋 构建消息上下文，file_ids: ['abc123', 'def456']
📄 添加文件上下文: 需求文档.pdf (长度: 1234 字符)
📄 添加文件上下文: 设计文档.pdf (长度: 2345 字符)
✅ 成功构建包含 2 个文件的上下文消息
```

## 后续优化建议

1. **持久化存储**: 当前使用内存存储，服务重启后文件会丢失。建议使用 Redis 或数据库存储。

2. **文件过期机制**: 添加文件过期时间，自动清理旧文件。

3. **文件大小限制**: 对单个文件的 Markdown 内容大小进行限制，避免超出模型上下文窗口。

4. **错误处理**: 增强错误处理，当文件不存在时给用户更友好的提示。

5. **文件管理 API**: 添加查询、删除文件的 API 端点。

## 相关文件

- `backend/api/routes.py` - 主要修复文件
- `backend/api/utils.py` - 工具函数更新
- `backend/tests/test_file_context.py` - 测试文件
- `backend/models.py` - 数据模型定义

## 修复时间

2025-10-11

## 修复人员

Augment Agent

