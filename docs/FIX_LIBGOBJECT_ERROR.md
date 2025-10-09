# 修复 libgobject-2.0-0 错误

## 🐛 错误信息

```
❌ 转换失败: Failed to convert /var/folders/s_/krsbdhwx0f1_v83zdjqmw4kr0000gn/T/tmpou7sfzcw/SSO.docx to PDF: 
cannot load library 'libgobject-2.0-0': dlopen(libgobject-2.0-0, 0x0002): tried: 
'libgobject-2.0-0' (no such file), 
'/System/Volumes/Preboot/Cryptexes/OSlibgobject-2.0-0' (no such file), 
'/usr/lib/libgobject-2.0-0' (no such file, not in dyld cache), 
'libgobject-2.0-0' (no such file).
```

## 🔍 问题原因

这个错误发生在 `marker-pdf` 库尝试将 `.docx` 文件转换为 PDF 时，系统找不到 `libgobject-2.0-0` 库。

`libgobject-2.0-0` 是 GLib 的一部分，是 GTK 和许多 Linux/Unix 应用程序的基础库。`marker-pdf` 内部使用 `weasyprint` 进行文档转换，而 `weasyprint` 依赖这些系统库。

## ✅ 解决方案

### 方案一：安装系统依赖（推荐）⭐

#### 步骤 1：安装 Homebrew（如果还没有）

```bash
# 检查是否已安装
brew --version

# 如果没有，安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 步骤 2：安装 GLib 和相关库

```bash
# 安装所有必需的系统库
brew install glib cairo pango gdk-pixbuf libffi gobject-introspection

# 如果需要，也安装 GTK
brew install gtk+3
```

#### 步骤 3：安装 Python 依赖

```bash
cd /Users/darkringsystem/PycharmProjects/autogenTest/backend

# 安装 weasyprint 和 mammoth
pip3 install weasyprint mammoth

# 或重新安装所有依赖
pip3 install -r requirements.txt
```

#### 步骤 4：验证安装

```bash
# 验证 GLib
python3 -c "import gi; print('✅ GLib: OK')"

# 验证 weasyprint
python3 -c "import weasyprint; print('✅ weasyprint: OK')"

# 验证 mammoth
python3 -c "import mammoth; print('✅ mammoth: OK')"

# 检查库文件是否存在
ls $(brew --prefix)/lib/libgobject-2.0*
```

#### 步骤 5：设置环境变量

```bash
# 检查 Homebrew 安装路径
brew --prefix
# Apple Silicon (M1/M2/M3): /opt/homebrew
# Intel Mac: /usr/local

# 设置环境变量（临时）
export DYLD_LIBRARY_PATH=$(brew --prefix)/lib:$DYLD_LIBRARY_PATH
export PKG_CONFIG_PATH=$(brew --prefix)/lib/pkgconfig:$PKG_CONFIG_PATH

# 验证环境变量
echo $DYLD_LIBRARY_PATH
```

#### 步骤 6：重启后端服务

```bash
cd /Users/darkringsystem/PycharmProjects/autogenTest/backend

# 使用启动脚本（已包含环境变量设置）
./start.sh

# 或手动启动
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 步骤 7：测试文件转换

1. 打开前端：http://localhost:3001
2. 上传一个 `.docx` 文件
3. 查看是否能成功转换

---

### 方案二：更新启动脚本

如果方案一不起作用，可能需要更新启动脚本的库路径。

#### 检查实际的 Homebrew 路径

```bash
# 获取 Homebrew 前缀
BREW_PREFIX=$(brew --prefix)
echo "Homebrew 安装在: $BREW_PREFIX"

# 检查 GLib 库
ls $BREW_PREFIX/lib/libgobject-2.0*

# 检查 GLib 版本
ls $BREW_PREFIX/lib/libgobject-2.0.*.dylib
```

#### 更新 start.sh

编辑 `backend/start.sh`：

```bash
#!/bin/bash

# 获取 Homebrew 路径
BREW_PREFIX=$(brew --prefix)

# 设置库路径
export DYLD_LIBRARY_PATH="$BREW_PREFIX/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$BREW_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"

# 设置 GI_TYPELIB_PATH（用于 GObject Introspection）
export GI_TYPELIB_PATH="$BREW_PREFIX/lib/girepository-1.0:$GI_TYPELIB_PATH"

# 启动后端服务
echo "🚀 启动后端服务..."
echo "📦 Homebrew 路径: $BREW_PREFIX"
echo "📦 DYLD_LIBRARY_PATH: $DYLD_LIBRARY_PATH"
python3 main.py
```

---

### 方案三：使用 PyGObject

如果上述方法都不行，可以尝试安装 PyGObject：

```bash
# 安装 PyGObject
pip3 install PyGObject

# 验证
python3 -c "import gi; gi.require_version('GLib', '2.0'); from gi.repository import GLib; print('✅ PyGObject: OK')"
```

---

### 方案四：禁用 DOCX 转换（临时方案）

如果你暂时不需要 DOCX 转换功能，可以只使用 PDF 文件：

1. **只上传 PDF 文件**，避免触发 DOCX 转换
2. **将 DOCX 手动转换为 PDF**：
   - 使用 Microsoft Word
   - 使用 Google Docs
   - 使用在线转换工具

---

## 🔧 调试步骤

### 1. 检查库是否安装

```bash
# 检查 GLib
brew list glib

# 检查库文件
find $(brew --prefix) -name "libgobject-2.0*"

# 应该看到类似输出：
# /opt/homebrew/lib/libgobject-2.0.0.dylib
# /opt/homebrew/lib/libgobject-2.0.dylib
```

### 2. 检查 Python 能否找到库

```python
# 创建测试脚本 test_glib.py
import ctypes
import ctypes.util

# 尝试查找库
lib_path = ctypes.util.find_library('gobject-2.0')
print(f"库路径: {lib_path}")

if lib_path:
    try:
        lib = ctypes.CDLL(lib_path)
        print("✅ 成功加载库")
    except Exception as e:
        print(f"❌ 加载失败: {e}")
else:
    print("❌ 找不到库")
```

运行测试：

```bash
python3 test_glib.py
```

### 3. 检查环境变量

```bash
# 检查当前环境变量
echo $DYLD_LIBRARY_PATH
echo $PKG_CONFIG_PATH

# 应该包含 Homebrew 的 lib 目录
```

### 4. 查看详细错误

```bash
# 启动后端时查看详细日志
cd backend
python3 -c "import sys; sys.path.insert(0, '.'); import main"

# 或使用调试模式
python3 -m pdb main.py
```

---

## 📋 完整的安装命令（一键执行）

```bash
#!/bin/bash

echo "🔧 开始修复 libgobject-2.0-0 错误..."

# 1. 安装系统依赖
echo "📦 安装系统依赖..."
brew install glib cairo pango gdk-pixbuf libffi gobject-introspection gtk+3

# 2. 安装 Python 依赖
echo "🐍 安装 Python 依赖..."
cd /Users/darkringsystem/PycharmProjects/autogenTest/backend
pip3 install weasyprint mammoth PyGObject

# 3. 验证安装
echo "✅ 验证安装..."
python3 -c "import gi; print('✅ GLib: OK')" || echo "❌ GLib 安装失败"
python3 -c "import weasyprint; print('✅ weasyprint: OK')" || echo "❌ weasyprint 安装失败"
python3 -c "import mammoth; print('✅ mammoth: OK')" || echo "❌ mammoth 安装失败"

# 4. 检查库文件
echo "📚 检查库文件..."
BREW_PREFIX=$(brew --prefix)
ls $BREW_PREFIX/lib/libgobject-2.0* || echo "❌ 找不到 libgobject-2.0"

# 5. 设置环境变量
echo "🔧 设置环境变量..."
export DYLD_LIBRARY_PATH="$BREW_PREFIX/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$BREW_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export GI_TYPELIB_PATH="$BREW_PREFIX/lib/girepository-1.0:$GI_TYPELIB_PATH"

echo "✅ 修复完成！"
echo "📝 请使用 ./start.sh 启动后端服务"
```

保存为 `fix_libgobject.sh`，然后运行：

```bash
chmod +x fix_libgobject.sh
./fix_libgobject.sh
```

---

## 🎯 预期结果

修复成功后：

1. **上传 DOCX 文件**：
   ```
   ✅ 文件上传成功
   ⏳ 正在解析...
   ✅ 解析完成
   ```

2. **后端日志**：
   ```
   📄 开始转换文件: SSO.docx
   ✅ 转换成功: SSO.docx -> SSO.pdf
   📝 开始解析 PDF...
   ✅ 解析完成
   ```

3. **前端显示**：
   - 文件列表显示 ✅ 图标
   - 标签显示"已解析"
   - 可以基于文件内容提问

---

## 🆘 如果问题仍然存在

### 检查清单

- [ ] Homebrew 已安装
- [ ] GLib 已安装 (`brew list glib`)
- [ ] 库文件存在 (`ls $(brew --prefix)/lib/libgobject-2.0*`)
- [ ] Python 依赖已安装 (`pip3 list | grep weasyprint`)
- [ ] 环境变量已设置 (`echo $DYLD_LIBRARY_PATH`)
- [ ] 使用 `./start.sh` 启动后端
- [ ] 后端服务正常运行 (`curl http://localhost:8000/health`)

### 替代方案

如果所有方法都不行，可以考虑：

1. **使用 Docker**：
   ```bash
   # 创建 Dockerfile，包含所有依赖
   # 在容器中运行后端服务
   ```

2. **使用虚拟机**：
   - 在 Linux 虚拟机中运行后端
   - macOS 前端连接到虚拟机后端

3. **只使用 PDF**：
   - 手动将 DOCX 转换为 PDF
   - 只上传 PDF 文件

---

## 📚 相关文档

- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 问题排查指南
- [MACOS_SETUP.md](./MACOS_SETUP.md) - macOS 设置指南
- [DEPENDENCY_INSTALLATION.md](./DEPENDENCY_INSTALLATION.md) - 依赖安装指南

---

## 💡 预防措施

为了避免将来出现类似问题：

1. **使用虚拟环境**：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

2. **记录环境配置**：
   - 记录 Homebrew 安装的包
   - 记录环境变量设置
   - 记录 Python 依赖版本

3. **定期更新依赖**：
   ```bash
   brew update && brew upgrade
   pip3 install --upgrade -r requirements.txt
   ```

---

## ✅ 总结

`libgobject-2.0-0` 错误是由于缺少 GLib 系统库导致的。通过安装 Homebrew 和相关系统库，设置正确的环境变量，并使用启动脚本启动后端服务，应该可以解决这个问题。

如果问题仍然存在，请检查上述清单，或考虑使用替代方案。🚀

