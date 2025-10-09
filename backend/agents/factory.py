"""
智能体工厂
负责创建、注册和管理所有智能体
"""
from typing import Dict, Type, Optional, Any, List
from enum import Enum

from agents.base_agent import BaseAgent, BaseTeamAgent
from config import Settings


class AgentType(Enum):
    """智能体类型枚举"""
    # 单智能体类型
    CHAT = "chat"                           # 普通对话智能体
    TESTCASE_GENERATOR = "testcase_generator"   # 测试用例生成器
    TESTCASE_REVIEWER = "testcase_reviewer"     # 测试用例评审员
    TESTCASE_OPTIMIZER = "testcase_optimizer"   # 测试用例优化器
    
    # 团队智能体类型
    TESTCASE_TEAM = "testcase_team"         # 测试用例团队
    IMAGE_ANALYSIS_TEAM = "image_analysis_team"  # 图片分析团队


class AgentRegistry:
    """
    智能体注册表
    
    管理所有可用的智能体类型及其对应的类
    """
    
    def __init__(self):
        """初始化注册表"""
        self._registry: Dict[AgentType, Type[BaseAgent]] = {}
        
    def register(self, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """
        注册智能体类型
        
        参数:
            agent_type: 智能体类型
            agent_class: 智能体类
        """
        if agent_type in self._registry:
            print(f"⚠️ 智能体类型 {agent_type.value} 已存在，将被覆盖")
        
        self._registry[agent_type] = agent_class
        print(f"✅ 已注册智能体类型: {agent_type.value} -> {agent_class.__name__}")
        
    def get(self, agent_type: AgentType) -> Optional[Type[BaseAgent]]:
        """
        获取智能体类
        
        参数:
            agent_type: 智能体类型
            
        返回:
            智能体类，如果不存在则返回 None
        """
        return self._registry.get(agent_type)
    
    def list_types(self) -> List[AgentType]:
        """
        列出所有已注册的智能体类型
        
        返回:
            智能体类型列表
        """
        return list(self._registry.keys())
    
    def is_registered(self, agent_type: AgentType) -> bool:
        """
        检查智能体类型是否已注册
        
        参数:
            agent_type: 智能体类型
            
        返回:
            是否已注册
        """
        return agent_type in self._registry


class AgentFactory:
    """
    智能体工厂
    
    负责创建、管理和编排智能体
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        初始化工厂
        
        参数:
            settings: 配置实例
        """
        if settings is None:
            from config import settings as global_settings
            settings = global_settings
            
        self.settings = settings
        self.registry = AgentRegistry()
        self._agent_cache: Dict[str, BaseAgent] = {}  # 智能体缓存
        
    def register_agent(self, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """
        注册智能体类型
        
        参数:
            agent_type: 智能体类型
            agent_class: 智能体类
        """
        self.registry.register(agent_type, agent_class)
    
    async def create_agent(
        self,
        agent_type: AgentType,
        name: Optional[str] = None,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> BaseAgent:
        """
        创建智能体实例
        
        参数:
            agent_type: 智能体类型
            name: 智能体名称（可选，默认使用类型名称）
            cache_key: 缓存键（可选，如果提供则会缓存实例）
            **kwargs: 传递给智能体构造函数的额外参数
            
        返回:
            智能体实例
            
        异常:
            ValueError: 如果智能体类型未注册
        """
        # 检查缓存
        if cache_key and cache_key in self._agent_cache:
            print(f"💾 从缓存获取智能体: {cache_key}")
            return self._agent_cache[cache_key]
        
        # 获取智能体类
        agent_class = self.registry.get(agent_type)
        if agent_class is None:
            raise ValueError(f"智能体类型 {agent_type.value} 未注册")
        
        # 创建智能体实例
        if name is None:
            name = agent_type.value
            
        print(f"🏭 创建智能体: {name} (类型: {agent_type.value})")
        
        agent = agent_class(
            name=name,
            settings=self.settings,
            **kwargs
        )
        
        # 初始化智能体
        await agent.initialize()
        
        # 缓存智能体
        if cache_key:
            self._agent_cache[cache_key] = agent
            print(f"💾 已缓存智能体: {cache_key}")
        
        return agent
    
    def get_cached_agent(self, cache_key: str) -> Optional[BaseAgent]:
        """
        获取缓存的智能体
        
        参数:
            cache_key: 缓存键
            
        返回:
            智能体实例，如果不存在则返回 None
        """
        return self._agent_cache.get(cache_key)
    
    def remove_cached_agent(self, cache_key: str) -> None:
        """
        移除缓存的智能体
        
        参数:
            cache_key: 缓存键
        """
        if cache_key in self._agent_cache:
            del self._agent_cache[cache_key]
            print(f"🗑️ 已移除缓存的智能体: {cache_key}")
    
    async def cleanup_agent(self, cache_key: str) -> None:
        """
        清理并移除缓存的智能体
        
        参数:
            cache_key: 缓存键
        """
        agent = self.get_cached_agent(cache_key)
        if agent:
            await agent.cleanup()
            self.remove_cached_agent(cache_key)
    
    async def cleanup_all(self) -> None:
        """清理所有缓存的智能体"""
        print("🧹 清理所有缓存的智能体...")
        for cache_key in list(self._agent_cache.keys()):
            await self.cleanup_agent(cache_key)
        print("✅ 所有智能体已清理")
    
    def list_registered_types(self) -> List[AgentType]:
        """
        列出所有已注册的智能体类型
        
        返回:
            智能体类型列表
        """
        return self.registry.list_types()
    
    def list_cached_agents(self) -> List[str]:
        """
        列出所有缓存的智能体键
        
        返回:
            缓存键列表
        """
        return list(self._agent_cache.keys())


# 全局工厂实例
_global_factory: Optional[AgentFactory] = None


def get_agent_factory(settings: Optional[Settings] = None) -> AgentFactory:
    """
    获取全局智能体工厂实例
    
    参数:
        settings: 配置实例
        
    返回:
        AgentFactory 实例
    """
    global _global_factory
    
    if _global_factory is None:
        _global_factory = AgentFactory(settings)
        print("🏭 全局智能体工厂已创建")
    
    return _global_factory

