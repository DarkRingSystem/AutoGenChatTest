"""
图片分析流式处理服务模块
负责处理图片分析团队的 SSE 流式响应，显示每个智能体的回复
"""
from typing import AsyncGenerator, Any, Dict
from models import SSEMessage
from utils.token_counter import get_token_counter


class ImageAnalysisStreamService:
    """图片分析流式处理服务类"""

    # 智能体角色映射
    AGENT_ROLES = {
        "UI_Expert": "🎨 UI 专家",
        "Interaction_Analyst": "🔄 交互分析师",
        "Test_Scenario_Expert": "📋 测试场景专家",
    }

    def __init__(self):
        """初始化图片分析流式处理服务"""
        self.current_agent = None
        self.agent_responses: Dict[str, str] = {}
        self.agent_last_sent_length: Dict[str, int] = {}  # 记录每个智能体上次发送的内容长度
        self.agent_started: Dict[str, bool] = {}  # 记录智能体是否已经开始
        self.message_count = 0
        self.token_counter = get_token_counter()
        self.session_id = ""
        self.user_message_seen = False  # 是否已经看到用户消息

    async def process_stream(
        self,
        event_stream: AsyncGenerator[Any, None],
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        处理图片分析团队事件流并生成 SSE 响应

        参数:
            event_stream: 团队事件流
            session_id: 会话 ID

        生成:
            SSE 格式的字符串
        """
        # 保存会话 ID
        self.session_id = session_id

        # 发送初始状态
        yield self._create_status_message("图片分析团队协作中...")

        try:
            # 处理事件流
            async for event in event_stream:
                # 处理不同类型的事件
                async for sse_message in self._handle_event(event):
                    yield sse_message

            # 发送最后一个智能体的完成消息（如果有）
            if self.current_agent:
                yield self._create_agent_done_message(self.current_agent)
                self.current_agent = None

            # 发送完成信号
            yield self._create_done_message()

            # 计算并发送 token 统计
            yield self._create_token_message()

        except Exception as e:
            yield self._create_error_message(str(e))

        finally:
            # 发送最终事件以关闭流
            yield "data: [DONE]\n\n"

    async def _handle_event(self, event: Any) -> AsyncGenerator[str, None]:
        """
        处理单个事件

        参数:
            event: 事件对象

        生成:
            SSE 格式的字符串
        """
        # 增加消息计数
        self.message_count += 1

        # 获取事件类型和信息
        event_type = self._get_event_type(event)
        source = getattr(event, 'source', 'unknown')
        content = getattr(event, 'content', '')

        # 根据事件类型处理
        if event_type == 'TextMessage':
            async for sse_msg in self._handle_text_message(event, source, content):
                yield sse_msg
        elif event_type == 'ModelClientStreamingChunkEvent':
            async for sse_msg in self._handle_streaming_chunk(event, source, content):
                yield sse_msg
        else:
            # 其他事件类型暂时忽略
            # print(f"🔍 忽略事件类型: {event_type}, source={source}")
            pass

    def _get_event_type(self, event: Any) -> str:
        """获取事件类型"""
        return getattr(event, 'type', type(event).__name__)

    async def _handle_text_message(
        self,
        event: Any,
        source: str,
        content: str
    ) -> AsyncGenerator[str, None]:
        """处理文本消息事件"""
        # 过滤用户消息
        if self._is_user_message(source, content):
            self.user_message_seen = True
            # print(f"🚫 过滤用户消息: source={source}")
            return

        # 过滤非智能体消息
        if source not in self.AGENT_ROLES:
            # print(f"🚫 过滤非智能体消息: source={source}")
            return

        # 检测智能体切换
        if source != self.current_agent:
            # 如果之前有智能体在工作，发送完成消息
            if self.current_agent:
                yield self._create_agent_done_message(self.current_agent)

            # 切换到新智能体
            self.current_agent = source

            # 初始化智能体响应（如果还没有记录）
            if source not in self.agent_responses:
                self.agent_responses[source] = ""
                self.agent_last_sent_length[source] = 0
                # print(f"🆕 初始化 {source} 的响应缓冲区")

            # 发送智能体开始消息（只在第一次出现时发送）
            if not self.agent_started.get(source, False):
                yield self._create_agent_start_message(source)
                self.agent_started[source] = True
                # print(f"🚀 {source} 开始工作")

        # 处理完整的文本消息（非流式）
        if content and content != self.agent_responses.get(source, ""):
            self.agent_responses[source] = content
            self.agent_last_sent_length[source] = len(content)
            yield self._create_agent_message(source, content)
            # print(f"✅ 发送 {source} 的完整消息，长度: {len(content)}")

    async def _handle_streaming_chunk(
        self,
        event: Any,
        source: str,
        content: str
    ) -> AsyncGenerator[str, None]:
        """处理流式块事件"""
        # 过滤非智能体消息
        if source not in self.AGENT_ROLES:
            return

        # 检测智能体切换
        if source != self.current_agent:
            # 如果之前有智能体在工作，发送完成消息
            if self.current_agent:
                yield self._create_agent_done_message(self.current_agent)

            # 切换到新智能体
            self.current_agent = source

            # 初始化智能体响应（如果还没有记录）
            if source not in self.agent_responses:
                self.agent_responses[source] = ""
                self.agent_last_sent_length[source] = 0

            # 发送智能体开始消息（只在第一次出现时发送）
            if not self.agent_started.get(source, False):
                yield self._create_agent_start_message(source)
                self.agent_started[source] = True

        # 累积流式内容
        chunk_content = getattr(event, 'content', '')
        if chunk_content:
            self.agent_responses[source] += chunk_content
            current_length = len(self.agent_responses[source])

            # 发送累积的完整内容
            yield self._create_agent_message(source, self.agent_responses[source])
            self.agent_last_sent_length[source] = current_length

    def _is_user_message(self, source: str, content: str) -> bool:
        """
        判断是否为用户消息

        参数:
            source: 消息来源
            content: 消息内容

        返回:
            True 如果是用户消息，否则 False
        """
        # 检查来源
        if source == 'user':
            return True

        # 检查是否为第一条消息（通常是用户的图片分析请求）
        if not self.user_message_seen and self.message_count == 1:
            return True

        # 检查内容是否包含图片分析请求的特征
        if "请分析以下 UI 界面图片" in content or "工作流程说明" in content:
            return True

        return False

    def _create_status_message(self, status: str) -> str:
        """创建状态消息"""
        message = SSEMessage(
            type="status",
            content=status,
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_agent_start_message(self, agent_name: str) -> str:
        """创建智能体开始消息"""
        message = SSEMessage(
            type="agent_start",
            content=f"{self.AGENT_ROLES.get(agent_name, agent_name)} 开始分析...",
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name),
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_agent_message(self, agent_name: str, content: str) -> str:
        """创建智能体消息"""
        message = SSEMessage(
            type="agent_message",
            content=content,
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name),
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_agent_done_message(self, agent_name: str) -> str:
        """创建智能体完成消息"""
        message = SSEMessage(
            type="agent_done",
            content=f"{self.AGENT_ROLES.get(agent_name, agent_name)} 分析完成",
            agent_name=agent_name,
            agent_role=self.AGENT_ROLES.get(agent_name, agent_name),
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_done_message(self) -> str:
        """创建完成消息"""
        message = SSEMessage(
            type="done",
            content="图片分析完成",
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_error_message(self, error: str) -> str:
        """创建错误消息"""
        message = SSEMessage(
            type="error",
            content=f"错误: {error}",
            session_id=self.session_id
        )
        return message.to_sse_format()

    def _create_token_message(self) -> str:
        """创建 token 统计消息"""
        # 计算所有智能体响应的 token 数
        total_tokens = 0
        for response in self.agent_responses.values():
            total_tokens += self.token_counter.count_tokens(response)

        message = SSEMessage(
            type="token_usage",
            content=f"总计使用 {total_tokens} tokens",
            token_usage={
                "total_tokens": total_tokens,
                "message_count": self.message_count
            },
            session_id=self.session_id
        )
        return message.to_sse_format()

