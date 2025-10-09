"""
团队流式处理服务模块
负责处理团队模式的 SSE 流式响应，显示每个智能体的回复
"""
from typing import AsyncGenerator, Any, Dict
from models import SSEMessage, TokenUsage
from utils.token_counter import get_token_counter


class TeamStreamService:
    """团队流式处理服务类"""

    # 智能体角色映射
    AGENT_ROLES = {
        "TestCase_Generator": "🎯 测试用例生成专家",
        "TestCase_Reviewer": "🔍 测试用例评审专家",
        "TestCase_Optimizer": "✨ 测试用例优化专家",
    }

    def __init__(self):
        """初始化团队流式处理服务"""
        self.current_agent = None
        self.agent_responses: Dict[str, str] = {}
        self.message_count = 0
        self.token_counter = get_token_counter()
        self.user_message = ""
        self.waiting_for_feedback = False  # 是否正在等待用户反馈
        self.feedback_agent = None  # 等待反馈的智能体名称

    async def process_stream(
        self,
        event_stream: AsyncGenerator[Any, None],
        user_message: str
    ) -> AsyncGenerator[str, None]:
        """
        处理团队事件流并生成 SSE 响应

        参数:
            event_stream: AutoGen 团队事件流
            user_message: 用户消息

        生成:
            SSE 格式的字符串
        """
        try:
            # 保存用户消息
            self.user_message = user_message

            # 发送初始状态
            yield self._create_status_message("团队协作中...")

            # 重置状态
            self._reset_state()

            # 处理事件流
            async for event in event_stream:
                self.message_count += 1
                event_type = self._get_event_type(event)

                # 获取事件来源（智能体名称）
                source = self._get_event_source(event)

                # 处理不同类型的事件
                if event_type == 'TextMessage':
                    async for sse_msg in self._handle_text_message(event, source):
                        yield sse_msg

                elif event_type == 'ModelClientStreamingChunkEvent':
                    async for sse_msg in self._handle_streaming_chunk(event, source):
                        yield sse_msg

            # 检查是否需要等待用户反馈
            if self.current_agent and self._should_wait_for_feedback(self.current_agent):
                # 发送智能体完成消息
                yield self._create_agent_done_message(self.current_agent)

                # 发送反馈请求
                yield self._create_feedback_request_message(self.current_agent)

                # 标记等待反馈状态
                self.waiting_for_feedback = True
                self.feedback_agent = self.current_agent
            elif self.current_agent and self._is_final_answer(self.current_agent):
                # Optimizer 完成，这是最终回答
                yield self._create_agent_done_message(self.current_agent)

                # 发送完成信号（最终回答）
                yield self._create_done_message()
            else:
                # 其他情况，发送完成信号
                yield self._create_done_message()

            # 计算并发送 token 统计
            yield self._create_token_message()

        except Exception as e:
            print(f"❌ Error in process_stream: {e}")
            import traceback
            traceback.print_exc()
            yield self._create_error_message(str(e))

        finally:
            # 发送最终事件以关闭流
            yield "data: [DONE]\n\n"

    def _reset_state(self) -> None:
        """重置内部状态"""
        self.current_agent = None
        self.agent_responses = {}
        self.message_count = 0

    def _get_event_type(self, event: Any) -> str:
        """
        获取事件类型

        参数:
            event: AutoGen 事件

        返回:
            事件类型字符串
        """
        return getattr(event, 'type', type(event).__name__)

    def _get_event_source(self, event: Any) -> str:
        """
        获取事件来源（智能体名称）

        参数:
            event: AutoGen 事件

        返回:
            智能体名称
        """
        return getattr(event, 'source', 'unknown')

    async def _handle_text_message(
        self,
        event: Any,
        source: str
    ) -> AsyncGenerator[str, None]:
        """
        处理文本消息事件

        参数:
            event: 文本消息事件
            source: 消息来源（智能体名称）

        生成:
            SSE 格式的字符串
        """
        content = getattr(event, 'content', '')

        # 跳过用户消息
        if source == 'user' or content == self.user_message:
            return

        # 检测智能体切换
        if source != self.current_agent and source != 'unknown':
            # 如果之前有智能体在工作，发送完成消息
            if self.current_agent:
                yield self._create_agent_done_message(self.current_agent)

                # 检查是否需要等待用户反馈
                if self._should_wait_for_feedback(self.current_agent):
                    yield self._create_feedback_request_message(self.current_agent)
                    self.waiting_for_feedback = True
                    self.feedback_agent = self.current_agent
                    return

            # 切换到新智能体
            self.current_agent = source
            self.agent_responses[source] = ""

            # 发送智能体开始消息
            yield self._create_agent_start_message(source)

        # 发送智能体消息
        if content and source in self.AGENT_ROLES:
            self.agent_responses[source] = content
            yield self._create_agent_message(source, content)

    async def _handle_streaming_chunk(
        self,
        event: Any,
        source: str
    ) -> AsyncGenerator[str, None]:
        """
        处理流式文本块事件

        参数:
            event: 流式文本块事件
            source: 消息来源（智能体名称）

        生成:
            SSE 格式的字符串
        """
        chunk_content = getattr(event, 'content', '')

        if not chunk_content:
            return

        # 检测智能体切换
        if source != self.current_agent and source != 'unknown':
            # 如果之前有智能体在工作，发送完成消息
            if self.current_agent:
                yield self._create_agent_done_message(self.current_agent)

            # 切换到新智能体
            self.current_agent = source
            self.agent_responses[source] = ""

            # 发送智能体开始消息
            yield self._create_agent_start_message(source)

        # 累积智能体响应
        if source not in self.agent_responses:
            self.agent_responses[source] = ""
        self.agent_responses[source] += chunk_content

        # 发送流式块
        if source in self.AGENT_ROLES:
            message = SSEMessage(
                type="agent_message",
                content=chunk_content,
                agent_name=source,
                agent_role=self.AGENT_ROLES.get(source, source)
            )
            yield message.to_sse_format()

    def _create_agent_start_message(self, agent_name: str) -> str:
        """
        创建智能体开始消息

        参数:
            agent_name: 智能体名称

        返回:
            SSE 格式的字符串
        """
        message = SSEMessage(
            type="agent_start",
            content="",
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name)
        )
        return message.to_sse_format()

    def _create_agent_message(self, agent_name: str, content: str) -> str:
        """
        创建智能体消息

        参数:
            agent_name: 智能体名称
            content: 消息内容

        返回:
            SSE 格式的字符串
        """
        message = SSEMessage(
            type="agent_message",
            content=content,
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name)
        )
        return message.to_sse_format()

    def _create_agent_done_message(self, agent_name: str) -> str:
        """
        创建智能体完成消息

        参数:
            agent_name: 智能体名称

        返回:
            SSE 格式的字符串
        """
        message = SSEMessage(
            type="agent_done",
            content=self.agent_responses.get(agent_name, ""),
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name)
        )
        return message.to_sse_format()

    def _create_status_message(self, status: str) -> str:
        """创建状态消息"""
        message = SSEMessage(type="status", content=status)
        return message.to_sse_format()

    def _create_token_message(self) -> str:
        """创建 token 统计消息"""
        # 计算所有智能体响应的总 token
        all_responses = "\n\n".join(self.agent_responses.values())
        input_tokens = self.token_counter.count_tokens(self.user_message)
        output_tokens = self.token_counter.count_tokens(all_responses)
        total_tokens = input_tokens + output_tokens

        token_usage = TokenUsage(
            total=total_tokens,
            input=input_tokens,
            output=output_tokens
        )

        message = SSEMessage(
            type="tokens",
            content="",
            tokens=token_usage
        )
        return message.to_sse_format()

    def _create_done_message(self) -> str:
        """创建完成消息"""
        # 如果还有当前智能体，发送其完成消息
        if self.current_agent:
            agent_done = self._create_agent_done_message(self.current_agent)
            self.current_agent = None
            return agent_done

        message = SSEMessage(
            type="done",
            content="团队协作完成"
        )
        return message.to_sse_format()

    def _create_error_message(self, error: str) -> str:
        """创建错误消息"""
        message = SSEMessage(type="error", content=f"错误: {error}")
        return message.to_sse_format()

    def _should_wait_for_feedback(self, agent_name: str) -> bool:
        """
        判断是否需要等待用户反馈

        参数:
            agent_name: 智能体名称

        返回:
            True 如果需要等待反馈
        """
        # Reviewer 完成后等待用户反馈
        # Generator 单独运行时也等待反馈（用户指定 @TestCase_Generator）
        # Optimizer 完成后不等待，直接结束（最终回答）
        return agent_name in ["TestCase_Reviewer", "TestCase_Generator"]

    def _is_final_answer(self, agent_name: str) -> bool:
        """
        判断是否为最终回答

        参数:
            agent_name: 智能体名称

        返回:
            True 如果是最终回答
        """
        # Optimizer 的回答是最终回答
        return agent_name == "TestCase_Optimizer"

    def _create_feedback_request_message(self, agent_name: str) -> str:
        """
        创建反馈请求消息

        参数:
            agent_name: 智能体名称

        返回:
            SSE 格式的字符串
        """
        message = SSEMessage(
            type="feedback_request",
            content=f"{self.AGENT_ROLES.get(agent_name, agent_name)} 已完成，请提供反馈",
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name),
            available_agents=list(self.AGENT_ROLES.keys())  # 提供可用智能体列表
        )
        return message.to_sse_format()

