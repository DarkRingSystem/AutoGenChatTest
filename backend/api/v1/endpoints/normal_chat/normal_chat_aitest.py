"""
优化的普通聊天 API 端点
基于 Microsoft AutoGen 框架和 FastAPI 的 SSE 流式响应实现

主要优化：
1. 完善的错误处理和日志记录
2. 优化的 SSE 流式响应处理
3. 改进的会话管理
4. 更好的资源清理机制
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.v1.endpoints.normal_chat.chat_model import NormalChatRequest
from core.orchestration_service_aitest import NormalChatOrchestrationAitest
from services.normal_chat_stream_service_aitest import NormalChatStreamServiceAitest

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 会话存储（生产环境应使用 Redis 或数据库）
session_storage: Dict[str, Dict] = {}
# 活跃的编排器存储
active_orchestrators: Dict[str, NormalChatOrchestrationAitest] = {}


@router.post("/api/v1/normal_chat/stream_aitest")
async def normal_chat_stream_aitest(request: NormalChatRequest):
    """
    优化的 SSE 流式聊天响应端点
    
    主要改进：
    - 完善的错误处理
    - 优化的资源管理
    - 改进的流式响应处理
    - 更好的会话管理
    
    参数:
        request: 包含消息的聊天请求
    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    session_id = None
    orchestrator = None
    
    try:
        # 验证请求
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="消息内容不能为空")

        # 生成或使用现有会话 ID
        if request.session_id is None:
            session_id = f"normal_chat_{uuid.uuid4()}"
            request.session_id = session_id
        else:
            session_id = request.session_id

        logger.info(f"🚀 开始处理聊天请求 - 会话ID: {session_id}")

        # 构建会话数据
        session_data = {
            "message": request.message.strip(),
            "session_id": session_id,
            "file_ids": request.file_ids or [],
            "is_feedback": request.is_feedback or False,
            "target_agent": request.target_agent,
            "orchestration_service": "NormalChatOrchestrationAitest"
        }

        # 检查是否已有现存的编排器
        if session_id in active_orchestrators:
            # 复用现有编排器
            orchestrator = active_orchestrators[session_id]
            logger.info(f"🔄 复用现有编排器 - 会话ID: {session_id}")

            # 更新会话数据
            session_storage[session_id] = session_data
            logger.info(f"📝 会话数据已更新 - 会话ID: {session_id}")
        else:
            # 创建新编排器
            orchestrator = NormalChatOrchestrationAitest(session_data)
            active_orchestrators[session_id] = orchestrator

            # 保存会话数据
            session_storage[session_id] = session_data
            logger.info(f"📝 新会话数据已保存 - 会话ID: {session_id}")

            # 初始化编排器
            await orchestrator.initialize()
            logger.info(f"✅ 新编排器初始化完成 - 会话ID: {session_id}")

        # 创建流式服务
        stream_service = NormalChatStreamServiceAitest()

        # 确保编排器已正确初始化
        if orchestrator is None:
            logger.error(f"❌ 编排器未正确初始化 - 会话ID: {session_id}")
            raise HTTPException(status_code=500, detail="编排器初始化失败")

        # 生成流式响应
        async def generate_stream():
            """生成 SSE 流式响应"""
            try:
                # 再次检查编排器是否可用
                if orchestrator is None:
                    raise RuntimeError("编排器未初始化")

                # 获取智能体事件流
                event_stream = orchestrator.run_stream(task=request.message.strip())

                # 处理事件流并转换为 SSE 格式
                async for sse_message in stream_service.process_stream(
                    event_stream,
                    request.message.strip(),
                    session_id
                ):
                    yield sse_message

            except Exception as e:
                logger.error(f"❌ 流式响应生成失败 - 会话ID: {session_id}, 错误: {str(e)}")
                # 发送错误消息
                error_message = {
                    "type": "error",
                    "content": f"处理请求时发生错误: {str(e)}",
                    "session_id": session_id
                }
                yield f"data: {json.dumps(error_message, ensure_ascii=False)}\n\n"
                # 只在出错时清理会话
                await cleanup_session(session_id)
            finally:
                # 正常情况下不清理会话，保持会话状态以便后续请求使用
                # 只清理编排器的临时资源，但保留会话数据
                if session_id in active_orchestrators:
                    try:
                        # 这里可以添加一些轻量级的清理，但不删除会话数据
                        logger.info(f"🔄 会话请求完成，保持会话状态 - 会话ID: {session_id}")
                    except Exception as cleanup_error:
                        logger.warning(f"⚠️ 会话状态维护警告 - 会话ID: {session_id}, 错误: {str(cleanup_error)}")

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "X-Session-ID": session_id,
            }
        )

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        logger.error(f"❌ 处理聊天请求失败 - 会话ID: {session_id}, 错误: {str(e)}")
        # 清理资源
        if session_id:
            await cleanup_session(session_id)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    获取会话状态
    
    参数:
        session_id: 会话 ID
    返回:
        会话状态信息
    """
    try:
        if session_id not in session_storage:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session_data = session_storage[session_id]
        orchestrator = active_orchestrators.get(session_id)
        
        status = {
            "session_id": session_id,
            "exists": True,
            "orchestrator_active": orchestrator is not None,
            "message": session_data.get("message", ""),
            "created_at": session_data.get("created_at"),
            "last_activity": session_data.get("last_activity")
        }
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取会话状态失败 - 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话状态失败: {str(e)}")


@router.delete("/session/{session_id}")
async def cleanup_session_endpoint(session_id: str):
    """
    清理会话资源的端点
    
    参数:
        session_id: 会话 ID
    返回:
        清理结果
    """
    try:
        result = await cleanup_session(session_id)
        return {"session_id": session_id, "cleaned": result}
        
    except Exception as e:
        logger.error(f"❌ 清理会话失败 - 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理会话失败: {str(e)}")


async def cleanup_session(session_id: str) -> bool:
    """
    清理会话资源
    
    参数:
        session_id: 会话 ID
    返回:
        是否成功清理
    """
    try:
        cleaned = False
        
        # 清理编排器
        if session_id in active_orchestrators:
            orchestrator = active_orchestrators[session_id]
            try:
                await orchestrator.cleanup()
                logger.info(f"🧹 编排器已清理 - 会话ID: {session_id}")
            except Exception as e:
                logger.warning(f"⚠️ 编排器清理失败 - 会话ID: {session_id}, 错误: {str(e)}")
            finally:
                del active_orchestrators[session_id]
                cleaned = True
        
        # 清理会话数据
        if session_id in session_storage:
            del session_storage[session_id]
            logger.info(f"🧹 会话数据已清理 - 会话ID: {session_id}")
            cleaned = True
            
        return cleaned
        
    except Exception as e:
        logger.error(f"❌ 清理会话资源失败 - 会话ID: {session_id}, 错误: {str(e)}")
        return False


@router.get("/api/v1/normal_chat/health")
async def health_check():
    """
    健康检查端点
    
    返回:
        服务健康状态
    """
    try:
        return {
            "status": "healthy",
            "service": "normal_chat_aitest",
            "active_sessions": len(session_storage),
            "active_orchestrators": len(active_orchestrators)
        }
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务不健康")
