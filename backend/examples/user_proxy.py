import autogen
from typing import List, Dict, Any, Union

# 请在这里设置你的 LLM API 配置
# 例如，使用 OpenAI 的 GPT-4
config_list = [{
    "model": "gpt-4-turbo",
    "api_key": "sk-...",  # 你的 OpenAI API Key
}]


#### 第 2 步：定义我们的智能体

# 定义 UserProxyAgent，它代表人类用户
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="TERMINATE",  # 每次群聊结束后，会询问用户是否继续或终止
    max_consecutive_auto_reply=10,
    code_execution_config=False,  # 此示例中我们不实际执行代码
    system_message="You are the user. You can provide tasks and give feedback on the results. "
                   "To direct a message to a specific agent for revision, please use the '@' symbol, "
                   "for example: '@Coder, please fix the bug.'",
)

# 定义 Coder Agent
coder = autogen.AssistantAgent(
    name="Coder",
    llm_config={"config_list": config_list},
    system_message="You are a senior python programmer. You write clean, efficient, and correct code. "
                   "When you receive feedback, you will revise your code based on the instructions."
)

# 定义 Product Manager Agent
pm = autogen.AssistantAgent(
    name="Product_Manager",
    llm_config={"config_list": config_list},
    system_message="You are a product manager. Your job is to clarify requirements, "
                   "break down tasks, and ensure the final product meets the user's needs."
)

#### 第 3 步：创建自定义的发言者选择函数 (核心)


def custom_speaker_selection_func(
        last_speaker: autogen.Agent,
        groupchat: autogen.GroupChat
) -> Union[autogen.Agent, str, None]:
    """
    自定义发言者选择函数，实现 @AgentName 的定向消息功能。
    """
    messages = groupchat.messages

    # 检查最后一条消息是否来自用户
    if len(messages) > 1 and last_speaker.name == "User_Proxy":
        last_msg = messages[-1]['content']

        # 遍历所有可选的智能体，检查是否被 @ 提及
        for agent in groupchat.agents:
            if f"@{agent.name}" in last_msg:
                # 如果找到，直接将下一个发言权交给被提及的智能体
                print(f"[DEBUG] User directed message to {agent.name}. Forcing next speaker.")
                return agent

    # 如果没有检测到用户指定，则回退到默认的 'auto' 模式
    # 'auto' 模式会使用 LLM 来决定下一个发言者
    print("[DEBUG] No specific agent mentioned by user. Using 'auto' selection.")
    return 'auto'



#### 第 4 步：设置群聊并启动对话

# 创建一个包含所有智能体的列表
agents = [user_proxy, coder, pm]

# 创建 GroupChat 对象
group_chat = autogen.GroupChat(
    agents=agents,
    messages=[],
    max_round=12
)

# 创建 GroupChatManager，并传入我们的自定义函数！
manager = autogen.GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list},
    # 这里是关键！
    speaker_selection_method=custom_speaker_selection_func
)

# 启动对话
user_proxy.initiate_chat(
    manager,
    message="Please write a simple Python function to add two numbers."
)


# Coder's possible response
def add(a, b):
    return a + b


# Coder's revised response
def add(a: int, b: int) -> int:
    return a + b
