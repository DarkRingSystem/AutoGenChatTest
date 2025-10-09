# macOS 系统设置指南

## 🍎 macOS 用户必读

如果您在 macOS 上运行此项目，需要额外的设置步骤来支持 DOCX、PPTX 等 Office 文档的转换。

---

## 📋 问题说明

### 错误信息
```
❌ 转换失败: Failed to convert xxx.docx to PDF: No module named 'weasyprint'
```

或者：
```
OSError: cannot load library 'libgobject-2.0-0'
```

### 原因
marker 库在转换 Office 文档时需要：
1. **Python 库**: weasyprint
2. **系统库**: cairo, pango, gdk-pixbuf, libffi 等

macOS 上，即使安装了 weasyprint，Python 也可能找不到 Homebrew 安装的系统库。

---

## ✅ 完整解决方案

### 步骤 1: 安装 Homebrew（如果还没有）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步骤 2: 安装系统依赖

```bash
brew install cairo pango gdk-pixbuf libffi
```

这会安装以下库：
- **cairo**: 2D 图形库
- **pango**: 文本渲染库
- **gdk-pixbuf**: 图像加载库
- **libffi**: 外部函数接口库

以及它们的依赖：
- libpng, freetype, fontconfig
- glib, harfbuzz, fribidi
- jpeg-turbo, libtiff
- 等等...

### 步骤 3: 安装 Python 依赖

```bash
pip3 install weasyprint
```

### 步骤 4: 使用启动脚本（推荐）

项目提供了一个启动脚本 `backend/start.sh`，它会自动设置环境变量：

```bash
cd backend
./start.sh
```

启动脚本内容：
```bash
#!/bin/bash

# 设置 Homebrew 库路径
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"

# 启动后端服务
python3 main.py
```

### 步骤 5: 验证安装

```bash
# 设置环境变量
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# 测试 weasyprint
python3 -c "import weasyprint; print('✅ weasyprint version:', weasyprint.__version__)"

# 应该输出：
# ✅ weasyprint version: 66.0
```

---

## 🚀 启动服务

### 方法 1: 使用启动脚本（推荐）

```bash
cd backend
./start.sh
```

### 方法 2: 手动设置环境变量

```bash
cd backend
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
python3 main.py
```

### 方法 3: 添加到 shell 配置文件（永久生效）

**如果使用 zsh（macOS 默认）**:
```bash
echo 'export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"' >> ~/.zshrc
source ~/.zshrc
```

**如果使用 bash**:
```bash
echo 'export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

然后就可以直接运行：
```bash
cd backend
python3 main.py
```

---

## 🔍 环境变量说明

### DYLD_LIBRARY_PATH
- **作用**: 告诉 macOS 动态链接器在哪里查找共享库
- **值**: `/opt/homebrew/lib` - Homebrew 在 Apple Silicon Mac 上的库路径
- **注意**: Intel Mac 上 Homebrew 路径是 `/usr/local/lib`

### PKG_CONFIG_PATH
- **作用**: 帮助编译工具找到库的配置信息
- **值**: `/opt/homebrew/lib/pkgconfig`

---

## 🛠️ 故障排查

### 问题 1: 启动脚本没有执行权限

**错误**:
```
Permission denied: ./start.sh
```

**解决**:
```bash
chmod +x backend/start.sh
```

### 问题 2: Homebrew 路径不同

**Intel Mac 用户**，Homebrew 安装在 `/usr/local`，需要修改环境变量：

```bash
# 修改 backend/start.sh
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
```

**检查 Homebrew 路径**:
```bash
brew --prefix
# Apple Silicon: /opt/homebrew
# Intel: /usr/local
```

### 问题 3: 仍然找不到库

**检查库是否安装**:
```bash
ls /opt/homebrew/lib/libgobject*
# 应该看到: libgobject-2.0.0.dylib
```

**检查环境变量**:
```bash
echo $DYLD_LIBRARY_PATH
# 应该包含: /opt/homebrew/lib
```

**重新安装系统依赖**:
```bash
brew reinstall cairo pango gdk-pixbuf libffi
```

### 问题 4: Python 版本问题

**确保使用正确的 Python**:
```bash
which python3
# 应该是: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
# 或: /opt/homebrew/bin/python3

python3 --version
# 应该 >= 3.9
```

---

## 📝 完整安装流程（macOS）

```bash
# 1. 安装 Homebrew（如果需要）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装系统依赖
brew install cairo pango gdk-pixbuf libffi

# 3. 安装 Python 依赖
cd backend
pip3 install -r requirements.txt

# 4. 验证安装
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
python3 -c "import weasyprint; print('✅ OK')"

# 5. 启动服务
./start.sh
```

---

## ✅ 成功标志

启动后端服务后，应该看到：

```
🚀 启动后端服务...
📦 DYLD_LIBRARY_PATH: /opt/homebrew/lib:
INFO:     Will watch for changes in these directories: ['/Users/.../backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ 会话管理服务初始化成功！
INFO:     Application startup complete.
```

然后上传 DOCX 文件应该能成功解析！

---

## 🎯 快速测试

```bash
# 1. 启动后端
cd backend
./start.sh

# 2. 在另一个终端，测试上传
curl -X POST "http://localhost:8000/api/convert/markdown/batch" \
  -F "files=@test.docx" \
  -F "max_concurrent=3"

# 应该返回成功的 JSON 响应
```

---

## 📚 相关文档

- **依赖安装**: [DEPENDENCY_INSTALLATION.md](DEPENDENCY_INSTALLATION.md)
- **问题排查**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **快速开始**: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

---

## 💡 提示

1. **推荐使用启动脚本** - 最简单可靠
2. **或添加到 shell 配置** - 一次设置，永久生效
3. **Intel Mac 用户** - 注意修改路径为 `/usr/local`
4. **遇到问题** - 查看 [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

## 🎉 总结

macOS 上使用文件转换功能需要：
1. ✅ 安装 Homebrew 系统依赖
2. ✅ 安装 Python weasyprint
3. ✅ 设置 DYLD_LIBRARY_PATH 环境变量
4. ✅ 使用 `./start.sh` 启动服务

完成这些步骤后，所有文件格式都能正常转换！🚀

