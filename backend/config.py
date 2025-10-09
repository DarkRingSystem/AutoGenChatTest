"""
配置管理模块
负责加载和管理应用配置
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置类"""

    # API 配置
    api_key: str
    model_name: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/v1"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"

    # 应用配置
    app_title: str = "AutoGen 聊天 API"
    app_description: str = "基于 AutoGen 0.7.5 和 SSE 流式传输的 FastAPI 后端"
    app_version: str = "1.0.0"

    # CORS 配置
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # AI 模型配置
    system_message: str = "你是一个有帮助的 AI 助手。请提供清晰、简洁和准确的回答。"
    enable_streaming: bool = True

    # UI-TARS 模型配置（用于 UI 自动化和图像分析）
    uitars_model: str = "doubao-1-5-ui-tars-250428"
    uitars_api_key: Optional[str] = "0e58effd-fe97-4809-91ee-a631585d0ac2"# 如果为 None，使用默认 api_key
    uitars_base_url: Optional[str] = "https://ark.cn-beijing.volces.com/api/v3"  # 如果为 None，使用默认 base_url

    # 视觉模型配置（用于图像理解）
    vision_model: Optional[str] = None  # 如果为 None，使用默认 model_name
    vision_api_key: Optional[str] = None  # 如果为 None，使用默认 api_key
    vision_base_url: Optional[str] = None  # 如果为 None，使用默认 base_url

    # Markdown 转换配置 (Marker)
    markdown_use_llm: bool = False
    markdown_force_ocr: bool = False
    markdown_disable_image_extraction: bool = False
    markdown_output_format: str = "markdown"
    markdown_max_file_size_mb: int = 100
    markdown_max_batch_files: int = 10
    markdown_max_concurrent: int = 3

    # Markdown LLM 配置（可选，用于提升转换精度）
    markdown_llm_service: Optional[str] = None
    markdown_llm_api_key: Optional[str] = None
    markdown_llm_base_url: Optional[str] = None
    markdown_llm_model: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        # 解决 model_name 与 Pydantic 保护命名空间冲突
        protected_namespaces = ()
        
    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量创建配置实例

        注意：Pydantic Settings 会自动从环境变量读取配置
        环境变量名会自动转换：markdown_use_llm -> MARKDOWN_USE_LLM
        这个方法主要用于兼容旧代码，实际上可以直接使用 Settings()
        """
        # Pydantic Settings 会自动读取所有环境变量
        # 只需要传入必需的参数（没有默认值的）
        return cls(
            api_key=os.getenv("API_KEY", ""),
        )
    
    def validate_config(self) -> None:
        """验证配置"""
        if not self.api_key:
            raise ValueError("API_KEY 环境变量未设置，请在 .env 文件中配置")
    
    def display_config(self) -> None:
        """显示配置信息"""
        print(f"🚀 正在初始化 AI 模型...")
        print(f"   模型: {self.model_name}")
        print(f"   API: {self.base_url}")
        print(f"   服务器: {self.host}:{self.port}")
        print(f"\n📄 Markdown 转换配置:")
        print(f"   使用 LLM: {self.markdown_use_llm}")
        print(f"   强制 OCR: {self.markdown_force_ocr}")
        print(f"   禁用图片提取: {self.markdown_disable_image_extraction}")
        print(f"   输出格式: {self.markdown_output_format}")
        print(f"   最大文件大小: {self.markdown_max_file_size_mb}MB")
        print(f"   批量处理最大文件数: {self.markdown_max_batch_files}")
        print(f"   最大并发数: {self.markdown_max_concurrent}")


# 全局配置实例
settings = Settings.from_env()

