/**
 * 普通对话容器组件
 * 临时方案：导入原 App 组件并固定为 normal 模式
 */
import React from 'react';
import LegacyApp from '../LegacyApp';

export default function ChatNormalContainer({ isDark }) {
  return <LegacyApp initialMode="normal" isDark={isDark} />;
}

