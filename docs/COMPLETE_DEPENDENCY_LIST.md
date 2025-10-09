# 完整依赖列表

## 📦 文件上传功能所需的所有依赖

本文档列出了文件上传和转换功能所需的**所有**依赖，包括 Python 包和系统库。

---

## 🐍 Python 依赖

### 核心框架
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.10.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.1
```

### AutoGen 智能体
```
autogen-agentchat==0.7.5
autogen-ext[openai]==0.7.5
```

### Token 计数
```
tiktoken>=0.5.0
```

### 文件转换核心依赖 ⭐
```
marker-pdf>=1.0.0          # 文件转换核心库
python-multipart>=0.0.6    # FastAPI 文件上传支持
weasyprint>=66.0           # DOCX 等格式转 PDF
mammoth>=1.11.0            # DOCX 转 HTML
```

### marker-pdf 的依赖（自动安装）
```
torch>=2.7.0
transformers>=4.45.2
surya-ocr>=0.17.0
Pillow>=10.1.0,<11.0.0
anthropic>=0.46.0
openai>=1.65.2
scikit-learn>=1.6.1
numpy>=1.22.0
scipy>=1.8.0
opencv-python-headless==4.11.0.86
pdftext>=0.6.3
pypdfium2==4.30.0
huggingface-hub>=0.34.0
safetensors>=0.4.3
tokenizers>=0.22.0
regex>=2024.4.28
rapidfuzz>=3.8.1
ftfy>=6.1.1
markdown2>=2.5.2
markdownify>=1.1.0
beautifulsoup4>=4.9
google-genai>=1.0.0
google-auth>=2.14.1
click>=8.2.0
filetype>=1.2.0
pre-commit>=4.2.0
einops>=0.8.1
joblib>=1.2.0
threadpoolctl>=3.1.0
tenacity>=8.2.3
+ 更多...
```

---

## 🖥️ 系统依赖（macOS）

### Homebrew 包
```bash
brew install cairo pango gdk-pixbuf libffi
```

### 详细列表
安装上述 Homebrew 包时，会自动安装以下系统库：

#### cairo 依赖
- libpng
- freetype
- fontconfig
- pcre2
- glib
- xorgproto
- libxau
- libxdmcp
- libxcb
- libx11
- libxext
- libxrender
- lzo
- pixman

#### pango 依赖
- fribidi
- graphite2
- harfbuzz

#### gdk-pixbuf 依赖
- jpeg-turbo
- libtiff

#### 总计
约 **24 个系统库**

---

## 📋 完整安装命令

### macOS

```bash
# 1. 安装 Homebrew（如果需要）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装系统依赖
brew install cairo pango gdk-pixbuf libffi

# 3. 安装 Python 依赖
cd backend
pip3 install -r requirements.txt

# 或手动安装核心依赖
pip3 install \
  fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv \
  autogen-agentchat==0.7.5 autogen-ext[openai]==0.7.5 \
  tiktoken \
  marker-pdf python-multipart weasyprint mammoth

# 4. 验证安装
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
python3 -c "import marker; print('marker: OK')"
python3 -c "import weasyprint; print('weasyprint: OK')"
python3 -c "import mammoth; print('mammoth: OK')"

# 5. 启动服务
./start.sh
```

### Linux (Ubuntu/Debian)

```bash
# 1. 安装系统依赖
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# 2. 安装 Python 依赖
cd backend
pip3 install -r requirements.txt

# 3. 启动服务
python3 main.py
```

### Windows

```bash
# 1. 下载并安装 GTK3 Runtime
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

# 2. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 3. 启动服务
python main.py
```

---

## ✅ 验证安装

### 检查 Python 包

```bash
# 检查所有核心包
python3 -c "
import fastapi
import uvicorn
import pydantic
import autogen_agentchat
import tiktoken
import marker
import weasyprint
import mammoth
print('✅ 所有核心包已安装')
"
```

### 检查系统库（macOS）

```bash
# 检查 Homebrew 库
ls /opt/homebrew/lib/libgobject* 2>/dev/null && echo "✅ libgobject 已安装" || echo "❌ libgobject 未安装"
ls /opt/homebrew/lib/libcairo* 2>/dev/null && echo "✅ libcairo 已安装" || echo "❌ libcairo 未安装"
ls /opt/homebrew/lib/libpango* 2>/dev/null && echo "✅ libpango 已安装" || echo "❌ libpango 未安装"
```

### 检查环境变量（macOS）

```bash
echo $DYLD_LIBRARY_PATH
# 应该包含: /opt/homebrew/lib
```

---

## 🔍 依赖大小估算

### Python 包
- **marker-pdf 及依赖**: ~2.5 GB（包括 torch, transformers 等）
- **其他包**: ~500 MB
- **总计**: ~3 GB

### 系统库（macOS）
- **Homebrew 包**: ~100 MB

### 总磁盘空间
- **约 3.1 GB**

---

## 📊 依赖关系图

```
文件上传功能
├── FastAPI (Web 框架)
│   └── python-multipart (文件上传)
│
├── marker-pdf (文件转换核心)
│   ├── torch (深度学习)
│   ├── transformers (NLP 模型)
│   ├── surya-ocr (OCR)
│   ├── Pillow (图像处理)
│   ├── pdftext (PDF 文本提取)
│   │   └── pypdfium2 (PDF 渲染)
│   └── 其他 30+ 依赖
│
├── weasyprint (DOCX 转 PDF)
│   ├── cairo (2D 图形) ← 系统库
│   ├── pango (文本渲染) ← 系统库
│   ├── gdk-pixbuf (图像加载) ← 系统库
│   └── libffi (FFI) ← 系统库
│
└── mammoth (DOCX 转 HTML)
    └── cobble (依赖注入)
```

---

## 🎯 最小依赖集

如果只需要基本的文件转换功能（不包括 AutoGen 智能体）：

```bash
pip3 install \
  fastapi \
  uvicorn[standard] \
  pydantic \
  python-multipart \
  marker-pdf \
  weasyprint \
  mammoth
```

---

## 🚨 常见依赖冲突

### Pillow 版本冲突

```
autogen-core 0.7.5 requires pillow>=11.0.0
marker-pdf requires pillow<11.0.0,>=10.1.0
```

**解决方法**: 这个冲突可以忽略，marker-pdf 的 Pillow 10.4.0 可以正常工作。

### httpx 版本冲突

marker-pdf 可能会升级 httpx 版本，这通常不会造成问题。

---

## 📝 requirements.txt 完整内容

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.10.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.1
autogen-agentchat==0.7.5
autogen-ext[openai]==0.7.5
tiktoken>=0.5.0
marker-pdf>=1.0.0
python-multipart>=0.0.6
weasyprint>=66.0
mammoth>=1.11.0
```

---

## 🔄 更新依赖

```bash
# 更新所有依赖到最新版本
cd backend
pip3 install -r requirements.txt --upgrade

# 或更新特定包
pip3 install marker-pdf --upgrade
pip3 install weasyprint --upgrade
pip3 install mammoth --upgrade
```

---

## 📚 相关文档

- **依赖安装**: [DEPENDENCY_INSTALLATION.md](DEPENDENCY_INSTALLATION.md)
- **macOS 设置**: [MACOS_SETUP.md](MACOS_SETUP.md)
- **问题排查**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

## ✨ 总结

文件上传功能需要：

1. **4 个核心 Python 包**: marker-pdf, python-multipart, weasyprint, mammoth
2. **30+ 个依赖包**: 由 marker-pdf 自动安装
3. **4 个系统库** (macOS): cairo, pango, gdk-pixbuf, libffi
4. **环境变量** (macOS): DYLD_LIBRARY_PATH

总安装时间：约 5-10 分钟  
总磁盘空间：约 3.1 GB

所有依赖安装完成后，即可支持所有文件格式的转换！🎉

