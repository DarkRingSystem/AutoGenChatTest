"""
智能体基类
定义所有智能体的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from config import Settings


class BaseAgent(ABC):
    """
    智能体基类
    
    所有智能体都应该继承此类并实现必要的方法
    """
    
    def __init__(
        self,
        name: str,
        settings: Optional[Settings] = None,
        model_client: Optional[OpenAIChatCompletionClient] = None,
        system_message: Optional[str] = None,
    ):
        """
        初始化智能体
        
        参数:
            name: 智能体名称
            settings: 配置实例
            model_client: 模型客户端（可选，如果不提供则需要子类创建）
            system_message: 系统提示词（可选，如果不提供则需要子类提供）
        """
        if settings is None:
            from config import settings as global_settings
            settings = global_settings
            
        self.name = name
        self.settings = settings
        self.model_client = model_client
        self.system_message = system_message
        self.agent: Optional[AssistantAgent] = None
        
    @abstractmethod
    async def initialize(self) -> None:
        """
        初始化智能体
        
        子类必须实现此方法来创建 AutoGen 智能体实例
        """
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """
        获取智能体类型
        
        返回:
            智能体类型标识符（如 "chat", "testcase_generator" 等）
        """
        pass
    
    def get_agent(self) -> Optional[AssistantAgent]:
        """
        获取 AutoGen 智能体实例
        
        返回:
            AssistantAgent 实例
        """
        return self.agent
    
    def get_name(self) -> str:
        """
        获取智能体名称
        
        返回:
            智能体名称
        """
        return self.name
    
    async def cleanup(self) -> None:
        """
        清理资源
        
        子类可以重写此方法来清理特定资源
        """
        if self.model_client:
            try:
                await self.model_client.close()
                print(f"🧹 {self.name} 资源已清理")
            except Exception as e:
                print(f"⚠️ {self.name} 清理资源时出错: {e}")
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.get_agent_type()}')"


class BaseTeamAgent(BaseAgent):
    """
    团队智能体基类
    
    用于需要多个智能体协作的场景
    """
    
    def __init__(
        self,
        name: str,
        settings: Optional[Settings] = None,
    ):
        """
        初始化团队智能体
        
        参数:
            name: 团队名称
            settings: 配置实例
        """
        super().__init__(name=name, settings=settings)
        self.agents: List[AssistantAgent] = []
        self.team: Optional[Any] = None
        
    @abstractmethod
    def create_team_members(self) -> List[AssistantAgent]:
        """
        创建团队成员
        
        子类必须实现此方法来创建团队中的所有智能体
        
        返回:
            智能体列表
        """
        pass
    
    @abstractmethod
    def create_team_workflow(self) -> Any:
        """
        创建团队工作流
        
        子类必须实现此方法来定义团队协作流程
        可以返回 RoundRobinGroupChat, GraphFlow 等
        
        返回:
            团队工作流实例
        """
        pass
    
    async def initialize(self) -> None:
        """
        初始化团队智能体
        
        创建团队成员和工作流
        """
        print(f"🚀 正在初始化团队: {self.name}...")
        
        # 创建团队成员
        self.agents = self.create_team_members()
        print(f"   ✓ 已创建 {len(self.agents)} 个团队成员")
        
        # 创建团队工作流
        self.team = self.create_team_workflow()
        print(f"   ✓ 团队工作流已创建")
        
        print(f"✅ 团队 {self.name} 初始化成功！")
    
    def get_team(self) -> Optional[Any]:
        """
        获取团队工作流实例
        
        返回:
            团队工作流实例
        """
        return self.team
    
    def get_team_members(self) -> List[AssistantAgent]:
        """
        获取团队成员列表
        
        返回:
            智能体列表
        """
        return self.agents
    
    async def cleanup(self) -> None:
        """
        清理团队资源
        """
        # 清理所有团队成员的模型客户端
        for agent in self.agents:
            if hasattr(agent, 'model_client') and agent.model_client:
                try:
                    await agent.model_client.close()
                except Exception as e:
                    print(f"⚠️ 清理 {agent.name} 资源时出错: {e}")
        
        print(f"🧹 团队 {self.name} 资源已清理")

