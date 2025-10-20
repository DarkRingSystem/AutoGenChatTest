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
    import asyncio

    # 启动时初始化服务
    await initialize_services()

    try:
        yield
    finally:
        # 关闭时清理资源
        print("🔄 开始应用关闭流程...")

        try:
            # 给清理过程更多时间
            await asyncio.wait_for(cleanup_services(), timeout=10.0)
        except asyncio.TimeoutError:
            print("⚠️ 服务清理超时，强制关闭")
        except asyncio.CancelledError:
            print("⚠️ 服务清理被取消")
        except Exception as e:
            print(f"⚠️ 服务清理过程中出错: {e}")

        # 等待所有挂起的任务完成（排除当前任务和系统任务）
        try:
            current_task = asyncio.current_task()
            pending_tasks = [
                task for task in asyncio.all_tasks()
                if not task.done() and task is not current_task
            ]
            if pending_tasks:
                print(f"⏳ 等待 {len(pending_tasks)} 个挂起任务完成...")
                # 使用 wait 而不是 gather，这样可以更好地处理取消
                done, pending = await asyncio.wait(
                    pending_tasks,
                    timeout=2.0,  # 减少超时时间
                    return_when=asyncio.ALL_COMPLETED
                )
                if pending:
                    # 不打印警告，直接取消剩余任务
                    for task in pending:
                        task.cancel()
                    # 给一点时间让任务响应取消
                    await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            pass  # 超时是正常的，不需要警告
        except asyncio.CancelledError:
            pass  # 取消是正常的，不需要警告
        except Exception as e:
            # 只在真正的错误时打印
            if not isinstance(e, (asyncio.TimeoutError, asyncio.CancelledError)):
                print(f"⚠️ 等待任务完成时出错: {e}")

        print("✅ 应用关闭流程完成")


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
        expose_headers=["X-Conversation-ID", "X-Team-Mode", "x-session-id"],  # 允许前端读取自定义响应头
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
