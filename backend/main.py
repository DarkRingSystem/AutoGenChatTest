"""
基于 AutoGen 0.7.5 和 SSE 流式传输的 FastAPI 后端

优雅的分层架构：
- config.py: 配置管理
- models.py: 数据模型
- services/: 业务逻辑层
  - ai_service.py: AI 智能体管理
  - stream_service.py: 流式处理
- api/: API 路由层
  - routes.py: 路由定义
- core/: 核心模块
  - dependencies.py: 依赖注入
"""
import warnings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 过滤 Pydantic 的 model_ 命名空间警告（来自 autogen 库）
warnings.filterwarnings(
    "ignore",
    message=".*has conflict with protected namespace \"model_\".*",
    category=UserWarning,
    module="pydantic._internal._fields"
)

from config import settings
from api.routes import router
from core.dependencies import initialize_services, cleanup_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    负责初始化和清理资源
    """
    # 启动时初始化服务
    await initialize_services()

    yield

    # 关闭时清理资源
    await cleanup_services()


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例

    返回:
        配置好的 FastAPI 应用
    """
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # 配置 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
        expose_headers=["X-Conversation-ID", "X-Team-Mode"],  # 允许前端读取自定义响应头
    )

    # 注册路由
    app.include_router(router)

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    # 显示配置信息
    settings.display_config()
    print()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
