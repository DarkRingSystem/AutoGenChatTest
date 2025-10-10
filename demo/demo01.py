import asyncio
import logging
from autogen_core import EVENT_LOGGER_NAME
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


deepseek_model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-42502abc841f4df9ad01d4e07b9eed42",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "family": "deepseek",
        "multiple_system_messages": True,
    }
)

async def main():
    result = await deepseek_model_client.create([UserMessage(content="Hello World!", source="user")])
    print(result)
    await deepseek_model_client.close()

asyncio.run(main())
