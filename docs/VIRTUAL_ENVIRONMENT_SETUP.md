# 虚拟环境设置指南

## 📚 概述

本项目使用 Python 虚拟环境（`.venv`）来管理依赖，确保项目依赖与系统 Python 隔离，避免版本冲突。

---

## ✅ 已完成的配置

### 1. 虚拟环境创建

```bash
# 虚拟环境位置
/Users/darkringsystem/PycharmProjects/autogenTest/.venv

# Python 版本
Python 3.11.9
```

### 2. 依赖安装

所有必需的依赖已安装在虚拟环境中：

```bash
✅ fastapi>=0.115.0
✅ uvicorn[standard]>=0.32.0
✅ pydantic>=2.10.0
✅ autogen-agentchat==0.7.5
✅ autogen-ext[openai]==0.7.5
✅ marker-pdf[full]>=1.0.0
✅ weasyprint>=66.0
✅ mammoth>=1.11.0
✅ PyGObject>=3.54.3
✅ python-multipart>=0.0.6
```

### 3. 系统依赖

通过 Homebrew 安装的系统库：

```bash
✅ glib 2.86.0
✅ cairo 1.18.4
✅ pango 1.57.0
✅ gdk-pixbuf 2.44.3
✅ libffi 3.5.2
✅ gobject-introspection 1.86.0
✅ gtk+3 3.24.51
```

### 4. 启动脚本更新

`backend/start.sh` 已更新，自动：
- ✅ 激活虚拟环境
- ✅ 设置 Homebrew 库路径
- ✅ 配置环境变量
- ✅ 启动后端服务

---

## 🚀 使用方法

### 启动后端（推荐方式）

```bash
cd backend
./start.sh
```

启动脚本会自动：
1. 激活虚拟环境
2. 设置环境变量（`DYLD_LIBRARY_PATH`, `PKG_CONFIG_PATH`, `GI_TYPELIB_PATH`）
3. 启动 uvicorn 服务器

### 启动前端

```bash
cd frontend
npm run dev
```

### 手动激活虚拟环境

如果需要手动操作：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 验证 Python 路径
which python
# 输出: /Users/darkringsystem/PycharmProjects/autogenTest/.venv/bin/python

# 设置环境变量
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export GI_TYPELIB_PATH="/opt/homebrew/lib/girepository-1.0:$GI_TYPELIB_PATH"

# 运行 Python 脚本
python main.py

# 退出虚拟环境
deactivate
```

---

## 🔧 维护和管理

### 安装新依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装新包
pip install package-name

# 更新 requirements.txt
pip freeze > backend/requirements.txt

# 退出虚拟环境
deactivate
```

### 更新依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 更新所有依赖
pip install --upgrade -r backend/requirements.txt

# 或更新单个包
pip install --upgrade package-name

# 退出虚拟环境
deactivate
```

### 重建虚拟环境

如果虚拟环境损坏或需要重建：

```bash
# 删除旧的虚拟环境
rm -rf .venv

# 创建新的虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 安装额外的依赖（用于 DOCX 转换）
pip install weasyprint mammoth PyGObject

# 退出虚拟环境
deactivate
```

---

## 🧪 测试和验证

### 测试虚拟环境

```bash
# 激活虚拟环境
source .venv/bin/activate

# 检查 Python 版本
python --version

# 检查已安装的包
pip list

# 验证关键依赖
python -c "import fastapi; print('✅ fastapi')"
python -c "import autogen_agentchat; print('✅ autogen')"
python -c "import marker; print('✅ marker-pdf')"

# 退出虚拟环境
deactivate
```

### 测试 weasyprint

```bash
# 激活虚拟环境并设置环境变量
source .venv/bin/activate
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# 运行测试脚本
python test_weasyprint.py

# 应该看到:
# ✅ weasyprint 导入成功
# ✅ PDF 生成成功！
# ✅ 测试 PDF 已保存到: /tmp/test_weasyprint.pdf

# 退出虚拟环境
deactivate
```

### 测试后端服务

```bash
# 启动后端
cd backend
./start.sh

# 在另一个终端测试 API
curl http://localhost:8000/health

# 应该返回:
# {"status":"healthy","agent_initialized":true,"session_count":0}
```

---

## 📋 环境变量说明

### DYLD_LIBRARY_PATH

指定动态库搜索路径，让 Python 能找到 Homebrew 安装的系统库（如 `libgobject-2.0-0`）。

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

### PKG_CONFIG_PATH

指定 pkg-config 搜索路径，用于编译时查找库的配置信息。

```bash
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
```

### GI_TYPELIB_PATH

指定 GObject Introspection 类型库路径，用于 PyGObject。

```bash
export GI_TYPELIB_PATH="/opt/homebrew/lib/girepository-1.0:$GI_TYPELIB_PATH"
```

---

## 🐛 常见问题

### 1. 虚拟环境未激活

**症状**：运行 `which python` 显示系统 Python 路径

**解决**：
```bash
source .venv/bin/activate
```

### 2. 找不到 libgobject-2.0-0

**症状**：
```
OSError: cannot load library 'libgobject-2.0-0'
```

**解决**：
```bash
# 确保设置了环境变量
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# 或使用启动脚本
cd backend && ./start.sh
```

### 3. 依赖冲突

**症状**：
```
ERROR: Cannot install autogen-agentchat and marker-pdf because these package versions have conflicting dependencies.
```

**解决**：
```bash
# 使用虚拟环境，不要使用 --break-system-packages
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. 模块未找到

**症状**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决**：
```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 重新安装依赖
pip install -r backend/requirements.txt
```

---

## 💡 最佳实践

### 1. 始终使用虚拟环境

```bash
# ✅ 正确
source .venv/bin/activate
pip install package-name

# ❌ 错误
pip3 install --break-system-packages package-name
```

### 2. 使用启动脚本

```bash
# ✅ 推荐：使用启动脚本（自动激活虚拟环境和设置环境变量）
cd backend && ./start.sh

# ❌ 不推荐：手动启动（容易忘记设置环境变量）
python3 main.py
```

### 3. 定期更新依赖

```bash
# 每月更新一次依赖
source .venv/bin/activate
pip install --upgrade -r backend/requirements.txt
pip freeze > backend/requirements.txt
deactivate
```

### 4. 记录环境配置

在 `.env` 文件中记录环境配置：

```bash
# .env
PYTHON_VERSION=3.11.9
VENV_PATH=.venv
HOMEBREW_PREFIX=/opt/homebrew
```

---

## 📚 相关文档

- [FIX_LIBGOBJECT_ERROR.md](./FIX_LIBGOBJECT_ERROR.md) - libgobject 错误修复指南
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 问题排查指南
- [MACOS_SETUP.md](./MACOS_SETUP.md) - macOS 设置指南
- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - 快速开始指南

---

## ✅ 验证清单

在开始开发前，确保：

- [ ] 虚拟环境已创建（`.venv` 目录存在）
- [ ] 虚拟环境已激活（`which python` 指向 `.venv/bin/python`）
- [ ] 所有依赖已安装（`pip list` 显示所有必需的包）
- [ ] 系统库已安装（`brew list glib` 等）
- [ ] 环境变量已设置（`echo $DYLD_LIBRARY_PATH` 包含 `/opt/homebrew/lib`）
- [ ] 后端服务可以启动（`./start.sh` 成功）
- [ ] weasyprint 可以工作（`python test_weasyprint.py` 成功）
- [ ] API 可以访问（`curl http://localhost:8000/health` 返回正常）

---

## 🎉 总结

使用虚拟环境的好处：

✅ **隔离依赖** - 项目依赖与系统 Python 隔离  
✅ **避免冲突** - 不同项目可以使用不同版本的包  
✅ **易于管理** - 可以轻松重建和迁移环境  
✅ **安全可靠** - 不会影响系统 Python 和其他项目  
✅ **版本控制** - 可以通过 requirements.txt 精确控制依赖版本  

现在项目已经完全使用虚拟环境运行，所有依赖都已正确安装！🚀

