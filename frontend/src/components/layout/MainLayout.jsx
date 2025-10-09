import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp, FloatButton, Menu } from 'antd';
import {
  HomeOutlined,
  MessageOutlined,
  ExperimentOutlined,
  PictureOutlined,
  SunOutlined,
  MoonOutlined,
} from '@ant-design/icons';
import './MainLayout.css';

export default function MainLayout() {
  const [isDark, setIsDark] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const toggleTheme = () => {
    setIsDark(!isDark);
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
          {/* 顶部导航栏 */}
          {location.pathname !== '/home' && (
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
                  <FloatButton
                    icon={isDark ? <SunOutlined /> : <MoonOutlined />}
                    onClick={toggleTheme}
                    tooltip={isDark ? '切换到亮色主题' : '切换到深色主题'}
                    style={{ position: 'static' }}
                  />
                </div>
              </div>
            </header>
          )}

          {/* 主内容区域 */}
          <main className="main-content">
            <Outlet context={{ isDark, toggleTheme }} />
          </main>
        </div>
      </AntApp>
    </ConfigProvider>
  );
}

