"""
测试用例团队智能体
包含 Generator、Reviewer、Optimizer 三个智能体的协作团队
"""
from typing import Optional, List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import SourceMatchTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

from agents.base_agent import BaseTeamAgent
from config import Settings
from prompts.prompt_loader import load_prompt, PromptNames


class TestCaseTeamAgent(BaseTeamAgent):
    """
    测试用例团队智能体
    
    团队成员：
    - TestCase_Generator: 生成测试用例
    - TestCase_Reviewer: 评审测试用例
    - TestCase_Optimizer: 优化测试用例
    
    工作流程：
    - 默认模式：Generator → Reviewer（等待用户反馈）
    - 单智能体模式：只运行指定的智能体
    - 优化模式：Generator → Reviewer → Optimizer
    """
    
    def __init__(
        self,
        name: str = "TestCaseTeam",
        settings: Optional[Settings] = None,
        specific_agent: Optional[str] = None,
    ):
        """
        初始化测试用例团队
        
        参数:
            name: 团队名称
            settings: 配置实例
            specific_agent: 指定只创建某个智能体（可选）
                          - None: 创建 Generator + Reviewer
                          - "TestCase_Generator": 只创建 Generator
                          - "TestCase_Reviewer": 只创建 Reviewer
                          - "TestCase_Optimizer": 只创建 Optimizer
        """
        super().__init__(name=name, settings=settings)
        self.specific_agent = specific_agent
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        
    async def initialize(self) -> None:
        """初始化测试用例团队"""
        print(f"🚀 正在初始化测试用例团队: {self.name}...")
        
        # 验证配置
        self.settings.validate_config()
        
        # 创建模型客户端
        self.model_client = self._create_model_client()
        
        # 调用父类的初始化方法
        await super().initialize()
        
        if self.specific_agent:
            print(f"✅ 测试用例团队初始化成功！只包含智能体: {self.specific_agent}")
        else:
            print(f"✅ 测试用例团队初始化成功！包含 {len(self.agents)} 个智能体")
    
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
    
    def create_team_members(self) -> List[AssistantAgent]:
        """
        创建团队成员
        
        返回:
            智能体列表
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
        if self.specific_agent == "TestCase_Generator":
            agents = [test_generator_agent]
            print(f"   🎯 只创建 Generator 智能体")
        elif self.specific_agent == "TestCase_Reviewer":
            agents = [test_reviewer_agent]
            print(f"   🎯 只创建 Reviewer 智能体")
        elif self.specific_agent == "TestCase_Optimizer":
            agents = [test_optimizer_agent]
            print(f"   🎯 只创建 Optimizer 智能体")
        else:
            # 默认：Generator → Reviewer（不包含 Optimizer）
            agents = [test_generator_agent, test_reviewer_agent]
            print(f"   🎯 创建 Generator 和 Reviewer 智能体")
        
        return agents
    
    def create_team_workflow(self) -> RoundRobinGroupChat:
        """
        创建团队工作流
        
        返回:
            RoundRobinGroupChat 实例
        """
        # 获取团队中的智能体名称
        agent_names = [agent.name for agent in self.agents]
        
        print(f"   🎯 创建团队工作流，智能体: {agent_names}")
        
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
        team = RoundRobinGroupChat(
            participants=self.agents,
            termination_condition=termination_condition | max_message_termination,
        )
        
        return team
    
    def get_agent_type(self) -> str:
        """
        获取智能体类型
        
        返回:
            智能体类型标识符
        """
        return "testcase_team"
    
    async def run(self, task: str):
        """
        运行团队任务（非流式）
        
        参数:
            task: 任务描述
            
        返回:
            团队执行结果
        """
        if self.team is None:
            raise RuntimeError("团队未初始化，请先调用 initialize()")
        
        result = await self.team.run(task=task)
        return result
    
    async def run_stream(self, task: str):
        """
        运行团队任务（流式）
        
        参数:
            task: 任务描述
            
        返回:
            流式响应生成器
        """
        if self.team is None:
            raise RuntimeError("团队未初始化，请先调用 initialize()")
        
        async for chunk in self.team.run_stream(task=task):
            yield chunk
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self.model_client:
            try:
                await self.model_client.close()
                print(f"🧹 {self.name} 模型客户端已清理")
            except Exception as e:
                print(f"⚠️ 清理 {self.name} 模型客户端时出错: {e}")
        
        # 调用父类的清理方法
        await super().cleanup()

