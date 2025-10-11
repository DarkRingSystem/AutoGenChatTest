"""
API 工具函数
"""
from typing import List, Optional, Dict


def build_message_with_file_context(message: str, file_ids: Optional[List[str]] = None) -> str:
    """
    构建包含文件上下文的消息

    Args:
        message: 用户消息
        file_ids: 文件 ID 列表（可选）

    Returns:
        包含文件上下文的完整消息

    Note:
        此函数已弃用，请使用 routes.py 中的 _build_message_with_file_context
        保留此函数仅为向后兼容
    """
    if not file_ids:
        # 如果没有文件，直接返回原始消息
        return message

    # 导入 routes 中的实现
    from .routes import get_file_storage

    # 获取文件存储
    storage = get_file_storage()

    # 获取文件内容
    file_contexts = []
    for file_id in file_ids:
        if file_id in storage:
            file_data = storage[file_id]
            filename = file_data.get("filename", "unknown")
            markdown = file_data.get("markdown", "")

            if markdown:
                file_contexts.append(f"### 文件: {filename}\n\n{markdown}")

    if not file_contexts:
        # 如果没有找到文件内容，返回原始消息
        return message

    # 构建完整消息
    context_text = "\n\n---\n\n".join(file_contexts)
    full_message = f"""请结合以下文件内容和用户问题进行解答：

{context_text}

---

用户问题：{message}"""

    return full_message

