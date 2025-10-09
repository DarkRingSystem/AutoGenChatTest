"""
API 路由模块
定义所有 API 端点
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, Dict
import uuid
import re

from models import (
    ChatRequest, ChatResponse, HealthResponse,
    MarkdownConvertRequest, MarkdownConvertResponse,
    BatchMarkdownConvertResponse,
    ImageAnalysisRequest, ImageAnalysisResponse
)
from core.dependencies import get_ai_service, get_stream_service, get_session_service
from config import settings

# 文件内容存储（简单的内存存储，生产环境应使用数据库或缓存）
file_storage = {}

# 团队服务缓存（用于保持团队状态）
_team_service_cache: Dict[str, any] = {}

router = APIRouter()


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



def _build_message_with_file_context(message: str, file_ids: Optional[list[str]]) -> str:
    """
    构建包含文件上下文的消息

    参数:
        message: 用户原始消息
        file_ids: 文件 ID 列表

    返回:
        包含文件上下文的完整消息
    """
    if not file_ids or len(file_ids) == 0:
        return message

    # 获取文件存储
    file_storage = get_file_storage()

    # 获取文件内容
    file_contexts = []
    for file_id in file_ids:
        if file_id in file_storage:
            file_data = file_storage[file_id]
            filename = file_data.get("filename", "unknown")
            markdown = file_data.get("markdown", "")

            if markdown:
                file_contexts.append(f"### 文件: {filename}\n\n{markdown}")

    if not file_contexts:
        return message

    # 构建完整消息
    context_text = "\n\n---\n\n".join(file_contexts)
    full_message = f"""请结合以下文件内容和用户问题进行解答：

{context_text}

---

用户问题：{message}"""

    return full_message


def _extract_final_message(result) -> str:
    """
    从结果中提取最终消息

    参数:
        result: 智能体运行结果

    返回:
        最终消息字符串
    """
    if not result.messages:
        return "未生成响应"

    # 从后往前查找第一个有效消息
    for msg in reversed(result.messages):
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            return msg.content

    return "未生成响应"



@router.get("/")
async def root():
    """根端点"""
    return {
        "message": "AutoGen 聊天 API",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    session_service = get_session_service()
    session_count = await session_service.get_session_count()

    return HealthResponse(
        status="healthy",
        agent_initialized=True,
        session_count=session_count
    )


@router.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    使用 SSE 的流式聊天响应（支持会话隔离）

    参数:
        request: 包含消息的聊天请求

    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 构建包含文件上下文的消息
    from .utils import build_message_with_file_context
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
            "X-Session-ID": session.session_id,  # 返回会话 ID
        }
    )


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    非流式聊天端点（支持会话隔离）

    参数:
        request: 包含消息的聊天请求

    返回:
        包含完整消息的 ChatResponse
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
        from .utils import extract_final_message
        final_message = extract_final_message(result)

        return ChatResponse(
            message=final_message,
            conversation_id=session.session_id,
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sessions")
async def list_sessions():
    """
    列出所有会话

    返回:
        会话列表
    """
    session_service = get_session_service()
    sessions = await session_service.list_sessions()

    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """
    获取会话信息

    参数:
        session_id: 会话 ID

    返回:
        会话信息
    """
    session_service = get_session_service()
    session_info = await session_service.get_session_info(session_id)

    if not session_info:
        raise HTTPException(status_code=404, detail="会话不存在")

    return session_info


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话

    参数:
        session_id: 会话 ID

    返回:
        删除结果
    """
    session_service = get_session_service()
    success = await session_service.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "message": "会话已删除",
        "session_id": session_id
    }



@router.post("/api/team-chat/stream")
async def team_chat_stream(request: ChatRequest):
    """
    测试用例团队模式的流式聊天响应

    支持两种模式：
    1. 新对话：不传 conversation_id，创建新的团队会话
    2. 继续对话：传 conversation_id 和 is_feedback=True，继续之前的会话

    参数:
        request: 包含消息的聊天请求

    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 导入服务
    from services.ai_service import TestCasesTeamAIService
    from services.team_stream_service import TeamStreamService
    from services.team_session_service import get_team_session_service

    # 获取会话服务
    session_service = get_team_session_service()

    # 初始化变量
    conversation_id = None
    team_service = None
    feedback_message = None

    # 判断是新对话还是继续对话
    if request.is_feedback and request.conversation_id:
        # 继续对话：从会话中恢复团队
        session = session_service.get_session(request.conversation_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        if not session.waiting_for_feedback:
            raise HTTPException(status_code=400, detail="当前会话不在等待反馈状态")

        # 检查用户是否同意（空消息或包含"同意"/"APPROVE"）
        is_user_approved = not request.message.strip() or "同意" in request.message or "APPROVE" in request.message.upper()

        if is_user_approved:
            # 用户同意，调用 Optimizer 给出最终回答
            conversation_id = request.conversation_id

            # 清理旧的团队实例
            old_team_service = _get_cached_team_service(conversation_id)
            if old_team_service:
                await old_team_service.cleanup()
                _remove_cached_team_service(conversation_id)

            # 添加用户同意到会话
            session_service.add_message(conversation_id, "user", "同意")

            # 获取对话历史
            history = session_service.get_conversation_history(conversation_id)

            # 构建给 Optimizer 的消息
            history_text = "\n\n".join([
                f"{'用户' if msg['role'] == 'user' else msg['role']}: {msg['content']}"
                for msg in history[:-1]  # 排除最后一条（"同意"）
            ])

            optimizer_message = f"对话历史：\n{history_text}\n\n用户已同意以上方案。请作为测试用例优化器，结合生成器和评审员的意见，给出最终优化的测试用例。"

            # 创建新的团队实例（只包含 Optimizer）
            team_service = TestCasesTeamAIService(settings)
            await team_service.initialize(specific_agent="TestCase_Optimizer")

            # 缓存团队实例
            _cache_team_service(conversation_id, team_service)

            # 设置为最终回答模式
            feedback_message = optimizer_message

            print(f"✅ 用户同意，调用 Optimizer 给出最终回答")

            # 继续执行后续流程（运行 Optimizer）
        else:
            # 用户提供了反馈，创建新的团队实例继续对话
            conversation_id = request.conversation_id

            # 清理旧的团队实例
            old_team_service = _get_cached_team_service(conversation_id)
            if old_team_service:
                await old_team_service.cleanup()
                _remove_cached_team_service(conversation_id)

            # 添加用户反馈到会话
            session_service.add_message(conversation_id, "user", request.message)

            # 解析目标智能体（如果用户使用 @ 提及）
            target_agent = _parse_target_agent(request.message)

            # 构建反馈消息（包含对话历史）
            history = session_service.get_conversation_history(conversation_id)

            # 构建包含历史的消息
            history_text = "\n\n".join([
                f"{'用户' if msg['role'] == 'user' else msg['role']}: {msg['content']}"
                for msg in history[:-1]  # 排除最后一条（当前反馈）
            ])

            if target_agent == "all":
                # 用户选择 @all，重新运行 Generator → Reviewer 流程
                feedback_message = f"对话历史：\n{history_text}\n\n用户反馈（@all）: {request.message}"

                # 创建新的团队服务实例（Generator → Reviewer）
                team_service = TestCasesTeamAIService(settings)
                await team_service.initialize()  # 默认包含 Generator 和 Reviewer

                print(f"🔄 继续对话 {conversation_id}，@all 重新运行 Generator → Reviewer 流程")
            elif target_agent:
                # 用户指定了特定智能体，只运行该智能体
                feedback_message = f"对话历史：\n{history_text}\n\n用户反馈（@{target_agent}）: {request.message}"

                # 创建新的团队服务实例（只包含指定的智能体）
                team_service = TestCasesTeamAIService(settings)
                await team_service.initialize(specific_agent=target_agent)

                print(f"🎯 继续对话 {conversation_id}，指定智能体: {target_agent}")
            else:
                # 用户未指定智能体，重复 Generator → Reviewer 流程
                feedback_message = f"对话历史：\n{history_text}\n\n用户反馈: {request.message}"

                # 创建新的团队服务实例（Generator → Reviewer）
                team_service = TestCasesTeamAIService(settings)
                await team_service.initialize()  # 默认包含 Generator 和 Reviewer

                print(f"📝 继续对话 {conversation_id}，重复 Generator → Reviewer 流程")

            # 更新缓存
            _cache_team_service(conversation_id, team_service)

    else:
        # 新对话：创建新的团队和会话
        conversation_id = session_service.create_session()

        # 创建团队服务实例
        team_service = TestCasesTeamAIService(settings)
        await team_service.initialize()

        # 缓存团队实例
        _cache_team_service(conversation_id, team_service)

        # 添加用户消息到会话
        session_service.add_message(conversation_id, "user", request.message)

        feedback_message = request.message

        print(f"🆕 创建新对话 {conversation_id}")

    # 构建包含文件上下文的消息
    from .utils import build_message_with_file_context
    message_with_context = build_message_with_file_context(feedback_message, request.file_ids)

    # 创建团队流服务
    from services.team_stream_service import TeamStreamService
    team_stream_service = TeamStreamService()

    # 从团队获取事件流
    async def get_event_stream():
        try:
            # 无论是新对话还是继续对话，都传入消息
            # AutoGen 的 RoundRobinGroupChat 会自动维护对话历史
            async for event in team_service.run_stream(message=message_with_context):
                yield event
        except Exception as e:
            print(f"❌ 团队流错误: {e}")
            raise

    # 处理流式响应
    sse_stream = team_stream_service.process_stream(get_event_stream(), request.message)

    # 在流结束后更新会话状态
    async def sse_stream_with_session_update():
        current_conversation_id = conversation_id
        try:
            async for chunk in sse_stream:
                yield chunk

            # 保存智能体的回答到会话历史
            for agent_name, response in team_stream_service.agent_responses.items():
                if response:  # 只保存非空回答
                    session_service.add_message(current_conversation_id, agent_name, response)
                    print(f"💾 保存 {agent_name} 的回答到会话历史")

            # 检查是否需要等待反馈
            if team_stream_service.waiting_for_feedback:
                session_service.set_waiting_for_feedback(
                    current_conversation_id,
                    True,
                    team_stream_service.feedback_agent
                )
                print(f"⏸️ 会话 {current_conversation_id} 等待用户反馈")
            else:
                # 对话结束，清理资源
                session_service.set_waiting_for_feedback(current_conversation_id, False)
                _remove_cached_team_service(current_conversation_id)
                await team_service.cleanup()
                print(f"✅ 会话 {current_conversation_id} 已完成")
        except Exception as e:
            print(f"❌ SSE 流错误: {e}")
            # 清理资源
            _remove_cached_team_service(current_conversation_id)
            await team_service.cleanup()
            raise

    return StreamingResponse(
        sse_stream_with_session_update(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Team-Mode": "true",
            "X-Conversation-ID": conversation_id,
        }
    )


@router.post("/api/convert/markdown", response_model=MarkdownConvertResponse)
async def convert_to_markdown(
    file: UploadFile = File(..., description="要转换的文件"),
    use_llm: bool = Form(default=None, description="是否使用 LLM 提升转换精度"),
    force_ocr: bool = Form(default=None, description="是否强制对所有内容进行 OCR"),
    disable_image_extraction: bool = Form(default=None, description="是否禁用图片提取"),
    page_range: Optional[str] = Form(default=None, description="页面范围，例如: '0,5-10,20'"),
    output_format: str = Form(default=None, description="输出格式"),
    llm_api_key: Optional[str] = Form(default=None, description="LLM API 密钥"),
    llm_base_url: Optional[str] = Form(default=None, description="LLM API 基础 URL"),
    llm_model: Optional[str] = Form(default=None, description="LLM 模型名称"),
):
    """
    将上传的文件转换为 Markdown 格式

    支持的文件格式:
    - PDF (.pdf)
    - 图片 (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
    - PowerPoint (.pptx, .ppt)
    - Word (.docx, .doc)
    - Excel (.xlsx, .xls)
    - HTML (.html, .htm)
    - EPUB (.epub)

    参数:
        file: 上传的文件
        use_llm: 是否使用 LLM 提升转换精度
        force_ocr: 是否强制对所有内容进行 OCR
        disable_image_extraction: 是否禁用图片提取
        page_range: 页面范围
        output_format: 输出格式
        llm_api_key: LLM API 密钥（如果使用 LLM）
        llm_base_url: LLM API 基础 URL（如果使用 LLM）
        llm_model: LLM 模型名称（如果使用 LLM）

    返回:
        MarkdownConvertResponse: 包含转换结果的响应
    """
    from services.markdown_converter_service import MarkdownConverterService

    try:
        # 读取文件内容
        file_bytes = await file.read()

        # 使用配置文件的默认值，如果参数为 None
        final_use_llm = use_llm if use_llm is not None else settings.markdown_use_llm
        final_force_ocr = force_ocr if force_ocr is not None else settings.markdown_force_ocr
        final_disable_image = disable_image_extraction if disable_image_extraction is not None else settings.markdown_disable_image_extraction
        final_output_format = output_format if output_format is not None else settings.markdown_output_format

        # LLM 配置优先使用传入参数，否则使用配置文件
        final_llm_api_key = llm_api_key or settings.markdown_llm_api_key
        final_llm_base_url = llm_base_url or settings.markdown_llm_base_url
        final_llm_model = llm_model or settings.markdown_llm_model
        final_llm_service = settings.markdown_llm_service if final_use_llm and final_llm_api_key else None

        # 创建转换服务
        converter_service = MarkdownConverterService(
            use_llm=final_use_llm,
            force_ocr=final_force_ocr,
            disable_image_extraction=final_disable_image,
            output_format=final_output_format,
            llm_service=final_llm_service,
            llm_api_key=final_llm_api_key,
            llm_base_url=final_llm_base_url,
            llm_model=final_llm_model,
        )

        # 检查文件格式是否支持
        if not converter_service.is_supported_file(file.filename):
            supported_formats = converter_service.get_supported_formats()
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持的格式: {', '.join(supported_formats)}"
            )

        # 转换文件
        result = await converter_service.convert_file_bytes(
            file_bytes=file_bytes,
            filename=file.filename,
            page_range=page_range
        )

        return MarkdownConvertResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@router.get("/api/convert/supported-formats")
async def get_supported_formats():
    """
    获取支持的文件格式列表

    返回:
        支持的文件格式列表
    """
    from services.markdown_converter_service import MarkdownConverterService

    converter_service = MarkdownConverterService()
    supported_formats = converter_service.get_supported_formats()

    return {
        "supported_formats": supported_formats,
        "total": len(supported_formats)
    }


@router.post("/api/convert/markdown/batch", response_model=BatchMarkdownConvertResponse)
async def convert_multiple_to_markdown(
    files: list[UploadFile] = File(..., description=f"要转换的多个文件（最多{settings.markdown_max_batch_files}个，每个最大{settings.markdown_max_file_size_mb}MB）"),
    use_llm: bool = Form(default=None, description="是否使用 LLM 提升转换精度"),
    force_ocr: bool = Form(default=None, description="是否强制对所有内容进行 OCR"),
    disable_image_extraction: bool = Form(default=None, description="是否禁用图片提取"),
    page_range: Optional[str] = Form(default=None, description="页面范围，例如: '0,5-10,20'"),
    output_format: str = Form(default=None, description="输出格式"),
    max_concurrent: int = Form(default=None, description="最大并发转换数"),
    llm_api_key: Optional[str] = Form(default=None, description="LLM API 密钥"),
    llm_base_url: Optional[str] = Form(default=None, description="LLM API 基础 URL"),
    llm_model: Optional[str] = Form(default=None, description="LLM 模型名称"),
):
    """
    批量转换多个文件为 Markdown 格式（并发处理）

    支持的文件格式:
    - PDF (.pdf)
    - 图片 (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
    - PowerPoint (.pptx, .ppt)
    - Word (.docx, .doc)
    - Excel (.xlsx, .xls)
    - HTML (.html, .htm)
    - EPUB (.epub)

    参数:
        files: 上传的多个文件
        use_llm: 是否使用 LLM 提升转换精度
        force_ocr: 是否强制对所有内容进行 OCR
        disable_image_extraction: 是否禁用图片提取
        page_range: 页面范围
        output_format: 输出格式
        max_concurrent: 最大并发转换数（默认: 3，建议不超过 5）
        llm_api_key: LLM API 密钥（如果使用 LLM）
        llm_base_url: LLM API 基础 URL（如果使用 LLM）
        llm_model: LLM 模型名称（如果使用 LLM）

    返回:
        BatchMarkdownConvertResponse: 包含所有文件转换结果的响应
    """
    from services.markdown_converter_service import MarkdownConverterService

    try:
        # 检查文件数量
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="至少需要上传一个文件")

        if len(files) > settings.markdown_max_batch_files:
            raise HTTPException(
                status_code=400,
                detail=f"单次最多支持 {settings.markdown_max_batch_files} 个文件"
            )

        # 检查文件大小
        MAX_FILE_SIZE = settings.markdown_max_file_size_mb * 1024 * 1024
        for file in files:
            # 读取文件大小
            file.file.seek(0, 2)  # 移动到文件末尾
            file_size = file.file.tell()
            file.file.seek(0)  # 重置到文件开头

            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 大小超过限制（最大 {settings.markdown_max_file_size_mb}MB）"
                )

        # 使用配置文件的默认值
        final_use_llm = use_llm if use_llm is not None else settings.markdown_use_llm
        final_force_ocr = force_ocr if force_ocr is not None else settings.markdown_force_ocr
        final_disable_image = disable_image_extraction if disable_image_extraction is not None else settings.markdown_disable_image_extraction
        final_output_format = output_format if output_format is not None else settings.markdown_output_format
        final_max_concurrent = max_concurrent if max_concurrent is not None else settings.markdown_max_concurrent

        # LLM 配置
        final_llm_api_key = llm_api_key or settings.markdown_llm_api_key
        final_llm_base_url = llm_base_url or settings.markdown_llm_base_url
        final_llm_model = llm_model or settings.markdown_llm_model
        final_llm_service = settings.markdown_llm_service if final_use_llm and final_llm_api_key else None

        # 创建转换服务
        converter_service = MarkdownConverterService(
            use_llm=final_use_llm,
            force_ocr=final_force_ocr,
            disable_image_extraction=final_disable_image,
            output_format=final_output_format,
            llm_service=final_llm_service,
            llm_api_key=final_llm_api_key,
            llm_base_url=final_llm_base_url,
            llm_model=final_llm_model,
        )

        # 读取所有文件内容
        files_data = []
        for file in files:
            # 检查文件格式
            if not converter_service.is_supported_file(file.filename):
                # 添加失败结果
                files_data.append((None, file.filename, "不支持的文件格式"))
            else:
                file_bytes = await file.read()
                files_data.append((file_bytes, file.filename, None))

        # 分离有效文件和无效文件
        valid_files = [(fb, fn) for fb, fn, err in files_data if err is None]
        invalid_files = [(fn, err) for fb, fn, err in files_data if err is not None]

        # 并发转换有效文件
        results = []

        if valid_files:
            conversion_results = await converter_service.convert_multiple_file_bytes(
                files_data=valid_files,
                page_range=page_range,
                max_concurrent=final_max_concurrent
            )
            results.extend(conversion_results)

        # 添加无效文件的结果
        for filename, error in invalid_files:
            results.append({
                "success": False,
                "message": error,
                "markdown": "",
                "metadata": {},
                "images": {},
                "filename": filename
            })

        # 为每个成功的文件生成 ID 并存储内容
        for result in results:
            if result.get("success", False):
                file_id = str(uuid.uuid4())
                result["file_id"] = file_id

                # 存储文件内容到内存（包含文件名和 markdown 内容）
                file_storage[file_id] = {
                    "filename": result.get("filename", "unknown"),
                    "markdown": result.get("markdown", ""),
                    "metadata": result.get("metadata", {})
                }
            else:
                result["file_id"] = None

        # 统计结果
        success_count = sum(1 for r in results if r.get("success", False))
        failed_count = len(results) - success_count

        return BatchMarkdownConvertResponse(
            total=len(results),
            success_count=success_count,
            failed_count=failed_count,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量转换失败: {str(e)}")



@router.post("/api/image-analysis/stream")
async def image_analysis_stream(
    image: Optional[UploadFile] = File(None, description="上传的图片文件"),
    session_id: Optional[str] = Form(None, description="会话 ID"),
    image_url: Optional[str] = Form(None, description="图片 URL"),
    web_url: Optional[str] = Form(None, description="图片所在页面的 URL"),
    test_description: Optional[str] = Form(None, description="测试场景描述"),
    additional_context: Optional[str] = Form(None, description="附加上下文信息"),
    target_url: Optional[str] = Form(None, description="目标页面 URL")
):
    """
    图片分析流式 API（支持 SSE）

    支持两种方式提供图片：
    1. 上传图片文件（image 参数）
    2. 提供图片 URL（image_url 参数）

    返回流式事件，包括：
    - agent_start: 智能体开始工作
    - agent_message: 智能体消息
    - agent_done: 智能体完成
    - done: 分析完成
    - error: 错误信息
    """
    from services.image_analysis_stream_service import ImageAnalysisStreamService

    try:
        # 生成会话 ID
        if not session_id:
            session_id = f"img_{uuid.uuid4().hex[:12]}"

        print(f"\n{'='*60}")
        print(f"📸 图片分析请求")
        print(f"{'='*60}")
        print(f"会话 ID: {session_id}")

        # 处理图片数据
        image_data = None
        if image:
            # 读取上传的图片文件
            content = await image.read()
            image_data = base64.b64encode(content).decode('utf-8')
            print(f"图片文件: {image.filename} ({len(content)} 字节)")
        elif image_url:
            print(f"图片 URL: {image_url}")
        else:
            raise HTTPException(status_code=400, detail="必须提供图片文件或图片 URL")

        if web_url:
            print(f"页面 URL: {web_url}")
        if test_description:
            print(f"测试描述: {test_description}")

        # 创建流式服务
        stream_service = ImageAnalysisStreamService()

        # 创建图片分析团队并初始化
        from agents.image_analyzer_team import ImageAnalyzerTeam
        analyzer_team = ImageAnalyzerTeam(settings)
        await analyzer_team.initialize()

        # 执行流式分析
        event_stream = analyzer_team.analyze_image_stream(
            session_id=session_id,
            image_data=image_data,
            image_url=image_url,
            web_url=web_url,
            test_description=test_description,
            additional_context=additional_context,
            target_url=target_url
        )

        # 处理事件流并生成 SSE 响应
        async def generate_sse():
            async for sse_message in stream_service.process_stream(event_stream, session_id):
                yield sse_message

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id,
            }
        )

    except Exception as e:
        print(f"❌ 图片分析错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")


@router.post("/api/image-analysis", response_model=ImageAnalysisResponse)
async def image_analysis(
    image: Optional[UploadFile] = File(None, description="上传的图片文件"),
    session_id: Optional[str] = Form(None, description="会话 ID"),
    image_url: Optional[str] = Form(None, description="图片 URL"),
    web_url: Optional[str] = Form(None, description="图片所在页面的 URL"),
    test_description: Optional[str] = Form(None, description="测试场景描述"),
    additional_context: Optional[str] = Form(None, description="附加上下文信息"),
    target_url: Optional[str] = Form(None, description="目标页面 URL")
):
    """
    图片分析非流式 API

    支持两种方式提供图片：
    1. 上传图片文件（image 参数）
    2. 提供图片 URL（image_url 参数）

    返回完整的分析结果
    """
    try:
        # 生成会话 ID
        if not session_id:
            session_id = f"img_{uuid.uuid4().hex[:12]}"

        print(f"\n{'='*60}")
        print(f"📸 图片分析请求（非流式）")
        print(f"{'='*60}")
        print(f"会话 ID: {session_id}")

        # 处理图片数据
        image_data = None
        if image:
            # 读取上传的图片文件
            content = await image.read()
            image_data = base64.b64encode(content).decode('utf-8')
            print(f"图片文件: {image.filename} ({len(content)} 字节)")
        elif image_url:
            print(f"图片 URL: {image_url}")
        else:
            raise HTTPException(status_code=400, detail="必须提供图片文件或图片 URL")

        # 创建图片分析团队并初始化
        from agents.image_analyzer_team import ImageAnalyzerTeam
        analyzer_team = ImageAnalyzerTeam(settings)
        await analyzer_team.initialize()

        # 执行分析
        results = await analyzer_team.analyze_image(
            session_id=session_id,
            image_data=image_data,
            image_url=image_url,
            web_url=web_url,
            test_description=test_description,
            additional_context=additional_context,
            target_url=target_url
        )

        # 返回结果
        return ImageAnalysisResponse(
            session_id=session_id,
            ui_analysis=results["ui_analysis"],
            interaction_analysis=results["interaction_analysis"],
            test_scenarios=results["test_scenarios"],
            chat_history=results["chat_history"],
            summary=results["summary"],
            status="success"
        )

    except Exception as e:
        print(f"❌ 图片分析错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")

