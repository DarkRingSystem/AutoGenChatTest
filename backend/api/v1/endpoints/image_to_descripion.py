import base64

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, Dict
import uuid
import re

router = APIRouter()

@router.post("/api/image-to-description")
async def image_to_description(
    file: UploadFile = File(..., description="要转换的图片文件")
    analysis_type: str = Form(..., description="分析类型（ocr、caption）")
    additional_context: Optional[str] = Form(None, description="附加上下文信息")
  
):
    """上传图片并启动AI描述生成任务"""

    try:
        # 校验文件
        if not file.file.content_type or not file.conten_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传有效的图片文件")
        
        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)

        # 检查文件大小（限制为10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="图片文件大小超过限制（最大10MB）")
        
        # 转换为base64编码
        image_base64 = base64.b64encode(file_content).decode('utf-8')

        # 生成会话ID
        session_id = str(uuid.uuid4())[:12]

        # 记录当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 存储会话信息
        active_sessions[session_id] = {
            "start_time": current_time,
            "image_base64": image_base64,
            "analysis_type": analysis_type,
            "additional_context": additional_context,
            "status": "processing"
        }

        # 创建消息队列
        message_queue = asyncio.Queue()
        message_queues[session_id] = message_queue

        # 立即启动后台分析任务
        asyncio.create_task(process_description_generation_task(session_id))

        logger.info(f"图片描述任务已启动，会话ID: {session_id},文件名: {file.filename}")

        return JSONResponse(content={"session_id": session_id})


    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

async def process_description_generation_task(session_id: str):
    """处理图片描述生成任务"""
    try:
        logger.info(f"开始处理图片描述生成任务，会话ID: {session_id}")

        # 从会话信息中获取图片数据
        session_info = active_sessions.get(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话未找到")
        
        session_info = active_sessions[session_id]
        message_queue = message_queues.get(session_id)

        if not message_queue:
            raise HTTPException(status_code=500, detail="消息队列未找到")

        # 发送开始消息
        start_message = StreamMessage(
            message_id=f"start-{uuid.uuid4()}",
            type="message",
            source="图片描述生成器",
            content="🔍 开始分析图片，生成测试用例描述",
            region="analysis",
            platform="web",
            is_final=False,
            session_id=session_id
        )
        await message_queue.put(start_message)

        # 更新进度
        active_sessions[session_id]["progress"] = 10
        active_sessions[session_id]["test_activity"] = dateime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 设置消息回调函数

        async def message_callback(message: str):
            await message_queue.put(message)


        # 创建响应收集器
        from utils.response_collector import ResponseCollector
        from utils import AgentPlatform
        collector = ResponseCollector(message_callback, AgentPlatform.WEB)
        collector.set_callback(message_callback)

        # 获取Web编排器
        

        # 获取文件信息
        file_info = session_info["file_info"]
        additional_context = session_info["additional_context"]

        # 更新进度
        active_sessions[session_id]["progress"] = 30

        # 使用编排器执行图片描述生成
        await orchestrator.generate_description_from_image(
            file_info, additional_context, collector
        )
        




