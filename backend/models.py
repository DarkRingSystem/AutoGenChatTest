"""
数据模型模块
定义请求和响应的数据结构
"""
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field

# 普通聊天的请求和响应模型
class ChatRequest(BaseModel):
    """普通聊天请求模型"""
    message: str = Field(..., min_length=1, description="用户消息内容")
    conversation_id: Optional[str] = Field(None, description="会话 ID")
    file_ids: Optional[list[str]] = Field(None, description="已解析文件的 ID 列表")
    is_feedback: bool = Field(default=False, description="是否为反馈消息")
    target_agent: Optional[str] = Field(None, description="目标智能体名称（用于反馈）")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "你好，请介绍一下量子计算",
                "conversation_id": "conv_123",
                "file_ids": ["file_123", "file_456"],
                "is_feedback": False,
                "target_agent": None
            }
        }


class ChatResponse(BaseModel):
    """普通聊天响应模型"""
    message: str = Field(..., description="AI 回复内容")
    conversation_id: str = Field(..., description="会话 ID")
    status: str = Field(default="success", description="响应状态")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "量子计算是一种利用量子力学原理进行计算的技术...",
                "conversation_id": "conv_123",
                "status": "success"
            }
        }

# 健康检查的响应模型
class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: Literal["healthy", "unhealthy"] = Field(..., description="服务状态")
    agent_initialized: bool = Field(..., description="AI 智能体是否已初始化")
    session_count: Optional[int] = Field(None, description="当前会话数量")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "agent_initialized": True,
                "session_count": 5
            }
        }


class TokenUsage(BaseModel):
    """Token 使用统计模型"""
    total: int = Field(0, description="总 token 数")
    input: int = Field(0, description="输入 token 数")
    output: int = Field(0, description="输出 token 数")

    def format_display(self) -> str:
        """格式化显示"""
        return f"Tokens:{self.total}↑{self.input}↓{self.output}"


class SSEMessage(BaseModel):
    """SSE 消息模型"""
    type: Literal["status", "chunk", "message", "tool_call", "tool_result", "done", "error", "tokens", "token_usage", "agent_start", "agent_message", "agent_done", "feedback_request"]
    content: str | dict | list
    tokens: Optional[TokenUsage] = Field(None, description="Token 使用统计")
    token_usage: Optional[Dict[str, Any]] = Field(None, description="Token 使用详情")
    agent_name: Optional[str] = Field(None, description="智能体名称")
    agent_role: Optional[str] = Field(None, description="智能体角色")
    available_agents: Optional[list[str]] = Field(None, description="可用的智能体列表")
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


class MarkdownConvertRequest(BaseModel):
    """Markdown 转换请求模型"""
    use_llm: bool = Field(default=False, description="是否使用 LLM 提升转换精度")
    force_ocr: bool = Field(default=False, description="是否强制对所有内容进行 OCR")
    disable_image_extraction: bool = Field(default=False, description="是否禁用图片提取")
    page_range: Optional[str] = Field(None, description="页面范围，例如: '0,5-10,20'")
    output_format: str = Field(default="markdown", description="输出格式 (markdown, json, html, chunks)")

    class Config:
        json_schema_extra = {
            "example": {
                "use_llm": False,
                "force_ocr": False,
                "disable_image_extraction": False,
                "page_range": "0-10",
                "output_format": "markdown"
            }
        }


class MarkdownConvertResponse(BaseModel):
    """Markdown 转换响应模型"""
    success: bool = Field(..., description="转换是否成功")
    message: str = Field(..., description="响应消息")
    markdown: str = Field(default="", description="转换后的 Markdown 文本")
    metadata: dict = Field(default_factory=dict, description="文档元数据")
    images: dict = Field(default_factory=dict, description="提取的图片字典")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "转换成功",
                "markdown": "# 文档标题\n\n这是转换后的内容...",
                "metadata": {
                    "page_count": 10,
                    "table_of_contents": []
                },
                "images": {}
            }
        }


class BatchMarkdownConvertResponse(BaseModel):
    """批量 Markdown 转换响应模型"""
    total: int = Field(..., description="总文件数")
    success_count: int = Field(..., description="成功转换的文件数")
    failed_count: int = Field(..., description="转换失败的文件数")
    results: list[dict] = Field(..., description="每个文件的转换结果")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "success_count": 2,
                "failed_count": 1,
                "results": [
                    {
                        "filename": "doc1.pdf",
                        "success": True,
                        "markdown": "# 文档1...",
                        "metadata": {},
                        "images": {}
                    },
                    {
                        "filename": "doc2.pdf",
                        "success": True,
                        "markdown": "# 文档2...",
                        "metadata": {},
                        "images": {}
                    },
                    {
                        "filename": "doc3.pdf",
                        "success": False,
                        "message": "转换失败: 文件损坏"
                    }
                ]
            }
        }



class ImageAnalysisRequest(BaseModel):
    """图片分析请求模型"""
    session_id: Optional[str] = Field(None, description="会话 ID")
    image_data: Optional[str] = Field(None, description="图片 base64 编码数据")
    image_url: Optional[str] = Field(None, description="图片 URL")
    web_url: Optional[str] = Field(None, description="图片所在页面的 URL")
    test_description: Optional[str] = Field(None, description="测试场景描述")
    additional_context: Optional[str] = Field(None, description="附加上下文信息")
    target_url: Optional[str] = Field(None, description="目标页面 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "img_session_001",
                "image_url": "https://example.com/screenshot.png",
                "web_url": "https://example.com/login",
                "test_description": "登录页面 UI 测试",
                "additional_context": "需要重点关注表单验证"
            }
        }


class ImageAnalysisResponse(BaseModel):
    """图片分析响应模型"""
    session_id: str = Field(..., description="会话 ID")
    ui_analysis: List[str] = Field(..., description="UI 专家的分析结果")
    interaction_analysis: List[str] = Field(..., description="交互分析师的分析结果")
    test_scenarios: List[str] = Field(..., description="测试场景专家的分析结果")
    chat_history: List[Dict[str, str]] = Field(..., description="完整对话历史")
    summary: str = Field(..., description="分析摘要")
    status: str = Field(default="success", description="响应状态")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "img_session_001",
                "ui_analysis": ["页面包含登录表单，包括用户名和密码输入框..."],
                "interaction_analysis": ["用户需要输入用户名和密码，然后点击登录按钮..."],
                "test_scenarios": ["场景1：正常登录流程测试..."],
                "chat_history": [
                    {"source": "user", "content": "请分析这个登录页面"},
                    {"source": "UI_Expert", "content": "这是一个标准的登录页面..."}
                ],
                "summary": "该登录页面包含标准的用户名密码输入框...",
                "status": "success"
            }
        }
