"""
优化的编排服务模块
基于 Microsoft AutoGen 框架的智能体编排服务

主要优化：
1. 完整的运行时生命周期管理
2. 改进的智能体注册和消息处理
3. 更好的错误处理和资源清理
4. 支持流式响应的事件处理
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage

from core.agent_factory_aitest import AgentFactoryAitest
from core.llm_clients import get_default_model_client
from config import settings

# 配置日志
logger = logging.getLogger(__name__)


class NormalChatOrchestrationAitest:
    """
    优化的普通对话编排服务类
    
    负责管理智能体的生命周期、消息路由和流式响应处理
    """
    
    def __init__(self, session_data: Dict[str, Any]):
        """
        初始化编排服务
        
        参数:
            session_data: 会话数据，包含消息、会话ID等信息
        """
        self.session_data = session_data
        self.session_id = session_data.get("session_id")
        self.message = session_data.get("message", "")
        
        # 核心组件
        self.agent_factory: Optional[AgentFactoryAitest] = None
        self.assistant_agent: Optional[AssistantAgent] = None
        
        # 状态管理
        self.is_initialized = False
        self.is_running = False
        
        # 配置
        self.model_client = None
        
        logger.info(f"🏗️ 编排服务已创建 - 会话ID: {self.session_id}")
    
    async def initialize(self) -> None:
        """
        初始化编排服务
        
        包括：
        1. 创建模型客户端
        2. 初始化智能体工厂
        3. 创建智能体
        """
        try:
            if self.is_initialized:
                logger.warning(f"⚠️ 编排服务已初始化 - 会话ID: {self.session_id}")
                return
            
            logger.info(f"🚀 开始初始化编排服务 - 会话ID: {self.session_id}")
            
            # 1. 创建模型客户端
            await self._initialize_model_client()
            
            # 2. 初始化智能体工厂
            await self._initialize_agent_factory()
            
            # 3. 创建智能体
            await self._create_agents()
            
            self.is_initialized = True
            logger.info(f"✅ 编排服务初始化完成 - 会话ID: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ 编排服务初始化失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
            await self.cleanup()
            raise e
    
    async def _initialize_model_client(self) -> None:
        """初始化模型客户端"""
        try:
            self.model_client = get_default_model_client(settings)
            logger.info(f"✅ 模型客户端已创建 - 会话ID: {self.session_id}")
        except Exception as e:
            logger.error(f"❌ 模型客户端创建失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
            raise e
    
    async def _initialize_agent_factory(self) -> None:
        """初始化智能体工厂"""
        try:
            self.agent_factory = AgentFactoryAitest()
            logger.info(f"✅ 智能体工厂已创建 - 会话ID: {self.session_id}")
        except Exception as e:
            logger.error(f"❌ 智能体工厂创建失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
            raise e
    
    async def _create_agents(self) -> None:
        """创建智能体"""
        try:
            if not self.agent_factory or not self.model_client:
                raise ValueError("智能体工厂或模型客户端未初始化")
            
            # 创建助手智能体
            self.assistant_agent = await self.agent_factory.create_assistant_agent(
                name="normal_chat_assistant",
                model_client=self.model_client,
                system_message=settings.system_message,
                enable_streaming=settings.enable_streaming
            )
            
            logger.info(f"✅ 智能体已创建 - 会话ID: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ 智能体创建失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
            raise e
    
    async def run_stream(self, task: str) -> AsyncGenerator[Any, None]:
        """
        运行智能体并返回流式响应
        
        参数:
            task: 任务描述（用户消息）
            
        生成:
            智能体事件流
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("编排服务未初始化")
            
            if not self.assistant_agent:
                raise RuntimeError("智能体未创建")
            
            self.is_running = True
            logger.info(f"🏃 开始运行智能体 - 会话ID: {self.session_id}")
            
            # 运行智能体并获取流式响应
            async for event in self.assistant_agent.run_stream(task=task):
                yield event
                
                # 记录事件类型（用于调试）
                event_type = type(event).__name__
                logger.debug(f"📨 收到事件: {event_type} - 会话ID: {self.session_id}")
            
            logger.info(f"✅ 智能体运行完成 - 会话ID: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ 智能体运行失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
            raise e
        finally:
            self.is_running = False
    
    async def run(self, task: str) -> TaskResult:
        """
        运行智能体并返回最终结果（非流式）
        
        参数:
            task: 任务描述（用户消息）
            
        返回:
            任务结果
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("编排服务未初始化")
            
            if not self.assistant_agent:
                raise RuntimeError("智能体未创建")
            
            self.is_running = True
            logger.info(f"🏃 开始运行智能体（非流式） - 会话ID: {self.session_id}")
            
            result = await self.assistant_agent.run(task=task)
            
            logger.info(f"✅ 智能体运行完成（非流式） - 会话ID: {self.session_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 智能体运行失败（非流式） - 会话ID: {self.session_id}, 错误: {str(e)}")
            raise e
        finally:
            self.is_running = False
    
    async def cleanup(self) -> None:
        """
        清理资源
        
        包括：
        1. 停止运行中的任务
        2. 清理智能体
        3. 关闭模型客户端连接
        """
        try:
            logger.info(f"🧹 开始清理编排服务资源 - 会话ID: {self.session_id}")
            
            # 标记为未运行状态
            self.is_running = False
            
            # 清理智能体
            if self.assistant_agent:
                try:
                    # 如果智能体有清理方法，调用它
                    if hasattr(self.assistant_agent, 'cleanup'):
                        await self.assistant_agent.cleanup()
                except Exception as e:
                    logger.warning(f"⚠️ 智能体清理失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
                finally:
                    self.assistant_agent = None
            
            # 清理模型客户端
            if self.model_client:
                try:
                    # 关闭模型客户端连接
                    if hasattr(self.model_client, 'close'):
                        await self.model_client.close()
                except Exception as e:
                    logger.warning(f"⚠️ 模型客户端清理失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
                finally:
                    self.model_client = None
            
            # 清理智能体工厂
            self.agent_factory = None
            
            # 标记为未初始化状态
            self.is_initialized = False
            
            logger.info(f"✅ 编排服务资源清理完成 - 会话ID: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ 编排服务资源清理失败 - 会话ID: {self.session_id}, 错误: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取编排服务状态
        
        返回:
            状态信息字典
        """
        return {
            "session_id": self.session_id,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "has_agent": self.assistant_agent is not None,
            "has_model_client": self.model_client is not None,
            "message": self.message,
            "timestamp": datetime.now().isoformat()
        }
