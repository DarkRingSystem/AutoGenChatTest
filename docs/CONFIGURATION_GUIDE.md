# 配置管理指南

本文档说明项目中的配置管理方式和最佳实践。

## 📋 目录

- [后端配置](#后端配置)
- [Markdown 转换配置](#markdown-转换配置)
- [环境变量](#环境变量)
- [配置优先级](#配置优先级)

---

## 🔧 后端配置

### 配置文件位置

**主配置文件**：`backend/config.py`

这是后端的统一配置管理文件，使用 Pydantic Settings 进行配置管理。

### 配置类结构

```python
class Settings(BaseSettings):
    # AI 模型配置
    api_key: str
    model_name: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/v1"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Markdown 转换配置
    markdown_use_llm: bool = False
    markdown_force_ocr: bool = False
    markdown_disable_image_extraction: bool = False
    markdown_output_format: str = "markdown"
    markdown_max_file_size_mb: int = 100
    markdown_max_batch_files: int = 10
    markdown_max_concurrent: int = 3
    
    # Markdown LLM 配置（可选）
    markdown_llm_service: Optional[str] = None
    markdown_llm_api_key: Optional[str] = None
    markdown_llm_base_url: Optional[str] = None
    markdown_llm_model: Optional[str] = None
```

### 使用配置

```python
from config import settings

# 访问配置
print(settings.model_name)
print(settings.markdown_max_file_size_mb)

# 在 API 路由中使用
if len(files) > settings.markdown_max_batch_files:
    raise HTTPException(status_code=400, detail="文件数量超限")
```

---

## 📄 Markdown 转换配置

### Marker 配置说明

Marker 是后端使用的文档转 Markdown 工具，支持以下配置：

#### 基础配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `markdown_use_llm` | bool | false | 是否使用 LLM 提升转换精度 |
| `markdown_force_ocr` | bool | false | 是否强制对所有内容进行 OCR |
| `markdown_disable_image_extraction` | bool | false | 是否禁用图片提取 |
| `markdown_output_format` | str | "markdown" | 输出格式 (markdown/json/html/chunks) |

#### 文件限制配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `markdown_max_file_size_mb` | int | 100 | 单个文件最大大小（MB） |
| `markdown_max_batch_files` | int | 10 | 批量处理最大文件数 |
| `markdown_max_concurrent` | int | 3 | 最大并发转换数 |

#### LLM 配置（可选）

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `markdown_llm_service` | str | None | LLM 服务类路径 |
| `markdown_llm_api_key` | str | None | LLM API 密钥 |
| `markdown_llm_base_url` | str | None | LLM API 基础 URL |
| `markdown_llm_model` | str | None | LLM 模型名称 |

---

## 🌍 环境变量

### 后端环境变量

在 `backend/.env` 文件中配置：

```bash
# AI 模型配置
API_KEY=your_deepseek_api_key_here
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1

# 服务器配置
HOST=0.0.0.0
PORT=8000

# Markdown 转换配置
MARKDOWN_USE_LLM=false
MARKDOWN_FORCE_OCR=false
MARKDOWN_DISABLE_IMAGE_EXTRACTION=false
MARKDOWN_OUTPUT_FORMAT=markdown
MARKDOWN_MAX_FILE_SIZE_MB=100
MARKDOWN_MAX_BATCH_FILES=10
MARKDOWN_MAX_CONCURRENT=3

# Markdown LLM 配置（可选）
# MARKDOWN_LLM_SERVICE=marker.services.openai.OpenAIService
# MARKDOWN_LLM_API_KEY=your_openai_api_key_here
# MARKDOWN_LLM_BASE_URL=https://api.openai.com/v1
# MARKDOWN_LLM_MODEL=gpt-4
```

---

## 🔄 配置优先级

### 后端配置优先级

1. **API 请求参数**（最高优先级）
2. **环境变量**（`.env` 文件）
3. **配置文件默认值**（`config.py`）

示例：

```python
# 1. API 参数优先
use_llm = Form(default=None)  # 用户传入

# 2. 如果 API 参数为 None，使用配置文件
final_use_llm = use_llm if use_llm is not None else settings.markdown_use_llm

# 3. 配置文件从环境变量读取，如果环境变量未设置，使用默认值
markdown_use_llm: bool = False  # 默认值
```

---

## 📝 最佳实践

### 1. 统一管理

✅ **推荐**：在 `config.py` 中统一管理后端配置
❌ **避免**：在代码中硬编码配置值

### 2. 环境变量

✅ **推荐**：敏感信息（API Key）使用环境变量  
❌ **避免**：将敏感信息提交到版本控制

### 3. 默认值

✅ **推荐**：为所有配置提供合理的默认值  
❌ **避免**：强制要求所有配置都必须设置

### 4. 文档

✅ **推荐**：在 `.env.example` 中提供配置示例  
✅ **推荐**：在代码中添加配置说明注释

### 5. 验证

✅ **推荐**：在启动时验证必需的配置  
✅ **推荐**：提供清晰的错误提示

---

## 🔍 配置示例

### 启用 LLM 提升转换精度

**backend/.env**:
```bash
MARKDOWN_USE_LLM=true
MARKDOWN_LLM_SERVICE=marker.services.openai.OpenAIService
MARKDOWN_LLM_API_KEY=sk-xxx
MARKDOWN_LLM_BASE_URL=https://api.openai.com/v1
MARKDOWN_LLM_MODEL=gpt-4
```

### 调整文件大小限制

**backend/.env**:
```bash
MARKDOWN_MAX_FILE_SIZE_MB=200
MARKDOWN_MAX_BATCH_FILES=20
MARKDOWN_MAX_CONCURRENT=5
```

---

## 🆘 常见问题

### Q: 如何修改默认配置？

A: 修改 `backend/config.py` 中的默认值，或在 `.env` 文件中设置环境变量。

### Q: API 参数和配置文件哪个优先？

A: API 参数优先级最高，可以覆盖配置文件的设置。

### Q: 如何添加新的配置项？

A: 
1. 在 `backend/config.py` 的 `Settings` 类中添加新字段
2. 在 `backend/.env.example` 中添加示例
3. 更新此文档

---

## 📚 相关文档

- [Pydantic Settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Marker 配置文档](https://github.com/datalab-to/marker)
- [FastAPI 配置文档](https://fastapi.tiangolo.com/advanced/settings/)

