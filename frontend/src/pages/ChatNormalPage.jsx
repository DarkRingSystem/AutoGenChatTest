import React, { useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import ChatNormalContainer from '../components/chat/ChatNormalContainer';

export default function ChatNormalPage() {
  const { isDark, registerClearSession } = useOutletContext();

  useEffect(() => {
    document.title = 'AutoGen Chat - 普通对话';
  }, []);

  return (
    <div className="chat-normal-page" style={{ height: '100%' }}>
      <ChatNormalContainer
        isDark={isDark}
        registerClearSession={registerClearSession}
      />
    </div>
  );
}

