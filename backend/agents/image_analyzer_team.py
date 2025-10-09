"""
UI 图片分析智能体团队
基于 AutoGen GraphFlow 实现并行分析工作流
支持多模态消息和团队协作，生成测试场景和自动化脚本建议
"""
from typing import Optional, Dict, Any, List, Union
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_agentchat.base import TaskResult
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import Image

from agents.base_agent import BaseTeamAgent
from config import Settings
from core.llm_clients import get_uitars_model_client, get_default_model_client
from prompts.prompt_loader import load_prompt, PromptNames


class ImageAnalyzerTeam(BaseTeamAgent):
    """
    UI 图片分析智能体团队

    工作流程（使用 GraphFlow）：
    1. UI_Expert 和 Interaction_Analyst 并行分析图片 (✅)
    2. 两者完成后，结果汇总到 Test_Scenario_Expert (✅)
    3. Test_Scenario_Expert 综合分析并生成测试场景 (✅)
    4. 将测试场景发送给playwright脚本生成专家，生成脚本并执行反馈 (🚧)

    团队成员：
    - UI_Expert: 负责视觉和布局分析
    - Interaction_Analyst: 负责交互行为分析
    - Test_Scenario_Expert: 负责综合分析和测试场景设计
    - 脚本生成专家
    """

    def __init__(
        self,
        name: str = "ImageAnalyzerTeam",
        settings: Optional[Settings] = None,
    ):
        """
        初始化图片分析团队

        参数:
            name: 团队名称
            settings: 配置实例，如果为 None 则使用全局配置
        """
        super().__init__(name=name, settings=settings)

        self.uitars_model_client: Optional[OpenAIChatCompletionClient] = None
        self.default_model_client: Optional[OpenAIChatCompletionClient] = None
        self.ui_expert: Optional[AssistantAgent] = None
        self.interaction_analyst: Optional[AssistantAgent] = None
        self.test_scenario_expert: Optional[AssistantAgent] = None

    async def initialize(self) -> None:
        """初始化图片分析团队"""
        print(f"🚀 正在初始化 UI 图片分析团队: {self.name}...")

        # 创建 UI-TARS 模型客户端（用于 UI 和交互分析）
        self.uitars_model_client = get_uitars_model_client(self.settings)

        # 创建默认模型客户端（用于测试场景专家）
        self.default_model_client = get_default_model_client(self.settings)

        # 调用父类的初始化方法
        await super().initialize()

        print(f"✅ UI 图片分析团队 {self.name} 初始化成功！")

    def create_team_members(self) -> List[AssistantAgent]:
        """创建团队成员智能体"""

        # 1. UI 专家 - 负责视觉和布局分析（使用 UI-TARS 模型）
        self.ui_expert = AssistantAgent(
            name="UI_Expert",
            model_client=self.uitars_model_client,
            system_message=load_prompt(PromptNames.UI_EXPERT),
            model_client_stream=self.settings.enable_streaming,
        )

        # 2. 交互分析师 - 负责交互行为分析（使用 UI-TARS 模型）
        self.interaction_analyst = AssistantAgent(
            name="Interaction_Analyst",
            model_client=self.uitars_model_client,
            system_message=load_prompt(PromptNames.INTERACTION_ANALYST),
            model_client_stream=self.settings.enable_streaming,
        )

        # 3. 测试场景专家 - 负责综合分析和测试场景设计（使用默认对话模型 deepseek）
        self.test_scenario_expert = AssistantAgent(
            name="Test_Scenario_Expert",
            model_client=self.default_model_client,
            system_message=load_prompt(PromptNames.TEST_SCENARIO_EXPERT),
            model_client_stream=self.settings.enable_streaming,
        )

        print(f"   ✓ 已创建 3 个团队成员")
        print(f"     - {self.ui_expert.name} (UI-TARS 模型)")
        print(f"     - {self.interaction_analyst.name} (UI-TARS 模型)")
        print(f"     - {self.test_scenario_expert.name} (DeepSeek 对话模型)")

        return [self.ui_expert, self.interaction_analyst, self.test_scenario_expert]

    def create_team_workflow(self) -> GraphFlow:
        """
        创建 GraphFlow 工作流

        工作流结构（并行执行，前端顺序展示）：
        ┌─────────────┐
        │  用户输入    │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    UI_Expert   Interaction_Analyst
        │             │
        └──────┬──────┘
               │
               ▼
        Test_Scenario_Expert
        """
        # 创建 DiGraphBuilder
        builder = DiGraphBuilder()

        # 添加节点
        builder.add_node(self.ui_expert)
        builder.add_node(self.interaction_analyst)
        builder.add_node(self.test_scenario_expert)

        # 添加边：UI_Expert 和 Interaction_Analyst 并行处理
        # 两者都完成后，结果汇总到 Test_Scenario_Expert
        builder.add_edge(self.ui_expert, self.test_scenario_expert)
        builder.add_edge(self.interaction_analyst, self.test_scenario_expert)

        # 构建图
        graph = builder.build()

        # 创建终止条件：最大消息数
        termination_condition = MaxMessageTermination(20)

        # 创建 GraphFlow 团队
        team = GraphFlow(
            participants=builder.get_participants(),
            graph=graph,
            termination_condition=termination_condition,
        )

        print(f"   ✓ GraphFlow 工作流已建立")

        return team

    def get_agent_type(self) -> str:
        """
        获取智能体类型

        返回:
            智能体类型标识符
        """
        return "image_analysis_team"

    async def cleanup(self) -> None:
        """清理资源"""
        if self.uitars_model_client:
            try:
                await self.uitars_model_client.close()
                print(f"🧹 {self.name} UI-TARS 模型客户端已清理")
            except Exception as e:
                print(f"⚠️ 清理 {self.name} UI-TARS 模型客户端时出错: {e}")

        if self.default_model_client:
            try:
                await self.default_model_client.close()
                print(f"🧹 {self.name} 默认模型客户端已清理")
            except Exception as e:
                print(f"⚠️ 清理 {self.name} 默认模型客户端时出错: {e}")

        # 调用父类的清理方法
        await super().cleanup()

    async def analyze_image(
        self,
        session_id: Optional[str] = None,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        web_url: Optional[str] = None,
        test_description: Optional[str] = None,
        additional_context: Optional[str] = None,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析 UI 图片

        参数:
            session_id: 会话 ID
            image_data: 图片字节流base64编码
            image_url: 图片路径（本地路径或 URL）
            web_url: 图片所在页面的 URL
            test_description: 测试场景描述
            additional_context: 附加上下文信息
            target_url: 目标页面 URL

        返回:
            分析结果字典，包含：
            - ui_analysis: UI 专家的分析
            - interaction_analysis: 交互分析师的分析
            - test_scenarios: 测试场景专家的综合分析
            - chat_history: 完整的对话历史
        """
        if not self.team:
            raise RuntimeError("团队未初始化，请先调用 initialize()")

        # 验证至少提供了一种图片来源
        if not image_data and not image_url:
            raise ValueError("必须提供 image_data 或 image_url 中的至少一个")

        # 构建任务描述
        task = self._build_task_message(
            session_id=session_id,
            image_data=image_data,
            image_url=image_url,
            web_url=web_url,
            test_description=test_description,
            additional_context=additional_context,
            target_url=target_url
        )

        print(f"\n🔍 开始分析 UI 图片...")
        if session_id:
            print(f"   会话 ID: {session_id}")
        if image_url:
            print(f"   图片 URL: {image_url}")
        if image_data:
            print(f"   图片数据: base64 编码（{len(image_data)} 字符）")
        if web_url:
            print(f"   页面 URL: {web_url}")
        if test_description:
            print(f"   测试描述: {test_description}")

        # 运行团队分析
        result = await self.team.run(task=task)

        # 解析分析结果
        analysis_results = self._parse_analysis_results(result)

        print(f"\n✅ UI 图片分析完成！")
        print(f"   消息总数: {len(result.messages)}")

        return analysis_results

    async def analyze_image_stream(
        self,
        session_id: Optional[str] = None,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        web_url: Optional[str] = None,
        test_description: Optional[str] = None,
        additional_context: Optional[str] = None,
        target_url: Optional[str] = None
    ):
        """
        流式分析 UI 图片（支持实时输出）

        参数:
            session_id: 会话 ID
            image_data: 图片字节流base64编码
            image_url: 图片路径（本地路径或 URL）
            web_url: 图片所在页面的 URL
            test_description: 测试场景描述
            additional_context: 附加上下文信息
            target_url: 目标页面 URL

        生成:
            分析过程中的事件流
        """
        if not self.team:
            raise RuntimeError("团队未初始化，请先调用 initialize()")

        # 验证至少提供了一种图片来源
        if not image_data and not image_url:
            raise ValueError("必须提供 image_data 或 image_url 中的至少一个")

        # 构建任务描述
        task = self._build_task_message(
            session_id=session_id,
            image_data=image_data,
            image_url=image_url,
            web_url=web_url,
            test_description=test_description,
            additional_context=additional_context,
            target_url=target_url
        )

        print(f"\n🔍 开始流式分析 UI 图片...")
        if session_id:
            print(f"   会话 ID: {session_id}")
        if image_url:
            print(f"   图片 URL: {image_url}")

        # 运行团队分析（流式）
        async for event in self.team.run_stream(task=task):
            yield event

    def _build_task_message(
        self,
        session_id: Optional[str] = None,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        web_url: Optional[str] = None,
        test_description: Optional[str] = None,
        additional_context: Optional[str] = None,
        target_url: Optional[str] = None
    ) -> Union[TextMessage, MultiModalMessage]:
        """
        构建任务消息（支持多模态）

        参数:
            session_id: 会话 ID
            image_data: 图片字节流base64编码
            image_url: 图片路径（本地路径或 URL）
            web_url: 图片所在页面 URL
            test_description: 测试场景描述
            additional_context: 附加上下文信息
            target_url: 目标页面 URL

        返回:
            MultiModalMessage（如果有图片）或 TextMessage
        """
        # 构建文本部分
        text_parts = []

        # 添加会话信息
        if session_id:
            text_parts.append(f"会话 ID: {session_id}\n")

        # 添加分析任务说明
        text_parts.append("请分析以下 UI 界面图片：\n")

        # 添加页面 URL 信息
        if web_url:
            text_parts.append(f"图片所在页面 URL: {web_url}\n")

        # 添加目标 URL 信息
        if target_url:
            text_parts.append(f"目标页面 URL: {target_url}\n")

        # 添加测试描述
        if test_description:
            text_parts.append(f"测试场景描述: {test_description}\n")

        # 添加附加上下文
        if additional_context:
            text_parts.append(f"附加上下文信息: {additional_context}\n")

        # 添加工作流程说明
        text_parts.extend([
            "\n工作流程说明：",
            "1. UI_Expert 和 Interaction_Analyst 将并行分析图片（使用 UI-TARS 模型）",
            "   - UI_Expert: 分析界面的视觉元素、布局结构、设计规范",
            "   - Interaction_Analyst: 分析界面的交互行为、用户流程、操作逻辑",
            "",
            "2. 两位专家完成分析后，系统会整理他们的分析结果",
            "",
            "3. Test_Scenario_Expert 将基于整理后的信息（纯文本），设计全面的测试场景",
            "   - 注意：Test_Scenario_Expert 不会看到图片，只会看到前两位专家的文字分析",
            "   - 请基于文字描述设计测试用例和测试场景",
            "",
            "请各位专家按照自己的职责进行分析。",
        ])

        text_content = "\n".join(text_parts)

        # 如果有图片，创建多模态消息
        if image_url or image_data:
            content: List[Union[str, Image]] = [text_content]

            if image_url:
                # 使用 image_url
                content.append(Image.from_uri(image_url))
            elif image_data:
                # 使用 base64 数据
                content.append(Image.from_base64(image_data))

            return MultiModalMessage(content=content, source="user")
        else:
            # 纯文本消息
            return TextMessage(content=text_content, source="user")

    def _parse_analysis_results(self, result: TaskResult) -> Dict[str, Any]:
        """
        解析团队分析结果

        参数:
            result: 团队运行结果

        返回:
            结构化的分析结果
        """
        analysis_results = {
            "ui_analysis": [],
            "interaction_analysis": [],
            "test_scenarios": [],
            "chat_history": [],
            "summary": "",
        }

        # 遍历所有消息
        for message in result.messages:
            # 保存完整对话历史
            if isinstance(message, TextMessage):
                analysis_results["chat_history"].append({
                    "source": message.source,
                    "content": message.content,
                })

                # 根据来源分类
                if message.source == "UI_Expert":
                    analysis_results["ui_analysis"].append(message.content)
                elif message.source == "Interaction_Analyst":
                    analysis_results["interaction_analysis"].append(message.content)
                elif message.source == "Test_Scenario_Expert":
                    analysis_results["test_scenarios"].append(message.content)

        # 生成摘要
        analysis_results["summary"] = self._generate_summary(analysis_results)

        return analysis_results

    def _generate_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成分析摘要

        参数:
            analysis_results: 分析结果

        返回:
            摘要文本
        """
        summary_parts = [
            "=== UI 图片分析摘要 ===",
            "",
            f"UI 分析条目数: {len(analysis_results['ui_analysis'])}",
            f"交互分析条目数: {len(analysis_results['interaction_analysis'])}",
            f"测试场景条目数: {len(analysis_results['test_scenarios'])}",
            f"总消息数: {len(analysis_results['chat_history'])}",
            "",
            "分析已完成，可用于后续的测试脚本生成。",
        ]

        return "\n".join(summary_parts)
