# Markdown 转换组件实现文档

## 实现概述

基于您的要求，我实现了一套完整的 Markdown 转换组件，该组件：

1. ✅ **接收文件并返回 Markdown 格式文本**
2. ✅ **严格参考 marker 官方源码实现**（https://github.com/datalab-to/marker）
3. ✅ **遵循项目现有的代码架构和风格**

## 实现的文件清单

### 核心服务层

#### 1. `backend/services/markdown_converter_service.py`
**功能**: Markdown 转换服务核心实现

**主要类**: `MarkdownConverterService`

**核心方法**:
- `convert_file(file_path, page_range)`: 转换本地文件
- `convert_file_bytes(file_bytes, filename, page_range)`: 转换字节流（支持文件上传）
- `get_supported_formats()`: 获取支持的文件格式
- `is_supported_file(filename)`: 检查文件是否支持

**参考的 marker 官方代码**:
```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser
```

**实现特点**:
- 完全基于 marker 官方 API
- 支持所有 marker 支持的文件格式（PDF, 图片, PPTX, DOCX, XLSX, HTML, EPUB）
- 支持 LLM 增强模式
- 支持强制 OCR
- 支持图片提取
- 支持多种输出格式（markdown, json, html, chunks）

### 数据模型层

#### 2. `backend/models.py` (更新)
**新增模型**:

**`MarkdownConvertRequest`**: 转换请求模型
```python
class MarkdownConvertRequest(BaseModel):
    use_llm: bool = False
    force_ocr: bool = False
    disable_image_extraction: bool = False
    page_range: Optional[str] = None
    output_format: str = "markdown"
```

**`MarkdownConvertResponse`**: 转换响应模型
```python
class MarkdownConvertResponse(BaseModel):
    success: bool
    message: str
    markdown: str
    metadata: dict
    images: dict
```

### API 路由层

#### 3. `backend/api/routes.py` (更新)
**新增端点**:

**`POST /api/convert/markdown`**: 文件转换端点
- 支持文件上传（multipart/form-data）
- 支持所有配置参数
- 返回转换结果

**`GET /api/convert/supported-formats`**: 获取支持的文件格式
- 返回所有支持的文件扩展名列表

### 示例代码

#### 4. `backend/examples/markdown_converter_example.py`
**功能**: Python SDK 使用示例

**包含示例**:
- 基础转换
- LLM 增强转换
- 强制 OCR 转换
- JSON 格式输出
- 检查支持的格式
- 从字节流转换

#### 5. `backend/examples/markdown_converter_api_example.py`
**功能**: HTTP API 使用示例

**包含示例**:
- 获取支持的格式
- 基础 PDF 转换
- 使用 LLM 增强
- 强制 OCR 转换
- JSON 格式输出

### 测试代码

#### 6. `backend/tests/test_markdown_converter.py`
**功能**: 单元测试

**测试覆盖**:
- 服务初始化
- 文件格式检查
- 文件转换
- 字节流转换
- LLM 配置
- API 端点

### 文档

#### 7. `backend/docs/MARKDOWN_CONVERTER_GUIDE.md`
**功能**: 完整使用指南

**内容**:
- 功能概述
- 支持的文件格式
- 安装说明
- Python SDK 使用
- HTTP API 使用
- 配置选项
- 性能优化
- 常见问题

#### 8. `backend/docs/MARKDOWN_CONVERTER_QUICKSTART.md`
**功能**: 快速开始指南

**内容**:
- 5 分钟快速上手
- 常用场景示例
- 配置参数说明
- 性能参考
- 故障排查

### 依赖配置

#### 9. `backend/requirements.txt` (更新)
**新增依赖**:
```
marker-pdf>=1.0.0
python-multipart>=0.0.6
```

## 架构设计

### 分层架构

```
┌─────────────────────────────────────────┐
│         API Layer (routes.py)           │
│  - POST /api/convert/markdown           │
│  - GET /api/convert/supported-formats   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Service Layer (markdown_converter)   │
│  - MarkdownConverterService             │
│  - convert_file()                       │
│  - convert_file_bytes()                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Marker Library (Official)          │
│  - PdfConverter                         │
│  - ConfigParser                         │
│  - create_model_dict()                  │
│  - text_from_rendered()                 │
└─────────────────────────────────────────┘
```

### 与现有代码的集成

本实现完全遵循项目现有的架构模式：

1. **服务层**: 参考 `ai_service.py` 的设计模式
2. **API 层**: 参考现有的路由设计
3. **模型层**: 使用 Pydantic 模型，与现有模型一致
4. **示例代码**: 参考 `file_processpr_example.py` 的风格

## 核心实现细节

### 1. 转换器初始化

```python
def _initialize_converter(self) -> None:
    """初始化 marker 转换器"""
    # 创建配置解析器（参考 marker 官方示例）
    config_parser = ConfigParser(self.config)
    
    # 创建转换器（完全按照 marker 官方 API）
    self.converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service()
    )
```

**参考**: marker 官方 README 中的 "Use from python" 部分

### 2. 文件转换

```python
async def convert_file(self, file_path: str) -> Dict[str, Any]:
    """转换文件为 Markdown"""
    # 执行转换（参考 marker 官方 API）
    rendered = self.converter(file_path)
    
    # 提取文本和图片（参考 marker 官方 API）
    text, metadata, images = text_from_rendered(rendered)
    
    return {
        "success": True,
        "markdown": text,
        "metadata": metadata,
        "images": images
    }
```

**参考**: marker 官方 README 中的转换示例

### 3. LLM 配置

```python
# 支持多种 LLM 服务（参考 marker 官方文档）
if "openai" in llm_service.lower():
    self.config["openai_api_key"] = llm_api_key
    self.config["openai_base_url"] = llm_base_url
    self.config["openai_model"] = llm_model
elif "gemini" in llm_service.lower():
    self.config["gemini_api_key"] = llm_api_key
elif "claude" in llm_service.lower():
    self.config["claude_api_key"] = llm_api_key
```

**参考**: marker 官方 README 中的 "LLM Services" 部分

## 使用示例

### Python SDK

```python
from services.markdown_converter_service import MarkdownConverterService

# 创建服务
converter = MarkdownConverterService()

# 转换文件
result = await converter.convert_file("document.pdf")

# 获取 Markdown
markdown_text = result["markdown"]
```

### HTTP API

```bash
curl -X POST "http://localhost:8000/api/convert/markdown" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"
```

## 支持的功能

### 文件格式
- ✅ PDF (.pdf)
- ✅ 图片 (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
- ✅ PowerPoint (.pptx, .ppt)
- ✅ Word (.docx, .doc)
- ✅ Excel (.xlsx, .xls)
- ✅ HTML (.html, .htm)
- ✅ EPUB (.epub)

### 转换选项
- ✅ 基础转换
- ✅ LLM 增强（支持 OpenAI, Gemini, Claude, Ollama）
- ✅ 强制 OCR
- ✅ 图片提取
- ✅ 页面范围选择

### 输出格式
- ✅ Markdown
- ✅ JSON
- ✅ HTML
- ✅ Chunks

## 测试方法

### 1. 运行 Python SDK 示例

```bash
cd backend
python examples/markdown_converter_example.py
```

### 2. 运行 API 示例

```bash
# 终端 1: 启动服务
python main.py

# 终端 2: 运行示例
python examples/markdown_converter_api_example.py
```

### 3. 运行单元测试

```bash
pytest tests/test_markdown_converter.py -v
```

## 性能特点

- **速度**: 基于 marker 的高效转换引擎
- **精度**: 支持 LLM 增强，提升转换质量
- **灵活性**: 支持多种配置选项
- **可扩展性**: 易于添加新的转换选项

## 参考资料

1. **marker 官方仓库**: https://github.com/datalab-to/marker
2. **marker 官方文档**: README.md 中的使用说明
3. **项目现有代码**: 
   - `backend/examples/file_processpr_example.py`
   - `backend/services/ai_service.py`
   - `backend/api/routes.py`

## 总结

本实现完全满足您的要求：

1. ✅ **接收文件，返回 Markdown**: 通过 `convert_file()` 和 `convert_file_bytes()` 方法
2. ✅ **参考 marker 官方源码**: 严格按照 marker 官方 API 实现
3. ✅ **遵循项目架构**: 与现有代码风格一致
4. ✅ **提供完整示例**: Python SDK 和 HTTP API 示例
5. ✅ **详细文档**: 使用指南和快速开始文档
6. ✅ **单元测试**: 覆盖主要功能

您可以立即开始使用这个组件进行文件到 Markdown 的转换！

