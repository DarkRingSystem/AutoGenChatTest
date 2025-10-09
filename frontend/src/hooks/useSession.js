import { useState, useEffect } from 'react';

/**
 * 会话管理 Hook
 * 为每个模式维护独立的会话 ID
 */
export function useSession(mode) {
  const [conversationId, setConversationId] = useState(null);

  // 从 localStorage 恢复会话 ID
  useEffect(() => {
    const storageKey = `${mode}_conversation_id`;
    const savedId = localStorage.getItem(storageKey);
    if (savedId) {
      setConversationId(savedId);
      console.log(`📂 恢复 ${mode} 会话 ID:`, savedId);
    }
  }, [mode]);

  // 保存会话 ID 到 localStorage
  useEffect(() => {
    if (conversationId) {
      const storageKey = `${mode}_conversation_id`;
      localStorage.setItem(storageKey, conversationId);
      console.log(`💾 保存 ${mode} 会话 ID:`, conversationId);
    }
  }, [conversationId, mode]);

  // 清除会话
  const clearSession = () => {
    setConversationId(null);
    const storageKey = `${mode}_conversation_id`;
    localStorage.removeItem(storageKey);
    console.log(`🗑️ 清除 ${mode} 会话 ID`);
  };

  return { conversationId, setConversationId, clearSession };
}

