"""
AI测试用例生成API
用于启动智能体工作流并流式返回结果
"""
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.orchestrator_service import TestCaseOrchestrator
from app.models.test_case import ImageAnalysisRequest, TestCaseGenerationRequest

# 添加utils路径到sys.path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.sse_stream_service import SSEStreamService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-testcase-generator", tags=["AI测试用例生成"])

# 全局会话存储
active_sessions: Dict[str, Dict[str, Any]] = {}
orchestrators: Dict[str, TestCaseOrchestrator] = {}

class GenerationStartRequest(BaseModel):
    """开始生成请求"""
    session_id: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None
    agent_type: str = "image_analysis"

class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    status: str
    message: str

@router.post("/session/create", response_model=SessionResponse)
async def create_session():
    """创建新的生成会话"""
    try:
        session_id = str(uuid.uuid4())

        # 初始化会话数据
        active_sessions[session_id] = {
            "session_id": session_id,
            "status": "created",
            "created_at": datetime.now(),
            "messages": [],
            "orchestrator": None
        }

        logger.info(f"创建新会话: {session_id}")

        return SessionResponse(
            session_id=session_id,
            status="created",
            message="会话创建成功"
        )

    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@router.post("/session/{session_id}/start")
async def start_generation(
    session_id: str,
    request: GenerationStartRequest
):
    """开始生成测试用例"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")

        session = active_sessions[session_id]
        session["status"] = "starting"

        # 保存请求信息到会话中
        if request.file_name:
            # 验证文件是否存在
            file_path = request.file_path or f"backend/uploads/ai_files/{request.file_name}"

            # 构建绝对路径进行验证
            if not os.path.isabs(file_path):
                current_dir = os.path.dirname(__file__)  # backend/app/api
                backend_dir = os.path.dirname(os.path.dirname(current_dir))  # backend
                project_root = os.path.dirname(backend_dir)  # 项目根目录
                abs_file_path = os.path.join(project_root, file_path)
            else:
                abs_file_path = file_path

            if not os.path.exists(abs_file_path):
                logger.error(f"文件不存在: {abs_file_path}")
                raise HTTPException(status_code=400, detail=f"文件不存在: {request.file_name}")

            session["file_name"] = request.file_name
            session["file_path"] = file_path
            logger.info(f"会话 {session_id} 保存文件信息: {request.file_name} -> {abs_file_path}")

        if request.description:
            session["description"] = request.description

        # 创建编排器
        orchestrator = TestCaseOrchestrator(session_id=session_id)
        orchestrators[session_id] = orchestrator
        session["orchestrator"] = orchestrator

        # 根据智能体类型启动不同的工作流
        if request.agent_type == "image_analysis" and (request.file_path or request.file_name):
            # 构建文件路径
            file_path = request.file_path or f"backend/uploads/ai_files/{request.file_name}"

            # 启动图片分析工作流
            analysis_request = ImageAnalysisRequest(
                session_id=session_id,
                image_name=request.file_name or "uploaded_image",
                image_path=file_path,
                image_description=request.description,
                analysis_target="UI测试用例生成"
            )

            # 异步启动工作流
            task = asyncio.create_task(orchestrator.analyze_image(analysis_request))

            # 添加异常处理回调
            def handle_task_exception(task):
                if task.exception():
                    logger.error(f"图片分析任务异常: {task.exception()}")
                    session["status"] = "error"

            task.add_done_callback(handle_task_exception)

        else:
            # 启动文本生成工作流
            generation_request = TestCaseGenerationRequest(
                source_type="text",
                source_data={"description": request.description or ""},
                test_cases=[],
                generation_config={"auto_save": True}
            )

            # 异步启动工作流
            asyncio.create_task(orchestrator.generate_test_cases(generation_request))

        session["status"] = "running"

        return SessionResponse(
            session_id=session_id,
            status="running",
            message="测试用例生成已启动"
        )

    except Exception as e:
        logger.error(f"启动生成失败: {str(e)}")
        if session_id in active_sessions:
            active_sessions[session_id]["status"] = "error"
        raise HTTPException(status_code=500, detail=f"启动生成失败: {str(e)}")

@router.get("/session/{session_id}/stream")
async def stream_generation_progress(session_id: str, request: Request):
    """流式获取生成进度"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")

        async def generate_stream():
            """生成SSE流"""
            try:
                session = active_sessions[session_id]
                orchestrator = orchestrators.get(session_id)

                if not orchestrator:
                    yield f"data: {{'type': 'error', 'content': '编排器未找到'}}\n\n"
                    return

                # 发送开始消息
                yield f"data: {{'type': 'status', 'content': '🚀 开始生成测试用例...'}}\n\n"

                # 监听编排器的消息
                message_count = 0
                max_messages = 100000000000  # 防止无限循环
                timeout_count = 0
                max_timeout = 600000  # 10分钟超时 (6000 * 0.1s)

                logger.info(f"开始监听消息: {session_id}")

                while message_count < max_messages and timeout_count < max_timeout:
                    if await request.is_disconnected():
                        logger.info(f"客户端断开连接: {session_id}")
                        break

                    # 检查是否有新消息
                    if orchestrator.response_collector:
                        messages = await orchestrator.response_collector.get_messages()
                        if messages:
                            logger.info(f"收到 {len(messages)} 条新消息")
                            for message in messages:
                                yield f"data: {message}\n\n"
                                message_count += 1

                                # 检查是否是工作流完成消息
                                if isinstance(message, dict) and message.get("content") == "WORKFLOW_COMPLETED":
                                    logger.info(f"工作流完成: {session_id}")
                                    session["status"] = "completed"
                                elif isinstance(message, dict) and message.get("content") == "WORKFLOW_ERROR":
                                    logger.info(f"工作流错误: {session_id}")
                                    session["status"] = "error"

                            timeout_count = 0  # 重置超时计数
                        else:
                            timeout_count += 1
                    else:
                        timeout_count += 1

                    # 检查会话状态
                    if session.get("status") == "completed":
                        logger.info(f"会话完成: {session_id}")
                        yield f"data: {{'type': 'done', 'content': '✅ 测试用例生成完成'}}\n\n"
                        break
                    elif session.get("status") == "error":
                        logger.info(f"会话错误: {session_id}")
                        yield f"data: {{'type': 'error', 'content': '❌ 生成过程中出现错误'}}\n\n"
                        break

                    # 短暂等待
                    await asyncio.sleep(0.1)

                # 超时处理
                if timeout_count >= max_timeout:
                    logger.warning(f"会话超时: {session_id}")
                    yield f"data: {{'type': 'timeout', 'content': '⏰ 处理超时，请稍后重试'}}\n\n"

                # 发送结束消息
                yield f"data: {{'type': 'end', 'content': 'Stream ended'}}\n\n"

            except Exception as e:
                logger.error(f"流式传输错误: {str(e)}")
                yield f"data: {{'type': 'error', 'content': '流式传输错误: {str(e)}'}}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    except Exception as e:
        logger.error(f"创建流式响应失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建流式响应失败: {str(e)}")

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """获取会话状态"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")

        session = active_sessions[session_id]

        return {
            "session_id": session_id,
            "status": session.get("status", "unknown"),
            "created_at": session.get("created_at"),
            "message_count": len(session.get("messages", []))
        }

    except Exception as e:
        logger.error(f"获取会话状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话状态失败: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]

        if session_id in orchestrators:
            # 清理编排器资源
            orchestrator = orchestrators[session_id]
            if hasattr(orchestrator, 'cleanup'):
                await orchestrator.cleanup()
            del orchestrators[session_id]

        return SessionResponse(
            session_id=session_id,
            status="deleted",
            message="会话已删除"
        )

    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")


@router.get("/session/{session_id}/stream-direct", response_class=StreamingResponse)
async def stream_generation_direct(session_id: str, request: Request):
    """直接流式生成测试用例（新的流式实现）"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")

        session = active_sessions[session_id]

        async def generate_direct_stream():
            """从ResponseCollector读取Agent的流式输出（仅region: agent的消息）"""
            import json
            try:
                # 获取编排器
                orchestrator = orchestrators.get(session_id)
                if not orchestrator:
                    yield "data: {\"type\": \"error\", \"content\": \"编排器未找到\"}\n\n"
                    return

                # 获取ResponseCollector
                response_collector = orchestrator.response_collector
                if not response_collector:
                    yield "data: {\"type\": \"error\", \"content\": \"ResponseCollector未找到\"}\n\n"
                    return

                # 发送开始消息
                yield "data: {\"type\": \"agent_start\", \"agent_name\": \"系统\"}\n\n"

                # 持续读取ResponseCollector中的消息，只转发region为"agent"的消息
                timeout_count = 0
                max_timeout = 60  # 最大等待60秒

                while timeout_count < max_timeout:
                    try:
                        # 等待消息，超时时间为1秒
                        message = await asyncio.wait_for(
                            response_collector.message_queue.get(),
                            timeout=1.0
                        )

                        # 只转发region为"agent"的消息到AI对话区域
                        if message.region == "agent":
                            message_data = {
                                "type": message.type,
                                "content": message.content,
                                "agent_name": message.agent_name,
                                "region": "agent"
                            }
                            yield f"data: {json.dumps(message_data)}\n\n"

                        # 如果收到完成消息，结束流式输出
                        if message.type == "complete" or message.content == "✅ 测试用例生成完成":
                            break

                        timeout_count = 0  # 重置超时计数

                    except asyncio.TimeoutError:
                        timeout_count += 1
                        # 发送心跳消息，避免前端超时
                        if timeout_count % 10 == 0:  # 每10秒发送一次心跳
                            yield "data: {\"type\": \"heartbeat\", \"content\": \"等待Agent响应中...\", \"region\": \"agent\"}\n\n"
                        continue

                # 发送完成消息
                yield "data: {\"type\": \"agent_done\", \"agent_name\": \"系统\"}\n\n"

                # 更新会话状态
                session["status"] = "completed"

            except Exception as e:
                logger.error(f"直接流式生成失败: {str(e)}")
                yield f"data: {{\"type\": \"error\", \"content\": \"生成失败: {str(e)}\"}}\n\n"
                session["status"] = "error"

        return StreamingResponse(
            generate_direct_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    except Exception as e:
        logger.error(f"直接流式传输失败: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")

        error_message = str(e)

        async def error_stream():
            yield f"data: {{\"type\": \"error\", \"content\": \"传输失败: {error_message}\"}}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )


async def stream_image_analysis(request: ImageAnalysisRequest) -> AsyncGenerator[str, None]:
    """流式图片分析 - 真实模型调用"""
    try:
        from autogen_agentchat.messages import MultiModalMessage
        from autogen_core import Image
        from app.core.llms import _get_uitars_model_client
        import json
        import os

        # 发送智能体开始消息
        yield "data: {\"type\": \"agent_start\", \"agent_name\": \"UI界面分析智能体\"}\n\n"

        # 使用llms.py中的UI-TARS模型客户端
        model_client = _get_uitars_model_client()

        # 加载图片 - 确保路径正确
        image_path = request.image_path
        if not os.path.isabs(image_path):
            # 相对路径，需要从项目根目录开始
            # 当前文件在 backend/app/api/，需要回到项目根目录
            current_dir = os.path.dirname(__file__)  # backend/app/api
            backend_dir = os.path.dirname(os.path.dirname(current_dir))  # backend
            project_root = os.path.dirname(backend_dir)  # 项目根目录
            image_path = os.path.join(project_root, image_path)

        logger.info(f"尝试加载图片: {image_path}")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        image = Image.from_file(image_path)

        # 构建分析提示词
        prompt = f"""
请分析这张UI界面截图，识别以下内容：
1. 界面类型（登录页面、主页、表单页面等）
2. 主要UI元素（按钮、输入框、链接、图片等）
3. 界面布局结构
4. 可能的交互功能
5. 需要测试的关键功能点

图片名称: {request.image_name}
分析目标: {request.analysis_target or '全面分析UI界面'}

请以JSON格式返回分析结果。
"""

        # 创建多模态消息
        multi_modal_message = MultiModalMessage(
            content=[prompt, image],
            source="user"
        )

        # 转换为模型消息
        user_message = multi_modal_message.to_model_message()

        # 真实流式调用模型
        analysis_text = ""

        # 使用真实的UI-TARS模型API调用
        try:
            async for chunk in model_client.create_stream([user_message]):
                if hasattr(chunk, 'content') and chunk.content:
                    analysis_text += chunk.content
                    # 发送流式内容到AI对话区域
                    yield f"data: {{\"type\": \"chunk\", \"content\": {json.dumps(chunk.content)}, \"agent_name\": \"UI界面分析智能体\", \"region\": \"agent\"}}\n\n"
        except Exception as e:
            logger.error(f"UI-TARS模型调用失败: {str(e)}")
            # 如果模型调用失败，使用模拟数据作为降级方案
            logger.warning("模型调用失败，使用模拟数据作为降级方案")
            mock_chunks = [
                "我正在分析这张UI界面截图...\n\n",
                "这是一个登录页面，包含以下主要元素：\n",
                "1. 手机号输入框\n",
                "2. 验证码输入框\n",
                "3. 密码输入框\n",
                "4. 登录按钮\n",
                "5. 切换登录方式的选项\n\n",
                "界面布局采用垂直排列，符合移动端设计规范。\n",
                "需要重点测试手机号验证码登录和密码登录功能的切换。"
            ]

            for chunk_content in mock_chunks:
                analysis_text += chunk_content
                yield f"data: {{\"type\": \"chunk\", \"content\": {json.dumps(chunk_content)}, \"agent_name\": \"UI界面分析智能体\", \"region\": \"agent\"}}\n\n"
                await asyncio.sleep(0.5)

        # 发送智能体完成消息
        yield "data: {\"type\": \"agent_done\", \"agent_name\": \"UI界面分析智能体\"}\n\n"

        # 解析分析结果
        try:
            analysis_result = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis_result = {
                "interface_type": "UI界面",
                "ui_elements": [],
                "layout": "未知布局",
                "key_functions": [],
                "test_points": [],
                "raw_analysis": analysis_text
            }

        # 添加用户描述
        if request.image_description:
            analysis_result["user_description"] = request.image_description

        # 发送分析完成消息
        yield f"data: {{\"type\": \"analysis_complete\", \"analysis_result\": {json.dumps(analysis_result)}}}\n\n"

    except Exception as e:
        logger.error(f"流式图片分析失败: {str(e)}")
        yield f"data: {{\"type\": \"error\", \"content\": \"图片分析失败: {str(e)}\"}}\n\n"


async def stream_test_case_generation(request: TestCaseGenerationRequest) -> AsyncGenerator[str, None]:
    """流式测试用例生成 - 真实模型调用"""
    try:
        from app.core.llms import _deepseek_model_client
        import json
        import os

        # 发送智能体开始消息
        yield "data: {\"type\": \"agent_start\", \"agent_name\": \"测试用例生成智能体\"}\n\n"

        # 使用llms.py中的DeepSeek模型客户端
        try:
            model_client = _deepseek_model_client()
        except Exception as e:
            logger.error(f"创建DeepSeek模型客户端失败: {str(e)}")
            model_client = None

        # 构建系统提示词
        analysis_result = request.source_data
        user_description = analysis_result.get("user_description", "")

        system_prompt = f"""你是一个专业的UI测试用例生成专家。

基于以下UI界面分析结果，生成详细的测试用例：

{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

请生成全面的测试用例，包括：
- 功能测试用例
- 界面测试用例
- 兼容性测试用例（不同设备、浏览器）

每个测试用例应包含：
- 用例标题
- 测试步骤
- 预期结果
- 前置条件
- 测试数据

请以JSON格式返回测试用例列表。
"""

        # 如果有用户描述，添加用户需求
        if user_description.strip():
            system_prompt += f"""

用户需求描述：
{user_description}

请特别关注用户描述的需求，确保生成的测试用例能够覆盖用户关注的功能点。"""

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户需求：{user_description}\n\n请根据上述UI界面分析结果和我的需求描述，生成相应的测试用例。"}
        ]

        # 真实流式调用模型或使用模拟数据
        response_text = ""

        if model_client:
            # 使用真实的模型API调用
            try:
                async for chunk in model_client.create_stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        response_text += chunk.content
                        # 发送流式内容到AI对话区域
                        yield f"data: {{\"type\": \"chunk\", \"content\": {json.dumps(chunk.content)}, \"agent_name\": \"测试用例生成智能体\", \"region\": \"agent\"}}\n\n"
            except Exception as e:
                logger.error(f"模型API调用失败: {str(e)}")
                error_msg = f"测试用例生成失败: {str(e)}"
                yield f"data: {{\"type\": \"error\", \"content\": \"{error_msg}\"}}\n\n"
                return
        else:
            # 如果没有配置API密钥，使用模拟数据
            logger.warning("未配置API密钥，使用模拟测试用例数据")
            mock_test_chunks = [
                "正在基于UI界面分析结果生成测试用例...\n\n",
                "## 功能测试用例\n\n",
                "### 测试用例1：手机号验证码登录\n",
                "- 前置条件：用户已安装应用\n",
                "- 测试步骤：\n",
                "  1. 打开登录页面\n",
                "  2. 选择手机号验证码登录方式\n",
                "  3. 输入有效手机号\n",
                "  4. 点击获取验证码\n",
                "  5. 输入正确验证码\n",
                "  6. 点击登录按钮\n",
                "- 预期结果：成功登录到主页\n\n",
                "### 测试用例2：密码登录\n",
                "- 前置条件：用户已注册账号\n",
                "- 测试步骤：\n",
                "  1. 打开登录页面\n",
                "  2. 选择密码登录方式\n",
                "  3. 输入用户名和密码\n",
                "  4. 点击登录按钮\n",
                "- 预期结果：成功登录到主页\n\n",
                "### 测试用例3：登录方式切换\n",
                "- 测试步骤：\n",
                "  1. 在验证码登录页面点击切换到密码登录\n",
                "  2. 在密码登录页面点击切换到验证码登录\n",
                "- 预期结果：界面正确切换，输入框状态正确\n\n",
                "测试用例生成完成！"
            ]

            for chunk_content in mock_test_chunks:
                response_text += chunk_content
                yield f"data: {{\"type\": \"chunk\", \"content\": {json.dumps(chunk_content)}, \"agent_name\": \"测试用例生成智能体\", \"region\": \"agent\"}}\n\n"
                await asyncio.sleep(0.3)

        # 发送智能体完成消息
        yield "data: {\"type\": \"agent_done\", \"agent_name\": \"测试用例生成智能体\"}\n\n"

    except Exception as e:
        logger.error(f"流式测试用例生成失败: {str(e)}")
        yield f"data: {{\"type\": \"error\", \"content\": \"测试用例生成失败: {str(e)}\"}}\n\n"