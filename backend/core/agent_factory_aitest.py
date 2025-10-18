"""
优化的智能体工厂模块
基于 Microsoft AutoGen 框架的智能体创建和管理

主要优化：
1. 修复原有的语法错误和逻辑问题
2. 改进的错误处理和验证
3. 支持多种类型的智能体创建
4. 更好的资源管理和清理
"""

import logging
from typing import Optional, Dict, Any, List
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """智能体配置模型"""
    name: str = Field(..., description="智能体名称")
    system_message: Optional[str] = Field(None, description="系统消息")
    model_client: Optional[OpenAIChatCompletionClient] = Field(None, description="模型客户端")
    enable_streaming: bool = Field(True, description="是否启用流式传输")
    description: Optional[str] = Field(None, description="智能体描述")
    
    class Config:
        arbitrary_types_allowed = True


class AgentFactoryAitest:
    """
    优化的智能体工厂类
    
    负责创建和管理各种类型的 AutoGen 智能体
    """
    
    def __init__(self):
        """初始化智能体工厂"""
        self.created_agents: Dict[str, Any] = {}
        logger.info("🏭 智能体工厂已初始化")
    
    async def create_assistant_agent(
        self,
        name: str,
        model_client: OpenAIChatCompletionClient,
        system_message: Optional[str] = None,
        enable_streaming: bool = True,
        description: Optional[str] = None
    ) -> AssistantAgent:
        """
        创建助手智能体
        
        参数:
            name: 智能体名称
            model_client: 模型客户端
            system_message: 系统消息
            enable_streaming: 是否启用流式传输
            description: 智能体描述
            
        返回:
            AssistantAgent 实例
        """
        try:
            # 验证参数
            if not name or not name.strip():
                raise ValueError("智能体名称不能为空")
            
            if not model_client:
                raise ValueError("模型客户端不能为空")
            
            # 设置默认值
            if system_message is None:
                system_message = "你是一个有帮助的AI助手。请提供清晰、简洁和准确的回答。"
            
            if description is None:
                description = f"智能助手 - {name}"
            
            logger.info(f"🤖 开始创建助手智能体: {name}")
            
            # 创建智能体
            agent = AssistantAgent(
                name=name,
                model_client=model_client,
                system_message=system_message,
                description=description,
                model_client_stream=enable_streaming
            )
            
            # 保存到已创建的智能体字典
            self.created_agents[name] = {
                "agent": agent,
                "type": "AssistantAgent",
                "config": {
                    "name": name,
                    "system_message": system_message,
                    "enable_streaming": enable_streaming,
                    "description": description
                }
            }
            
            logger.info(f"✅ 助手智能体创建成功: {name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ 助手智能体创建失败: {name}, 错误: {str(e)}")
            raise e
    
    async def create_user_proxy_agent(
        self,
        name: str,
        input_func: Optional[callable] = None,
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: int = 10,
        code_execution_config: Optional[Dict[str, Any]] = None,
        system_message: Optional[str] = None
    ) -> UserProxyAgent:
        """
        创建用户代理智能体
        
        参数:
            name: 智能体名称
            input_func: 输入函数
            human_input_mode: 人工输入模式
            max_consecutive_auto_reply: 最大连续自动回复次数
            code_execution_config: 代码执行配置
            system_message: 系统消息
            
        返回:
            UserProxyAgent 实例
        """
        try:
            # 验证参数
            if not name or not name.strip():
                raise ValueError("智能体名称不能为空")
            
            # 设置默认值
            if system_message is None:
                system_message = "你是用户的代理，负责与其他智能体交互。"
            
            if code_execution_config is None:
                code_execution_config = False  # 默认禁用代码执行
            
            logger.info(f"👤 开始创建用户代理智能体: {name}")
            
            # 创建智能体
            agent = UserProxyAgent(
                name=name,
                input_func=input_func,
                human_input_mode=human_input_mode,
                max_consecutive_auto_reply=max_consecutive_auto_reply,
                code_execution_config=code_execution_config,
                system_message=system_message
            )
            
            # 保存到已创建的智能体字典
            self.created_agents[name] = {
                "agent": agent,
                "type": "UserProxyAgent",
                "config": {
                    "name": name,
                    "human_input_mode": human_input_mode,
                    "max_consecutive_auto_reply": max_consecutive_auto_reply,
                    "system_message": system_message
                }
            }
            
            logger.info(f"✅ 用户代理智能体创建成功: {name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ 用户代理智能体创建失败: {name}, 错误: {str(e)}")
            raise e
    
    def get_agent(self, name: str) -> Optional[Any]:
        """
        获取已创建的智能体
        
        参数:
            name: 智能体名称
            
        返回:
            智能体实例或 None
        """
        agent_info = self.created_agents.get(name)
        return agent_info["agent"] if agent_info else None
    
    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取智能体信息
        
        参数:
            name: 智能体名称
            
        返回:
            智能体信息字典或 None
        """
        return self.created_agents.get(name)
    
    def list_agents(self) -> List[str]:
        """
        列出所有已创建的智能体名称
        
        返回:
            智能体名称列表
        """
        return list(self.created_agents.keys())
    
    def get_agents_summary(self) -> Dict[str, Any]:
        """
        获取智能体摘要信息
        
        返回:
            智能体摘要字典
        """
        summary = {
            "total_count": len(self.created_agents),
            "agents": {}
        }
        
        for name, info in self.created_agents.items():
            summary["agents"][name] = {
                "type": info["type"],
                "config": info["config"]
            }
        
        return summary
    
    async def cleanup_agent(self, name: str) -> bool:
        """
        清理指定的智能体
        
        参数:
            name: 智能体名称
            
        返回:
            是否成功清理
        """
        try:
            if name not in self.created_agents:
                logger.warning(f"⚠️ 智能体不存在: {name}")
                return False
            
            agent_info = self.created_agents[name]
            agent = agent_info["agent"]
            
            # 如果智能体有清理方法，调用它
            if hasattr(agent, 'cleanup'):
                try:
                    await agent.cleanup()
                except Exception as e:
                    logger.warning(f"⚠️ 智能体清理方法调用失败: {name}, 错误: {str(e)}")
            
            # 从字典中移除
            del self.created_agents[name]
            
            logger.info(f"🧹 智能体已清理: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 智能体清理失败: {name}, 错误: {str(e)}")
            return False
    
    async def cleanup_all_agents(self) -> int:
        """
        清理所有智能体
        
        返回:
            成功清理的智能体数量
        """
        try:
            agent_names = list(self.created_agents.keys())
            cleaned_count = 0
            
            for name in agent_names:
                if await self.cleanup_agent(name):
                    cleaned_count += 1
            
            logger.info(f"🧹 已清理 {cleaned_count}/{len(agent_names)} 个智能体")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ 批量清理智能体失败: {str(e)}")
            return 0
    
    def validate_agent_config(self, config: AgentConfig) -> bool:
        """
        验证智能体配置
        
        参数:
            config: 智能体配置
            
        返回:
            是否有效
        """
        try:
            # 验证名称
            if not config.name or not config.name.strip():
                logger.error("❌ 智能体名称不能为空")
                return False
            
            # 验证模型客户端（如果提供）
            if config.model_client and not isinstance(config.model_client, OpenAIChatCompletionClient):
                logger.error("❌ 模型客户端类型不正确")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 智能体配置验证失败: {str(e)}")
            return False
