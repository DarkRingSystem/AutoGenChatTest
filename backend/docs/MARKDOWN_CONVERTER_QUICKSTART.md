# Markdown 转换服务 - 快速开始

## 5 分钟快速上手

### 步骤 1: 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

这将安装以下关键依赖：
- `marker-pdf`: marker 官方库
- `python-multipart`: 文件上传支持
- 其他必需依赖

### 步骤 2: 运行示例代码

#### 方式 A: 直接使用 Python SDK

```bash
python examples/markdown_converter_example.py
```

这将运行多个示例，展示：
- ✅ 基础文件转换
- ✅ 强制 OCR 转换
- ✅ 从字节流转换
- ✅ 检查支持的文件格式

#### 方式 B: 使用 HTTP API

**终端 1 - 启动服务:**
```bash
python main.py
```

**终端 2 - 运行 API 示例:**
```bash
python examples/markdown_converter_api_example.py
```

### 步骤 3: 自定义使用

#### Python SDK 示例

```python
import asyncio
from services.markdown_converter_service import MarkdownConverterService

async def convert_my_file():
    # 创建转换服务
    converter = MarkdownConverterService(
        use_llm=False,           # 不使用 LLM（更快）
        force_ocr=False,         # 不强制 OCR
        output_format="markdown" # 输出 Markdown 格式
    )
    
    # 转换文件
    result = await converter.convert_file("your-file.pdf")
    
    if result["success"]:
        # 保存 Markdown 文件
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result["markdown"])
        print("✅ 转换成功！输出已保存到 output.md")
    else:
        print(f"❌ 转换失败: {result['message']}")

# 运行
asyncio.run(convert_my_file())
```

#### HTTP API 示例

```python
import requests

# 转换文件
with open("your-file.pdf", "rb") as f:
    files = {"file": ("document.pdf", f)}
    data = {"output_format": "markdown"}
    
    response = requests.post(
        "http://localhost:8000/api/convert/markdown",
        files=files,
        data=data
    )
    
    result = response.json()
    
    if result["success"]:
        # 保存 Markdown
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result["markdown"])
        print("✅ 转换成功！")
```

## 常用场景

### 场景 1: 转换 PDF 为 Markdown

```python
converter = MarkdownConverterService()
result = await converter.convert_file("document.pdf")
```

### 场景 2: 转换扫描版 PDF（强制 OCR）

```python
converter = MarkdownConverterService(force_ocr=True)
result = await converter.convert_file("scanned.pdf")
```

### 场景 3: 使用 LLM 提升精度

```python
converter = MarkdownConverterService(
    use_llm=True,
    llm_service="marker.services.openai.OpenAIService",
    llm_api_key="your-api-key",
    llm_base_url="https://api.openai.com/v1",
    llm_model="gpt-4"
)
result = await converter.convert_file("complex-document.pdf")
```

### 场景 4: 转换图片中的文字

```python
converter = MarkdownConverterService(force_ocr=True)
result = await converter.convert_file("screenshot.png")
```

### 场景 5: 批量转换多个文件（并发处理）

```python
import asyncio
from pathlib import Path

async def batch_convert():
    converter = MarkdownConverterService()

    # 获取所有 PDF 文件
    file_paths = [str(fp) for fp in Path("input_folder").glob("*.pdf")]

    # 并发转换（最大并发数为 3）
    results = await converter.convert_multiple_files(
        file_paths=file_paths,
        max_concurrent=3
    )

    # 保存结果
    for result in results:
        if result["success"]:
            file_path = Path(result["file_path"])
            output_path = f"output/{file_path.stem}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["markdown"])
            print(f"✅ {file_path.name} 转换成功")
        else:
            print(f"❌ {result['file_path']}: {result['message']}")

asyncio.run(batch_convert())
```

### 场景 6: 批量转换（HTTP API）

```python
import requests
from pathlib import Path

# 准备多个文件
files = []
for file_path in ["/path/to/file1.pdf", "/path/to/file2.pdf"]:
    with open(file_path, 'rb') as f:
        files.append(('files', (Path(file_path).name, f.read())))

data = {'max_concurrent': '3'}

# 批量转换
response = requests.post(
    "http://localhost:8000/api/convert/markdown/batch",
    files=files,
    data=data
)

result = response.json()
print(f"成功: {result['success_count']}/{result['total']}")
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_llm` | bool | False | 是否使用 LLM 提升精度 |
| `force_ocr` | bool | False | 是否强制 OCR（适用于扫描版） |
| `disable_image_extraction` | bool | False | 是否禁用图片提取 |
| `output_format` | str | "markdown" | 输出格式（markdown/json/html/chunks） |
| `llm_service` | str | None | LLM 服务类路径 |
| `llm_api_key` | str | None | LLM API 密钥 |
| `llm_base_url` | str | None | LLM API 基础 URL |
| `llm_model` | str | None | LLM 模型名称 |

## 输出格式

### Markdown 格式（默认）

```markdown
# 文档标题

## 章节 1

这是正文内容...

| 表头1 | 表头2 |
|-------|-------|
| 数据1 | 数据2 |

![图片](image_id)
```

### JSON 格式

```json
{
  "success": true,
  "message": "转换成功",
  "markdown": "...",
  "metadata": {
    "page_count": 10,
    "table_of_contents": [...]
  },
  "images": {
    "image_id": "base64_encoded_data"
  }
}
```

## 性能参考

| 场景 | 处理时间 | 说明 |
|------|----------|------|
| 简单 PDF（10页） | ~3-5秒 | 不使用 LLM |
| 复杂 PDF（10页） | ~10-15秒 | 使用 LLM |
| 扫描版 PDF（10页） | ~15-20秒 | 强制 OCR |
| 图片 OCR | ~1-2秒 | 单张图片 |

*注: 使用 GPU 可显著提升速度*

## 故障排查

### 问题 1: 安装 marker-pdf 失败

**解决方案:**
```bash
# 确保 Python 版本 >= 3.10
python --version

# 升级 pip
pip install --upgrade pip

# 重新安装
pip install marker-pdf
```

### 问题 2: 转换速度慢

**解决方案:**
```bash
# 使用 GPU 加速
export TORCH_DEVICE=cuda

# 或在代码中设置
import os
os.environ["TORCH_DEVICE"] = "cuda"
```

### 问题 3: 内存不足

**解决方案:**
- 禁用图片提取: `disable_image_extraction=True`
- 分批处理大文件
- 增加系统内存

### 问题 4: OCR 识别不准确

**解决方案:**
- 设置 `force_ocr=True`
- 使用 LLM 增强: `use_llm=True`
- 提高图片质量

## 下一步

- 📖 阅读 [完整文档](MARKDOWN_CONVERTER_GUIDE.md)
- 🔧 查看 [API 文档](http://localhost:8000/docs)
- 💡 参考 [示例代码](../examples/)
- 🌟 访问 [marker 官方仓库](https://github.com/datalab-to/marker)

## 获取帮助

- GitHub Issues: 提交问题和建议
- 文档: 查看完整使用指南
- 示例: 参考示例代码

---

**祝使用愉快！** 🚀

