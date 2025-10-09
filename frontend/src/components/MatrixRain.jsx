/**
 * 黑客帝国风格的矩阵雨背景组件
 */
import React, { useEffect, useRef } from 'react';
import './MatrixRain.css';

const MatrixRain = ({ isDark = true }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // 设置 canvas 尺寸
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // 字符集 - 包含数字、字母、日文片假名、特殊符号
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()_+-=[]{}|;:,.<>?/~`';
    const charArray = chars.split('');

    // 字体大小
    const fontSize = 14;

    // 列数
    const columns = Math.floor(canvas.width / fontSize);

    // 同步下落状态
    let isSyncPhase = true; // 是否处于同步下落阶段
    let syncCompleted = false; // 同步下落是否完成

    // 每列的 Y 坐标（初始都从顶部开始，用于同步下落）
    const drops = Array(columns).fill(0);

    // 每列的速度（初始统一速度，同步下落后随机）
    const speeds = Array(columns).fill(0.6); // 同步下落时的统一速度（较慢，更优雅）

    // 每列的亮度
    const brightness = Array(columns).fill(0).map(() => Math.random() * 0.5 + 0.5);

    // 绘制函数
    const draw = () => {
      // 半透明背景，产生拖尾效果
      if (isDark) {
        // 深色模式：黑色背景
        ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      } else {
        // 明亮模式：白色背景
        ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
      }
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 绘制字符
      for (let i = 0; i < drops.length; i++) {
        // 随机选择字符
        const char = charArray[Math.floor(Math.random() * charArray.length)];

        // 计算位置
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // 计算透明度 - 越靠近顶部越亮
        const distanceFromTop = drops[i];
        const maxDistance = canvas.height / fontSize;
        const fadeRatio = Math.max(0, 1 - distanceFromTop / maxDistance);

        if (isDark) {
          // 深色模式：绿色字符
          // 顶部字符最亮（白色/浅绿）
          if (distanceFromTop < 3) {
            const whiteIntensity = brightness[i] * (1 - distanceFromTop / 3);
            ctx.fillStyle = `rgba(200, 255, 200, ${whiteIntensity})`;
          } else {
            // 其他字符绿色，渐变透明
            const alpha = brightness[i] * fadeRatio * 0.8;
            ctx.fillStyle = `rgba(0, 255, 70, ${alpha})`;
          }
        } else {
          // 明亮模式：黑色字符
          // 顶部字符最深（深黑）
          if (distanceFromTop < 3) {
            const blackIntensity = brightness[i] * (1 - distanceFromTop / 3);
            ctx.fillStyle = `rgba(50, 50, 50, ${blackIntensity})`;
          } else {
            // 其他字符黑色，渐变透明
            const alpha = brightness[i] * fadeRatio * 0.6;
            ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
          }
        }

        ctx.font = `${fontSize}px "Courier New", monospace`;
        ctx.fillText(char, x, y);

        // 更新 Y 坐标
        drops[i] += speeds[i];

        // 同步下落阶段的处理
        if (isSyncPhase) {
          // 检查是否所有列都已经下落到底部
          if (y > canvas.height) {
            // 当前列已到达底部，标记为完成
            if (!syncCompleted) {
              // 检查是否所有列都到达底部
              const allDropsCompleted = drops.every((drop, idx) => drop * fontSize > canvas.height);
              if (allDropsCompleted) {
                // 同步下落完成，切换到随机模式
                isSyncPhase = false;
                syncCompleted = true;

                // 重置所有列为随机位置和速度
                for (let j = 0; j < drops.length; j++) {
                  drops[j] = -Math.random() * 100;
                  speeds[j] = Math.random() * 0.8 + 0.5;
                  brightness[j] = Math.random() * 0.5 + 0.5;
                }
              }
            }
          }
        } else {
          // 随机下落阶段的处理
          if (y > canvas.height && Math.random() > 0.975) {
            drops[i] = -Math.random() * 20;
            brightness[i] = Math.random() * 0.5 + 0.5;
            speeds[i] = Math.random() * 0.8 + 0.5;
          }
        }
      }
    };

    // 动画循环
    const interval = setInterval(draw, 33); // ~30 FPS

    // 清理
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [isDark]); // 添加 isDark 依赖，主题切换时重新绘制

  return <canvas ref={canvasRef} className="matrix-rain-canvas" />;
};

export default MatrixRain;

