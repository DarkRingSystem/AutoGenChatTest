# Frontend 文档目录

本目录包含前端相关的文档。

## 📁 文档列表

- **README.md**: 前端项目说明
- **FILE_UPLOAD_TEST_GUIDE.md**: 文件上传功能测试指南

## 🎨 前端技术栈

- **框架**: React 18
- **构建工具**: Vite
- **UI 库**: Ant Design
- **动画**: Framer Motion
- **样式**: CSS Modules
- **HTTP 客户端**: Axios

## 📂 前端目录结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── CyberpunkRobot.jsx
│   │   ├── ImageAnalyzer.jsx
│   │   ├── ModeSelector.jsx
│   │   ├── NeonRocket.jsx
│   │   ├── NeonTestTube.jsx
│   │   ├── NeonImageAnalyzer.jsx
│   │   └── ...
│   ├── App.jsx              # 主应用组件
│   ├── App.css              # 全局样式
│   └── main.jsx             # 入口文件
├── index.html               # HTML 模板
├── package.json             # 依赖配置
└── vite.config.js           # Vite 配置
```

## 🚀 开发指南

### 启动开发服务器

```bash
cd frontend
npm install
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 🔗 相关文档

- [模式选择页面实现](../模式选择页面实现完成.md)
- [UI 图片分析功能](../UI图片分析功能完成总结.md)
- [卡片霓虹灯图标实现](../卡片霓虹灯图标实现完成.md)
- [前端测试用例智能体模式](../前端测试用例智能体模式实现.md)

