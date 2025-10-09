import React, { useState, useRef } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp, Button, Menu, Space, Tooltip } from 'antd';
import {
  HomeOutlined,
  MessageOutlined,
  ExperimentOutlined,
  PictureOutlined,
  SunOutlined,
  MoonOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import './MainLayout.css';

export default function MainLayout() {
  const [isDark, setIsDark] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const clearSessionRef = useRef(null); // 用于存储清空会话的回调函数

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  // 注册清空会话的回调函数（由子组件调用）
  const registerClearSession = (callback) => {
    clearSessionRef.current = callback;
  };

  // 清空会话
  const handleClearSession = () => {
    if (clearSessionRef.current) {
      clearSessionRef.current();
    }
  };

  // 菜单项配置
  const menuItems = [
    {
      key: '/home',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/chat/normal',
      icon: <MessageOutlined />,
      label: '普通对话',
    },
    {
      key: '/chat/testcase',
      icon: <ExperimentOutlined />,
      label: '测试用例',
    },
    {
      key: '/image-analysis',
      icon: <PictureOutlined />,
      label: '图片分析',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  // 获取当前选中的菜单项
  const selectedKey = location.pathname;

  // 判断是否在功能页面（非首页）
  const isInModePage = location.pathname !== '/home' && location.pathname !== '/';

  // 判断是否在首页
  const isHomePage = location.pathname === '/home' || location.pathname === '/';

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#00b96b',
        },
      }}
    >
      <AntApp>
        <div className={`main-layout ${isDark ? 'dark' : 'light'}`}>
          {/* 顶部导航栏 - 仅在非首页显示 */}
          {!isHomePage && (
            <header className="main-header">
              <div className="header-content">
                <div className="logo">
                  <span className="logo-icon">🤖</span>
                  <span className="logo-text">AutoGen Chat</span>
                </div>

                <Menu
                  mode="horizontal"
                  selectedKeys={[selectedKey]}
                  items={menuItems}
                  onClick={handleMenuClick}
                  className="main-menu"
                />

                <div className="header-actions">
                  <Space size="middle">
                    {/* 清空会话按钮 - 仅在功能页面显示 */}
                    {isInModePage && (
                      <Tooltip title="清空对话">
                        <Button
                          type="text"
                          icon={<ClearOutlined />}
                          onClick={handleClearSession}
                          className="action-button"
                        />
                      </Tooltip>
                    )}

                    {/* 主题切换按钮 */}
                    <Tooltip title={isDark ? '切换到亮色主题' : '切换到深色主题'}>
                      <Button
                        type="text"
                        icon={isDark ? <SunOutlined /> : <MoonOutlined />}
                        onClick={toggleTheme}
                        className="action-button"
                      />
                    </Tooltip>
                  </Space>
                </div>
              </div>
            </header>
          )}

          {/* 主内容区域 */}
          <main className="main-content">
            <Outlet context={{ isDark, toggleTheme, registerClearSession }} />
          </main>
        </div>
      </AntApp>
    </ConfigProvider>
  );
}

