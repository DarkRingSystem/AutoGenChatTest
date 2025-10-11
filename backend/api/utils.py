"""
API 工具函数
"""
from typing import List, Optional


def build_message_with_file_context(message: str, file_ids: Optional[List[str]] = None) -> str:
    """
    构建包含文件上下文的消息
    
    Args:
        message: 用户消息
        file_ids: 文件 ID 列表（可选）
    
    Returns:
        包含文件上下文的完整消息
    """
    if not file_ids:
        # 如果没有文件，直接返回原始消息
        return message
    
    # TODO: 实现文件内容读取和上下文构建
    # 目前只是简单地附加文件 ID 信息
    file_context = f"\n\n[附加文件: {', '.join(file_ids)}]"
    
    return message + file_context

