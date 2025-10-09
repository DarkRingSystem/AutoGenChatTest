# 问题排查指南

## 🔧 常见错误及解决方案

### 1. ❌ No module named 'weasyprint' 或 'mammoth'

**错误信息**:
```
Failed to convert /var/folders/.../xxx.docx to PDF: No module named 'weasyprint'
```

或者：
```
Failed to convert /var/folders/.../xxx.docx to PDF: No module named 'mammoth'
```

或者：
```
OSError: cannot load library 'libgobject-2.0-0'
```

**原因**: marker 转换 DOCX 等格式时需要 weasyprint 和 mammoth 库及其系统依赖

**解决方法**:

**macOS 用户** ⭐:
```bash
# 1. 安装系统依赖
brew install cairo pango gdk-pixbuf libffi

# 2. 安装 Python 依赖
pip3 install weasyprint mammoth

# 3. 使用启动脚本
cd backend
./start.sh
```

**详细说明**: 参考 [MACOS_SETUP.md](MACOS_SETUP.md)

**Linux/Windows 用户**:
```bash
# 安装依赖
pip3 install weasyprint mammoth

# 验证安装
python3 -c "import weasyprint; print('weasyprint: OK')"
python3 -c "import mammoth; print('mammoth: OK')"
```

**如果安装失败**，参考 [DEPENDENCY_INSTALLATION.md](DEPENDENCY_INSTALLATION.md) 中的系统依赖安装说明。

---

### 2. ❌ Form data requires "python-multipart"

**错误信息**:
```
RuntimeError: Form data requires "python-multipart" to be installed.
```

**原因**: FastAPI 处理文件上传需要 python-multipart

**解决方法**:
```bash
pip3 install python-multipart
```

---

### 3. ❌ 文件上传后没有反应

**可能原因**:
- 后端服务未启动
- 端口被占用
- 网络连接问题

**排查步骤**:

1. **检查后端服务**:
```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 应该返回:
# {"status":"healthy","agent_initialized":true,"session_count":0}
```

2. **检查端口占用**:
```bash
# macOS/Linux
lsof -i :8000

# 如果端口被占用，杀死进程
kill -9 <PID>
```

3. **查看后端日志**:
```bash
# 启动后端时查看日志
cd backend
python3 main.py

# 查看是否有错误信息
```

---

### 4. ❌ 文件解析失败

**错误信息**:
```
❌ 转换失败: Failed to convert xxx
```

**可能原因**:
- 文件损坏
- 文件格式不支持
- 缺少依赖

**排查步骤**:

1. **检查文件格式**:
```
支持的格式:
- PDF: .pdf
- 图片: .png, .jpg, .jpeg, .gif, .bmp, .tiff
- PowerPoint: .pptx, .ppt
- Word: .docx, .doc
- Excel: .xlsx, .xls
- HTML: .html, .htm
- EPUB: .epub
```

2. **检查文件大小**:
```
- 单个文件最大: 100MB
- 如果文件过大，尝试压缩或分割
```

3. **检查依赖**:
```bash
# 验证 marker-pdf
python3 -c "import marker; print('marker: OK')"

# 验证 weasyprint
python3 -c "import weasyprint; print('weasyprint: OK')"
```

4. **查看详细错误**:
```bash
# 查看后端日志，找到详细错误信息
cd backend
python3 main.py
# 上传文件，查看控制台输出
```

---

### 5. ❌ 智能体没有基于文件内容回答

**可能原因**:
- 文件未成功解析
- 文件 ID 未正确传递
- 后端上下文构建失败

**排查步骤**:

1. **检查文件解析状态**:
```
- 文件列表中应该显示 ✅ 图标
- 标签显示"已解析"
```

2. **检查用户消息**:
```
- 用户消息应该显示 📎 包含 X 个文件
- 如果没有显示，说明文件 ID 未传递
```

3. **检查浏览器控制台**:
```javascript
// 打开浏览器开发者工具 (F12)
// 查看 Network 标签
// 找到 /api/chat/stream 请求
// 查看 Request Payload:
{
  "message": "用户问题",
  "file_ids": ["uuid-123", "uuid-456"]  // 应该有这个字段
}
```

4. **检查后端日志**:
```bash
# 后端应该输出文件上下文构建信息
# 查看是否有 file_ids 相关日志
```

---

### 6. ❌ 前端样式错误

**可能原因**:
- CSS 文件未加载
- 组件导入错误
- 主题切换问题

**解决方法**:

1. **重启前端服务**:
```bash
cd frontend
npm run dev
```

2. **清除浏览器缓存**:
```
- Chrome: Ctrl+Shift+Delete (Windows) 或 Cmd+Shift+Delete (Mac)
- 选择"缓存的图片和文件"
- 点击"清除数据"
```

3. **检查控制台错误**:
```
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签
- 查看是否有 CSS 或 JS 加载错误
```

---

### 7. ❌ 端口已被占用

**错误信息**:
```
[Errno 48] Address already in use
```

**解决方法**:

**后端 (8000)**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
# 修改 backend/main.py:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**前端 (3000/3001/3002)**:
```bash
# Vite 会自动尝试其他端口
# 如果需要指定端口，修改 frontend/vite.config.js:
server: {
  port: 3003
}
```

---

### 8. ❌ CORS 错误

**错误信息**:
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3002' has been blocked by CORS policy
```

**原因**: 跨域请求被阻止

**解决方法**:

检查 `backend/main.py` 中的 CORS 配置:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 9. ❌ 文件上传超时

**可能原因**:
- 文件太大
- 网络慢
- 服务器处理慢

**解决方法**:

1. **增加超时时间**:
```javascript
// frontend/src/components/FileUpload.jsx
const response = await fetch('...', {
  method: 'POST',
  body: formData,
  signal: AbortSignal.timeout(300000)  // 5 分钟超时
});
```

2. **压缩文件**:
```
- 减小文件大小
- 或分批上传
```

---

### 10. ❌ 内存不足

**错误信息**:
```
MemoryError: Unable to allocate array
```

**原因**: 处理大文件时内存不足

**解决方法**:

1. **减小文件大小**:
```
- 压缩文件
- 减少上传数量
```

2. **增加系统内存**:
```
- 关闭其他应用
- 增加虚拟内存
```

3. **使用流式处理** (需要修改代码):
```python
# 分块处理大文件
# 而不是一次性加载到内存
```

---

## 🔍 调试技巧

### 1. 查看后端日志

```bash
cd backend
python3 main.py

# 观察控制台输出
# 查找错误信息和堆栈跟踪
```

### 2. 查看前端日志

```
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 查看错误信息
4. 切换到 Network 标签
5. 查看 API 请求和响应
```

### 3. 测试 API

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试文件上传
curl -X POST "http://localhost:8000/api/convert/markdown/batch" \
  -F "files=@test.pdf" \
  -F "max_concurrent=3"

# 测试聊天
curl -X POST "http://localhost:8000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","file_ids":["uuid-123"]}'
```

### 4. 检查文件存储

```python
# 在 backend/api/routes.py 中添加调试代码
print(f"文件存储: {file_storage}")
print(f"文件 ID 列表: {file_ids}")
```

---

## 📋 问题排查清单

遇到问题时，按照以下清单逐项检查：

### 后端
- [ ] Python 版本 >= 3.9
- [ ] 所有依赖已安装 (pip list)
- [ ] weasyprint 已安装
- [ ] 后端服务正常启动
- [ ] 端口 8000 未被占用
- [ ] /health 端点返回正常
- [ ] 环境变量配置正确

### 前端
- [ ] Node.js 版本 >= 16
- [ ] npm 依赖已安装
- [ ] 前端服务正常启动
- [ ] 浏览器控制台无错误
- [ ] 网络请求正常
- [ ] CORS 配置正确

### 文件上传
- [ ] 文件格式支持
- [ ] 文件大小 < 100MB
- [ ] 文件数量 <= 10
- [ ] 文件未损坏
- [ ] 解析状态显示正常
- [ ] 文件 ID 正确传递

---

## 🆘 获取帮助

如果以上方法都无法解决问题：

1. **查看文档**:
   - `FILE_UPLOAD_ARCHITECTURE.md` - 架构说明
   - `FILE_UPLOAD_FEATURE_SUMMARY.md` - 功能总结
   - `DEPENDENCY_INSTALLATION.md` - 依赖安装

2. **检查日志**:
   - 后端控制台输出
   - 前端浏览器控制台
   - Network 请求详情

3. **提供信息**:
   - 错误信息完整截图
   - 后端日志
   - 前端控制台日志
   - 操作步骤
   - 系统环境 (OS, Python 版本, Node.js 版本)

---

## ✅ 快速修复命令

```bash
# 重新安装所有依赖
cd backend && pip3 install -r requirements.txt
cd ../frontend && npm install

# 重启所有服务
# 终端 1
cd backend && python3 main.py

# 终端 2
cd frontend && npm run dev

# 清除缓存
rm -rf backend/__pycache__
rm -rf frontend/node_modules/.cache
```

问题解决后，记得更新文档，帮助其他人！

