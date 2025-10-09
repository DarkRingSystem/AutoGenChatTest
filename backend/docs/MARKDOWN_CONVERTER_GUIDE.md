# Markdown 转换服务使用指南

## 概述

Markdown 转换服务是一个基于 [marker](https://github.com/datalab-to/marker) 官方库实现的高精度文档转换组件，可以将各种格式的文件转换为 Markdown、JSON、HTML 或 Chunks 格式。

### 主要特性

- ✅ **多格式支持**: PDF, 图片, PPTX, DOCX, XLSX, HTML, EPUB
- ✅ **高精度转换**: 基于 marker 的深度学习模型
- ✅ **LLM 增强**: 可选使用 LLM 提升转换质量
- ✅ **OCR 支持**: 支持扫描版文档和图片 OCR
- ✅ **图片提取**: 自动提取文档中的图片
- ✅ **多种输出格式**: Markdown, JSON, HTML, Chunks
- ✅ **API 接口**: 提供 RESTful API 和 Python SDK

## 支持的文件格式

| 类型 | 扩展名 |
|------|--------|
| PDF | `.pdf` |
| 图片 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff` |
| PowerPoint | `.pptx`, `.ppt` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| HTML | `.html`, `.htm` |
| EPUB | `.epub` |

## 安装依赖

```bash
# 安装 marker 和相关依赖
pip install marker-pdf python-multipart

# 或者使用 requirements.txt
pip install -r backend/requirements.txt
```

## 使用方式

### 方式 1: Python SDK

#### 基础转换

```python
from services.markdown_converter_service import MarkdownConverterService

# 创建转换服务
converter = MarkdownConverterService(
    use_llm=False,
    force_ocr=False,
    disable_image_extraction=False,
    output_format="markdown"
)

# 转换文件
result = await converter.convert_file("/path/to/file.pdf")

if result["success"]:
    print(result["markdown"])  # Markdown 文本
    print(result["metadata"])  # 元数据
    print(result["images"])    # 提取的图片
```

#### 使用 LLM 增强转换

```python
converter = MarkdownConverterService(
    use_llm=True,
    output_format="markdown",
    llm_service="marker.services.openai.OpenAIService",
    llm_api_key="your-api-key",
    llm_base_url="https://api.openai.com/v1",
    llm_model="gpt-4"
)

result = await converter.convert_file("/path/to/file.pdf")
```

#### 强制 OCR（适用于扫描版文档）

```python
converter = MarkdownConverterService(
    force_ocr=True,  # 强制 OCR
    output_format="markdown"
)

result = await converter.convert_file("/path/to/scanned.pdf")
```

#### 从字节流转换（模拟文件上传）

```python
with open("/path/to/file.pdf", 'rb') as f:
    file_bytes = f.read()

result = await converter.convert_file_bytes(
    file_bytes=file_bytes,
    filename="document.pdf"
)
```

#### 批量转换多个文件（并发处理）

```python
converter = MarkdownConverterService()

# 准备文件列表
file_paths = [
    "/path/to/file1.pdf",
    "/path/to/file2.pdf",
    "/path/to/file3.pdf"
]

# 并发转换（最大并发数为 3）
results = await converter.convert_multiple_files(
    file_paths=file_paths,
    max_concurrent=3
)

# 处理结果
for result in results:
    if result["success"]:
        print(f"✅ {result['file_path']}: {len(result['markdown'])} 字符")
    else:
        print(f"❌ {result['file_path']}: {result['message']}")
```

#### 批量转换字节流

```python
# 准备文件数据
files_data = []
for file_path in file_paths:
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    files_data.append((file_bytes, Path(file_path).name))

# 并发转换
results = await converter.convert_multiple_file_bytes(
    files_data=files_data,
    max_concurrent=3
)
```

### 方式 2: HTTP API

#### 启动服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动。

#### API 端点

##### 1. 获取支持的文件格式

```bash
GET /api/convert/supported-formats
```

**响应示例:**
```json
{
  "supported_formats": [".pdf", ".png", ".jpg", ...],
  "total": 13
}
```

##### 2. 转换单个文件为 Markdown

```bash
POST /api/convert/markdown
Content-Type: multipart/form-data
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 要转换的文件 |
| `use_llm` | Boolean | ❌ | 是否使用 LLM（默认: false） |
| `force_ocr` | Boolean | ❌ | 是否强制 OCR（默认: false） |
| `disable_image_extraction` | Boolean | ❌ | 是否禁用图片提取（默认: false） |
| `page_range` | String | ❌ | 页面范围，如 "0,5-10,20" |
| `output_format` | String | ❌ | 输出格式（默认: markdown） |
| `llm_api_key` | String | ❌ | LLM API 密钥 |
| `llm_base_url` | String | ❌ | LLM API 基础 URL |
| `llm_model` | String | ❌ | LLM 模型名称 |

**使用 curl:**

```bash
# 基础转换
curl -X POST "http://localhost:8000/api/convert/markdown" \
  -F "file=@/path/to/file.pdf" \
  -F "use_llm=false" \
  -F "force_ocr=false" \
  -F "output_format=markdown"

# 使用 LLM 增强
curl -X POST "http://localhost:8000/api/convert/markdown" \
  -F "file=@/path/to/file.pdf" \
  -F "use_llm=true" \
  -F "llm_api_key=your-api-key" \
  -F "llm_base_url=https://api.openai.com/v1" \
  -F "llm_model=gpt-4"
```

**使用 Python requests:**

```python
import requests

url = "http://localhost:8000/api/convert/markdown"

with open("/path/to/file.pdf", 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/octet-stream')}
    data = {
        'use_llm': 'false',
        'force_ocr': 'false',
        'output_format': 'markdown'
    }
    
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    if result['success']:
        print(result['markdown'])
```

**响应示例:**

```json
{
  "success": true,
  "message": "转换成功",
  "markdown": "# 文档标题\n\n这是转换后的内容...",
  "metadata": {
    "page_count": 10,
    "table_of_contents": [...]
  },
  "images": {}
}
```

##### 3. 批量转换多个文件为 Markdown

```bash
POST /api/convert/markdown/batch
Content-Type: multipart/form-data
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | File[] | ✅ | 要转换的多个文件（最多 20 个） |
| `use_llm` | Boolean | ❌ | 是否使用 LLM（默认: false） |
| `force_ocr` | Boolean | ❌ | 是否强制 OCR（默认: false） |
| `disable_image_extraction` | Boolean | ❌ | 是否禁用图片提取（默认: false） |
| `page_range` | String | ❌ | 页面范围 |
| `output_format` | String | ❌ | 输出格式（默认: markdown） |
| `max_concurrent` | Integer | ❌ | 最大并发数（默认: 3，建议不超过 5） |
| `llm_api_key` | String | ❌ | LLM API 密钥 |
| `llm_base_url` | String | ❌ | LLM API 基础 URL |
| `llm_model` | String | ❌ | LLM 模型名称 |

**使用 curl:**

```bash
# 批量转换多个文件
curl -X POST "http://localhost:8000/api/convert/markdown/batch" \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf" \
  -F "files=@file3.pdf" \
  -F "max_concurrent=3"
```

**使用 Python requests:**

```python
import requests

url = "http://localhost:8000/api/convert/markdown/batch"

# 准备多个文件
files = []
for file_path in ["/path/to/file1.pdf", "/path/to/file2.pdf"]:
    with open(file_path, 'rb') as f:
        files.append(('files', (Path(file_path).name, f.read(), 'application/octet-stream')))

data = {
    'max_concurrent': '3',
    'output_format': 'markdown'
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"总文件数: {result['total']}")
print(f"成功: {result['success_count']}")
print(f"失败: {result['failed_count']}")

for file_result in result['results']:
    if file_result['success']:
        print(f"✅ {file_result['filename']}")
    else:
        print(f"❌ {file_result['filename']}: {file_result['message']}")
```

**响应示例:**

```json
{
  "total": 3,
  "success_count": 2,
  "failed_count": 1,
  "results": [
    {
      "filename": "doc1.pdf",
      "success": true,
      "message": "转换成功",
      "markdown": "# 文档1...",
      "metadata": {...},
      "images": {}
    },
    {
      "filename": "doc2.pdf",
      "success": true,
      "message": "转换成功",
      "markdown": "# 文档2...",
      "metadata": {...},
      "images": {}
    },
    {
      "filename": "doc3.pdf",
      "success": false,
      "message": "转换失败: 不支持的文件格式"
    }
  ]
}
```

## 配置选项

### 输出格式

- `markdown`: Markdown 格式（默认）
- `json`: JSON 格式（包含结构化信息）
- `html`: HTML 格式
- `chunks`: 分块格式（适用于 RAG）

### LLM 服务

支持以下 LLM 服务：

1. **OpenAI / 兼容 API**
   ```python
   llm_service="marker.services.openai.OpenAIService"
   llm_api_key="your-api-key"
   llm_base_url="https://api.openai.com/v1"
   llm_model="gpt-4"
   ```

2. **Google Gemini**
   ```python
   llm_service="marker.services.gemini.GoogleGeminiService"
   llm_api_key="your-gemini-api-key"
   ```

3. **Claude**
   ```python
   llm_service="marker.services.claude.ClaudeService"
   llm_api_key="your-claude-api-key"
   ```

4. **Ollama（本地模型）**
   ```python
   llm_service="marker.services.ollama.OllamaService"
   ```

## 示例代码

### 示例 1: 基础转换

参考 `backend/examples/markdown_converter_example.py`

```bash
python backend/examples/markdown_converter_example.py
```

### 示例 2: API 调用

参考 `backend/examples/markdown_converter_api_example.py`

```bash
# 先启动服务
python backend/main.py

# 在另一个终端运行示例
python backend/examples/markdown_converter_api_example.py
```

## 性能优化建议

1. **批量处理**: 对于多个文件，建议复用同一个 `MarkdownConverterService` 实例
2. **GPU 加速**: marker 支持 GPU 加速，设置 `TORCH_DEVICE=cuda` 环境变量
3. **禁用图片提取**: 如果不需要图片，设置 `disable_image_extraction=True` 可以提升速度
4. **选择性使用 LLM**: LLM 会显著增加处理时间，仅在需要最高精度时使用

## 常见问题

### Q: 转换速度慢怎么办？

A: 
- 使用 GPU 加速（设置 `TORCH_DEVICE=cuda`）
- 禁用图片提取（`disable_image_extraction=True`）
- 不使用 LLM（`use_llm=False`）

### Q: 扫描版 PDF 识别不准确？

A: 设置 `force_ocr=True` 强制使用 OCR

### Q: 如何提升转换精度？

A: 
- 设置 `use_llm=True` 使用 LLM 增强
- 设置 `force_ocr=True` 对于图片密集型文档

### Q: 支持哪些语言？

A: marker 的 OCR 引擎 surya 支持多种语言，详见 [surya 文档](https://github.com/VikParuchuri/surya)

## 参考资料

- [marker 官方仓库](https://github.com/datalab-to/marker)
- [marker 文档](https://github.com/datalab-to/marker#readme)
- [API 文档](http://localhost:8000/docs)（启动服务后访问）

## 许可证

本组件基于 marker 库实现，遵循其许可证要求。

