# 启动脚本使用指南

## 📋 脚本列表

项目提供了多个启动脚本，适用于不同的场景：

| 脚本 | 平台 | 虚拟环境 | 推荐场景 |
|------|------|----------|----------|
| **start.sh** | macOS/Linux | ✅ 是 | **本地开发（推荐）** |
| **start-simple.sh** | macOS/Linux | ❌ 否 | 系统环境已配置 |
| **start.bat** | Windows | ✅ 是 | **Windows 开发（推荐）** |

## 🚀 快速开始

### macOS / Linux

**推荐使用 start.sh（使用虚拟环境）**：

```bash
./start.sh
```

如果系统 Python 环境已配置好所有依赖，也可以使用简化版：

```bash
./start-simple.sh
```

### Windows

**双击运行或命令行执行**：

```cmd
start.bat
```

## 📖 详细说明

### 1. start.sh（推荐用于本地开发）

**特点**：
- ✅ 使用虚拟环境（backend/venv）
- ✅ 自动检查并创建虚拟环境
- ✅ 自动检查并安装依赖
- ✅ 自动检查 .env 配置文件
- ✅ 彩色输出，易于阅读
- ✅ 优雅的错误处理
- ✅ Ctrl+C 自动清理进程

**使用步骤**：

1. **首次运行**：
   ```bash
   ./start.sh
   ```
   
   脚本会自动：
   - 检查虚拟环境，不存在则创建
   - 检查依赖，缺失则安装
   - 检查 .env 文件，不存在则创建

2. **后续运行**：
   ```bash
   ./start.sh
   ```
   
   直接启动，无需额外操作

3. **停止服务**：
   - 按 `Ctrl+C`
   - 脚本会自动停止后端和前端服务

**输出示例**：

```
════════════════════════════════════════════════════════════════
  🚀 AutoGen AI Chat - 开发环境启动
════════════════════════════════════════════════════════════════

🔍 Checking virtual environment...
✅ All dependencies are installed

════════════════════════════════════════════════════════════════
  🔧 Starting Backend Server (Virtual Environment)
════════════════════════════════════════════════════════════════

⏳ Waiting for backend to initialize...

════════════════════════════════════════════════════════════════
  🎨 Starting Frontend Server
════════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════════
  ✅ Application Started Successfully!
════════════════════════════════════════════════════════════════

📡 Backend API:    http://localhost:8000
🎨 Frontend UI:    http://localhost:3000
📚 API Docs:       http://localhost:8000/docs
📖 ReDoc:          http://localhost:8000/redoc

💡 Tips:
   - Backend uses virtual environment: backend/venv
   - Backend auto-reloads on code changes
   - Frontend auto-reloads on code changes

Press Ctrl+C to stop all servers
```

### 2. start-simple.sh（简化版）

**特点**：
- ❌ 不使用虚拟环境
- ✅ 使用系统 Python 环境
- ✅ 快速启动
- ✅ 适合已配置好环境的情况

**使用场景**：
- 系统 Python 环境已安装所有依赖
- 不想使用虚拟环境
- 快速测试

**使用步骤**：

```bash
./start-simple.sh
```

**注意事项**：
- 需要确保系统 Python 环境已安装所有依赖
- 可能与其他项目的依赖冲突

### 3. start.bat（Windows 版本）

**特点**：
- ✅ 使用虚拟环境（backend\venv）
- ✅ 自动检查并创建虚拟环境
- ✅ 自动检查并安装依赖
- ✅ 在独立窗口中运行后端和前端
- ✅ 易于查看日志

**使用步骤**：

1. **首次运行**：
   - 双击 `start.bat`
   - 或在命令行中运行：`start.bat`

2. **后续运行**：
   - 双击 `start.bat`

3. **停止服务**：
   - 关闭后端和前端的命令行窗口

**输出示例**：

```
================================================================
  AutoGen AI Chat - Development Environment (Windows)
================================================================

Checking virtual environment...
[OK] All dependencies are installed

================================================================
  Starting Backend Server (Virtual Environment)
================================================================

Waiting for backend to initialize...

================================================================
  Starting Frontend Server
================================================================

================================================================
  Application Started Successfully!
================================================================

[OK] Backend API:    http://localhost:8000
[OK] Frontend UI:    http://localhost:3000
[OK] API Docs:       http://localhost:8000/docs
[OK] ReDoc:          http://localhost:8000/redoc

Tips:
   - Backend uses virtual environment: backend\venv
   - Backend auto-reloads on code changes
   - Frontend auto-reloads on code changes
   - Close the terminal windows to stop servers
```

## 🔧 故障排除

### 问题 1: 权限错误（macOS/Linux）

**现象**：
```
bash: ./start.sh: Permission denied
```

**解决方案**：
```bash
chmod +x start.sh
./start.sh
```

### 问题 2: 虚拟环境创建失败

**现象**：
```
Error: Failed to create virtual environment
```

**解决方案**：
```bash
# 手动创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt
pip install "pillow>=11.0.0" --upgrade
```

### 问题 3: 端口被占用

**现象**：
```
Error: Address already in use
```

**解决方案**：

**macOS/Linux**：
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :3000  # 前端

# 杀死进程
kill -9 <PID>
```

**Windows**：
```cmd
# 查找占用端口的进程
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 杀死进程
taskkill /PID <PID> /F
```

### 问题 4: Node.js 未安装

**现象**：
```
Error: Node.js is not installed
```

**解决方案**：
- 访问 https://nodejs.org/
- 下载并安装 Node.js LTS 版本
- 重新运行启动脚本

### 问题 5: 依赖安装失败

**现象**：
```
Error: Failed to install dependencies
```

**解决方案**：
```bash
# 清理并重新安装
cd backend
rm -rf venv  # macOS/Linux
# 或
rmdir /s venv  # Windows

# 重新运行启动脚本
./start.sh  # macOS/Linux
start.bat   # Windows
```

## 💡 最佳实践

### 1. 本地开发

**推荐使用**：
- macOS/Linux: `./start.sh`
- Windows: `start.bat`

**原因**：
- 使用虚拟环境，隔离依赖
- 自动检查和安装依赖
- 不会污染系统环境

### 2. 生产部署

不推荐使用这些脚本，应该使用：
- Docker 容器
- systemd 服务（Linux）
- PM2 进程管理器
- Gunicorn/Uvicorn（后端）
- Nginx（前端静态文件）

参考：[README.md](../README.md) 的部署章节

### 3. 团队协作

**建议**：
1. 统一使用虚拟环境
2. 提交 `requirements.txt` 到版本控制
3. 不提交 `venv/` 目录
4. 在 `.gitignore` 中排除虚拟环境

## 📚 相关文档

- [README.md](../README.md) - 项目总览
- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [MARKER_PDF_INSTALLATION.md](MARKER_PDF_INSTALLATION.md) - Marker PDF 安装指南

## 🆘 获取帮助

如果遇到问题：
1. 查看本文档的故障排除章节
2. 查看 [README.md](../README.md) 的故障排除章节
3. 检查后端和前端的日志输出
4. 提交 Issue 到项目仓库

---

**祝开发愉快！** 🎉

