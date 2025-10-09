"""
智能体模块
包含各种 AI 智能体的实现和工厂
"""
from .base_agent import BaseAgent, BaseTeamAgent
from .factory import AgentFactory, AgentType, AgentRegistry, get_agent_factory
from .chat_agent import ChatAgent

__all__ = [
    'BaseAgent',
    'BaseTeamAgent',
    'AgentFactory',
    'AgentType',
    'AgentRegistry',
    'get_agent_factory',
    'ChatAgent',
    'register_all_agents',
]


# 延迟导入以避免循环依赖
_agents_registered = False


def register_all_agents():
    """注册所有智能体类型到全局工厂"""
    global _agents_registered

    if _agents_registered:
        return

    factory = get_agent_factory()

    # 注册单智能体
    factory.register_agent(AgentType.CHAT, ChatAgent)

    # 延迟导入团队智能体（避免循环依赖）
    # from .image_analyzer_team import ImageAnalyzerTeam
    # factory.register_agent(AgentType.IMAGE_ANALYSIS_TEAM, ImageAnalyzerTeam)

    _agents_registered = True
    print("✅ 所有智能体类型已注册到工厂")

