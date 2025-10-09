import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout.jsx'
import Home from './pages/Home.jsx'
import ChatNormalPage from './pages/ChatNormalPage.jsx'
import ChatTestCasePage from './pages/ChatTestCasePage.jsx'
import ImageAnalysisPage from './pages/ImageAnalysisPage.jsx'
import './index.css'

// 创建路由配置
const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/home" replace />,
      },
      {
        path: 'home',
        element: <Home />,
      },
      {
        path: 'chat/normal',
        element: <ChatNormalPage />,
      },
      {
        path: 'chat/testcase',
        element: <ChatTestCasePage />,
      },
      {
        path: 'image-analysis',
        element: <ImageAnalysisPage />,
      },
    ],
  },
]);

// 临时禁用 Strict Mode 以解决 SSE 流式传输中的重复累加问题
// Strict Mode 在开发模式下会双重调用状态更新函数，导致内容重复
// TODO: 使用 useReducer 重构状态管理后可以重新启用
ReactDOM.createRoot(document.getElementById('root')).render(
  <RouterProvider router={router} />
)

