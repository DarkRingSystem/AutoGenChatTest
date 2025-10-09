# Markdown 转换组件

> 基于 [marker](https://github.com/datalab-to/marker) 官方库实现的高精度文档转换组件

## 🎯 功能特性

- ✅ 支持多种文件格式（PDF, 图片, PPTX, DOCX, XLSX, HTML, EPUB）
- ✅ 高精度转换，基于深度学习模型
- ✅ 可选 LLM 增强模式
- ✅ 支持 OCR 识别
- ✅ 自动提取图片
- ✅ 多种输出格式（Markdown, JSON, HTML, Chunks）
- ✅ 提供 Python SDK 和 HTTP API

## 📦 安装

```bash
cd backend
pip install -r requirements.txt
```

## 🚀 快速开始

### Python SDK

```python
from services.markdown_converter_service import MarkdownConverterService

# 创建转换服务
converter = MarkdownConverterService()

# 转换文件
result = await converter.convert_file("document.pdf")

# 获取 Markdown
print(result["markdown"])
```

### HTTP API

```bash
# 启动服务
python main.py

# 转换文件
curl -X POST "http://localhost:8000/api/convert/markdown" \
  -F "file=@document.pdf"
```

## 📚 文档

- [完整使用指南](../backend/docs/MARKDOWN_CONVERTER_GUIDE.md)
- [快速开始](../backend/docs/MARKDOWN_CONVERTER_QUICKSTART.md)
- [实现文档](../backend/docs/MARKDOWN_CONVERTER_IMPLEMENTATION.md)

## 💡 示例代码

### 示例 1: 基础转换

```python
import asyncio
from services.markdown_converter_service import MarkdownConverterService

async def main():
    converter = MarkdownConverterService()
    result = await converter.convert_file("document.pdf")
    
    if result["success"]:
        print(result["markdown"])

asyncio.run(main())
```

### 示例 2: 使用 LLM 增强

```python
converter = MarkdownConverterService(
    use_llm=True,
    llm_service="marker.services.openai.OpenAIService",
    llm_api_key="your-api-key",
    llm_model="gpt-4"
)

result = await converter.convert_file("complex-document.pdf")
```

### 示例 3: 强制 OCR（扫描版文档）

```python
converter = MarkdownConverterService(force_ocr=True)
result = await converter.convert_file("scanned.pdf")
```

## 🔧 API 端点

### 转换文件

```
POST /api/convert/markdown
```

**参数**:
- `file`: 文件（必填）
- `use_llm`: 是否使用 LLM（可选）
- `force_ocr`: 是否强制 OCR（可选）
- `output_format`: 输出格式（可选）

**响应**:
```json
{
  "success": true,
  "message": "转换成功",
  "markdown": "# 文档内容...",
  "metadata": {...},
  "images": {...}
}
```

### 获取支持的格式

```
GET /api/convert/supported-formats
```

## 📖 支持的文件格式

| 类型 | 扩展名 |
|------|--------|
| PDF | `.pdf` |
| 图片 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff` |
| PowerPoint | `.pptx`, `.ppt` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| HTML | `.html`, `.htm` |
| EPUB | `.epub` |

## 🎨 输出格式

- **Markdown**: 标准 Markdown 格式（默认）
- **JSON**: 结构化 JSON 格式
- **HTML**: HTML 格式
- **Chunks**: 分块格式（适用于 RAG）

## 🧪 运行示例

### Python SDK 示例

```bash
python examples/markdown_converter_example.py
```

### HTTP API 示例

```bash
# 终端 1: 启动服务
python main.py

# 终端 2: 运行示例
python examples/markdown_converter_api_example.py
```

## 🧪 运行测试

```bash
pytest tests/test_markdown_converter.py -v
```

## ⚙️ 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_llm` | bool | False | 是否使用 LLM 提升精度 |
| `force_ocr` | bool | False | 是否强制 OCR |
| `disable_image_extraction` | bool | False | 是否禁用图片提取 |
| `output_format` | str | "markdown" | 输出格式 |
| `llm_service` | str | None | LLM 服务类路径 |
| `llm_api_key` | str | None | LLM API 密钥 |
| `llm_base_url` | str | None | LLM API 基础 URL |
| `llm_model` | str | None | LLM 模型名称 |

## 🔍 常见问题

### Q: 如何提升转换速度？

A: 
- 使用 GPU 加速（设置 `TORCH_DEVICE=cuda`）
- 禁用图片提取（`disable_image_extraction=True`）
- 不使用 LLM（`use_llm=False`）

### Q: 如何提升转换精度？

A:
- 使用 LLM 增强（`use_llm=True`）
- 强制 OCR（`force_ocr=True`）

### Q: 支持哪些 LLM 服务？

A: 支持 OpenAI, Gemini, Claude, Ollama 等

## 📁 文件结构

```
backend/
├── services/
│   └── markdown_converter_service.py  # 核心服务
├── api/
│   └── routes.py                      # API 路由（已更新）
├── models.py                          # 数据模型（已更新）
├── examples/
│   ├── markdown_converter_example.py      # Python SDK 示例
│   └── markdown_converter_api_example.py  # HTTP API 示例
├── tests/
│   └── test_markdown_converter.py     # 单元测试
├── docs/
│   ├── MARKDOWN_CONVERTER_GUIDE.md         # 完整指南
│   ├── MARKDOWN_CONVERTER_QUICKSTART.md    # 快速开始
│   └── MARKDOWN_CONVERTER_IMPLEMENTATION.md # 实现文档
└── requirements.txt                   # 依赖（已更新）
```

## 🌟 参考资料

- [marker 官方仓库](https://github.com/datalab-to/marker)
- [marker 官方文档](https://github.com/datalab-to/marker#readme)
- [API 文档](http://localhost:8000/docs)

## 📝 许可证

本组件基于 marker 库实现，遵循其许可证要求。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**开始使用**: 查看 [快速开始指南](../backend/docs/MARKDOWN_CONVERTER_QUICKSTART.md) 🚀

