"""
playwright脚本生成智能体
基于autogen 消息机制实现工作流
图片分析团队将必要上下文发送给playwright_script_generate_agent主题
playwright_script_generate_agent订阅主题playwright_script_generate来获取消息
playwright_script_generate_agent调用llm生成playwright脚本并保存在服务器上
"""
from typing import Optional, Dict, Any, List, Union
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_agentchat.base import TaskResult
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import Image

from config import Settings
from core.llm_clients import get_uitars_model_client, get_default_model_client
from prompts.prompt_loader import load_prompt, PromptNames

class ImageAnalyzerTeam:
    """
    playwright脚本生成智能体

    """
    def __init__(self, settings: Optional[Settings] = None):