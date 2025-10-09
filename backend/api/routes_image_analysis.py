"""
图片分析路由
路径: /api/image-analysis/*
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import base64
import uuid

from models import ImageAnalysisRequest, ImageAnalysisResponse
from config import settings

router = APIRouter(prefix="/api/image-analysis", tags=["image-analysis"])


@router.post("/stream")
async def image_analysis_stream(
    image: UploadFile = File(...),
    prompt: str = "分析这张 UI 界面图片，生成详细的测试用例"
):
    """
    图片分析 - 流式响应
    
    参数:
        image: 上传的图片文件
        prompt: 分析提示词
    
    返回:
        包含 SSE 格式数据的 StreamingResponse
    """
    try:
        # 生成会话 ID
        conversation_id = f"img_{uuid.uuid4().hex[:12]}"
        
        print(f"📸 图片分析请求")
        print("=" * 60)
        print(f"会话 ID: {conversation_id}")
        
        # 读取图片内容
        content = await image.read()
        
        # 转换为 base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # 创建图片分析团队
        from agents.factory import get_agent_factory, AgentType
        from agents import register_all_agents
        
        register_all_agents()
        factory = get_agent_factory(settings)
        
        analyzer_team = await factory.create_agent(
            agent_type=AgentType.IMAGE_ANALYSIS_TEAM,
            name="ImageAnalyzerTeam",
        )
        
        # 构建多模态消息
        multimodal_message = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]
        
        # 获取流式响应
        async def event_generator():
            try:
                async for event in analyzer_team.get_team().run_stream(task=multimodal_message):
                    # 转换为 SSE 格式
                    if hasattr(event, 'content'):
                        content = event.content
                        if isinstance(content, str):
                            yield f"data: {content}\n\n"
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    yield f"data: {item['text']}\n\n"
                                elif isinstance(item, str):
                                    yield f"data: {item}\n\n"
                    else:
                        yield f"data: {str(event)}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"❌ 流式处理错误: {e}")
                yield f"data: [ERROR] {str(e)}\n\n"
            
            finally:
                # 清理资源
                await analyzer_team.cleanup()
        
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
    
    except Exception as e:
        print(f"❌ 图片分析错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")


@router.post("/", response_model=ImageAnalysisResponse)
async def image_analysis(
    image: UploadFile = File(...),
    prompt: str = "分析这张 UI 界面图片，生成详细的测试用例"
):
    """
    图片分析 - 非流式响应
    
    参数:
        image: 上传的图片文件
        prompt: 分析提示词
    
    返回:
        ImageAnalysisResponse 包含分析结果
    """
    try:
        # 生成会话 ID
        conversation_id = f"img_{uuid.uuid4().hex[:12]}"
        
        print(f"📸 图片分析请求（非流式）")
        print("=" * 60)
        print(f"会话 ID: {conversation_id}")
        
        # 读取图片内容
        content = await image.read()
        
        # 转换为 base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # 创建图片分析团队
        from agents.factory import get_agent_factory, AgentType
        from agents import register_all_agents
        
        register_all_agents()
        factory = get_agent_factory(settings)
        
        analyzer_team = await factory.create_agent(
            agent_type=AgentType.IMAGE_ANALYSIS_TEAM,
            name="ImageAnalyzerTeam",
        )
        
        # 构建多模态消息
        multimodal_message = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]
        
        # 运行分析
        result = await analyzer_team.get_team().run(task=multimodal_message)
        
        # 提取结果
        analysis_result = ""
        if result and result.messages:
            last_message = result.messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
                if isinstance(content, str):
                    analysis_result = content
                elif isinstance(content, list):
                    text_parts = [item.get('text', str(item)) if isinstance(item, dict) else str(item) 
                                  for item in content]
                    analysis_result = '\n'.join(text_parts)
        
        # 清理资源
        await analyzer_team.cleanup()
        
        return ImageAnalysisResponse(
            result=analysis_result,
            conversation_id=conversation_id,
            status="success"
        )
    
    except Exception as e:
        print(f"❌ 图片分析错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")


@router.get("/health")
async def image_analysis_health():
    """
    图片分析服务健康检查
    
    返回:
        健康状态
    """
    return {
        "status": "healthy",
        "service": "image-analysis",
        "models": {
            "ui_expert": "UI-TARS-2B-BF16",
            "interaction_analyst": "UI-TARS-2B-BF16",
            "test_scenario_expert": "deepseek-chat"
        }
    }

