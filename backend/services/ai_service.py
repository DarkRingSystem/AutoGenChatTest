"""
AI 服务模块
负责管理 AI 智能体的生命周期和交互
"""
from typing import Optional, List
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
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        self.agents: List[AssistantAgent] = []
        self.team: Optional[RoundRobinGroupChat] = None

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
        # 验证配置
        self.settings.validate_config()

        # 显示配置信息
        self.settings.display_config()

        # 创建模型信息（用于非官方模型）
        model_info = self._create_model_info()

        # 创建模型客户端
        self.model_client = OpenAIChatCompletionClient(
            model=self.settings.model_name,
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            model_info=model_info,
        )

        # 创建团队智能体
        self._create_team_agents(specific_agent)

        # 创建团队
        self._create_team()

        if specific_agent:
            print(f"✅ 测试用例 AI 团队初始化成功！只包含智能体: {specific_agent}")
        else:
            print(f"✅ 测试用例 AI 团队初始化成功！包含 {len(self.agents)} 个智能体")

    def _create_team_agents(self, specific_agent: Optional[str] = None) -> None:
        """
        创建测试用例团队中的多个智能体

        参数:
            specific_agent: 指定只创建某个智能体（可选）
        """
        # 创建测试用例生成智能体
        test_generator_agent = AssistantAgent(
            name="TestCase_Generator",
            model_client=self.model_client,
            system_message=load_prompt(PromptNames.TEST_CASE_GENERATOR),
            model_client_stream=self.settings.enable_streaming,
        )

        # 创建测试用例评审智能体
        test_reviewer_agent = AssistantAgent(
            name="TestCase_Reviewer",
            model_client=self.model_client,
            system_message=load_prompt(PromptNames.TEST_CASE_REVIEWER),
            model_client_stream=self.settings.enable_streaming,
        )

        # 创建测试用例优化智能体
        test_optimizer_agent = AssistantAgent(
            name="TestCase_Optimizer",
            model_client=self.model_client,
            system_message=load_prompt(PromptNames.TEST_CASE_OPTIMIZER),
            model_client_stream=self.settings.enable_streaming,
        )

        # 根据 specific_agent 决定包含哪些智能体
        if specific_agent == "TestCase_Generator":
            self.agents = [test_generator_agent]
            print(f"🎯 只创建 Generator 智能体")
        elif specific_agent == "TestCase_Reviewer":
            self.agents = [test_reviewer_agent]
            print(f"🎯 只创建 Reviewer 智能体")
        elif specific_agent == "TestCase_Optimizer":
            self.agents = [test_optimizer_agent]
            print(f"🎯 只创建 Optimizer 智能体")
        else:
            # 默认：Generator → Reviewer（不包含 Optimizer）
            self.agents = [test_generator_agent, test_reviewer_agent]
            print(f"🎯 创建 Generator 和 Reviewer 智能体")

    def _create_team(self) -> None:
        """创建团队（RoundRobinGroupChat）"""
        # 定义终止条件：
        # 1. 当 Reviewer 完成后停止，等待用户反馈
        # 2. 当 Optimizer 完成后停止（最终回答）
        # 3. 当指定智能体完成后停止（单智能体模式）

        # 获取团队中的智能体名称
        agent_names = [agent.name for agent in self.agents]

        print(f"🎯 创建团队，智能体: {agent_names}")

        # 根据团队组成动态设置终止条件
        if len(self.agents) == 1:
            # 单智能体模式：该智能体完成后立即停止
            single_agent_name = agent_names[0]
            print(f"   ✅ 单智能体模式，终止条件: {single_agent_name} 完成")
            termination_condition = SourceMatchTermination([single_agent_name])
        else:
            # 多智能体模式：Reviewer 或 Optimizer 完成后停止
            print(f"   ✅ 多智能体模式，终止条件: Reviewer 或 Optimizer 完成")
            reviewer_termination = SourceMatchTermination(["TestCase_Reviewer"])
            optimizer_termination = SourceMatchTermination(["TestCase_Optimizer"])
            termination_condition = reviewer_termination | optimizer_termination

        # 定义最大消息数终止条件（防止无限循环）
        max_message_termination = MaxMessageTermination(max_messages=20)

        # 创建轮询式团队聊天
        self.team = RoundRobinGroupChat(
            participants=self.agents,
            termination_condition=termination_condition | max_message_termination,
        )

    async def cleanup(self) -> None:
        """清理资源"""
        if self.model_client:
            await self.model_client.close()
            print("🧹 测试用例 AI 团队服务资源已清理")

    def _create_model_info(self) -> ModelInfo:
        """
        创建模型信息

        返回:
            ModelInfo 实例
        """
        return ModelInfo(
            vision=False,
            function_calling=False,
            json_output=True,
            structured_output=False,  # 添加 structured_output 字段
            family=self._get_model_family(),
        )

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

    def get_team(self) -> Optional[RoundRobinGroupChat]:
        """
        获取团队实例

        返回:
            RoundRobinGroupChat 实例或 None
        """
        return self.team

    def is_initialized(self) -> bool:
        """
        检查团队是否已初始化

        返回:
            True 如果已初始化，否则 False
        """
        return self.team is not None

    async def run(self, message: str):
        """
        运行团队（非流式）

        参数:
            message: 用户消息

        返回:
            团队运行结果
        """
        if not self.team:
            raise RuntimeError("团队未初始化")

        return await self.team.run(task=message)

    async def run_stream(self, message: str):
        """
        运行团队（流式）

        参数:
            message: 用户消息

        生成:
            团队事件流
        """
        if not self.team:
            raise RuntimeError("团队未初始化")

        async for event in self.team.run_stream(task=message):
            yield event

