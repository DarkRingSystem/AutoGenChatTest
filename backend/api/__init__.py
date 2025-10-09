"""
API 路由模块
整合所有子路由
"""
from fastapi import APIRouter
from api import (
    routes_home,
    routes_chat_normal,
    routes_chat_testcase,
    routes_image_analysis,
    routes_files
)

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(routes_home.router)
router.include_router(routes_chat_normal.router)
router.include_router(routes_chat_testcase.router)
router.include_router(routes_image_analysis.router)
router.include_router(routes_files.router)


# 根路径和健康检查
@router.get("/")
async def root():
    """API 根端点"""
    return {
        "message": "AutoGen Chat API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "home": "/api/home",
            "chat_normal": "/api/chat/normal",
            "chat_testcase": "/api/chat/testcase",
            "image_analysis": "/api/image-analysis",
            "files": "/api/files"
        }
    }


@router.get("/health")
async def health_check():
    """健康检查端点"""
    from core.dependencies import get_session_service

    session_service = get_session_service()
    session_count = await session_service.get_session_count()

    return {
        "status": "healthy",
        "version": "2.0.0",
        "session_count": session_count,
        "services": {
            "home": "active",
            "chat_normal": "active",
            "chat_testcase": "active",
            "image_analysis": "active",
            "files": "active"
        }
    }


__all__ = ['router']
