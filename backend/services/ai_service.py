"""
AI 服务模块
负责管理 AI 智能体的生命周期和交互
"""
from typing import Optional, List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination, SourceMatchTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._model_info import ModelInfo

from config import Settings
from prompts.prompt_loader import load_prompt, PromptNames
from agents.factory import get_agent_factory, AgentType
from agents.chat_agent import ChatAgent
from agents import register_all_agents


class AIService:
    """AI 服务类，管理 AutoGen 智能体"""

    def __init__(self, settings: Settings):
        """
        初始化 AI 服务

        参数:
            settings: 应用配置
        """
        self.settings = settings
        self.chat_agent: Optional[ChatAgent] = None
        self.factory = get_agent_factory(settings)

    async def initialize(self) -> None:
        """初始化 AI 智能体"""
        # 注册所有智能体类型
        register_all_agents()

        # 显示配置信息
        self.settings.display_config()

        # 使用工厂创建对话智能体
        self.chat_agent = await self.factory.create_agent(
            agent_type=AgentType.CHAT,
            name="assistant",
            cache_key="default_chat_agent"
        )

        print(f"✅ AI 服务初始化成功！")

    async def cleanup(self) -> None:
        """清理资源"""
        if self.chat_agent:
            await self.chat_agent.cleanup()
            self.factory.remove_cached_agent("default_chat_agent")
            print("🧹 AI 服务资源已清理")

    def get_agent(self) -> Optional[AssistantAgent]:
        """
        获取智能体实例

        返回:
            AssistantAgent 实例或 None
        """
        if self.chat_agent:
            return self.chat_agent.get_agent()
        return None

    def is_initialized(self) -> bool:
        """
        检查智能体是否已初始化

        返回:
            True 如果已初始化，否则 False
        """
        return self.chat_agent is not None and self.chat_agent.get_agent() is not None
    
    async def run(self, message: str):
        """
        运行智能体（非流式）
        
        参数:
            message: 用户消息
            
        返回:
            智能体运行结果
        """
        if not self.agent:
            raise RuntimeError("智能体未初始化")
        
        return await self.agent.run(task=message)
    
    async def run_stream(self, message: str):
        """
        运行智能体（流式）
        
        参数:
            message: 用户消息
            
        生成:
            智能体事件流
        """
        if not self.agent:
            raise RuntimeError("智能体未初始化")

        async for event in self.agent.run_stream(task=message):
            yield event


class TestCasesTeamAIService:
    """测试用例团队 AI 服务类，管理多个智能体协作生成和审查测试用例"""

    def __init__(self, settings: Settings):
        """
        初始化测试用例团队 AI 服务

        参数:
            settings: 应用配置
        """
        self.settings = settings
        self.team_agent: Optional[Any] = None
        self.factory = get_agent_factory(settings)

    async def initialize(self, specific_agent: Optional[str] = None) -> None:
        """
        初始化测试用例 AI 团队

        参数:
            specific_agent: 指定只初始化某个智能体（可选）
                          - None: 初始化所有智能体（Generator → Reviewer）
                          - "TestCase_Generator": 只初始化 Generator
                          - "TestCase_Reviewer": 只初始化 Reviewer
                          - "TestCase_Optimizer": 只初始化 Optimizer
        """
        # 注册所有智能体类型
        register_all_agents()

        # 显示配置信息
        self.settings.display_config()

        # 使用工厂创建测试用例团队智能体
        self.team_agent = await self.factory.create_agent(
            agent_type=AgentType.TESTCASE_TEAM,
            name="TestCaseTeam",
            specific_agent=specific_agent,
            # 不使用缓存，因为每次可能需要不同的 specific_agent 配置
        )

        print(f"✅ 测试用例团队服务初始化成功！")

    async def cleanup(self) -> None:
        """清理资源"""
        if self.team_agent:
            await self.team_agent.cleanup()
            print("🧹 测试用例团队服务资源已清理")

    def get_team(self) -> Optional[Any]:
        """
        获取团队实例

        返回:
            团队工作流实例或 None
        """
        if self.team_agent:
            return self.team_agent.get_team()
        return None

    def is_initialized(self) -> bool:
        """
        检查团队是否已初始化

        返回:
            True 如果已初始化，否则 False
        """
        return self.team_agent is not None and self.team_agent.get_team() is not None

    async def run(self, message: str):
        """
        运行团队（非流式）

        参数:
            message: 用户消息

        返回:
            团队运行结果
        """
        if not self.team_agent:
            raise RuntimeError("团队未初始化")

        return await self.team_agent.run(task=message)

    async def run_stream(self, message: str):
        """
        运行团队（流式）

        参数:
            message: 用户消息

        生成:
            团队事件流
        """
        if not self.team_agent:
            raise RuntimeError("团队未初始化")

        async for event in self.team_agent.run_stream(task=message):
            yield event

