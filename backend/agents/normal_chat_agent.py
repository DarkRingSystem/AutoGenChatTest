"""
普通聊天智能体
"""
from datetime import datetime
from typing import Any
import uuid
from venv import logger
from autogen_core import Image, MessageContext, RoutedAgent, TopicId, message_handler, type_subscription
from backend.api.v1.endpoints.normal_chat.chat_model import NormalChatRequest
from backend.core.llm_clients import get_deepseek_model_client
from backend.agents.prompt_builder import PromptBuilder
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent

@type_subscription(topic_type="normal_chat")
class NormalChatAgent(RoutedAgent):
    # 初始化智能体
    def __init__(self, model_client_instance=None,
                **kwargs):
        pass
    
    # 使用装饰器激活启用该方法，使用该方法进行消息传递
    @message_handler
    async def handle_normal_chat_request(
        self,
        message: NormalChatRequest,
        ctx: MessageContext
    ) -> None:
        
        try:
            logger.info(f"开始普通聊天请求: {message.session_id}")
            
            # 调用方法开始分析图片
            normal_chat_result = await self._normal_chat(message)
            logger.info(f"普通聊天请求处理完成: {message.session_id}")




        except Exception as e:
            logger.error(f"图片分析请求处理失败: {message.session_id}, 错误: {str(e)}")


    # 开始对话
    async def _normal_chat(self, message: NormalChatRequest) -> Any:
        """开始对话"""

        try:
            # 构建提示词
            system_message= PromptBuilder.create_normal_chat_prompt

            # 创建多智能体
            agent = await self.agent_factory.create_agent(
                agent_name="normal_chat",
                model_client=self._deepseek_model_client,
                system_message=system_message,
                model_client_stream=True,
            )
            # 调用智能体开始对话
            chat_stream_result = await agent.run_stream(task=message.message)

            # 流式输出发送到前端
            async for event in chat_stream_result:
                if isinstance(event, ModelClientStreamingChunkEvent):
                    if hasattr(event, 'content') and hasattr(event, 'source'):
                        return event.content
    
        except Exception as e:
            logger.error(f"普通聊天失败: {str(e)}")
            raise e