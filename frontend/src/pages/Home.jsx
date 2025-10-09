import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ModeSelector from '../components/ModeSelector';
import MatrixRain from '../components/MatrixRain';

export default function Home() {
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    document.title = 'AutoGen Chat - 选择模式';
  }, []);

  const handleModeSelect = (mode) => {
    // 根据模式导航到对应路径
    const routes = {
      'normal': '/chat/normal',
      'testcase': '/chat/testcase',
      'image-analyzer': '/image-analysis'
    };

    const path = routes[mode];
    if (path) {
      navigate(path);
    }
  };

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  return (
    <div className="home-page" style={{
      position: 'relative',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <MatrixRain />
      <ModeSelector
        onSelectMode={handleModeSelect}
        isDark={isDark}
        onToggleTheme={toggleTheme}
      />
    </div>
  );
}

