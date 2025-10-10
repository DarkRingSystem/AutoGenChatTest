# Windows 环境启动指南

## ✅ 已修复的问题

### 问题 1: requirements.txt 编码错误

**错误信息:**
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xac in position 235: illegal multibyte sequence
```

**原因:**
Windows 系统默认使用 GBK 编码，而 `requirements.txt` 文件中包含中文注释，导致 pip 无法正确解析。

**解决方案:**
✅ 已修复 - 移除了 `requirements.txt` 中的所有中文注释。

---

### 问题 2: .env 文件编码问题

**原因:**
`.env` 和 `.env.example` 文件中包含中文注释，可能在某些情况下导致读取问题。

**解决方案:**
✅ 已修复 - 将所有中文注释替换为英文注释。

---

### 问题 3: 依赖冲突 (最关键)

**错误信息:**
```
ERROR: Cannot install -r requirements.txt (line 9) and autogen-agentchat because these package versions have conflicting dependencies.

The conflict is caused by:
    marker-pdf 1.10.1 depends on Pillow<11.0.0 and >=10.1.0
    autogen-core 0.7.5 depends on pillow>=11.0.0
```

**原因:**
- `marker-pdf` (用于 PDF/Markdown 转换) 需要 `Pillow < 11.0.0`
- `autogen-core` (核心 AI 框架) 需要 `Pillow >= 11.0.0`
- 这两个包的 Pillow 版本要求互相冲突，无法同时安装

**解决方案:**
✅ 已修复 - 从主 `requirements.txt` 中移除了 `marker-pdf` 及其相关依赖。
- Markdown 转换功能现在是可选的
- 如需该功能，请参考 `backend/requirements-markdown.txt` 中的说明
- 核心 AI 聊天功能不受影响

---

## 启动步骤

### 方式一：使用启动脚本（推荐）

1. **双击运行 `start.bat`** 或在命令行中执行：
   ```cmd
   start.bat
   ```

2. 脚本会自动：
   - 检查并创建虚拟环境
   - 安装 Python 依赖
   - 检查并创建 .env 配置文件
   - 启动后端服务（端口 8000）
   - 安装前端依赖
   - 启动前端服务（端口 3000）

3. **配置 API 密钥**：
   - 首次运行时，脚本会提示编辑 `backend\.env` 文件
   - 打开 `backend\.env`，填入你的 API 密钥：
     ```env
     API_KEY=sk-your-deepseek-api-key
     MODEL_NAME=deepseek-chat
     BASE_URL=https://api.deepseek.com/v1
     ```

4. **访问应用**：
   - 前端: http://localhost:3000
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

---

### 方式二：手动启动

#### 1. 后端设置

```cmd
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 升级 Pillow（如果需要）
pip install "pillow>=11.0.0" --upgrade

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 启动后端
python main.py
```

#### 2. 前端设置

打开新的命令行窗口：

```cmd
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 常见问题

### 1. Python 版本问题

**错误:** `python: command not found` 或版本过低

**解决方案:**
- 确保安装了 Python 3.11 或更高版本
- 下载地址: https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### 2. Node.js 未安装

**错误:** `node: command not found`

**解决方案:**
- 安装 Node.js 18 或更高版本
- 下载地址: https://nodejs.org/
- 推荐安装 LTS 版本

### 3. 虚拟环境激活失败

**错误:** `venv\Scripts\activate : 无法加载文件...`

**解决方案:**
这是 PowerShell 执行策略限制。以管理员身份运行 PowerShell：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

或者使用 cmd.exe 而不是 PowerShell。

### 4. 端口被占用

**错误:** `Address already in use` 或 `端口已被占用`

**解决方案:**

查找并关闭占用端口的进程：
```cmd
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000

# 关闭进程（替换 PID 为实际进程 ID）
taskkill /PID <PID> /F

# 查找占用 3000 端口的进程
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

或者修改端口配置：
- 后端: 编辑 `backend\.env`，添加 `PORT=8001`
- 前端: 编辑 `frontend\vite.config.js`，修改 `server.port`

### 5. 依赖安装失败

**错误:** pip 安装依赖时出错

**解决方案:**

1. 升级 pip:
   ```cmd
   python -m pip install --upgrade pip
   ```

2. 使用国内镜像源（如果网络慢）:
   ```cmd
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. 单独安装问题依赖:
   ```cmd
   pip install fastapi uvicorn pydantic
   pip install autogen-agentchat==0.7.5
   pip install autogen-ext[openai]==0.7.5
   ```

### 6. marker-pdf 安装问题

**错误:** marker-pdf 或其依赖安装失败

**解决方案:**

marker-pdf 在 Windows 上可能需要额外的系统依赖。如果遇到问题：

1. 尝试单独安装:
   ```cmd
   pip install marker-pdf==1.10.1
   ```

2. 如果失败，可以暂时跳过（如果不需要 PDF 转换功能）:
   - 编辑 `requirements.txt`，注释掉相关行
   - 或者安装其他依赖后手动处理

### 7. API 密钥未配置

**错误:** `API_KEY not configured` 或认证失败

**解决方案:**
1. 确保 `backend\.env` 文件存在
2. 检查 API_KEY 是否正确填写
3. 确保没有多余的空格或引号
4. 重启后端服务

### 8. 前端无法连接后端

**错误:** `Network Error` 或 `Failed to fetch`

**解决方案:**
1. 确认后端已启动: 访问 http://localhost:8000/health
2. 检查防火墙设置
3. 确认前端配置正确（如果有 `frontend\.env`）
4. 检查浏览器控制台的详细错误信息

---

## 性能优化建议

### 1. 使用 SSD 存储虚拟环境

虚拟环境包含大量小文件，SSD 可以显著提升性能。

### 2. 配置 npm 缓存

```cmd
npm config set cache "D:\npm-cache" --global
```

### 3. 使用国内镜像源

**Python (pip):**
```cmd
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**Node.js (npm):**
```cmd
npm config set registry https://registry.npmmirror.com
```

---

## 开发工具推荐

### 1. 终端工具
- **Windows Terminal**: 现代化的终端工具
- **Git Bash**: 提供类 Unix 命令行体验

### 2. 代码编辑器
- **VS Code**: 推荐安装以下插件
  - Python
  - Pylance
  - ESLint
  - Prettier
  - GitLens

### 3. API 测试工具
- **Postman**: 测试 API 端点
- **Thunder Client**: VS Code 插件版 API 测试工具

---

## 验证安装

运行以下命令验证环境配置：

```cmd
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version

# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 测试后端健康检查
curl http://localhost:8000/health

# 或在浏览器中访问
# http://localhost:8000/health
```

---

## 获取帮助

如果遇到其他问题：

1. 查看后端日志（在后端终端窗口）
2. 查看前端控制台（浏览器 F12 开发者工具）
3. 查看 API 文档: http://localhost:8000/docs
4. 提交 Issue 到项目仓库

---

## 附录：完整的环境变量配置示例

`backend\.env` 文件示例：

```env
# DeepSeek Configuration (Recommended)
API_KEY=sk-your-deepseek-api-key-here
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Markdown Conversion Configuration
MARKDOWN_USE_LLM=false
MARKDOWN_FORCE_OCR=false
MARKDOWN_MAX_FILE_SIZE_MB=100
```

---

**最后更新:** 2025-10-10

