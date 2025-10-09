"""
测试用例生成路由
路径: /api/chat/testcase/*
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Dict
import re

from models import ChatRequest
from api.utils import build_message_with_file_context

router = APIRouter(prefix="/api/chat/testcase", tags=["chat-testcase"])

# 团队服务缓存（用于保持团队状态）
_team_service_cache: Dict[str, any] = {}


def _cache_team_service(conversation_id: str, team_service: any) -> None:
    """缓存团队服务实例"""
    _team_service_cache[conversation_id] = team_service
    print(f"💾 缓存团队实例: {conversation_id}")


def _get_cached_team_service(conversation_id: str) -> Optional[any]:
    """获取缓存的团队服务实例"""
    return _team_service_cache.get(conversation_id)


def _remove_cached_team_service(conversation_id: str) -> None:
    """移除缓存的团队服务实例"""
    if conversation_id in _team_service_cache:
        del _team_service_cache[conversation_id]
        print(f"🗑️ 移除团队实例缓存: {conversation_id}")


def _parse_target_agent(message: str) -> Optional[str]:
    """
    解析消息中的目标智能体
    
    支持格式：
    - @TestCase_Generator, @TestCase_Reviewer, @TestCase_Optimizer
    - @all (重新运行 Generator → Reviewer 流程)
    
    参数:
        message: 用户消息
    
    返回:
        智能体名称、"all" 或 None
    """
    # 先匹配 @all（不区分大小写）
    if re.search(r'@all\b', message, re.IGNORECASE):
        print(f"🔄 检测到 @all，将重新运行 Generator → Reviewer 流程")
        return "all"
    
    # 匹配 @智能体名称
    match = re.search(r'@(TestCase_\w+)', message)
    if match:
        agent_name = match.group(1)
        print(f"🎯 检测到目标智能体: {agent_name}")
        return agent_name
    
    return None


@router.post("/stream")
async def chat_testcase_stream(request: ChatRequest):
    """
    测试用例生成 - 流式响应（团队协作模式）
    
    参数:
        request: 包含消息的聊天请求
    
    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 生成或使用现有的 conversation_id
    conversation_id = request.conversation_id or f"testcase_{__import__('uuid').uuid4().hex[:16]}"
    
    # 检查是否为反馈消息
    is_feedback = request.is_feedback
    target_agent = request.target_agent or _parse_target_agent(request.message)
    
    # 获取或创建团队服务
    team_service = _get_cached_team_service(conversation_id)
    
    if team_service is None or not is_feedback:
        # 创建新的团队服务
        print(f"🆕 创建新对话 {conversation_id}")
        
        # 构建包含文件上下文的消息
        message_with_context = build_message_with_file_context(request.message, request.file_ids)
        
        # 创建团队流服务
        from services.team_stream_service import TeamStreamService
        team_stream_service = TeamStreamService()
        
        # 初始化团队（根据目标智能体决定模式）
        await team_stream_service.initialize(specific_agent=target_agent)
        
        # 缓存团队服务
        _cache_team_service(conversation_id, team_stream_service)
        
        # 获取流式响应
        async def event_generator():
            async for event in team_stream_service.run_stream(message_with_context):
                yield event
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "X-Conversation-ID": conversation_id,
            }
        )
    
    else:
        # 处理反馈消息
        print(f"💬 处理反馈消息 (会话: {conversation_id}, 目标: {target_agent})")
        
        feedback_message = request.message
        
        # 获取流式响应
        async def event_generator():
            async for event in team_service.handle_feedback_stream(
                feedback_message,
                target_agent=target_agent
            ):
                yield event
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "X-Conversation-ID": conversation_id,
            }
        )


@router.delete("/session/{conversation_id}")
async def delete_testcase_session(conversation_id: str):
    """
    删除测试用例会话
    
    参数:
        conversation_id: 会话 ID
    
    返回:
        删除结果
    """
    team_service = _get_cached_team_service(conversation_id)
    
    if team_service:
        # 清理团队服务
        await team_service.cleanup()
        _remove_cached_team_service(conversation_id)
        
        return {"message": "会话已删除", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@router.get("/session/{conversation_id}")
async def get_testcase_session_info(conversation_id: str):
    """
    获取测试用例会话信息
    
    参数:
        conversation_id: 会话 ID
    
    返回:
        会话信息
    """
    team_service = _get_cached_team_service(conversation_id)
    
    if team_service:
        return {
            "conversation_id": conversation_id,
            "status": "active",
            "team_initialized": team_service.is_initialized()
        }
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@router.get("/sessions")
async def list_testcase_sessions():
    """
    列出所有测试用例会话
    
    返回:
        会话列表
    """
    sessions = [
        {
            "conversation_id": conv_id,
            "status": "active"
        }
        for conv_id in _team_service_cache.keys()
    ]
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.post("/clear-all")
async def clear_all_testcase_sessions():
    """
    清除所有测试用例会话
    
    返回:
        清除结果
    """
    count = len(_team_service_cache)
    
    # 清理所有团队服务
    for team_service in _team_service_cache.values():
        await team_service.cleanup()
    
    _team_service_cache.clear()
    
    return {
        "message": f"已清除 {count} 个会话",
        "cleared_count": count
    }

