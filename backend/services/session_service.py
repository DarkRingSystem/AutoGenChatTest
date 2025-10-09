"""
会话管理服务模块
负责管理多个独立的 AI 会话，实现会话隔离
"""
import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._model_info import ModelInfo

from config import Settings


class Session:
    """会话类，表示一个独立的 AI 对话会话"""
    
    def __init__(
        self,
        session_id: str,
        agent: AssistantAgent,
        created_at: datetime
    ):
        """
        初始化会话
        
        参数:
            session_id: 会话 ID
            agent: AI 智能体实例
            created_at: 创建时间
        """
        self.session_id = session_id
        self.agent = agent
        self.created_at = created_at
        self.last_accessed = created_at
        self.message_count = 0
    
    def update_access_time(self) -> None:
        """更新最后访问时间"""
        self.last_accessed = datetime.now()
    
    def increment_message_count(self) -> None:
        """增加消息计数"""
        self.message_count += 1
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """
        检查会话是否过期
        
        参数:
            timeout_minutes: 超时时间（分钟）
            
        返回:
            True 如果已过期，否则 False
        """
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_accessed > timeout


class SessionService:
    """会话管理服务类，管理多个独立的 AI 会话"""
    
    def __init__(self, settings: Settings):
        """
        初始化会话管理服务
        
        参数:
            settings: 应用配置
        """
        self.settings = settings
        self.sessions: Dict[str, Session] = {}
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        self.model_info: Optional[ModelInfo] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """初始化会话管理服务"""
        # 创建共享的模型客户端
        self.model_info = self._create_model_info()
        self.model_client = OpenAIChatCompletionClient(
            model=self.settings.model_name,
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            model_info=self.model_info,
        )
        
        # 启动定期清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        
        print(f"✅ 会话管理服务初始化成功！")
    
    async def cleanup(self) -> None:
        """清理资源"""
        # 取消清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 清理所有会话
        async with self._lock:
            self.sessions.clear()
        
        # 关闭模型客户端
        if self.model_client:
            await self.model_client.close()
        
        print("🧹 会话管理服务资源已清理")
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """
        获取或创建会话
        
        参数:
            session_id: 会话 ID，如果为 None 则创建新会话
            
        返回:
            Session 实例
        """
        async with self._lock:
            # 如果没有提供 session_id，创建新会话
            if session_id is None:
                session_id = self._generate_session_id()
            
            # 如果会话已存在，返回现有会话
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.update_access_time()
                return session
            
            # 创建新会话
            session = await self._create_new_session(session_id)
            self.sessions[session_id] = session
            
            print(f"📝 创建新会话: {session_id} (总会话数: {len(self.sessions)})")
            
            return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话
        
        参数:
            session_id: 会话 ID
            
        返回:
            Session 实例或 None
        """
        async with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session.update_access_time()
            return session
    
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        参数:
            session_id: 会话 ID
            
        返回:
            True 如果删除成功，否则 False
        """
        async with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                print(f"🗑️ 删除会话: {session_id} (剩余会话数: {len(self.sessions)})")
                return True
            return False
    
    async def get_session_count(self) -> int:
        """
        获取当前会话数量
        
        返回:
            会话数量
        """
        async with self._lock:
            return len(self.sessions)
    
    async def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        获取会话信息
        
        参数:
            session_id: 会话 ID
            
        返回:
            会话信息字典或 None
        """
        session = await self.get_session(session_id)
        if session:
            return {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "message_count": session.message_count,
            }
        return None
    
    async def list_sessions(self) -> list[dict]:
        """
        列出所有会话
        
        返回:
            会话信息列表
        """
        async with self._lock:
            return [
                {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_accessed": session.last_accessed.isoformat(),
                    "message_count": session.message_count,
                }
                for session in self.sessions.values()
            ]
    
    async def _create_new_session(self, session_id: str) -> Session:
        """
        创建新会话
        
        参数:
            session_id: 会话 ID
            
        返回:
            Session 实例
        """
        # 为每个会话创建独立的智能体
        agent = AssistantAgent(
            name=f"assistant_{session_id[:8]}",  # 使用会话 ID 前缀作为名称
            model_client=self.model_client,  # 共享模型客户端
            system_message=self.settings.system_message,
            model_client_stream=self.settings.enable_streaming,
        )
        
        return Session(
            session_id=session_id,
            agent=agent,
            created_at=datetime.now()
        )
    
    def _generate_session_id(self) -> str:
        """
        生成唯一的会话 ID
        
        返回:
            会话 ID
        """
        return f"session_{uuid.uuid4().hex}"
    
    def _create_model_info(self) -> ModelInfo:
        """
        创建模型信息

        返回:
            ModelInfo 实例
        """
        return ModelInfo(
            vision=False,
            function_calling=False,
            json_output=True,
            structured_output=False,  # 添加 structured_output 字段
            family=self._get_model_family(),
        )
    
    def _get_model_family(self) -> str:
        """
        获取模型家族名称
        
        返回:
            模型家族名称
        """
        model_name_lower = self.settings.model_name.lower()
        
        if "deepseek" in model_name_lower:
            return "deepseek"
        elif "gpt" in model_name_lower:
            return "openai"
        elif "claude" in model_name_lower:
            return "anthropic"
        else:
            return "unknown"
    
    async def _cleanup_expired_sessions(self) -> None:
        """定期清理过期的会话"""
        while True:
            try:
                await asyncio.sleep(300)  # 每 5 分钟检查一次
                
                async with self._lock:
                    expired_sessions = [
                        session_id
                        for session_id, session in self.sessions.items()
                        if session.is_expired(timeout_minutes=30)
                    ]
                    
                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                    
                    if expired_sessions:
                        print(f"🧹 清理了 {len(expired_sessions)} 个过期会话 (剩余: {len(self.sessions)})")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ 清理会话时出错: {e}")

