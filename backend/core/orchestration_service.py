'''
编排服务模块
负责管理多个智能体的交互和编排
包括会话管理、消息路由、异常处理等

流程：
1 初始化
2 运行单线程运行环境（分布式运行时，修改此参数）
3 注册智能体（注册该功能使用到的所有智能体）
4 发送初始消息
5 处理消息循环
6 清理资源

'''

import logging
from autogen_core import SingleThreadedAgentRuntime, TopicId

class NormalChatOrchestration:
    """普通对话编排服务类"""
    async def _initialize_runtime(self, session_id: str) -> None:
        try:
            if self.runtime is None:
                self.runtime = SingleThreadedAgentRuntime() 

            # 注册普通对话智能体
            await self.__register_normal_chat_agents()

            # 注册流式响应搜集器
            await self.agent_factory.register_register_stream_collector(
                runtime = self.runtime,
                collector = self.response_collector
            )

            # 启动运行时
            self.runtime.start()

            logging.info(f"运行时初始化完成: {session_id}")

        except Exception as e:
            logging.error(f"运行时初始化失败: {str(e)}")
            raise e

        async def __register_normal_chat_agents(self) -> None:
             # 注册测试用例生成智能体
            await self.agent_factory.register_agent_to_runtime(
                self.runtime, 
                agent_type="normal_chat_agent"
                topic_type=TopicId("normal_chat_agent")
            # 注册所有普通对话相关智能体
            await self._register_test_case_agents()

            logging.info(f"普通对话智能体注册完成")

            # 发送信息到主题"normal_chat_agent"
            await self.runtime.publish_message(
                topic=TopicId("normal_chat_agent"),
                message="开始普通对话"
            )
    except Exception as e:
        print(f"❌ 普通对话编排服务初始化失败: {e}")

# class TesatCaseChatOrchestration:
#     """用例团队编排服务类"""
#     async def __init__(self) -> None:
#         self.runtime = SingleThreadedAgentRuntime()
#         self.topic_id = TopicId("testcase")