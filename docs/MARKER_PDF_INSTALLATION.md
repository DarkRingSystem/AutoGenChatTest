# Marker-PDF 安装和配置指南

## 📖 简介

`marker-pdf` 是一个强大的文档转换库，支持将 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 等文件转换为 Markdown 格式。

本项目已集成 marker-pdf 功能，但由于依赖冲突，需要特殊的安装步骤。

## ⚠️ 依赖冲突说明

`marker-pdf` 和 `autogen-core` 对 `pillow` 版本有不同要求：

- **marker-pdf**: 要求 `pillow<11.0.0,>=10.1.0`
- **autogen-core**: 要求 `pillow>=11.0.0`

这会导致依赖冲突警告，但实际上两个版本都可以工作。

## 🚀 安装步骤

### 1. 安装 marker-pdf

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装 marker-pdf
pip install marker-pdf

# 安装 DOCX 转换依赖
pip install weasyprint mammoth
```

### 2. 升级 pillow

安装 marker-pdf 后，pillow 会被降级到 10.4.0，需要手动升级：

```bash
pip install "pillow>=11.0.0" --upgrade
```

### 3. 验证安装

```bash
# 检查 pillow 版本
pip show pillow | grep Version
# 应该显示: Version: 11.3.0 或更高

# 检查 marker 是否可用
python -c "import marker; print('✅ marker 可用')"

# 检查 DOCX 转换依赖
python -c "import weasyprint; print('✅ weasyprint 可用')"
python -c "import mammoth; print('✅ mammoth 可用')"
```

## 🎯 使用说明

### 延迟导入机制

为了避免启动时下载模型（marker 首次导入时会自动下载 AI 模型），本项目使用了**延迟导入**机制：

- ✅ 后端启动时**不会**导入 marker 模块
- ✅ 只有在实际使用 Markdown 转换功能时才会导入
- ✅ 首次使用时会自动下载所需模型（约 1-2 分钟）

### API 端点

项目提供以下 Markdown 转换 API：

1. **单文件转换**
   ```
   POST /api/convert/markdown
   ```

2. **批量文件转换**
   ```
   POST /api/convert/markdown/batch
   ```

3. **获取支持的格式**
   ```
   GET /api/convert/supported-formats
   ```

### 支持的文件格式

- 📄 **PDF** (.pdf)
- 🖼️ **图片** (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
- 📊 **PowerPoint** (.pptx, .ppt)
- 📝 **Word** (.docx, .doc)
- 📈 **Excel** (.xlsx, .xls)
- 🌐 **HTML** (.html, .htm)
- 📚 **EPUB** (.epub)

## 🔧 配置选项

在 `backend/.env` 文件中配置：

```env
# Markdown 转换配置
MARKDOWN_MAX_FILE_SIZE_MB=10          # 最大文件大小（MB）
MARKDOWN_MAX_BATCH_FILES=10           # 批量转换最大文件数
MARKDOWN_USE_LLM=false                # 是否使用 LLM 提升转换精度
MARKDOWN_FORCE_OCR=false              # 是否强制 OCR
MARKDOWN_DISABLE_IMAGE_EXTRACTION=false  # 是否禁用图片提取
```

## 🐛 故障排除

### 问题 1: 依赖冲突警告

**现象**：
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
marker-pdf 1.10.1 requires Pillow<11.0.0,>=10.1.0, but you have pillow 11.3.0 which is incompatible.
```

**解决方案**：
这是预期的警告，可以忽略。pillow 11.3.0 与 marker-pdf 兼容，不会影响功能。

### 问题 2: 首次使用时很慢

**现象**：
首次调用 Markdown 转换 API 时响应很慢（1-2 分钟）

**原因**：
marker 首次导入时会自动下载 AI 模型

**解决方案**：
这是正常现象，模型下载完成后，后续使用会很快。

### 问题 3: 模块导入失败

**现象**：
```
ModuleNotFoundError: No module named 'marker'
```

**解决方案**：
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装 marker-pdf
pip install marker-pdf

# 升级 pillow
pip install "pillow>=11.0.0" --upgrade
```

### 问题 4: 后端启动时卡住

**现象**：
运行 `python main.py` 时长时间无响应

**原因**：
可能是 marker 模块在启动时被导入了

**解决方案**：
检查代码中是否有顶层导入 marker 模块，应该使用延迟导入：

```python
# ❌ 错误：顶层导入
from marker.converters.pdf import PdfConverter

# ✅ 正确：延迟导入
def some_function():
    from marker.converters.pdf import PdfConverter
    # 使用 PdfConverter
```

## 📚 相关文档

- [marker-pdf GitHub](https://github.com/datalab-to/marker)
- [marker-pdf 文档](https://github.com/datalab-to/marker/blob/main/README.md)
- [项目 Markdown 转换文档](MARKDOWN_CONVERTER_SUMMARY.md)

## 💡 最佳实践

1. **首次使用前预热**：
   ```bash
   # 在后台预先下载模型
   python -c "from marker.converters.pdf import PdfConverter"
   ```

2. **生产环境部署**：
   - 在 Docker 镜像构建时预先下载模型
   - 使用持久化存储保存模型文件

3. **性能优化**：
   - 对于大文件，考虑使用异步处理
   - 实现文件转换结果缓存

## ✅ 验证清单

安装完成后，请验证以下内容：

- [ ] pillow 版本 >= 11.0.0
- [ ] marker 模块可以导入
- [ ] 后端可以正常启动（不卡住）
- [ ] Markdown 转换 API 可以正常调用
- [ ] 转换结果正确

---

**安装完成！** 现在你可以使用 Markdown 转换功能了。🎉

