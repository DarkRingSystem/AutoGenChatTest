/**
 * 测试用例生成容器组件
 * 临时方案：导入原 App 组件并固定为 testcase 模式
 */
import React from 'react';
import LegacyApp from '../LegacyApp';

export default function ChatTestCaseContainer({ isDark, registerClearSession }) {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <LegacyApp
        initialMode="testcase"
        isDark={isDark}
        registerClearSession={registerClearSession}
        hideHeader={true}
      />
    </div>
  );
}

