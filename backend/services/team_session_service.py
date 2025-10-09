"""
团队会话管理服务
负责管理团队模式的对话历史和状态
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class TeamMessage:
    """团队消息"""
    role: str  # 'user' 或智能体名称
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TeamSession:
    """团队会话"""
    session_id: str
    messages: List[TeamMessage] = field(default_factory=list)
    waiting_for_feedback: bool = False
    last_agent: Optional[str] = None  # 最后一个回答的智能体
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TeamSessionService:
    """团队会话管理服务"""
    
    def __init__(self):
        """初始化会话管理服务"""
        self.sessions: Dict[str, TeamSession] = {}
    
    def create_session(self) -> str:
        """
        创建新会话
        
        返回:
            会话 ID
        """
        session_id = f"team_session_{uuid.uuid4().hex[:16]}"
        self.sessions[session_id] = TeamSession(session_id=session_id)
        print(f"✅ 创建团队会话: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[TeamSession]:
        """
        获取会话
        
        参数:
            session_id: 会话 ID
            
        返回:
            TeamSession 或 None
        """
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        添加消息到会话
        
        参数:
            session_id: 会话 ID
            role: 角色（user 或智能体名称）
            content: 消息内容
        """
        session = self.get_session(session_id)
        if session:
            message = TeamMessage(role=role, content=content)
            session.messages.append(message)
            session.updated_at = datetime.now()
            print(f"📝 添加消息到会话 {session_id}: {role}")
    
    def set_waiting_for_feedback(
        self, 
        session_id: str, 
        waiting: bool, 
        last_agent: Optional[str] = None
    ) -> None:
        """
        设置会话的反馈等待状态
        
        参数:
            session_id: 会话 ID
            waiting: 是否等待反馈
            last_agent: 最后一个回答的智能体
        """
        session = self.get_session(session_id)
        if session:
            session.waiting_for_feedback = waiting
            session.last_agent = last_agent
            session.updated_at = datetime.now()
            print(f"🔄 设置会话 {session_id} 反馈状态: waiting={waiting}, last_agent={last_agent}")
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        获取会话的对话历史
        
        参数:
            session_id: 会话 ID
            
        返回:
            消息列表
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        参数:
            session_id: 会话 ID
            
        返回:
            是否删除成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"🗑️ 删除团队会话: {session_id}")
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        清理过期会话
        
        参数:
            max_age_hours: 最大保留时间（小时）
            
        返回:
            清理的会话数量
        """
        from datetime import timedelta
        
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            age = now - session.updated_at
            if age > timedelta(hours=max_age_hours):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            print(f"🧹 清理了 {len(expired_sessions)} 个过期团队会话")
        
        return len(expired_sessions)


# 全局会话服务实例
_team_session_service: Optional[TeamSessionService] = None


def get_team_session_service() -> TeamSessionService:
    """
    获取团队会话服务实例（单例模式）
    
    返回:
        TeamSessionService 实例
    """
    global _team_session_service
    if _team_session_service is None:
        _team_session_service = TeamSessionService()
    return _team_session_service

