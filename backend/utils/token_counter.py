"""
Token 计数工具模块
用于估算文本的 token 数量
"""
import tiktoken
from typing import Optional


class TokenCounter:
    """Token 计数器类"""
    
    def __init__(self, model: str = "gpt-4"):
        """
        初始化 Token 计数器
        
        参数:
            model: 模型名称，用于选择合适的编码器
        """
        try:
            # 尝试获取模型的编码器
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 如果模型不存在，使用 cl100k_base（GPT-4 的编码器）
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        参数:
            text: 要计算的文本
            
        返回:
            token 数量
        """
        if not text:
            return 0
        
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception:
            # 如果编码失败，使用简单估算（平均每个字符 0.25 个 token）
            return len(text) // 4
    
    def count_messages_tokens(self, messages: list) -> int:
        """
        计算消息列表的总 token 数量
        
        参数:
            messages: 消息列表
            
        返回:
            总 token 数量
        """
        total = 0
        for message in messages:
            if isinstance(message, dict):
                # 消息格式：{"role": "user", "content": "..."}
                total += self.count_tokens(message.get("content", ""))
                # 每条消息的元数据大约 4 个 token
                total += 4
            elif isinstance(message, str):
                total += self.count_tokens(message)
        
        return total


# 全局单例
_token_counter: Optional[TokenCounter] = None


def get_token_counter(model: str = "gpt-4") -> TokenCounter:
    """
    获取 Token 计数器单例
    
    参数:
        model: 模型名称
        
    返回:
        TokenCounter 实例
    """
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter(model)
    return _token_counter

