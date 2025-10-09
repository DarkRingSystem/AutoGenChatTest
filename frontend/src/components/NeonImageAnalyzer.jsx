import React from 'react';
import { motion } from 'framer-motion';
import './NeonIcon.css';

const NeonImageAnalyzer = () => {
  return (
    <motion.div
      className="neon-icon"
      animate={{
        filter: [
          'drop-shadow(0 0 10px rgba(250, 112, 154, 0.8)) drop-shadow(0 0 20px rgba(254, 225, 64, 0.6))',
          'drop-shadow(0 0 20px rgba(250, 112, 154, 1)) drop-shadow(0 0 30px rgba(254, 225, 64, 0.8))',
          'drop-shadow(0 0 10px rgba(250, 112, 154, 0.8)) drop-shadow(0 0 20px rgba(254, 225, 64, 0.6))',
        ],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      <svg
        width="48"
        height="48"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 外框 - 图片框架 */}
        <motion.rect
          x="8"
          y="12"
          width="48"
          height="40"
          rx="4"
          stroke="url(#gradient-image-analyzer)"
          strokeWidth="2.5"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeInOut' }}
        />

        {/* 山峰图标 - 代表图片 */}
        <motion.path
          d="M 14 42 L 22 28 L 30 36 L 42 20 L 50 32 L 50 42 Z"
          fill="url(#gradient-mountain)"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 0.6, y: 0 }}
          transition={{ delay: 0.5, duration: 1 }}
        />

        {/* 太阳/月亮 */}
        <motion.circle
          cx="44"
          cy="22"
          r="4"
          fill="url(#gradient-sun)"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.8, duration: 0.5, type: 'spring' }}
        />

        {/* 扫描线 - 代表分析 */}
        <motion.line
          x1="12"
          y1="30"
          x2="52"
          y2="30"
          stroke="url(#gradient-scan)"
          strokeWidth="2"
          strokeDasharray="4 4"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{
            pathLength: [0, 1, 0],
            opacity: [0, 1, 0],
            y: [0, 20, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* AI 眼睛 - 左边 */}
        <motion.circle
          cx="20"
          cy="18"
          r="2"
          fill="url(#gradient-eye)"
          initial={{ scale: 0 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{
            delay: 1,
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* AI 眼睛 - 右边 */}
        <motion.circle
          cx="28"
          cy="18"
          r="2"
          fill="url(#gradient-eye)"
          initial={{ scale: 0 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{
            delay: 1.1,
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* 渐变定义 */}
        <defs>
          {/* 主框架渐变 */}
          <linearGradient id="gradient-image-analyzer" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fa709a" />
            <stop offset="50%" stopColor="#ff8c69" />
            <stop offset="100%" stopColor="#fee140" />
          </linearGradient>

          {/* 山峰渐变 */}
          <linearGradient id="gradient-mountain" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#fa709a" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#fee140" stopOpacity="0.4" />
          </linearGradient>

          {/* 太阳渐变 */}
          <radialGradient id="gradient-sun">
            <stop offset="0%" stopColor="#fee140" />
            <stop offset="100%" stopColor="#fa709a" />
          </radialGradient>

          {/* 扫描线渐变 */}
          <linearGradient id="gradient-scan" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#fa709a" stopOpacity="0" />
            <stop offset="50%" stopColor="#fee140" stopOpacity="1" />
            <stop offset="100%" stopColor="#fa709a" stopOpacity="0" />
          </linearGradient>

          {/* 眼睛渐变 */}
          <radialGradient id="gradient-eye">
            <stop offset="0%" stopColor="#fee140" />
            <stop offset="100%" stopColor="#fa709a" />
          </radialGradient>
        </defs>
      </svg>
    </motion.div>
  );
};

export default NeonImageAnalyzer;

