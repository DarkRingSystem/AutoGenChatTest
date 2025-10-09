"""
普通对话智能体
用于简单的问答对话场景
"""
from typing import Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

from agents.base_agent import BaseAgent
from config import Settings
from prompts.prompt_loader import load_prompt, PromptNames


class ChatAgent(BaseAgent):
    """
    普通对话智能体
    
    用于简单的一对一对话场景
    """
    
    def __init__(
        self,
        name: str = "assistant",
        settings: Optional[Settings] = None,
        model_client: Optional[OpenAIChatCompletionClient] = None,
        system_message: Optional[str] = None,
    ):
        """
        初始化对话智能体
        
        参数:
            name: 智能体名称
            settings: 配置实例
            model_client: 模型客户端（可选）
            system_message: 系统提示词（可选）
        """
        super().__init__(
            name=name,
            settings=settings,
            model_client=model_client,
            system_message=system_message
        )
        
    async def initialize(self) -> None:
        """初始化对话智能体"""
        print(f"🚀 正在初始化对话智能体: {self.name}...")
        
        # 验证配置
        self.settings.validate_config()
        
        # 如果没有提供模型客户端，则创建一个
        if self.model_client is None:
            self.model_client = self._create_model_client()
        
        # 如果没有提供系统提示词，则加载默认的
        if self.system_message is None:
            self.system_message = load_prompt(PromptNames.ASSISTANT)
        
        # 创建 AutoGen 智能体
        self.agent = AssistantAgent(
            name=self.name,
            model_client=self.model_client,
            system_message=self.system_message,
            model_client_stream=self.settings.enable_streaming,
        )
        
        print(f"✅ 对话智能体 {self.name} 初始化成功！")
    
    def _create_model_client(self) -> OpenAIChatCompletionClient:
        """
        创建模型客户端
        
        返回:
            OpenAIChatCompletionClient 实例
        """
        # 创建模型信息
        model_info = ModelInfo(
            vision=False,
            function_calling=False,
            json_output=True,
            structured_output=False,
            family=self._get_model_family(),
        )
        
        # 创建模型客户端
        client = OpenAIChatCompletionClient(
            model=self.settings.model_name,
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            model_info=model_info,
        )
        
        print(f"   ✓ 模型客户端已创建: {self.settings.model_name}")
        
        return client
    
    def _get_model_family(self) -> str:
        """
        获取模型家族名称
        
        返回:
            模型家族名称
        """
        model_name_lower = self.settings.model_name.lower()
        
        if "deepseek" in model_name_lower:
            return "deepseek"
        elif "gpt" in model_name_lower:
            return "openai"
        elif "claude" in model_name_lower:
            return "anthropic"
        else:
            return "unknown"
    
    def get_agent_type(self) -> str:
        """
        获取智能体类型
        
        返回:
            智能体类型标识符
        """
        return "chat"
    
    async def run(self, message: str):
        """
        运行对话（非流式）
        
        参数:
            message: 用户消息
            
        返回:
            智能体的响应
        """
        if self.agent is None:
            raise RuntimeError("智能体未初始化，请先调用 initialize()")
        
        result = await self.agent.run(task=message)
        return result
    
    async def run_stream(self, message: str):
        """
        运行对话（流式）
        
        参数:
            message: 用户消息
            
        返回:
            流式响应生成器
        """
        if self.agent is None:
            raise RuntimeError("智能体未初始化，请先调用 initialize()")
        
        async for chunk in self.agent.run_stream(task=message):
            yield chunk

