import React, { useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import ImageAnalyzer from '../components/ImageAnalyzer';
import MatrixRain from '../components/MatrixRain';
import '../components/LegacyApp.css';

export default function ImageAnalysisPage() {
  const { isDark } = useOutletContext();

  useEffect(() => {
    document.title = 'AutoGen Chat - 图片分析';
  }, []);

  return (
    <div className={`image-analysis-page ${isDark ? 'dark' : 'light'}`}
         style={{
           position: 'relative',
           height: '100%',
           overflow: 'auto'
         }}>
      {/* 矩阵雨背景 */}
      <MatrixRain isDark={isDark} />

      {/* 动态背景 */}
      <div className="animated-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      {/* 内容区域 */}
      <div style={{ position: 'relative', zIndex: 1, padding: '24px' }}>
        <ImageAnalyzer isDark={isDark} />
      </div>
    </div>
  );
}

