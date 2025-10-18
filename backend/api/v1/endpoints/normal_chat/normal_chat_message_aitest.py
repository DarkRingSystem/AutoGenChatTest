"""
基于 AutoGen 消息机制的普通聊天 API 端点
使用真正的消息发布-订阅模式进行智能体通信
"""

import logging
from typing import Dict, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from api.v1.endpoints.normal_chat.chat_model import NormalChatRequest
from core.message_orchestration_service_aitest import MessageOrchestrationServiceAitest
from services.normal_chat_stream_service_aitest import NormalChatStreamServiceAitest
from services.session_service import SessionService

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建路由器
normal_chat_message_router = APIRouter()

# 创建流式服务实例
stream_service = NormalChatStreamServiceAitest()


@normal_chat_message_router.get("/message_health")
async def message_health_check():
    """基于消息机制的健康检查端点"""
    logger.info("🏥 [API流程-步骤1] 收到消息机制健康检查请求")
    
    try:
        health_data = {
            "status": "healthy",
            "service": "normal_chat_message_aitest",
            "message_mechanism": "autogen_publish_subscribe",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        logger.info("✅ [API流程-步骤2] 消息机制健康检查通过")
        return health_data
        
    except Exception as e:
        logger.error(f"❌ [API流程-错误] 消息机制健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@normal_chat_message_router.post("/stream_aitest")
async def stream_message_aitest(
    request: NormalChatRequest,
    http_request: Request
):
    """
    基于 AutoGen 消息机制的流式聊天端点
    
    使用真正的消息发布-订阅模式：
    1. 编排服务发布消息到 topic_type="normal_chat"
    2. 智能体订阅并处理消息
    3. 智能体发送响应回编排服务
    4. 编排服务将响应流式传输给前端
    """
    
    # 生成会话ID
    session_id = request.session_id or f"normal_chat_{uuid.uuid4()}"
    
    logger.info(f"🔄 [API流程-步骤1] 收到基于消息机制的流式聊天请求 - 会话ID: {session_id}")
    logger.info(f"📝 [API流程-步骤2] 用户消息: {request.message}")
    logger.info(f"🎯 [API流程-步骤3] 目标智能体: {request.target_agent}")
    
    try:
        # 验证请求
        if not request.message or not request.message.strip():
            logger.warning(f"⚠️ [API流程-验证] 消息内容为空 - 会话ID: {session_id}")
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 准备会话数据
        session_data = {
            "session_id": session_id,
            "message": request.message.strip(),
            "target_agent": request.target_agent or "normal_chat",
            "file_ids": request.file_ids or [],
            "is_feedback": request.is_feedback or False,
            "user_id": getattr(request, 'user_id', None),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📋 [API流程-步骤4] 会话数据准备完成 - 会话ID: {session_id}")
        
        # 创建消息编排服务
        orchestrator = MessageOrchestrationServiceAitest(session_data)
        
        logger.info(f"🏗️ [API流程-步骤5] 消息编排服务已创建 - 会话ID: {session_id}")
        
        # 初始化编排服务
        await orchestrator.initialize()
        
        logger.info(f"✅ [API流程-步骤6] 消息编排服务初始化完成 - 会话ID: {session_id}")
        
        # 创建流式响应
        async def generate_stream():
            """生成 SSE 流式响应"""
            try:
                logger.info(f"🔄 [流式响应-开始] 开始生成流式响应 - 会话ID: {session_id}")
                
                # 获取智能体事件流
                event_stream = orchestrator.run_stream(task=request.message.strip())
                
                # 处理事件流并转换为 SSE 格式
                async for sse_message in stream_service.process_stream(
                    event_stream,
                    request.message.strip(),
                    session_id
                ):
                    yield sse_message
                
                logger.info(f"✅ [流式响应-完成] 流式响应生成完成 - 会话ID: {session_id}")
                
            except Exception as e:
                logger.error(f"❌ [流式响应-错误] 流式响应生成失败 - 会话ID: {session_id}, 错误: {str(e)}")
                
                # 发送错误消息
                error_message = f"data: {{\"type\": \"error\", \"content\": \"处理请求时发生错误: {str(e)}\", \"session_id\": \"{session_id}\"}}\n\n"
                yield error_message
                
            finally:
                # 清理资源
                try:
                    await orchestrator.cleanup()
                    logger.info(f"🧹 [流式响应-清理] 资源清理完成 - 会话ID: {session_id}")
                except Exception as cleanup_error:
                    logger.error(f"❌ [流式响应-清理] 资源清理失败 - 会话ID: {session_id}, 错误: {str(cleanup_error)}")
        
        # 返回流式响应
        response = StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "X-Session-ID": session_id
            }
        )
        
        logger.info(f"📡 [API流程-步骤7] 流式响应已创建 - 会话ID: {session_id}")
        
        return response
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        logger.error(f"❌ [API流程-错误] 处理请求失败 - 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@normal_chat_message_router.post("/send_message_aitest")
async def send_message_aitest(
    request: NormalChatRequest,
    http_request: Request
):
    """
    基于 AutoGen 消息机制的非流式聊天端点
    
    用于测试消息发布-订阅机制
    """
    
    # 生成会话ID
    session_id = request.session_id or f"normal_chat_{uuid.uuid4()}"
    
    logger.info(f"📤 [API流程-发送] 收到基于消息机制的发送消息请求 - 会话ID: {session_id}")
    
    try:
        # 验证请求
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 准备会话数据
        session_data = {
            "session_id": session_id,
            "message": request.message.strip(),
            "target_agent": request.target_agent or "normal_chat",
            "timestamp": datetime.now().isoformat()
        }
        
        # 创建消息编排服务
        orchestrator = MessageOrchestrationServiceAitest(session_data)
        
        # 初始化编排服务
        await orchestrator.initialize()
        
        # 发送消息到智能体
        await orchestrator.send_message_to_agent(request.message.strip())
        
        # 等待一段时间让智能体处理
        import asyncio
        await asyncio.sleep(2)
        
        # 清理资源
        await orchestrator.cleanup()
        
        # 返回成功响应
        response_data = {
            "status": "success",
            "message": "消息已通过 AutoGen 消息机制发送到智能体",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ [API流程-发送] 消息发送成功 - 会话ID: {session_id}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [API流程-发送] 消息发送失败 - 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


# 导出路由器
__all__ = ["normal_chat_message_router"]
