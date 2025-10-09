# AutoGen AI 聊天前端

一个现代化、炫酷的聊天界面，灵感来自 Gemini，使用 React、Ant Design X 和 Vite 构建。

## 功能特性

- 🎨 **精美界面** - Gemini 风格设计，渐变背景和流畅动画
- 🌊 **流式支持** - 使用 Ant Design X 组件实现实时 SSE 流式传输
- 📱 **响应式** - 完美适配桌面、平板和移动设备
- 🌓 **深色模式** - 支持浅色和深色主题切换
- ✨ **流畅动画** - 淡入效果、打字指示器和悬停动画
- 💬 **丰富 Markdown** - 完整的 Markdown 支持和代码高亮
- 🚀 **快速现代** - 使用 Vite 构建，开发体验极速

## 技术栈

- **React 18** - 现代 React 和 Hooks
- **Ant Design X** - 高级 AI 聊天组件，支持流式传输
- **Ant Design 5** - 精美的 UI 组件库
- **Vite** - 下一代前端构建工具
- **React Markdown** - Markdown 渲染，支持 GitHub 风格

## 快速开始

### 前置要求

- Node.js 18+ 和 npm/yarn/pnpm

### 安装

1. 安装依赖：
```bash
npm install
# 或
yarn install
# 或
pnpm install
```

2. 创建 `.env` 文件（可选）：
```bash
VITE_API_URL=http://localhost:8000
```

### 开发

启动开发服务器：
```bash
npm run dev
```

应用将在 `http://localhost:3000` 上运行

### 构建

生产环境构建：
```bash
npm run build
```

预览生产构建：
```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── App.jsx          # 主应用组件
│   ├── App.css          # 应用样式
│   ├── main.jsx         # 应用入口
│   └── index.css        # 全局样式
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
└── package.json         # 依赖和脚本
```

## 功能详解

### 欢迎屏幕
- 动画机器人图标
- 渐变文字效果
- 带悬停效果的快捷建议卡片
- 响应式网格布局

### 聊天界面
- 用户和助手消息气泡
- 每个角色的头像图标
- 流式打字指示器
- 平滑滚动到最新消息
- Markdown 渲染和语法高亮

### 消息发送器
- 简洁的输入框和发送按钮
- 消息处理时的加载状态
- 键盘快捷键（回车发送）
- 聚焦时的渐变边框效果

### 主题支持
- 浅色和深色模式切换
- 流畅的主题过渡
- 跨主题一致的配色方案

## 自定义

### 颜色
在 `App.css` 中编辑渐变颜色：
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### 建议提示
在 `App.jsx` 中修改 `SUGGESTIONS` 数组：
```javascript
const SUGGESTIONS = [
  { icon: <你的图标 />, text: '你的提示', color: '#你的颜色' },
  // ...
];
```

### API 端点
在 `.env` 中更改 API URL：
```
VITE_API_URL=http://你的-api-地址
```

## 浏览器支持

- Chrome/Edge（最新版）
- Firefox（最新版）
- Safari（最新版）
- 移动浏览器（iOS Safari、Chrome Mobile）

## 性能

- 代码分割优化加载
- 组件懒加载
- 优化的打包体积
- 流畅的 60fps 动画

## 贡献

欢迎提交问题和功能请求！

## 许可证

MIT

