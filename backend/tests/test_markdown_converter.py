"""
Markdown 转换服务测试

测试 MarkdownConverterService 的各项功能
"""
import pytest
import asyncio
import os
from pathlib import Path

from services.markdown_converter_service import MarkdownConverterService


class TestMarkdownConverterService:
    """Markdown 转换服务测试类"""
    
    def test_initialization(self):
        """测试服务初始化"""
        converter = MarkdownConverterService()
        
        assert converter.use_llm == False
        assert converter.force_ocr == False
        assert converter.disable_image_extraction == False
        assert converter.output_format == "markdown"
    
    def test_initialization_with_llm(self):
        """测试带 LLM 的服务初始化"""
        converter = MarkdownConverterService(
            use_llm=True,
            llm_service="marker.services.openai.OpenAIService",
            llm_api_key="test-key",
            llm_base_url="https://api.openai.com/v1",
            llm_model="gpt-4"
        )
        
        assert converter.use_llm == True
        assert "llm_service" in converter.config
        assert converter.config["openai_api_key"] == "test-key"
    
    def test_get_supported_formats(self):
        """测试获取支持的文件格式"""
        converter = MarkdownConverterService()
        formats = converter.get_supported_formats()
        
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert ".pdf" in formats
        assert ".png" in formats
        assert ".docx" in formats
    
    def test_is_supported_file(self):
        """测试文件格式检查"""
        converter = MarkdownConverterService()
        
        # 支持的格式
        assert converter.is_supported_file("document.pdf") == True
        assert converter.is_supported_file("image.png") == True
        assert converter.is_supported_file("presentation.pptx") == True
        assert converter.is_supported_file("spreadsheet.xlsx") == True
        
        # 不支持的格式
        assert converter.is_supported_file("text.txt") == False
        assert converter.is_supported_file("video.mp4") == False
    
    @pytest.mark.asyncio
    async def test_convert_file_not_exists(self):
        """测试转换不存在的文件"""
        converter = MarkdownConverterService()
        
        result = await converter.convert_file("/path/to/nonexistent/file.pdf")
        
        assert result["success"] == False
        assert "不存在" in result["message"]
        assert result["markdown"] == ""
    
    @pytest.mark.asyncio
    async def test_convert_image_file(self):
        """测试转换图片文件"""
        converter = MarkdownConverterService(
            force_ocr=True,
            disable_image_extraction=False
        )
        
        # 使用示例中的图片文件
        file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
        
        if os.path.exists(file_path):
            result = await converter.convert_file(file_path)
            
            assert result["success"] == True
            assert "markdown" in result
            assert "metadata" in result
            assert "images" in result
        else:
            pytest.skip(f"测试文件不存在: {file_path}")
    
    @pytest.mark.asyncio
    async def test_convert_file_bytes(self):
        """测试从字节流转换"""
        converter = MarkdownConverterService()
        
        # 使用示例中的图片文件
        file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            result = await converter.convert_file_bytes(
                file_bytes=file_bytes,
                filename="test.png"
            )
            
            assert result["success"] == True
            assert "markdown" in result
        else:
            pytest.skip(f"测试文件不存在: {file_path}")
    
    def test_config_with_different_llm_services(self):
        """测试不同 LLM 服务的配置"""
        
        # OpenAI
        converter_openai = MarkdownConverterService(
            use_llm=True,
            llm_service="marker.services.openai.OpenAIService",
            llm_api_key="test-key",
            llm_base_url="https://api.openai.com/v1",
            llm_model="gpt-4"
        )
        assert "openai_api_key" in converter_openai.config
        assert converter_openai.config["openai_api_key"] == "test-key"
        
        # Gemini
        converter_gemini = MarkdownConverterService(
            use_llm=True,
            llm_service="marker.services.gemini.GoogleGeminiService",
            llm_api_key="test-key",
            llm_model="gemini-pro"
        )
        assert "gemini_api_key" in converter_gemini.config
        
        # Claude
        converter_claude = MarkdownConverterService(
            use_llm=True,
            llm_service="marker.services.claude.ClaudeService",
            llm_api_key="test-key",
            llm_model="claude-3"
        )
        assert "claude_api_key" in converter_claude.config


class TestMarkdownConverterAPI:
    """Markdown 转换 API 测试类"""
    
    @pytest.mark.asyncio
    async def test_api_supported_formats(self, client):
        """测试获取支持格式的 API"""
        response = await client.get("/api/convert/supported-formats")
        
        assert response.status_code == 200
        data = response.json()
        assert "supported_formats" in data
        assert "total" in data
        assert data["total"] > 0
    
    @pytest.mark.asyncio
    async def test_api_convert_without_file(self, client):
        """测试不提供文件的转换 API"""
        response = await client.post("/api/convert/markdown")
        
        # 应该返回 422 错误（缺少必需参数）
        assert response.status_code == 422


# 运行测试的辅助函数
def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()

