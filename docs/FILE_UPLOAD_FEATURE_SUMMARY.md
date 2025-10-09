# 文件上传功能实现总结

## 🎯 功能概述

已成功实现前后端协同的文件上传和解析功能，用户可以在两个对话模式（普通对话和测试用例智能体）中上传文件，**后端自动解析文件内容并构建上下文**，前端只负责上传文件和显示状态。

## 🏗️ 架构设计

### 职责分离

- **前端职责**：
  - 文件上传和校验（大小、数量、格式）
  - 显示解析进度和状态
  - 传递文件 ID 给后端
  - 显示文件标记

- **后端职责**：
  - 文件解析和转换
  - 生成文件 ID 并存储内容
  - 根据文件 ID 构建上下文
  - 将上下文与用户问题合并后传递给智能体

## ✅ 实现的功能

### 1. 文件上传限制（前后端双重校验）

#### 前端校验
- ✅ 单个文件最大 100MB
- ✅ 最多上传 10 个文件
- ✅ 支持的文件格式检查

#### 后端校验
- ✅ 单个文件最大 100MB
- ✅ 最多上传 10 个文件（从 20 个调整为 10 个）
- ✅ 文件格式验证

### 2. 文件解析流程

1. **上传阶段**
   - 用户拖拽或点击上传文件
   - 前端实时校验文件大小和数量
   - 显示文件列表和文件信息

2. **解析阶段**
   - 用户点击"开始解析"按钮
   - 前端显示解析进度
   - 禁用输入框，提示"正在解析文件，请稍候..."
   - 调用后端批量转换 API

3. **完成阶段**
   - 显示解析结果（成功/失败）
   - 更新输入框提示："已加载 X 个文件，输入问题..."
   - 用户可以开始提问

### 3. 上下文集成（后端处理）

解析完成后，用户发送消息时：

**前端**：
- 提取成功解析的文件 ID
- 发送请求：`{ message: "用户问题", file_ids: ["file_123", "file_456"] }`
- 显示文件标记：📎 包含 X 个文件

**后端**：
- 接收文件 ID 列表
- 从存储中获取文件内容
- 构建完整上下文：
  ```
  请结合以下文件内容和用户问题进行解答：

  ### 文件: file1.pdf
  [文件1的markdown内容]

  ---

  ### 文件: file2.pdf
  [文件2的markdown内容]

  ---

  用户问题：[用户的实际问题]
  ```
- 将完整消息传递给智能体

## 📁 新增和修改的文件

### 前端文件（3个新增，2个修改）

#### 新增文件

1. **`frontend/src/components/FileUpload.jsx`**
   - 文件上传组件
   - 功能：
     - 拖拽上传
     - 文件列表显示
     - 文件大小和格式校验
     - 解析进度显示
     - 解析结果反馈

2. **`frontend/src/components/FileUpload.css`**
   - 文件上传组件样式
   - 支持深色/浅色主题
   - 响应式设计

#### 修改文件

3. **`frontend/src/App.jsx`**
   - 集成文件上传组件
   - 添加文件状态管理：
     - `uploadedFiles` - 上传的文件列表
     - `parsedFiles` - 已解析的文件列表
     - `isParsing` - 是否正在解析
   - 修改消息发送逻辑，添加文件上下文
   - 添加文件标记显示

4. **`frontend/src/App.css`**
   - 添加文件上传区域样式
   - 添加文件上下文标记样式

### 后端文件（2个修改）

5. **`backend/api/routes.py`**
   - 修改批量转换 API：
     - 最多 10 个文件（从 20 个调整）
     - 单个文件最大 100MB
     - 生成文件 ID 并存储内容
   - 修改聊天 API：
     - 接收文件 ID 列表
     - 构建文件上下文
     - 传递给智能体
   - 添加辅助函数：
     - `_build_message_with_file_context()` - 构建上下文

6. **`backend/models.py`**
   - 修改 `ChatRequest` 模型：
     - 添加 `file_ids` 字段

## 🚀 使用流程

### 1. 启动服务

```bash
# 后端（终端 1）
cd backend
python main.py

# 前端（终端 2）
cd frontend
npm run dev
```

### 2. 上传文件

1. 打开浏览器访问 http://localhost:3002
2. 选择对话模式（普通对话或测试用例智能体）
3. 在输入框上方看到文件上传区域
4. 拖拽或点击上传文件（支持多个文件）

### 3. 解析文件

1. 上传完成后，点击"开始解析"按钮
2. 等待解析完成（显示进度条）
3. 查看解析结果（成功/失败）

### 4. 提问

1. 解析成功后，输入框提示变为"已加载 X 个文件，输入问题..."
2. 输入问题，按 Enter 发送
3. 系统自动将文件内容作为上下文发送给智能体
4. 用户消息显示文件标记：📎 包含 X 个文件

## 🎨 界面特性

### 文件上传区域
- 拖拽上传支持
- 文件列表显示
- 文件大小显示
- 解析状态图标：
  - ⏳ 等待解析
  - 🔄 解析中
  - ✅ 解析成功
  - ❌ 解析失败

### 输入框提示
- 默认："输入消息，按 Enter 发送..."
- 解析中："正在解析文件，请稍候..."
- 已加载文件："已加载 X 个文件，输入问题..."

### 用户消息标记
- 包含文件的消息显示：📎 包含 X 个文件
- 蓝色标记，清晰可见

## 🔧 技术实现

### 前端技术栈
- **React** - UI 框架
- **Ant Design** - UI 组件库
- **Framer Motion** - 动画效果
- **Upload 组件** - 文件上传

### 后端技术栈
- **FastAPI** - Web 框架
- **marker-pdf** - 文件转换库
- **multipart/form-data** - 文件上传处理

### 文件校验逻辑

#### 前端校验
```javascript
// 文件大小检查
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
if (file.size > MAX_FILE_SIZE) {
  message.error(`文件超过 100MB 限制`);
  return false;
}

// 文件数量检查
const MAX_FILE_COUNT = 10;
if (fileList.length > MAX_FILE_COUNT) {
  message.error(`最多只能上传 10 个文件`);
  return Upload.LIST_IGNORE;
}

// 文件格式检查
const SUPPORTED_FORMATS = ['.pdf', '.png', '.jpg', ...];
const isSupported = SUPPORTED_FORMATS.some(format => 
  fileName.endsWith(format)
);
```

#### 后端校验
```python
# 文件数量检查
if len(files) > 10:
    raise HTTPException(status_code=400, detail="单次最多支持 10 个文件")

# 文件大小检查
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
for file in files:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"文件 {file.filename} 大小超过限制（最大 100MB）"
        )
```

### 前端：提取文件 ID

```javascript
// 获取成功解析的文件 ID
const fileIds = parsedFiles
  .filter(f => f.success && f.file_id)
  .map(f => f.file_id);

// 发送请求
const response = await fetch(endpoint, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userMessage,  // 原始用户消息
    file_ids: fileIds.length > 0 ? fileIds : undefined  // 文件 ID 列表
  }),
});
```

### 后端：构建上下文

```python
def _build_message_with_file_context(message: str, file_ids: Optional[list[str]]) -> str:
    """构建包含文件上下文的消息"""
    if not file_ids or len(file_ids) == 0:
        return message

    # 获取文件内容
    file_contexts = []
    for file_id in file_ids:
        if file_id in file_storage:
            file_data = file_storage[file_id]
            filename = file_data.get("filename", "unknown")
            markdown = file_data.get("markdown", "")

            if markdown:
                file_contexts.append(f"### 文件: {filename}\n\n{markdown}")

    if not file_contexts:
        return message

    # 构建完整消息
    context_text = "\n\n---\n\n".join(file_contexts)
    full_message = f"""请结合以下文件内容和用户问题进行解答：

{context_text}

---

用户问题：{message}"""

    return full_message
```

## 📊 支持的文件格式

- **PDF**: .pdf
- **图片**: .png, .jpg, .jpeg, .gif, .bmp, .tiff
- **PowerPoint**: .pptx, .ppt
- **Word**: .docx, .doc
- **Excel**: .xlsx, .xls
- **HTML**: .html, .htm
- **EPUB**: .epub

## 🎯 用户体验优化

### 1. 实时反馈
- 文件上传时显示文件信息
- 解析时显示进度条
- 解析完成后显示成功/失败状态

### 2. 状态管理
- 解析中禁用输入框
- 解析中禁用文件上传
- 发送消息时禁用文件操作

### 3. 错误处理
- 文件大小超限提示
- 文件数量超限提示
- 文件格式不支持提示
- 解析失败错误提示

### 4. 视觉反馈
- 文件列表动画效果
- 解析进度动画
- 状态图标变化
- 主题适配（深色/浅色）

## 🔍 测试场景

### 场景 1: 上传单个 PDF 文件
1. 上传一个 PDF 文件
2. 点击"开始解析"
3. 等待解析完成
4. 输入问题："总结一下文件内容"
5. 查看智能体回复

### 场景 2: 上传多个文件
1. 上传 3 个不同格式的文件（PDF, DOCX, PNG）
2. 点击"开始解析"
3. 查看解析结果
4. 输入问题："对比这几个文件的内容"
5. 查看智能体回复

### 场景 3: 文件大小限制测试
1. 尝试上传超过 100MB 的文件
2. 查看错误提示
3. 上传符合大小限制的文件

### 场景 4: 文件数量限制测试
1. 尝试上传超过 10 个文件
2. 查看错误提示
3. 上传 10 个以内的文件

### 场景 5: 不支持格式测试
1. 尝试上传不支持的文件格式（如 .txt）
2. 查看错误提示
3. 上传支持的文件格式

## 📝 注意事项

1. **文件大小**
   - 单个文件最大 100MB
   - 建议上传较小的文件以提高解析速度

2. **文件数量**
   - 最多 10 个文件
   - 文件越多，解析时间越长

3. **解析时间**
   - 取决于文件大小和数量
   - 大文件可能需要较长时间
   - 解析期间请耐心等待

4. **上下文长度**
   - 文件内容会作为上下文发送
   - 过多或过大的文件可能导致上下文过长
   - 建议上传相关性强的文件

## ✨ 核心特性总结

1. ✅ **双重校验** - 前后端都进行文件大小和数量校验
2. ✅ **实时反馈** - 解析过程中显示进度和状态
3. ✅ **禁用控制** - 解析期间禁用输入，防止误操作
4. ✅ **上下文集成** - 自动将文件内容作为上下文
5. ✅ **视觉标记** - 用户消息显示文件标记
6. ✅ **错误处理** - 完善的错误提示和处理
7. ✅ **主题适配** - 支持深色/浅色主题
8. ✅ **响应式设计** - 适配不同屏幕尺寸

文件上传功能已完全实现并可立即使用！🎉

