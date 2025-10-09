# 批量转换功能指南

## 概述

批量转换功能允许您同时转换多个文件，并通过并发处理显著提升转换效率。

### 主要特性

- ✅ **并发处理**: 同时处理多个文件，提升转换速度
- ✅ **可控并发数**: 自定义最大并发数（默认 3，建议不超过 5）
- ✅ **错误隔离**: 单个文件失败不影响其他文件
- ✅ **批量结果**: 一次性获取所有文件的转换结果
- ✅ **支持双接口**: Python SDK 和 HTTP API

## Python SDK 使用

### 基础批量转换

```python
from services.markdown_converter_service import MarkdownConverterService

# 创建转换服务
converter = MarkdownConverterService()

# 准备文件列表
file_paths = [
    "/path/to/file1.pdf",
    "/path/to/file2.pdf",
    "/path/to/file3.pdf"
]

# 批量转换（并发处理）
results = await converter.convert_multiple_files(
    file_paths=file_paths,
    max_concurrent=3  # 最大并发数
)

# 处理结果
for result in results:
    if result["success"]:
        print(f"✅ {result['file_path']}: 转换成功")
        print(f"   Markdown 长度: {len(result['markdown'])} 字符")
    else:
        print(f"❌ {result['file_path']}: {result['message']}")
```

### 批量转换字节流

```python
# 准备文件数据
files_data = []
for file_path in file_paths:
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    files_data.append((file_bytes, Path(file_path).name))

# 批量转换
results = await converter.convert_multiple_file_bytes(
    files_data=files_data,
    max_concurrent=3
)
```

### 批量转换文件夹

```python
from pathlib import Path

# 创建转换服务
converter = MarkdownConverterService()

# 获取文件夹中所有支持的文件
folder_path = "/path/to/folder"
all_files = []
for ext in converter.get_supported_formats():
    all_files.extend(Path(folder_path).glob(f"*{ext}"))

file_paths = [str(fp) for fp in all_files]

# 批量转换
results = await converter.convert_multiple_files(
    file_paths=file_paths,
    max_concurrent=3
)

# 保存结果
output_folder = Path(folder_path) / "markdown_output"
output_folder.mkdir(exist_ok=True)

for result in results:
    if result["success"]:
        filename = Path(result["file_path"]).stem + ".md"
        output_path = output_folder / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["markdown"])
```

## HTTP API 使用

### 批量转换端点

```
POST /api/convert/markdown/batch
Content-Type: multipart/form-data
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | File[] | ✅ | 要转换的多个文件（最多 20 个） |
| `max_concurrent` | Integer | ❌ | 最大并发数（默认: 3） |
| `use_llm` | Boolean | ❌ | 是否使用 LLM |
| `force_ocr` | Boolean | ❌ | 是否强制 OCR |
| `output_format` | String | ❌ | 输出格式 |

### 使用 curl

```bash
curl -X POST "http://localhost:8000/api/convert/markdown/batch" \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf" \
  -F "files=@file3.pdf" \
  -F "max_concurrent=3"
```

### 使用 Python requests

```python
import requests
from pathlib import Path

url = "http://localhost:8000/api/convert/markdown/batch"

# 准备多个文件
files = []
file_paths = ["/path/to/file1.pdf", "/path/to/file2.pdf"]

for file_path in file_paths:
    with open(file_path, 'rb') as f:
        files.append(('files', (Path(file_path).name, f.read(), 'application/octet-stream')))

data = {
    'max_concurrent': '3',
    'output_format': 'markdown'
}

# 发送请求
response = requests.post(url, files=files, data=data)
result = response.json()

# 处理结果
print(f"总文件数: {result['total']}")
print(f"成功: {result['success_count']}")
print(f"失败: {result['failed_count']}")

for file_result in result['results']:
    if file_result['success']:
        print(f"✅ {file_result['filename']}")
    else:
        print(f"❌ {file_result['filename']}: {file_result['message']}")
```

### 响应格式

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

## 性能优化

### 并发数选择

| 场景 | 推荐并发数 | 说明 |
|------|-----------|------|
| 不使用 LLM | 3-5 | 可以较高并发 |
| 使用 LLM | 2-3 | LLM 调用较慢，降低并发 |
| GPU 加速 | 5-10 | GPU 可支持更高并发 |
| CPU 处理 | 2-3 | CPU 资源有限 |

### 性能对比

以 6 个文件为例（每个文件约 2 秒处理时间）：

| 并发数 | 预计耗时 | 说明 |
|--------|---------|------|
| 1 | ~12 秒 | 串行处理 |
| 2 | ~6 秒 | 2 倍提速 |
| 3 | ~4 秒 | 3 倍提速 |
| 6 | ~2 秒 | 理论最快 |

### 最佳实践

1. **合理设置并发数**
   - 不使用 LLM: `max_concurrent=3-5`
   - 使用 LLM: `max_concurrent=2-3`
   - 根据系统资源调整

2. **批量大小控制**
   - API 限制: 最多 20 个文件
   - 建议: 每批 5-10 个文件
   - 大批量: 分批处理

3. **错误处理**
   - 检查每个文件的 `success` 字段
   - 记录失败文件，单独重试
   - 使用异常捕获

4. **资源管理**
   - 监控内存使用
   - 避免过高并发
   - 及时清理临时文件

## 示例代码

### 完整示例 1: 批量转换并保存

```python
import asyncio
from pathlib import Path
from services.markdown_converter_service import MarkdownConverterService

async def batch_convert_and_save():
    # 创建转换服务
    converter = MarkdownConverterService()
    
    # 准备文件列表
    file_paths = [
        "/path/to/file1.pdf",
        "/path/to/file2.pdf",
        "/path/to/file3.pdf"
    ]
    
    # 批量转换
    results = await converter.convert_multiple_files(
        file_paths=file_paths,
        max_concurrent=3
    )
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 保存结果
    success_count = 0
    for result in results:
        if result["success"]:
            file_path = Path(result["file_path"])
            output_path = output_dir / f"{file_path.stem}.md"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["markdown"])
            
            success_count += 1
            print(f"✅ {file_path.name} -> {output_path}")
        else:
            print(f"❌ {result['file_path']}: {result['message']}")
    
    print(f"\n完成！成功: {success_count}/{len(results)}")

asyncio.run(batch_convert_and_save())
```

### 完整示例 2: 性能测试

```python
import asyncio
import time
from services.markdown_converter_service import MarkdownConverterService

async def performance_test():
    file_paths = ["/path/to/file.pdf"] * 6  # 6 个相同文件
    
    # 测试不同并发数
    for max_concurrent in [1, 2, 3, 6]:
        converter = MarkdownConverterService()
        
        start_time = time.time()
        results = await converter.convert_multiple_files(
            file_paths=file_paths,
            max_concurrent=max_concurrent
        )
        end_time = time.time()
        
        elapsed = end_time - start_time
        success = sum(1 for r in results if r["success"])
        
        print(f"并发数 {max_concurrent}: {elapsed:.2f}秒 (成功: {success}/{len(results)})")

asyncio.run(performance_test())
```

## 常见问题

### Q: 最大并发数应该设置多少？

A: 
- 不使用 LLM: 3-5
- 使用 LLM: 2-3
- 根据系统资源和文件大小调整

### Q: 单次最多可以转换多少文件？

A: 
- API 限制: 20 个文件
- Python SDK: 无限制，但建议分批处理

### Q: 如何处理失败的文件？

A: 
```python
failed_files = [r["file_path"] for r in results if not r["success"]]
# 单独重试失败的文件
retry_results = await converter.convert_multiple_files(failed_files)
```

### Q: 批量转换会占用多少内存？

A: 
- 每个文件约 500MB-1GB（包括模型）
- 并发数 3: 约 3-5GB
- 建议: 至少 8GB 内存

## 运行示例

```bash
# Python SDK 示例
python backend/examples/batch_converter_example.py

# HTTP API 示例（需先启动服务）
python backend/main.py  # 终端 1
python backend/examples/batch_converter_api_example.py  # 终端 2
```

## 参考资料

- [完整使用指南](MARKDOWN_CONVERTER_GUIDE.md)
- [快速开始](MARKDOWN_CONVERTER_QUICKSTART.md)
- [示例代码](../examples/batch_converter_example.py)

