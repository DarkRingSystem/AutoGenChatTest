"""
LLM 模型客户端管理模块
提供各种 LLM 模型客户端的创建和管理功能
支持 UI 自动化、图像分析等多种场景
"""
from typing import Optional
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from config import Settings

# 全局模型客户端缓存
_deepseek_model_client: Optional[OpenAIChatCompletionClient] = None
_uitars_model_client: Optional[OpenAIChatCompletionClient] = None
_qwen_vl_least_client: Optional[OpenAIChatCompletionClient] = None


# default为deepseek-chat
_default_model_client: Optional[OpenAIChatCompletionClient] = None


async def deepseek_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient:
    """
    获取 DeepSeek 模型客户端，用于通用对话和文本处理

    参数:
        settings: 配置实例，如果为 None 则使用全局配置

    返回:
        OpenAIChatCompletionClient 实例
    """
    global _deepseek_model_client
    if _deepseek_model_client is None:
        if settings is None:
            from config import settings as global_settings
            settings = global_settings

        # 从配置中获取 DeepSeek 模型信息
        deepseek_model = getattr(settings, 'deepseek_model', 'deepseek-chat')
        deepseek_api_key = getattr(settings, 'deepseek_api_key', settings.api_key)
        deepseek_base_url = getattr(settings, 'deepseek_base_url', settings.base_url)


        _deepseek_model_client = OpenAIChatCompletionClient(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url, 
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True,
                "family": "deepseek",
                "multiple_system_messages": True,
            },
        )
        print(f"✅ DeepSeek 模型客户端已创建成功")

    return _deepseek_model_client


async def uitars_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient:
    """
    获取 UI-TARS 模型客户端，用于 UI 自动化和图像分析

    参数:
        settings: 配置实例，如果为 None 则使用全局配置

    返回:
        OpenAIChatCompletionClient 实例
    """
    global _uitars_model_client

    if _uitars_model_client is None:
        if settings is None:
            from config import settings as global_settings
            settings = global_settings

        # 从配置中获取 UI-TARS 模型信息
        uitars_model = getattr(settings, 'uitars_model', 'gpt-4o')
        uitars_api_key = getattr(settings, 'uitars_api_key', settings.api_key)
        uitars_base_url = getattr(settings, 'uitars_base_url', settings.base_url)

        # 调试信息
        print(f"\n🔍 UI-TARS 模型配置:")
        print(f"   模型: {uitars_model}")
        print(f"   API Key: {uitars_api_key[:20]}...{uitars_api_key[-10:] if uitars_api_key and len(uitars_api_key) > 30 else uitars_api_key}")
        print(f"   Base URL: {uitars_base_url}")

        _uitars_model_client = OpenAIChatCompletionClient(
            model=uitars_model,
            api_key=uitars_api_key,
            base_url=uitars_base_url,
            model_info={
                "vision": True,
                "function_calling": True,
                "json_output": True,
                "structured_output": True,
                "family": "unknown",
                "multiple_system_messages": True,
            },
        )
        print(f"✅ UI-TARS 模型客户端已创建成功")

    return _uitars_model_client


async def qwen_vl_least_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient:
    """
    获取千问视觉模型，用于图像理解和分析

    参数:
        settings: 配置实例，如果为 None 则使用全局配置

    返回:
        OpenAIChatCompletionClient 实例
    """
    global _qwen_vl_least_client

    if _qwen_vl_least_client is None:
        if settings is None:
            from config import settings as global_settings
            settings = global_settings

        # 从配置中获取视觉模型信息
        qwen_vl_least_model = getattr(settings, 'qwen_vl_least_model', settings.model_name)
        qwen_vl_least_api_key = getattr(settings, 'qwen_vl_least_api_key', settings.api_key)
        qwen_vl_least_base_url = getattr(settings, 'qwen_vl_least_base_url', settings.base_url)

        _qwen_vl_least_client = OpenAIChatCompletionClient(
            model=qwen_vl_least_model,
            api_key=qwen_vl_least_api_key,
            base_url=qwen_vl_least_base_url,
            model_info={
                "vision": True,
                "function_calling": True,
                "json_output": True,
                "structured_output": False,
                "family": await _get_model_family(qwen_vl_least_model),
                "multiple_system_messages": True,
            },
        )
        print(f"✅ 千问视觉模型客户端已创建: {qwen_vl_least_model}")

    return _qwen_vl_least_client


async def default_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient:
    """
    获取默认模型客户端，用于通用对话和文本处理

    参数:
        settings: 配置实例，如果为 None 则使用全局配置

    返回:
        OpenAIChatCompletionClient 实例
    """
    global _default_model_client

    if _default_model_client is None:
        if settings is None:
            from config import settings as global_settings
            settings = global_settings

        _default_model_client = OpenAIChatCompletionClient(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": False,
                "family": await _get_model_family(settings.model_name),
                "multiple_system_messages": True,
            },
        )
        print(f"✅ 默认模型客户端已创建: {settings.model_name}")

    return _default_model_client


def get_default_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient:
    """
    同步获取默认模型客户端（用于兼容性）

    参数:
        settings: 配置实例，如果为 None 则使用全局配置

    返回:
        OpenAIChatCompletionClient 实例
    """
    if settings is None:
        from config import settings as global_settings
        settings = global_settings

    return OpenAIChatCompletionClient(
        model=settings.model_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": False,
            "family": "deepseek",  # 简化处理
            "multiple_system_messages": True,
        },
    )


async def _get_model_family(model_name: Optional[str]) -> str:
    """
    根据模型名称推断模型家族

    参数:
        model_name: 模型名称，可以为 None

    返回:
        模型家族名称
    """
    if model_name is None:
        return "unknown"

    model_name_lower = model_name.lower()

    if "deepseek" in model_name_lower:
        return "deepseek"
    elif "gpt" in model_name_lower or "openai" in model_name_lower:
        return "openai"
    elif "claude" in model_name_lower:
        return "anthropic"
    elif "gemini" in model_name_lower:
        return "google"
    elif "qwen" in model_name_lower:
        return "qwen"
    elif "doubao" in model_name_lower or "ui-tars" in model_name_lower:
        return "doubao"
    else:
        return "unknown"


async def reset_model_clients() -> None:
    """
    重置所有模型客户端缓存
    用于配置更新后重新初始化客户端
    """
    global _uitars_model_client, _qwen_vl_least_client, _default_model_client, _deepseek_model_client

    _uitars_model_client = None
    _qwen_vl_least_client = None
    _default_model_client = None
    _deepseek_model_client = None

    print("🔄 所有模型客户端缓存已重置")

