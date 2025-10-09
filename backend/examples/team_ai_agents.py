import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from config import Settings


# Create an OpenAI model client.
model_client = OpenAIChatCompletionClient(
    model="deepseek",

    # api_key="sk-...", # Optional if you have an OPENAI_API_KEY env variable set.
)

# Create the Melchior-1 agent.
melchior_agent = AssistantAgent(
    "Melchior-1(Test Case Generation Agent)",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
    model_client_stream=True,
)

# Create the Balthasar-2 agent.
balthasar_agent = AssistantAgent(
    "Balthasar-2(Test Case Review Agent)",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    model_client_stream=True,
)

# Create the Casper-3 agent.
casper_agent = AssistantAgent(
    "Balthasar-2(Test Case Review Agent)",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    model_client_stream=True,
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the primary and critic agents.
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)
