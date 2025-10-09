import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './NeonIcon.css';

const NeonTestTube = () => {
  const [isHovered, setIsHovered] = useState(false);

  // 绿色霓虹灯配色（与卡片渐变一致）
  const neonColor = {
    primary: '#11998e',
    secondary: '#38ef7d',
    glow: '#4ade80'
  };

  return (
    <motion.div
      className="neon-icon"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ scale: 0, rotate: 180 }}
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
          <filter id="neon-glow-tube" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 试管主体 */}
        <motion.path
          d="M 22 12 L 22 38 Q 22 44 28 44 Q 34 44 34 38 L 34 12"
          stroke={neonColor.primary}
          strokeWidth="2"
          fill="none"
          filter="url(#neon-glow-tube)"
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

        {/* 试管口 */}
        <motion.line
          x1="20"
          y1="12"
          x2="36"
          y2="12"
          stroke={neonColor.primary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.6 
          }}
          transition={{ duration: 0.4, delay: 0.1 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '10px' : '5px'} ${neonColor.primary})`
          }}
        />

        {/* 液体表面 */}
        <motion.line
          x1="22"
          y1="28"
          x2="34"
          y2="28"
          stroke={neonColor.secondary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.4, 
            opacity: isHovered ? 1 : 0.6 
          }}
          transition={{ duration: 0.4, delay: 0.2 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '10px' : '5px'} ${neonColor.secondary})`
          }}
        />

        {/* 液体填充区域 */}
        <motion.path
          d="M 22 28 L 22 38 Q 22 44 28 44 Q 34 44 34 38 L 34 28 Z"
          fill={neonColor.secondary}
          opacity={isHovered ? 0.3 : 0.15}
          filter="url(#neon-glow-tube)"
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: isHovered ? 0.3 : 0.15
          }}
          transition={{ duration: 0.4, delay: 0.2 }}
        />

        {/* 刻度线 - 上 */}
        <motion.line
          x1="22"
          y1="18"
          x2="26"
          y2="18"
          stroke={neonColor.primary}
          strokeWidth="1.5"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.3 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.primary})`
          }}
        />

        {/* 刻度线 - 中上 */}
        <motion.line
          x1="22"
          y1="23"
          x2="26"
          y2="23"
          stroke={neonColor.primary}
          strokeWidth="1.5"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.35 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.primary})`
          }}
        />

        {/* 刻度线 - 中下 */}
        <motion.line
          x1="22"
          y1="33"
          x2="26"
          y2="33"
          stroke={neonColor.secondary}
          strokeWidth="1.5"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
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

        {/* 气泡 1 */}
        <motion.circle
          cx="26"
          cy="35"
          r="1.5"
          fill={neonColor.glow}
          filter="url(#neon-glow-tube)"
          initial={{ scale: 0, y: 0 }}
          animate={{ 
            scale: isHovered ? [0, 1, 1, 0] : 0,
            y: isHovered ? [0, 0, -8, -8] : 0,
            opacity: isHovered ? [0, 1, 1, 0] : 0
          }}
          transition={{ 
            duration: 2, 
            repeat: isHovered ? Infinity : 0,
            delay: 0.5 
          }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.glow})`
          }}
        />

        {/* 气泡 2 */}
        <motion.circle
          cx="30"
          cy="38"
          r="1.5"
          fill={neonColor.glow}
          filter="url(#neon-glow-tube)"
          initial={{ scale: 0, y: 0 }}
          animate={{ 
            scale: isHovered ? [0, 1, 1, 0] : 0,
            y: isHovered ? [0, 0, -10, -10] : 0,
            opacity: isHovered ? [0, 1, 1, 0] : 0
          }}
          transition={{ 
            duration: 2.5, 
            repeat: isHovered ? Infinity : 0,
            delay: 0.8 
          }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.glow})`
          }}
        />

        {/* 气泡 3 */}
        <motion.circle
          cx="28"
          cy="40"
          r="1"
          fill={neonColor.glow}
          filter="url(#neon-glow-tube)"
          initial={{ scale: 0, y: 0 }}
          animate={{ 
            scale: isHovered ? [0, 1, 1, 0] : 0,
            y: isHovered ? [0, 0, -12, -12] : 0,
            opacity: isHovered ? [0, 1, 1, 0] : 0
          }}
          transition={{ 
            duration: 2.2, 
            repeat: isHovered ? Infinity : 0,
            delay: 1.1 
          }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.glow})`
          }}
        />

        {/* 试管架 - 左 */}
        <motion.line
          x1="18"
          y1="20"
          x2="18"
          y2="26"
          stroke={neonColor.primary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.45 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.primary})`
          }}
        />

        {/* 试管架 - 右 */}
        <motion.line
          x1="38"
          y1="20"
          x2="38"
          y2="26"
          stroke={neonColor.primary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.3, delay: 0.45 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.primary})`
          }}
        />

        {/* 试管架 - 横杆 */}
        <motion.line
          x1="18"
          y1="23"
          x2="38"
          y2="23"
          stroke={neonColor.primary}
          strokeWidth="2"
          strokeLinecap="round"
          filter="url(#neon-glow-tube)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: isHovered ? 1 : 0.3, 
            opacity: isHovered ? 1 : 0.4 
          }}
          transition={{ duration: 0.4, delay: 0.5 }}
          style={{
            filter: `drop-shadow(0 0 ${isHovered ? '6px' : '3px'} ${neonColor.primary})`
          }}
        />
      </svg>
    </motion.div>
  );
};

export default NeonTestTube;

