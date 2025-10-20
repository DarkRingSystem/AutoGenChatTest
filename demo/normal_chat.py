import base64
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, Dict
import uuid
import re

from backend.api.v1.endpoints.normal_chat.chat_model import NormalChatRequest, NormalChatStreamResponse
from backend.core import orchestration_service

router = APIRouter()

"""
工作流程：
1. 用户发送消息FASTAPI接受前端信息
2. 会话管理
3. 构建消息启动编排服务
4. 根据服务类型调用对应类型的编排服务
    编排服务根据类型调用工厂创建对应agent
    编排服务启动运行时
    编排服务注册agent
    编排服务确定订阅关系
    编排服务接受用户消息，推送到对应主题
    编排服务流式输出响应
5. FASTAPI向前端输出响应流式输出
"""

# 文件内容存储（简单的内存存储，生产环境应使用数据库或缓存）
file_storage = {}

# 会话存储（简单的内存存储，生产环境应使用数据库或缓存）
session_storage: Dict[str, Dict] = {}   

@router.post("/api/v1/normal_chat/stream")
async def normal_chat_stream(request: NormalChatRequest):
    """
    使用 SSE 的流式聊天响应
    参数:
        request: 包含消息的聊天请求
    返回:
        包含 SSE 格式数据的 StreamingResponse
    """

    # 检查消息内容
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 如果没有提供会话 ID，则创建一个新的
    if request.session_id is None:
        request.session_id = f"normal_chat_{uuid.uuid4()}"

    logging.info(f"生成会话 ID: {request.session_id}")

    # 生成会话数据，构建消息用于启动编排服务
    session_data = {
        "message": request.message,
        "session_id": request.session_id,
        "file_ids": request.file_ids,
        "is_feedback": request.is_feedback,
        "target_agent": request.target_agent,
        "orchestration_service": "NormalChatOrchestration"  # 指定编排服务
    }

    # 保存会话数据
    session_storage[request.session_id] = session_data

    # 创建编排器

    orchestrator = orchestration_service.NormalChatOrchestration(session_data)

    # 发送启动编排服务
    await orchestrator.start_chat()

    # 生成流式响应
    async def generate_stream():
        async for event in orchestrator.run_stream(task=request.message):
            yield event

    return NormalChatStreamResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )