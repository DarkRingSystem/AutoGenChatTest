"""
API 工具函数
提供 API 路由使用的辅助函数
"""
from typing import Optional, List
from autogen_agentchat.base import TaskResult


def build_message_with_file_context(message: str, file_ids: Optional[List[str]] = None) -> str:
    """
    构建包含文件上下文的消息
    
    参数:
        message: 用户消息
        file_ids: 文件 ID 列表（可选）
    
    返回:
        包含文件上下文的消息
    """
    if not file_ids:
        return message
    
    # 如果有文件 ID，添加文件上下文提示
    file_context = f"\n\n[参考文件: {', '.join(file_ids)}]"
    return message + file_context


def extract_final_message(result: TaskResult) -> str:
    """
    从 TaskResult 中提取最终消息
    
    参数:
        result: AutoGen TaskResult 对象
    
    返回:
        最终消息文本
    """
    if not result or not result.messages:
        return ""
    
    # 获取最后一条消息
    last_message = result.messages[-1]
    
    # 提取消息内容
    if hasattr(last_message, 'content'):
        content = last_message.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 处理多模态消息
            text_parts = [item for item in content if isinstance(item, str)]
            return ' '.join(text_parts) if text_parts else str(content)
        else:
            return str(content)
    
    return str(last_message)

