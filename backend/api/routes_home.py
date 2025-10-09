"""
首页相关路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/home", tags=["home"])


@router.get("/")
async def home():
    """首页信息"""
    return {
        "message": "AutoGen Chat Application",
        "version": "1.0.0",
        "modes": [
            {
                "id": "normal",
                "name": "普通对话",
                "description": "与 AI 进行自然对话，支持文件上传",
                "path": "/chat/normal",
                "icon": "message"
            },
            {
                "id": "testcase",
                "name": "测试用例生成",
                "description": "智能体团队协作生成高质量测试用例",
                "path": "/chat/testcase",
                "icon": "experiment"
            },
            {
                "id": "image-analysis",
                "name": "图片分析",
                "description": "UI 界面分析和测试用例生成",
                "path": "/image-analysis",
                "icon": "picture"
            }
        ]
    }


@router.get("/stats")
async def get_stats():
    """获取应用统计信息"""
    from core.dependencies import get_session_service
    
    session_service = get_session_service()
    session_count = await session_service.get_session_count()
    
    return {
        "total_sessions": session_count,
        "active_modes": 3,
        "uptime": "running"
    }

