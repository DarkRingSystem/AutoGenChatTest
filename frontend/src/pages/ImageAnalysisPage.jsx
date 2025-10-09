import React, { useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import ImageAnalyzer from '../components/ImageAnalyzer';

export default function ImageAnalysisPage() {
  const { isDark } = useOutletContext();

  useEffect(() => {
    document.title = 'AutoGen Chat - 图片分析';
  }, []);

  return (
    <div className="image-analysis-page" style={{ height: '100%', padding: '24px' }}>
      <ImageAnalyzer isDark={isDark} />
    </div>
  );
}

