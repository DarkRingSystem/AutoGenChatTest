import React from 'react';
import { motion } from 'framer-motion';
import CyberpunkRobot from './CyberpunkRobot';
import NeonRocket from './NeonRocket';
import NeonTestTube from './NeonTestTube';
import NeonImageAnalyzer from './NeonImageAnalyzer';
import './ModeSelector.css';

const ModeSelector = ({ onSelectMode, isDark, onToggleTheme }) => {
  const modes = [
    {
      id: 'normal',
      title: '后端普通模式',
      description: '传统的 AI 助手对话模式，直接与模型进行交互',
      icon: <NeonRocket />,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      features: [
        '💬 直接模型对话',
        '🧠 快速响应',
        '📚 基础问答',
        '✨ 简单交互'
      ]
    },
    {
      id: 'orchestration',
      title: '后端编排模式',
      description: '使用 AutoGen 智能体编排系统，提供更智能的对话体验',
      icon: <NeonRocket />,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      features: [
        '🤖 智能体编排',
        '🔄 流程管理',
        '📊 会话跟踪',
        '⚡ 优化响应'
      ]
    },
    {
      id: 'testcase',
      title: '测试用例智能体模式',
      description: '由 3 个专业智能体协作，为您生成高质量的测试用例',
      icon: <NeonTestTube />,
      gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      features: [
        '🎯 测试用例生成',
        '🔍 专业评审',
        '✨ 智能优化',
        '👥 团队协作'
      ]
    },
    {
      id: 'image-analyzer',
      title: 'UI 图片分析模式',
      description: '上传 UI 截图，由 3 个专业智能体协作分析并生成测试场景',
      icon: <NeonImageAnalyzer />,
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      features: [
        '🖼️ UI 元素分析',
        '🔄 交互流程分析',
        '📋 测试场景生成',
        '👥 智能体协作'
      ]
    }
  ];

  return (
    <div className={`mode-selector ${isDark ? 'dark' : 'light'}`}>
      <motion.div
        className="mode-selector-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="mode-selector-header">
          <div className="logo">
            <CyberpunkRobot
              onClick={onToggleTheme}
              title={isDark ? '切换到明亮模式' : '切换到深色模式'}
            />
          </div>
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            欢迎使用 AI 助手
          </motion.h1>
          <motion.p
            className="subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            请选择您需要的服务模式
          </motion.p>
        </div>

        <div className="mode-cards">
          {modes.map((mode, index) => (
            <motion.div
              key={mode.id}
              className={`mode-card mode-card-${mode.id}`}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.03, y: -8, transition: { duration: 0.2 } }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelectMode(mode.id)}
            >
              <div className="mode-card-gradient" style={{ background: mode.gradient }} />
              <div className="mode-card-content">
                <div className="mode-icon">
                  {mode.icon}
                </div>
                <h2>{mode.title}</h2>
                <p className="description">{mode.description}</p>
                <div className="features">
                  {mode.features.map((feature, idx) => (
                    <motion.div
                      key={idx}
                      className="feature-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 + idx * 0.05 }}
                    >
                      {feature}
                    </motion.div>
                  ))}
                </div>
                <motion.button
                  className="select-button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  选择此模式
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="footer-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          💡 提示：选择模式后可随时返回重新选择
        </motion.div>
      </motion.div>
    </div>
  );
};

export default ModeSelector;

