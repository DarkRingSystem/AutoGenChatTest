"""
普通对话路由
路径: /api/chat/normal/*
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models import ChatRequest, ChatResponse
from core.dependencies import get_session_service, get_stream_service
from api.utils import build_message_with_file_context, extract_final_message

router = APIRouter(prefix="/api/chat/normal", tags=["chat-normal"])


@router.post("/stream")
async def chat_normal_stream(request: ChatRequest):
    """
    普通对话 - 流式响应（支持会话隔离）
    
    参数:
        request: 包含消息的聊天请求
    
    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 构建包含文件上下文的消息
    message_with_context = build_message_with_file_context(request.message, request.file_ids)
    
    # 获取服务实例
    session_service = get_session_service()
    stream_service = get_stream_service()
    
    # 获取或创建会话（每个 conversation_id 对应一个独立的智能体）
    session = await session_service.get_or_create_session(request.conversation_id)
    
    # 增加消息计数
    session.increment_message_count()
    
    # 从会话的智能体获取事件流
    async def get_event_stream():
        async for event in session.agent.run_stream(task=message_with_context):
            yield event
    
    # 处理流式响应（使用原始用户消息计算 token）
    sse_stream = stream_service.process_stream(get_event_stream(), request.message)
    
    return StreamingResponse(
        sse_stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 在 nginx 中禁用缓冲
            "X-Session-ID": session.session_id,  # 返回会话 ID（兼容旧版）
            "X-Conversation-ID": session.session_id,  # 返回会话 ID（前端使用）
        }
    )


@router.post("/", response_model=ChatResponse)
async def chat_normal(request: ChatRequest):
    """
    普通对话 - 非流式响应（支持会话隔离）
    
    参数:
        request: 包含消息的聊天请求
    
    返回:
        ChatResponse 包含 AI 的完整回复
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 获取服务实例
    session_service = get_session_service()
    
    # 获取或创建会话
    session = await session_service.get_or_create_session(request.conversation_id)
    
    # 增加消息计数
    session.increment_message_count()
    
    try:
        # 运行会话的智能体
        result = await session.agent.run(task=request.message)
        
        # 提取最终响应
        final_message = extract_final_message(result)
        
        return ChatResponse(
            message=final_message,
            conversation_id=session.session_id,
            status="success"
        )
    
    except Exception as e:
        print(f"❌ 对话错误: {e}")
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.delete("/session/{conversation_id}")
async def delete_normal_session(conversation_id: str):
    """
    删除普通对话会话
    
    参数:
        conversation_id: 会话 ID
    
    返回:
        删除结果
    """
    session_service = get_session_service()
    success = await session_service.delete_session(conversation_id)
    
    if success:
        return {"message": "会话已删除", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@router.get("/session/{conversation_id}")
async def get_normal_session_info(conversation_id: str):
    """
    获取普通对话会话信息
    
    参数:
        conversation_id: 会话 ID
    
    返回:
        会话信息
    """
    session_service = get_session_service()
    session_info = await session_service.get_session_info(conversation_id)
    
    if session_info:
        return session_info
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@router.get("/sessions")
async def list_normal_sessions():
    """
    列出所有普通对话会话
    
    返回:
        会话列表
    """
    session_service = get_session_service()
    sessions = await session_service.list_sessions()
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

