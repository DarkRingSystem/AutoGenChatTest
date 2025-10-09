import React, { useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import ChatTestCaseContainer from '../components/chat/ChatTestCaseContainer';

export default function ChatTestCasePage() {
  const { isDark } = useOutletContext();

  useEffect(() => {
    document.title = 'AutoGen Chat - 测试用例生成';
  }, []);

  return (
    <div className="chat-testcase-page" style={{ height: '100%' }}>
      <ChatTestCaseContainer isDark={isDark} />
    </div>
  );
}

