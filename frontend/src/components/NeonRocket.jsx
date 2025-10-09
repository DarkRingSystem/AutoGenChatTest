import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './NeonIcon.css';

const NeonRocket = () => {
  const [isHovered, setIsHovered] = useState(false);

  // 紫色霓虹灯配色（与卡片渐变一致）
  const neonColor = {
    primary: '#667eea',
    secondary: '#764ba2',
    glow: '#a78bfa'
  };

  return (
    <motion.div
      className="neon-icon"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
    >
      <svg
        width="56"
        height="56"
        viewBox="0 0 56 56"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 定义滤镜 */}
        <defs>
          <filter id="neon-glow-rocket" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 火箭主体 */}
        <motion.path
          d="M 28 8 L 32 18 L 32 38 L 28 42 L 24 38 L 24 18 Z"
          stroke={neonColor.primary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.6 
          }}
          transition={{ duration: 0.5 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '12px' : '6px'} ${neonColor.primary})`
          }}
        />

        {/* 火箭头部 */}
        <motion.path
          d="M 28 8 L 32 18 L 28 14 L 24 18 Z"
          fill={neonColor.primary}
          filter="url(#neon-glow-rocket)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.7,
            opacity: isHovered ? 1 : 0.6
          }}
          transition={{ duration: 0.3 }}
          style={{
            transformOrigin: '28px 14px',
            filter: `drop-shadow(0 0 ${isHovered ? '10px' : '5px'} ${neonColor.primary})`
          }}
        />

        {/* 窗口 */}
        <motion.circle
          cx="28"
          cy="24"
          r="3"
          stroke={neonColor.secondary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-rocket)"
          initial={{ scale: 0 }}
          animate={{ 
            scale: isHovered ? 1 : 0.6,
            opacity: isHovered ? 1 : 0.5
          }}
          transition={{ duration: 0.3, delay: 0.1 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.secondary})`
          }}
        />

        {/* 左翼 */}
        <motion.path
          d="M 24 32 L 18 38 L 18 42 L 24 38 Z"
          stroke={neonColor.secondary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.4, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.secondary})`
          }}
        />

        {/* 右翼 */}
        <motion.path
          d="M 32 32 L 38 38 L 38 42 L 32 38 Z"
          stroke={neonColor.secondary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.4, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.secondary})`
          }}
        />

        {/* 火焰 - 中心 */}
        <motion.path
          d="M 26 42 L 28 48 L 30 42"
          stroke={neonColor.glow}
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.5 
          }}
          transition={{ duration: 0.3, delay: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '10px' : '5px'} ${neonColor.glow})`
          }}
        />

        {/* 火焰 - 左 */}
        <motion.line
          x1="24"
          y1="42"
          x2="22"
          y2="46"
          stroke={neonColor.glow}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.35 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.glow})`
          }}
        />

        {/* 火焰 - 右 */}
        <motion.line
          x1="32"
          y1="42"
          x2="34"
          y2="46"
          stroke={neonColor.glow}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.35 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '8px' : '4px'} ${neonColor.glow})`
          }}
        />

        {/* 装饰线 - 上 */}
        <motion.line
          x1="26"
          y1="20"
          x2="30"
          y2="20"
          stroke={neonColor.secondary}
          strokeWidth="1.5"
          strokeLinecap="round"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.4 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />

        {/* 装饰线 - 下 */}
        <motion.line
          x1="26"
          y1="30"
          x2="30"
          y2="30"
          stroke={neonColor.secondary}
          strokeWidth="1.5"
          strokeLinecap="round"
          filter="url(#neon-glow-rocket)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.4 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.secondary})`
          }}
        />
      </svg>
    </motion.div>
  );
};

export default NeonRocket;

