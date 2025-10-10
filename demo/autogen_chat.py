import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import ModelClientStreamingChunkEvent
from autogen_agentchat.ui import Console

from demo.llms import model_client

agent = AssistantAgent(
    name="normal_chat_assistant",
    description="一般聊天AI",
    system_message="You are a helpful AI assistant.",
    model_client=model_client,
    reflect_on_tool_use=True,
    model_client_stream=True,
)

# 非流式输出
async def main():
    result = await agent.run(task="你好")
    print(result)

# 流式输出
async def main_stream():
    #run_stream出参为一个迭代器
    #流式输出方法
    async for event in agent.run_stream(task="你好"):
        print(event)

# 控制台调试,调试可查看效果
async def mian_console():
    await Console(agent.run_stream(task="你好"))

# 流式输出并过滤AI回答，过滤掉用户消息和result消息
async def main_stream_with_chunk():
    #run_stream出参为一个迭代器
    #流式输出方法
    stream = ""
    async for event in agent.run_stream(task="你好"):
        if isinstance(event,ModelClientStreamingChunkEvent):
            stream += event.content
            print(event.content)



if __name__ == "__main__":
    asyncio.run(main_stream_with_chunk())