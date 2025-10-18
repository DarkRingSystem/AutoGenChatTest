"""
基于 AutoGen 消息机制的普通聊天智能体
使用真正的消息发布-订阅模式进行通信
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from autogen_core import MessageContext, RoutedAgent, TopicId, message_handler, type_subscription
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_agentchat.base import TaskResult

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# 定义消息模型
class NormalChatRequest:
    """普通聊天请求消息"""
    def __init__(self, message: str, session_id: str, user_id: Optional[str] = None):
        self.message = message
        self.session_id = session_id
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()


class NormalChatResponse:
    """普通聊天响应消息"""
    def __init__(self, content: str, session_id: str, response_type: str = "message"):
        self.content = content
        self.session_id = session_id
        self.response_type = response_type
        self.timestamp = datetime.now().isoformat()


@type_subscription(topic_type="normal_chat")
class NormalChatAgentAitest(RoutedAgent):
    """
    基于 AutoGen 消息机制的普通聊天智能体
    
    功能：
    1. 订阅 topic_type="normal_chat" 的消息
    2. 接收用户聊天请求
    3. 使用 AssistantAgent 处理对话
    4. 将响应发送回编排服务
    """
    
    def __init__(self, description: str = "普通聊天智能体，负责处理用户的日常对话请求"):
        """
        初始化智能体
        
        参数:
            description: 智能体描述
        """
        super().__init__(description)
        self.assistant_agent: Optional[AssistantAgent] = None
        self.is_initialized = False
        
        logger.info("🤖 NormalChatAgentAitest 已创建")
    
    async def _initialize_assistant(self) -> None:
        """初始化助手智能体"""
        if self.is_initialized:
            return
            
        try:
            from core.llm_clients import get_default_model_client
            
            # 获取LLM客户端
            llm_client = get_default_model_client()
            
            # 创建助手智能体
            self.assistant_agent = AssistantAgent(
                name="normal_chat_assistant",
                model_client=llm_client,
                description="普通聊天助手智能体，负责处理用户的日常对话请求",
                system_message="你是一个友好、专业的AI助手。请用中文回答用户的问题，提供准确、有用的信息。"
            )
            
            self.is_initialized = True
            logger.info("✅ 助手智能体初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 助手智能体初始化失败: {str(e)}")
            raise e
    
    @message_handler
    async def handle_normal_chat_request(
        self,
        message: NormalChatRequest,
        ctx: MessageContext
    ) -> None:
        """
        处理普通聊天请求
        
        参数:
            message: 聊天请求消息
            ctx: 消息上下文
        """
        try:
            logger.info(f"🔄 [消息流程-步骤1] 智能体接收到聊天请求 - 会话ID: {message.session_id}")
            logger.info(f"📝 [消息流程-步骤2] 用户消息: {message.message}")
            
            # 确保助手智能体已初始化
            await self._initialize_assistant()
            
            # 处理聊天请求
            await self._process_chat_request(message, ctx)
            
            logger.info(f"✅ [消息流程-步骤3] 聊天请求处理完成 - 会话ID: {message.session_id}")
            
        except Exception as e:
            logger.error(f"❌ [消息流程-错误] 聊天请求处理失败 - 会话ID: {message.session_id}, 错误: {str(e)}")
            
            # 发送错误响应
            await self._send_error_response(message.session_id, str(e), ctx)
    
    async def _process_chat_request(self, message: NormalChatRequest, ctx: MessageContext) -> None:
        """
        处理聊天请求的核心逻辑
        
        参数:
            message: 聊天请求消息
            ctx: 消息上下文
        """
        try:
            session_id = message.session_id
            user_message = message.message.strip()
            
            logger.info(f"🏃 [处理流程-步骤1] 开始处理用户消息 - 会话ID: {session_id}")
            
            # 发送开始处理的状态消息
            await self._send_status_message(session_id, "thinking...", ctx)
            
            # 发送智能体开始处理的消息
            await self._send_agent_start_message(session_id, ctx)
            
            logger.info(f"🤖 [处理流程-步骤2] 启动智能体流式处理 - 会话ID: {session_id}")
            
            # 运行智能体并获取流式响应
            event_stream = self.assistant_agent.run_stream(task=user_message)
            
            # 处理流式事件
            full_response = ""
            async for event in event_stream:
                logger.debug(f"📡 [处理流程-事件] 收到事件: {type(event).__name__} - 会话ID: {session_id}")
                
                if isinstance(event, ModelClientStreamingChunkEvent):
                    # 处理流式内容块
                    if hasattr(event, 'content') and event.content:
                        chunk_content = event.content
                        full_response += chunk_content
                        await self._send_chunk_message(session_id, chunk_content, ctx)
                        
                elif isinstance(event, TextMessage):
                    # 处理完整文本消息
                    if hasattr(event, 'content') and event.content:
                        full_response = event.content
                        await self._send_text_message(session_id, event.content, ctx)
                        
                elif isinstance(event, TaskResult):
                    # 处理任务结果
                    logger.info(f"📋 [处理流程-结果] 任务完成 - 会话ID: {session_id}")
                    await self._send_task_result_message(session_id, event, ctx)
            
            logger.info(f"✅ [处理流程-步骤3] 智能体处理完成 - 会话ID: {session_id}, 响应长度: {len(full_response)}")
            
            # 发送完成消息
            await self._send_completion_message(session_id, full_response, ctx)
            
        except Exception as e:
            logger.error(f"❌ [处理流程-错误] 处理失败 - 会话ID: {session_id}, 错误: {str(e)}")
            raise e
    
    async def _send_status_message(self, session_id: str, status: str, ctx: MessageContext) -> None:
        """发送状态消息"""
        try:
            status_data = {
                "type": "status",
                "content": status,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # 发布状态消息到响应主题
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(status_data),
                    session_id=session_id,
                    response_type="status"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.debug(f"📤 发送状态消息 - 会话ID: {session_id}, 状态: {status}")
            
        except Exception as e:
            logger.error(f"❌ 发送状态消息失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_agent_start_message(self, session_id: str, ctx: MessageContext) -> None:
        """发送智能体开始处理消息"""
        try:
            start_data = {
                "type": "agent_start",
                "content": "智能体 normal_chat_assistant 开始处理",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(start_data),
                    session_id=session_id,
                    response_type="agent_start"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.debug(f"📤 发送智能体开始消息 - 会话ID: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ 发送智能体开始消息失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_chunk_message(self, session_id: str, content: str, ctx: MessageContext) -> None:
        """发送内容块消息"""
        try:
            chunk_data = {
                "type": "chunk",
                "content": content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(chunk_data),
                    session_id=session_id,
                    response_type="chunk"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.debug(f"📤 发送内容块 - 会话ID: {session_id}, 长度: {len(content)}")
            
        except Exception as e:
            logger.error(f"❌ 发送内容块失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_text_message(self, session_id: str, content: str, ctx: MessageContext) -> None:
        """发送文本消息"""
        try:
            text_data = {
                "type": "message",
                "content": content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(text_data),
                    session_id=session_id,
                    response_type="message"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.debug(f"📤 发送文本消息 - 会话ID: {session_id}, 长度: {len(content)}")
            
        except Exception as e:
            logger.error(f"❌ 发送文本消息失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_task_result_message(self, session_id: str, task_result: TaskResult, ctx: MessageContext) -> None:
        """发送任务结果消息"""
        try:
            result_data = {
                "type": "task_result",
                "content": str(task_result),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(result_data),
                    session_id=session_id,
                    response_type="task_result"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.debug(f"📤 发送任务结果 - 会话ID: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ 发送任务结果失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_completion_message(self, session_id: str, full_response: str, ctx: MessageContext) -> None:
        """发送完成消息"""
        try:
            completion_data = {
                "type": "completion",
                "content": full_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(completion_data),
                    session_id=session_id,
                    response_type="completion"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.info(f"📤 发送完成消息 - 会话ID: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ 发送完成消息失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _send_error_response(self, session_id: str, error_message: str, ctx: MessageContext) -> None:
        """发送错误响应"""
        try:
            error_data = {
                "type": "error",
                "content": f"处理请求时发生错误: {error_message}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.publish_message(
                NormalChatResponse(
                    content=str(error_data),
                    session_id=session_id,
                    response_type="error"
                ),
                topic_id=TopicId(type="normal_chat_response", source=session_id)
            )
            
            logger.error(f"📤 发送错误响应 - 会话ID: {session_id}, 错误: {error_message}")
            
        except Exception as e:
            logger.error(f"❌ 发送错误响应失败 - 会话ID: {session_id}, 错误: {str(e)}")
