import asyncio
from autogen_core import AgentId, BaseAgent, SingleThreadedAgentRuntime
from dataclasses import dataclass
from typing import Callable
from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler
from pydantic import BaseModel

# 定义一个消息类

class Message(BaseModel):
    content: str






# 定义一个修改器智能体 继承RoutedAgent这个基础类
@default_subscription
class Modifier(BaseAgent):
    def __init__(self, modify_val: Callable[[int], int]) -> None:
        super().__init__("A modifier agent.")
        self._modify_val = modify_val

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        val = self._modify_val(message.content)
        print(f"{'-'*80}\nModifier:\nModified {message.content} to {val}")
        await self.publish_message(Message(content=val), DefaultTopicId())  # type: ignore


@default_subscription
class Checker(BaseAgent):
    def __init__(self, run_until: Callable[[int], bool]) -> None:
        super().__init__("A checker agent.")
        self._run_until = run_until

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        if not self._run_until(message.content):
            print(f"{'-'*80}\nChecker:\n{message.content} passed the check, continue.")
            await self.publish_message(Message(content=message.content), DefaultTopicId())
        else:
            print(f"{'-'*80}\nChecker:\n{message.content} failed the check, stopping.")

#创建一个运行时环境
runtime = SingleThreadedAgentRuntime()

# Register the modifier and checker agents by providing

# their agent types, the factory functions for creating instance and subscriptions.
async def main():

    await Modifier.register(
        runtime,
        "modifier",
        # Modify the value by subtracting 1
        lambda: Modifier(lambda x: f"笑话: {x}"),
    )

    await Checker.register(
        runtime,
        "checker",
        # Run until the value is less than or equal to 1
        lambda: Checker(lambda x: f"翻译: {x}"),
    )

    # Start the runtime and send a direct message to the checker.
    runtime.start()
    await runtime.send_message(Message(10), AgentId("checker", "default"))
    await runtime.stop_when_idle()

asyncio.run(main())