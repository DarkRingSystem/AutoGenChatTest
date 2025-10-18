"""
优化的普通聊天流式响应处理服务
专门处理 Microsoft AutoGen 事件流并转换为 SSE 格式

主要功能：
1. 处理 AutoGen 各种事件类型
2. 转换为标准化的 SSE 格式
3. 提供完整的错误处理和日志记录
4. 支持 Token 统计和性能监控
"""

import json
import logging
from typing import AsyncGenerator, Any, Dict, Optional
from datetime import datetime

from autogen_agentchat.messages import (
    ModelClientStreamingChunkEvent, 
    TextMessage,
    ToolCallRequestEvent,
    ToolCallExecutionEvent
)
from api.v1.endpoints.normal_chat.chat_model import TokenUsage
# 简单的 token 计数器实现
def get_token_counter():
    """获取 token 计数器"""
    class SimpleTokenCounter:
        def count_tokens(self, text: str) -> int:
            """简单的 token 计数（按单词数估算）"""
            if not text:
                return 0
            # 简单估算：中文按字符数，英文按单词数
            chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
            english_words = len(text.replace('，', ' ').replace('。', ' ').replace('！', ' ').replace('？', ' ').split())
            return chinese_chars + english_words

    return SimpleTokenCounter()

# 配置日志
logger = logging.getLogger(__name__)


class SSEMessage:
    """SSE 消息封装类"""
    
    def __init__(
        self,
        type: str,
        content: Any,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        tokens: Optional[TokenUsage] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.type = type
        self.content = content
        self.agent_name = agent_name
        self.session_id = session_id
        self.tokens = tokens
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            "type": self.type,
            "content": self.content,
            "timestamp": self.timestamp
        }
        
        if self.agent_name:
            data["agent_name"] = self.agent_name
        
        if self.session_id:
            data["session_id"] = self.session_id
        
        if self.tokens:
            data["tokens"] = self.tokens.model_dump() if hasattr(self.tokens, 'model_dump') else self.tokens
        
        if self.metadata:
            data["metadata"] = self.metadata
        
        return data
    
    def to_sse_format(self) -> str:
        """转换为 SSE 格式"""
        return f"data: {json.dumps(self.to_dict(), ensure_ascii=False)}\n\n"


class NormalChatStreamServiceAitest:
    """
    优化的普通聊天流式响应处理服务
    
    负责处理 AutoGen 事件流并转换为前端可用的 SSE 格式
    """
    
    def __init__(self):
        """初始化流式服务"""
        self.message_count = 0
        self.full_response = ""
        self.token_counter = get_token_counter()
        self.start_time = datetime.now()
        
        # 状态跟踪
        self.user_message_seen = False
        self.agent_started = False
        self.processing_complete = False
        
        logger.info("🌊 流式响应服务已初始化")
    
    async def process_stream(
        self,
        event_stream: AsyncGenerator[Any, None],
        user_message: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        处理事件流并生成 SSE 响应
        
        参数:
            event_stream: AutoGen 事件流
            user_message: 用户消息
            session_id: 会话 ID
            
        生成:
            SSE 格式的字符串
        """
        try:
            logger.info(f"🌊 开始处理流式响应 - 会话ID: {session_id}")
            
            # 发送初始状态
            yield self._create_status_message("thinking", session_id)
            
            # 重置状态
            self._reset_state()
            
            # 处理事件流
            async for event in event_stream:
                self.message_count += 1
                event_type = self._get_event_type(event)
                
                logger.debug(f"📨 处理事件: {event_type} - 会话ID: {session_id}")
                
                # 根据事件类型处理
                if event_type == 'TextMessage':
                    async for sse_msg in self._handle_text_message(event, user_message, session_id):
                        yield sse_msg
                
                elif event_type == 'ModelClientStreamingChunkEvent':
                    async for sse_msg in self._handle_streaming_chunk(event, session_id):
                        yield sse_msg
                
                elif event_type == 'ToolCallRequestEvent':
                    async for sse_msg in self._handle_tool_call(event, session_id):
                        yield sse_msg
                
                elif event_type == 'ToolCallExecutionEvent':
                    async for sse_msg in self._handle_tool_result(event, session_id):
                        yield sse_msg
                
                else:
                    # 处理未知事件类型
                    async for sse_msg in self._handle_unknown_event(event, event_type, session_id):
                        yield sse_msg
            
            # 发送完成信息
            yield self._create_completion_summary(user_message, session_id)
            yield self._create_done_message(session_id)
            
            logger.info(f"✅ 流式响应处理完成 - 会话ID: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ 流式响应处理失败 - 会话ID: {session_id}, 错误: {str(e)}")
            yield self._create_error_message(str(e), session_id)
        finally:
            # 发送最终事件以关闭流
            yield "data: [DONE]\n\n"
    
    def _get_event_type(self, event: Any) -> str:
        """获取事件类型"""
        return type(event).__name__
    
    async def _handle_text_message(
        self, 
        event: TextMessage, 
        user_message: str, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """处理文本消息事件"""
        try:
            content = getattr(event, 'content', '')
            source = getattr(event, 'source', 'unknown')
            
            # 过滤用户消息（避免回显）
            if content == user_message and not self.user_message_seen:
                self.user_message_seen = True
                return
            
            # 发送智能体开始消息（如果还没发送）
            if not self.agent_started and source != 'user':
                self.agent_started = True
                yield self._create_agent_start_message(source, session_id)
            
            # 发送文本消息
            if content and content != user_message:
                message = SSEMessage(
                    type="message",
                    content=content,
                    agent_name=source,
                    session_id=session_id
                )
                yield message.to_sse_format()
                
        except Exception as e:
            logger.error(f"❌ 处理文本消息失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _handle_streaming_chunk(
        self, 
        event: ModelClientStreamingChunkEvent, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """处理流式文本块事件"""
        try:
            chunk_content = getattr(event, 'content', '')
            source = getattr(event, 'source', 'assistant')
            
            if not chunk_content:
                return
            
            # 发送智能体开始消息（如果还没发送）
            if not self.agent_started:
                self.agent_started = True
                yield self._create_agent_start_message(source, session_id)
            
            # 累积完整响应
            self.full_response += chunk_content
            
            # 发送流式块
            message = SSEMessage(
                type="chunk",
                content=chunk_content,
                agent_name=source,
                session_id=session_id,
                metadata={"full_response": self.full_response}
            )
            yield message.to_sse_format()
            
        except Exception as e:
            logger.error(f"❌ 处理流式块失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _handle_tool_call(
        self, 
        event: ToolCallRequestEvent, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """处理工具调用事件"""
        try:
            tools = getattr(event, 'content', [])
            source = getattr(event, 'source', 'assistant')
            
            if tools:
                tool_info = []
                for tool in tools:
                    tool_info.append({
                        'name': getattr(tool, 'name', ''),
                        'arguments': getattr(tool, 'arguments', ''),
                        'id': getattr(tool, 'id', '')
                    })
                
                message = SSEMessage(
                    type="tool_call",
                    content=tool_info,
                    agent_name=source,
                    session_id=session_id
                )
                yield message.to_sse_format()
                
        except Exception as e:
            logger.error(f"❌ 处理工具调用失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _handle_tool_result(
        self, 
        event: ToolCallExecutionEvent, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """处理工具执行结果事件"""
        try:
            result = getattr(event, 'content', '')
            source = getattr(event, 'source', 'system')
            
            message = SSEMessage(
                type="tool_result",
                content=result,
                agent_name=source,
                session_id=session_id
            )
            yield message.to_sse_format()
            
        except Exception as e:
            logger.error(f"❌ 处理工具结果失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    async def _handle_unknown_event(
        self, 
        event: Any, 
        event_type: str, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """处理未知事件类型"""
        try:
            logger.debug(f"🔍 处理未知事件类型: {event_type} - 会话ID: {session_id}")
            
            # 尝试提取内容
            content = getattr(event, 'content', str(event))
            source = getattr(event, 'source', 'system')
            
            message = SSEMessage(
                type="unknown",
                content=content,
                agent_name=source,
                session_id=session_id,
                metadata={"original_type": event_type}
            )
            yield message.to_sse_format()
            
        except Exception as e:
            logger.error(f"❌ 处理未知事件失败 - 会话ID: {session_id}, 错误: {str(e)}")
    
    def _create_status_message(self, status: str, session_id: str) -> str:
        """创建状态消息"""
        message = SSEMessage(
            type="status",
            content=status,
            session_id=session_id
        )
        return message.to_sse_format()
    
    def _create_agent_start_message(self, agent_name: str, session_id: str) -> str:
        """创建智能体开始消息"""
        message = SSEMessage(
            type="agent_start",
            content=f"智能体 {agent_name} 开始处理",
            agent_name=agent_name,
            session_id=session_id
        )
        return message.to_sse_format()
    
    def _create_completion_summary(self, user_message: str, session_id: str) -> str:
        """创建完成摘要"""
        try:
            # 计算 token 统计
            input_tokens = self.token_counter.count_tokens(user_message)
            output_tokens = self.token_counter.count_tokens(self.full_response)
            total_tokens = input_tokens + output_tokens
            
            token_usage = TokenUsage(
                total=total_tokens,
                input=input_tokens,
                output=output_tokens
            )
            
            # 计算处理时间
            processing_time = (datetime.now() - self.start_time).total_seconds()
            
            message = SSEMessage(
                type="token_usage",
                content="处理完成",
                session_id=session_id,
                tokens=token_usage,
                metadata={
                    "processing_time": processing_time,
                    "message_count": self.message_count,
                    "response_length": len(self.full_response)
                }
            )
            return message.to_sse_format()
            
        except Exception as e:
            logger.error(f"❌ 创建完成摘要失败 - 会话ID: {session_id}, 错误: {str(e)}")
            return self._create_error_message(f"摘要生成失败: {str(e)}", session_id)
    
    def _create_done_message(self, session_id: str) -> str:
        """创建完成消息"""
        message = SSEMessage(
            type="done",
            content="对话完成",
            session_id=session_id
        )
        return message.to_sse_format()
    
    def _create_error_message(self, error: str, session_id: str) -> str:
        """创建错误消息"""
        message = SSEMessage(
            type="error",
            content=f"错误: {error}",
            session_id=session_id
        )
        return message.to_sse_format()
    
    def _reset_state(self) -> None:
        """重置内部状态"""
        self.message_count = 0
        self.full_response = ""
        self.user_message_seen = False
        self.agent_started = False
        self.processing_complete = False
        self.start_time = datetime.now()
