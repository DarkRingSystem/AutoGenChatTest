"""
normal_chat数据模块
定义请求和响应的数据结构
"""

"""
字段规则
会话id统一使用session_id,值为uuid
"""
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field

# 普通聊天的请求和响应模型
class NormalChatRequest(BaseModel):
    """普通聊天请求模型"""
    message: str = Field(..., min_length=1, description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话 ID")
    file_ids: Optional[list[str]] = Field(None, description="已解析文件的 ID 列表")
    is_feedback: Optional[bool] = Field(default=False, description="是否为反馈消息")
    target_agent: Optional[str] = Field(None, description="目标智能体名称")


    class Config:
        json_schema_extra = {
            "example": {
                "message": "你好，请介绍一下量子计算",
                "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "file_ids": ["file_123", "file_456"],
                "is_feedback": False,
                "target_agent": None
            }
        }


# class ChatResponse(BaseModel):
#     """普通聊天非流式响应模型"""
#     message: str = Field(..., description="AI 回复内容")
#     session_id: str = Field(..., description="会话 ID")
#     status: str = Field(default="success", description="响应状态")

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "message": "量子计算是一种利用量子力学原理进行计算的技术...",
#                 "conversation_id": "conv_123",
#                 "status": "success"
#             }
#         }

class TokenUsage(BaseModel):
    """Token 使用统计模型"""
    total: int = Field(0, description="总 token 数")
    input: int = Field(0, description="输入 token 数")
    output: int = Field(0, description="输出 token 数")

    def format_display(self) -> str:
        """格式化显示"""
        return f"Tokens:{self.total}↑{self.input}↓{self.output}"

class NormalChatStreamResponse(BaseModel):
    """普通聊天流式SSE响应模型"""
    type: Literal["status", "chunk", "message", "tool_call", "tool_result", "done", "error", "tokens", "token_usage", "agent_start", "agent_message", "agent_done", "feedback_request"]
    content: str | dict | list
    tokens: Optional[TokenUsage] = Field(None, description="Token 使用统计")
    token_usage: Optional[Dict[str, Any]] = Field(None, description="Token 使用详情")
    agent_name: Optional[str] = Field(None, description="智能体名称")
    session_id: Optional[str] = Field(None, description="会话 ID")

    def to_sse_format(self) -> str:
        """转换为 SSE 格式"""
        import json
        return f"data: {json.dumps(self.model_dump())}\n\n"

class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="错误详情")
    status_code: int = Field(..., description="HTTP 状态码")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "消息不能为空",
                "status_code": 400
            }
        }