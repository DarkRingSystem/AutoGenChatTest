# 依赖安装说明

## 📦 后端依赖

### 核心依赖

文件上传和转换功能需要以下依赖：

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

### 安装方法

#### 方法 1: 使用 requirements.txt（推荐）

```bash
cd backend
pip install -r requirements.txt
```

#### 方法 2: 单独安装

```bash
# 核心框架
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv

# AutoGen 智能体
pip install autogen-agentchat==0.7.5 autogen-ext[openai]==0.7.5

# Token 计数
pip install tiktoken

# 文件转换
pip install marker-pdf python-multipart weasyprint mammoth
```

### 重要依赖说明

#### 1. marker-pdf
- **用途**: 文件转换核心库
- **支持格式**: PDF, 图片, DOCX, PPTX, XLSX, HTML, EPUB
- **版本**: >= 1.0.0

#### 2. python-multipart
- **用途**: FastAPI 文件上传支持
- **必需**: 处理 multipart/form-data 请求
- **版本**: >= 0.0.6

#### 3. weasyprint ⭐
- **用途**: marker 转换 DOCX 等格式时需要
- **必需**: 转换 Office 文档为 PDF
- **版本**: >= 66.0
- **错误提示**: `No module named 'weasyprint'`

#### 4. mammoth ⭐
- **用途**: marker 转换 DOCX 文件时需要
- **必需**: 将 DOCX 转换为 HTML
- **版本**: >= 1.11.0
- **错误提示**: `No module named 'mammoth'`

### 常见问题

#### Q1: 安装 marker-pdf 失败？

**可能原因**:
- 网络问题
- Python 版本不兼容（需要 Python 3.9+）

**解决方法**:
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple marker-pdf

# 或使用阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ marker-pdf
```

#### Q2: 转换 DOCX 时报错 "No module named 'weasyprint'"？

**原因**: marker 转换某些格式需要 weasyprint

**解决方法**:
```bash
pip install weasyprint
```

#### Q3: weasyprint 安装失败？

**可能原因**: 缺少系统依赖

**macOS 解决方法**:
```bash
# 安装 Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装系统依赖
brew install cairo pango gdk-pixbuf libffi

# 再次安装 weasyprint
pip install weasyprint

# ⚠️ 重要：macOS 需要设置环境变量
# 使用提供的启动脚本（推荐）
cd backend
./start.sh

# 或手动设置环境变量
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
python3 main.py
```

**Ubuntu/Debian 解决方法**:
```bash
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

pip install weasyprint
```

**Windows 解决方法**:
```bash
# 下载并安装 GTK3 Runtime
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

# 然后安装 weasyprint
pip install weasyprint
```

#### Q4: 虚拟环境中安装？

**推荐使用虚拟环境**:
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 🎨 前端依赖

### 核心依赖

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@ant-design/x": "^1.0.0",
    "antd": "^5.22.6",
    "framer-motion": "^11.15.0",
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.6.1"
  }
}
```

### 安装方法

```bash
cd frontend
npm install
```

### 常见问题

#### Q1: npm install 失败？

**解决方法**:
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

#### Q2: 使用国内镜像加速？

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

## 🔍 验证安装

### 后端验证

```bash
cd backend

# 验证 Python 版本
python3 --version  # 应该 >= 3.9

# 验证依赖
python3 -c "import marker; print('marker-pdf: OK')"
python3 -c "import weasyprint; print('weasyprint: OK')"
python3 -c "import fastapi; print('fastapi: OK')"
python3 -c "import autogen_agentchat; print('autogen: OK')"

# 启动服务测试
python3 main.py
```

### 前端验证

```bash
cd frontend

# 验证 Node.js 版本
node --version  # 应该 >= 16

# 验证 npm 版本
npm --version

# 启动服务测试
npm run dev
```

## 📋 完整安装流程

### 首次安装

```bash
# 1. 克隆项目（如果需要）
git clone <repository-url>
cd autogenTest

# 2. 安装后端依赖
cd backend
pip3 install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 配置环境变量
cd ../backend
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥

# 5. 启动服务
# 终端 1: 后端
cd backend
python3 main.py

# 终端 2: 前端
cd frontend
npm run dev
```

### 更新依赖

```bash
# 后端
cd backend
pip3 install -r requirements.txt --upgrade

# 前端
cd frontend
npm update
```

## ✅ 安装检查清单

安装完成后，确保以下项目都正常：

### 后端
- [ ] Python 版本 >= 3.9
- [ ] fastapi 已安装
- [ ] uvicorn 已安装
- [ ] autogen-agentchat 已安装
- [ ] marker-pdf 已安装
- [ ] python-multipart 已安装
- [ ] weasyprint 已安装 ⭐
- [ ] 后端服务可以启动
- [ ] 访问 http://localhost:8000/health 返回正常

### 前端
- [ ] Node.js 版本 >= 16
- [ ] npm 已安装
- [ ] 依赖安装成功
- [ ] 前端服务可以启动
- [ ] 访问 http://localhost:3002 显示正常

## 🚀 快速修复

如果遇到 `No module named 'weasyprint'` 错误：

```bash
# 快速修复
pip3 install weasyprint

# 如果失败，先安装系统依赖（macOS）
brew install cairo pango gdk-pixbuf libffi
pip3 install weasyprint

# 验证安装
python3 -c "import weasyprint; print('weasyprint installed successfully!')"
```

## 📝 总结

- ✅ 后端核心依赖: FastAPI, AutoGen, marker-pdf, weasyprint
- ✅ 前端核心依赖: React, Ant Design, Framer Motion
- ✅ 关键新增: weasyprint（转换 DOCX 等格式必需）
- ✅ 推荐使用虚拟环境
- ✅ 遇到问题先检查 Python 和 Node.js 版本

所有依赖安装完成后，即可正常使用文件上传功能！

