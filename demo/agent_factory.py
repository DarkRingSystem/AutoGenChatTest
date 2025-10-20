from typing import Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_core import SingleThreadedAgentRuntime, TopicId
from pydantic import BaseModel, Field
from autogen_ext.models.openai import OpenAIChatCompletionClient
import logging


"""
用于创建和管理 AutoGen 智能体的工厂模块
"""

class AgentFactoryRequest(BaseModel):
    """创建智能体请求模型"""
    session_id: Optional[str] = Field(None, description="会话 ID")
    agent_name: str = Field(None, description="智能体名称")
    model_client: OpenAIChatCompletionClient = Field(None, description="模型客户端")
    file_ids: Optional[list[str]] = Field(None, description="已解析文件的 ID 列表")
    model_client_stream: Optional[bool] = Field(True, description="是否使用流式传输")
    system_message: Optional[str] = Field(None, description="系统消息")

class AgentFactory(AgentFactoryRequest):
    """
    智能体工厂类
    传参创建相应的AssistantAgent实例
    """
    async def __init__(AgentFactoryRequest) -> None:
        super().__init__(AgentFactoryRequest)
        logging.info(f"✅ 智能体工厂已初始化，即将创建智能体: {AgentFactoryRequest.agent_name}")
    
    async def create_agent(AgentFactoryRequest) -> AssistantAgent:
        """创建 AutoGen 智能体"""
        agent = AssistantAgent(
            name = AgentFactoryRequest.agent_name,
            model_client = AgentFactoryRequest.model_client,
            system_message = AgentFactoryRequest.system_message,
            model_client_stream=AgentFactoryRequest.model_client_stream,
        )
        return agent
        logging.info(f"✅ 智能体 {agent.name} 已创建")
    
    async def register_agent_to_runtime(self, runtime: SingleThreadedAgentRuntime, agent_type: str, topic_type: TopicId, agent: AssistantAgent) -> None:
        """将智能体注册到运行时"""
        try:
            if self.agent is None:
                raise ValueError("智能体实例不能为空")          

            # 注册智能体
            await runtime.register_agent(
                agent=self.agent,
                agent_type=agent_type,
                topic_type=topic_type,
                lambda: self.create_agent(agent_type,**Kwargs)
            )
            logging.info(f"✅ 智能体 {self.agent.name} 已注册到运行时")
        
        except Exception as e:
            logging.error(f"❌ 智能体注册失败: {str(e)}")
            logging.error(f"❌ 错误类型: {type(e)}")

    async def register_stream_collector(self, runtime: SingleThreadedAgentRuntime, collector: ResponseCollector) -> None:
        """将流式响应搜集器注册到运行时"""
        try:
            await runtime.register_stream_collector(collector)
            logging.info(f"✅ 流式响应搜集器已注册到运行时")
        except Exception as e:
            logging.error(f"❌ 流式响应搜集器注册失败: {str(e)}")


