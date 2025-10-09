import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 临时禁用 Strict Mode 以解决 SSE 流式传输中的重复累加问题
// Strict Mode 在开发模式下会双重调用状态更新函数，导致内容重复
// TODO: 使用 useReducer 重构状态管理后可以重新启用
ReactDOM.createRoot(document.getElementById('root')).render(
  <App />
)

