# 前端路由重构方案

## 📋 目标

将当前单页面应用重构为多路由应用，为每个功能模块提供独立的 URL 路径。

---

## 🎯 路由设计

### URL 结构

```
/                          # 首页 - 模式选择器
├── /chat                  # 普通对话模式
├── /testcase              # 测试用例生成模式
└── /image-analysis        # 图片分析模式
```

### 页面标题

```javascript
{
  '/': 'AutoGen Chat - 选择模式',
  '/chat': 'AutoGen Chat - 普通对话',
  '/testcase': 'AutoGen Chat - 测试用例生成',
  '/image-analysis': 'AutoGen Chat - 图片分析'
}
```

---

## 📁 目录结构重构

### 新增目录

```
frontend/src/
├── pages/                      # 页面组件（新增）
│   ├── Home.jsx               # 首页 - 模式选择器
│   ├── ChatPage.jsx           # 普通对话页面
│   ├── TestCasePage.jsx       # 测试用例页面
│   └── ImageAnalysisPage.jsx  # 图片分析页面
│
├── components/                 # 组件重组
│   ├── layout/                # 布局组件（新增）
│   │   ├── Header.jsx         # 顶部导航
│   │   ├── Footer.jsx         # 底部信息
│   │   └── MainLayout.jsx     # 主布局
│   │
│   ├── chat/                  # 聊天组件（新增）
│   │   ├── ChatInterface.jsx  # 聊天界面
│   │   ├── MessageList.jsx    # 消息列表
│   │   └── MessageInput.jsx   # 输入框
│   │
│   ├── testcase/              # 测试用例组件（新增）
│   │   ├── TestCaseInterface.jsx
│   │   └── AgentPanel.jsx
│   │
│   ├── image/                 # 图片分析组件（新增）
│   │   └── ImageAnalyzer.jsx  # 从根目录移动
│   │
│   └── common/                # 通用组件（新增）
│       ├── MatrixRain.jsx     # 从根目录移动
│       ├── ModeSelector.jsx   # 从根目录移动
│       ├── FileUpload.jsx     # 从根目录移动
│       └── ThemeToggle.jsx    # 主题切换
│
├── hooks/                      # 自定义 Hooks（新增）
│   ├── useChat.js             # 聊天逻辑
│   ├── useSession.js          # 会话管理
│   ├── useFileUpload.js       # 文件上传
│   └── useTheme.js            # 主题管理
│
├── services/                   # API 服务（新增）
│   ├── api.js                 # API 基础配置
│   ├── chatService.js         # 聊天 API
│   ├── testcaseService.js     # 测试用例 API
│   └── imageService.js        # 图片分析 API
│
├── utils/                      # 工具函数（新增）
│   ├── helpers.js             # 通用辅助函数
│   └── constants.js           # 常量定义
│
└── routes/                     # 路由配置（新增）
    └── index.jsx              # 路由定义
```

---

## 🔧 实现步骤

### 阶段 1: 安装依赖

```bash
cd frontend
npm install react-router-dom
```

### 阶段 2: 创建路由配置

**文件**: `src/routes/index.jsx`

```jsx
import { createBrowserRouter } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import Home from '../pages/Home';
import ChatPage from '../pages/ChatPage';
import TestCasePage from '../pages/TestCasePage';
import ImageAnalysisPage from '../pages/ImageAnalysisPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'chat',
        element: <ChatPage />,
      },
      {
        path: 'testcase',
        element: <TestCasePage />,
      },
      {
        path: 'image-analysis',
        element: <ImageAnalysisPage />,
      },
    ],
  },
]);
```

### 阶段 3: 更新入口文件

**文件**: `src/main.jsx`

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <RouterProvider router={router} />
);
```

### 阶段 4: 创建主布局

**文件**: `src/components/layout/MainLayout.jsx`

```jsx
import { Outlet } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import Header from './Header';
import Footer from './Footer';
import MatrixRain from '../common/MatrixRain';
import { useTheme } from '../../hooks/useTheme';

export default function MainLayout() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <div className="app-container">
        <MatrixRain />
        <Header isDark={isDark} toggleTheme={toggleTheme} />
        <main className="main-content">
          <Outlet />
        </main>
        <Footer />
      </div>
    </ConfigProvider>
  );
}
```

### 阶段 5: 创建页面组件

#### 首页 - 模式选择器

**文件**: `src/pages/Home.jsx`

```jsx
import { useNavigate } from 'react-router-dom';
import ModeSelector from '../components/common/ModeSelector';

export default function Home() {
  const navigate = useNavigate();

  const handleModeSelect = (mode) => {
    navigate(`/${mode}`);
  };

  return (
    <div className="home-page">
      <ModeSelector onSelect={handleModeSelect} />
    </div>
  );
}
```

#### 普通对话页面

**文件**: `src/pages/ChatPage.jsx`

```jsx
import { useEffect } from 'react';
import ChatInterface from '../components/chat/ChatInterface';
import { useSession } from '../hooks/useSession';

export default function ChatPage() {
  useEffect(() => {
    document.title = 'AutoGen Chat - 普通对话';
  }, []);

  const { conversationId, setConversationId } = useSession('normal');

  return (
    <div className="chat-page">
      <ChatInterface
        mode="normal"
        conversationId={conversationId}
        setConversationId={setConversationId}
      />
    </div>
  );
}
```

### 阶段 6: 创建自定义 Hooks

**文件**: `src/hooks/useSession.js`

```javascript
import { useState, useEffect } from 'react';

export function useSession(mode) {
  const [conversationId, setConversationId] = useState(null);

  useEffect(() => {
    // 从 localStorage 恢复会话 ID
    const savedId = localStorage.getItem(`${mode}_conversation_id`);
    if (savedId) {
      setConversationId(savedId);
    }
  }, [mode]);

  useEffect(() => {
    // 保存会话 ID 到 localStorage
    if (conversationId) {
      localStorage.setItem(`${mode}_conversation_id`, conversationId);
    }
  }, [conversationId, mode]);

  const clearSession = () => {
    setConversationId(null);
    localStorage.removeItem(`${mode}_conversation_id`);
  };

  return { conversationId, setConversationId, clearSession };
}
```

### 阶段 7: 创建 API 服务

**文件**: `src/services/api.js`

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  },

  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};
```

---

## 🎨 导航组件设计

### 顶部导航栏

```jsx
import { Link, useLocation } from 'react-router-dom';
import { Menu } from 'antd';
import {
  HomeOutlined,
  MessageOutlined,
  ExperimentOutlined,
  PictureOutlined,
} from '@ant-design/icons';

export default function Header({ isDark, toggleTheme }) {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: <Link to="/chat">普通对话</Link>,
    },
    {
      key: '/testcase',
      icon: <ExperimentOutlined />,
      label: <Link to="/testcase">测试用例</Link>,
    },
    {
      key: '/image-analysis',
      icon: <PictureOutlined />,
      label: <Link to="/image-analysis">图片分析</Link>,
    },
  ];

  return (
    <header className="app-header">
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
      />
      <button onClick={toggleTheme}>
        {isDark ? '🌞' : '🌙'}
      </button>
    </header>
  );
}
```

---

## 📊 迁移计划

### 优先级

1. **高优先级** - 核心路由功能
   - [ ] 安装 react-router-dom
   - [ ] 创建路由配置
   - [ ] 创建主布局组件
   - [ ] 创建页面组件

2. **中优先级** - 代码重组
   - [ ] 拆分 App.jsx 为独立页面
   - [ ] 创建自定义 Hooks
   - [ ] 创建 API 服务层

3. **低优先级** - 优化增强
   - [ ] 添加页面过渡动画
   - [ ] 添加面包屑导航
   - [ ] 添加 404 页面

### 时间估算

- **阶段 1-3**: 1-2 小时（基础路由）
- **阶段 4-5**: 2-3 小时（页面拆分）
- **阶段 6-7**: 1-2 小时（Hooks 和服务）
- **测试和优化**: 1-2 小时

**总计**: 5-9 小时

---

## ✅ 验收标准

- [ ] 可以通过 URL 直接访问每个功能
- [ ] 浏览器前进/后退按钮正常工作
- [ ] 刷新页面保持在当前功能
- [ ] 每个页面有独立的标题
- [ ] 导航菜单高亮当前页面
- [ ] 会话 ID 在页面刷新后保持
- [ ] 所有现有功能正常工作

---

## 🚀 后续优化

### 1. 懒加载

```jsx
import { lazy, Suspense } from 'react';

const ChatPage = lazy(() => import('./pages/ChatPage'));
const TestCasePage = lazy(() => import('./pages/TestCasePage'));

// 在路由中使用
<Suspense fallback={<Loading />}>
  <ChatPage />
</Suspense>
```

### 2. 路由守卫

```jsx
function ProtectedRoute({ children }) {
  const isAuthenticated = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
}
```

### 3. 面包屑导航

```jsx
import { Breadcrumb } from 'antd';
import { useLocation, Link } from 'react-router-dom';

export default function BreadcrumbNav() {
  const location = useLocation();
  const pathSnippets = location.pathname.split('/').filter(i => i);

  return (
    <Breadcrumb>
      <Breadcrumb.Item>
        <Link to="/">首页</Link>
      </Breadcrumb.Item>
      {pathSnippets.map((snippet, index) => (
        <Breadcrumb.Item key={snippet}>
          {snippet}
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  );
}
```

---

## 📚 参考资源

- [React Router 官方文档](https://reactrouter.com/)
- [Ant Design 布局组件](https://ant.design/components/layout-cn/)
- [Vite 环境变量](https://vitejs.dev/guide/env-and-mode.html)

