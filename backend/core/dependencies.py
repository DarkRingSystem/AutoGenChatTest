"""
依赖注入模块
提供全局服务实例
"""
from typing import Optional
from services import AIService, StreamService, SessionService
from config import settings


# 全局服务实例
_ai_service: Optional[AIService] = None
_stream_service: Optional[StreamService] = None
_session_service: Optional[SessionService] = None


def get_ai_service() -> AIService:
    """
    获取 AI 服务实例（单例模式）

    返回:
        AIService 实例
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(settings)
    return _ai_service


def get_stream_service() -> StreamService:
    """
    获取流式处理服务实例（单例模式）

    返回:
        StreamService 实例
    """
    global _stream_service
    if _stream_service is None:
        _stream_service = StreamService()
    return _stream_service


def get_session_service() -> SessionService:
    """
    获取会话管理服务实例（单例模式）

    返回:
        SessionService 实例
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService(settings)
    return _session_service


async def initialize_services() -> None:
    """初始化所有服务"""
    # 初始化会话服务（新架构）
    session_service = get_session_service()
    await session_service.initialize()

    # 保留旧的 AI 服务以兼容（可选）
    # ai_service = get_ai_service()
    # await ai_service.initialize()


async def cleanup_services() -> None:
    """清理所有服务"""
    # 清理会话服务
    session_service = get_session_service()
    await session_service.cleanup()

    # 清理旧的 AI 服务（如果初始化了）
    # ai_service = get_ai_service()
    # await ai_service.cleanup()

