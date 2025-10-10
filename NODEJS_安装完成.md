# ✅ Node.js 安装完成

## 安装信息

- **版本**: Node.js 22.20.0 LTS (长期支持版本)
- **安装方式**: 通过 Windows Package Manager (winget)
- **状态**: ✅ 安装成功

## ⚠️ 重要：需要重启终端

Node.js 已经成功安装，但需要**重新打开终端窗口**才能使用 `node` 和 `npm` 命令。

### 方式 1: 重启终端（推荐）

1. **关闭当前所有终端窗口**
2. **重新打开终端**（PowerShell、CMD 或 Windows Terminal）
3. 验证安装：
   ```cmd
   node --version
   npm --version
   ```

### 方式 2: 刷新环境变量（PowerShell）

如果不想关闭终端，可以在 PowerShell 中运行：
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

然后验证：
```powershell
node --version
npm --version
```

## 验证安装

重启终端后，运行以下命令验证：

```cmd
# 检查 Node.js 版本
node --version
# 应该显示: v22.20.0

# 检查 npm 版本
npm --version
# 应该显示: 10.x.x (具体版本号)

# 测试 Node.js
node -e "console.log('Node.js 工作正常!')"
```

## 下一步：启动项目

Node.js 安装完成后，你可以启动项目了：

### 方式 1: 使用启动脚本

**重新打开终端后**，在项目目录运行：
```cmd
start.bat
```

### 方式 2: 手动启动前端

```cmd
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 完整启动流程

1. **关闭当前终端**
2. **重新打开终端**
3. **进入项目目录**:
   ```cmd
   cd D:\AI\AutoGenChatTest
   ```
4. **运行启动脚本**:
   ```cmd
   start.bat
   ```

启动脚本会自动：
- ✅ 检查并创建 Python 虚拟环境
- ✅ 安装后端依赖
- ✅ 启动后端服务（端口 8000）
- ✅ 安装前端依赖（使用刚安装的 npm）
- ✅ 启动前端服务（端口 3000）

## 访问应用

启动成功后，访问：
- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 常见问题

### Q: 重启终端后还是找不到 node 命令？

**A**: 检查环境变量：
1. 打开"系统属性" → "环境变量"
2. 在"系统变量"中找到 `Path`
3. 确认包含类似这样的路径：
   - `C:\Program Files\nodejs\`
4. 如果没有，手动添加后重启终端

### Q: npm install 很慢怎么办？

**A**: 使用国内镜像源：
```cmd
npm config set registry https://registry.npmmirror.com
```

### Q: 需要安装特定版本的 Node.js？

**A**: 当前安装的是 LTS 版本（22.20.0），这是推荐的稳定版本。如果需要其他版本，可以：
1. 卸载当前版本：`winget uninstall OpenJS.NodeJS.LTS`
2. 安装其他版本：访问 https://nodejs.org/

## 项目依赖安装

前端依赖会在首次运行 `start.bat` 或 `npm install` 时自动安装，包括：
- React 18
- Ant Design 5
- Vite
- 其他开发依赖

## 总结

✅ Node.js 22.20.0 LTS 安装成功  
⚠️ 需要重启终端才能使用  
✅ 后端 Python 依赖已修复  
✅ 项目已准备好启动  

**下一步**: 重启终端，然后运行 `start.bat` 启动项目！

---

**安装日期**: 2025-10-10  
**Node.js 版本**: v22.20.0 LTS  
**npm 版本**: 10.x.x

