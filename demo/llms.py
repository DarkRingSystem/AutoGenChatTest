import os

from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

def get_model_client() -> OpenAIChatCompletionClient:
    openai_model_client = OpenAIChatCompletionClient(
        model=os.getenv("MODEL_NAME"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY"),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": ModelFamily.UNKNOWN,
            "multiple_system_messages": True,
        }
    )
    return openai_model_client

model_client = get_model_client()
