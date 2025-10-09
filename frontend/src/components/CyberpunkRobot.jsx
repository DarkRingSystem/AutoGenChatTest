import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './CyberpunkRobot.css';

const CyberpunkRobot = ({ onClick, title }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [neonColor, setNeonColor] = useState({ primary: '', secondary: '' });

  // 霓虹灯颜色方案
  const colorSchemes = [
    { primary: '#00ffff', secondary: '#ff00ff' }, // 青色 + 品红
    { primary: '#ff00ff', secondary: '#00ff00' }, // 品红 + 绿色
    { primary: '#ffff00', secondary: '#ff0080' }, // 黄色 + 粉红
    { primary: '#00ff00', secondary: '#0080ff' }, // 绿色 + 蓝色
    { primary: '#ff0080', secondary: '#00ffff' }, // 粉红 + 青色
    { primary: '#0080ff', secondary: '#ffff00' }, // 蓝色 + 黄色
  ];

  // 每次刷新随机选择颜色
  useEffect(() => {
    const randomScheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
    setNeonColor(randomScheme);
  }, []);

  return (
    <motion.div
      className="cyberpunk-robot"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      title={title}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
    >
      <svg
        width="120"
        height="120"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 定义滤镜 - 霓虹灯发光效果 */}
        <defs>
          <filter id="neon-glow-primary" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="neon-glow-secondary" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 机器人头部外框 */}
        <motion.rect
          x="30"
          y="25"
          width="60"
          height="50"
          rx="8"
          stroke={neonColor.primary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-primary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.5 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '10px' : '5px'} ${neonColor.primary})`
          }}
        />

        {/* 左眼 */}
        <motion.circle
          cx="45"
          cy="45"
          r="6"
          fill={neonColor.primary}
          filter="url(#neon-glow-primary)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.6,
            opacity: isHovered ? 1 : 0.5
          }}
          transition={{ duration: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.primary})`
          }}
        />

        {/* 右眼 */}
        <motion.circle
          cx="75"
          cy="45"
          r="6"
          fill={neonColor.primary}
          filter="url(#neon-glow-primary)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.6,
            opacity: isHovered ? 1 : 0.5
          }}
          transition={{ duration: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.primary})`
          }}
        />

        {/* 嘴巴 - 横线 */}
        <motion.line
          x1="40"
          y1="60"
          x2="80"
          y2="60"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.4, delay: 0.1 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 天线左 */}
        <motion.line
          x1="40"
          y1="25"
          x2="35"
          y2="15"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 天线左顶部圆点 */}
        <motion.circle
          cx="35"
          cy="15"
          r="3"
          fill={neonColor.secondary}
          filter="url(#neon-glow-secondary)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.5,
            opacity: isHovered ? 1 : 0.4
          }}
          transition={{ duration: 0.3, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 天线右 */}
        <motion.line
          x1="80"
          y1="25"
          x2="85"
          y2="15"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 天线右顶部圆点 */}
        <motion.circle
          cx="85"
          cy="15"
          r="3"
          fill={neonColor.secondary}
          filter="url(#neon-glow-secondary)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.5,
            opacity: isHovered ? 1 : 0.4
          }}
          transition={{ duration: 0.3, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 身体 */}
        <motion.rect
          x="35"
          y="75"
          width="50"
          height="30"
          rx="5"
          stroke={neonColor.primary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-primary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.primary})`
          }}
        />

        {/* 身体中心线 */}
        <motion.line
          x1="60"
          y1="80"
          x2="60"
          y2="100"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.4, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 左臂 */}
        <motion.line
          x1="35"
          y1="80"
          x2="20"
          y2="90"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 右臂 */}
        <motion.line
          x1="85"
          y1="80"
          x2="100"
          y2="90"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-secondary)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />
      </svg>
    </motion.div>
  );
};

export default CyberpunkRobot;

