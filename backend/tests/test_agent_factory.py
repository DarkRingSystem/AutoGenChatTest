"""
智能体工厂测试
验证工厂模式的基本功能
"""
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from typing import Optional
from autogen_agentchat.agents import AssistantAgent

from agents.base_agent import BaseAgent
from agents.factory import AgentFactory, AgentType, get_agent_factory
from config import settings


class MockChatAgent(BaseAgent):
    """模拟的聊天智能体（用于测试）"""
    
    async def initialize(self) -> None:
        """初始化智能体"""
        print(f"   初始化 MockChatAgent: {self.name}")
        # 这里不创建真实的 AutoGen 智能体，只是模拟
        self.agent = None  # 在真实实现中会创建 AssistantAgent
        
    def get_agent_type(self) -> str:
        """获取智能体类型"""
        return "chat"


async def test_factory_basic():
    """测试工厂基本功能"""
    print("\n" + "="*60)
    print("测试 1: 工厂基本功能")
    print("="*60)
    
    # 创建工厂
    factory = AgentFactory(settings)
    print("✅ 工厂创建成功")
    
    # 注册智能体类型
    factory.register_agent(AgentType.CHAT, MockChatAgent)
    print("✅ 智能体类型注册成功")
    
    # 列出已注册的类型
    registered_types = factory.list_registered_types()
    print(f"✅ 已注册的智能体类型: {[t.value for t in registered_types]}")
    
    # 创建智能体
    agent = await factory.create_agent(
        agent_type=AgentType.CHAT,
        name="test_chat_agent",
        cache_key="test_chat_1"
    )
    print(f"✅ 智能体创建成功: {agent}")
    
    # 从缓存获取智能体
    cached_agent = factory.get_cached_agent("test_chat_1")
    assert cached_agent is agent, "缓存的智能体应该是同一个实例"
    print("✅ 缓存功能正常")
    
    # 列出缓存的智能体
    cached_keys = factory.list_cached_agents()
    print(f"✅ 缓存的智能体: {cached_keys}")
    
    # 清理智能体
    await factory.cleanup_agent("test_chat_1")
    assert factory.get_cached_agent("test_chat_1") is None, "智能体应该已被清理"
    print("✅ 清理功能正常")
    
    print("\n✅ 测试 1 通过！\n")


async def test_global_factory():
    """测试全局工厂实例"""
    print("\n" + "="*60)
    print("测试 2: 全局工厂实例")
    print("="*60)
    
    # 获取全局工厂
    factory1 = get_agent_factory()
    factory2 = get_agent_factory()
    
    assert factory1 is factory2, "全局工厂应该是单例"
    print("✅ 全局工厂单例模式正常")
    
    print("\n✅ 测试 2 通过！\n")


async def test_agent_creation_without_cache():
    """测试不使用缓存创建智能体"""
    print("\n" + "="*60)
    print("测试 3: 不使用缓存创建智能体")
    print("="*60)
    
    factory = AgentFactory(settings)
    factory.register_agent(AgentType.CHAT, MockChatAgent)
    
    # 创建智能体但不缓存
    agent1 = await factory.create_agent(
        agent_type=AgentType.CHAT,
        name="agent_1"
    )
    
    agent2 = await factory.create_agent(
        agent_type=AgentType.CHAT,
        name="agent_2"
    )
    
    assert agent1 is not agent2, "不使用缓存时应该创建不同的实例"
    print("✅ 不使用缓存时创建不同实例")
    
    # 清理
    await agent1.cleanup()
    await agent2.cleanup()
    
    print("\n✅ 测试 3 通过！\n")


async def test_unregistered_agent_type():
    """测试创建未注册的智能体类型"""
    print("\n" + "="*60)
    print("测试 4: 创建未注册的智能体类型")
    print("="*60)
    
    factory = AgentFactory(settings)
    
    try:
        # 尝试创建未注册的智能体类型
        await factory.create_agent(
            agent_type=AgentType.TESTCASE_GENERATOR,
            name="test_agent"
        )
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"✅ 正确抛出异常: {e}")
    
    print("\n✅ 测试 4 通过！\n")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 智能体工厂测试套件")
    print("="*60)
    
    try:
        await test_factory_basic()
        await test_global_factory()
        await test_agent_creation_without_cache()
        await test_unregistered_agent_type()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

