"""
Markdown 转换服务模块
基于 marker 库实现文件到 Markdown 的转换
参考: https://github.com/datalab-to/marker

注意：marker 模块使用延迟导入，避免启动时下载模型
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

# 延迟导入 marker 模块，避免启动时下载模型
# 这些模块会在实际使用时才导入


class MarkdownConverterService:
    """
    Markdown 转换服务类
    
    支持将 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 等文件转换为 Markdown 格式
    基于 marker 库实现高精度转换
    """
    
    def __init__(
        self,
        use_llm: bool = False,
        force_ocr: bool = False,
        disable_image_extraction: bool = False,
        output_format: str = "markdown",
        llm_service: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        """
        初始化 Markdown 转换服务
        
        参数:
            use_llm: 是否使用 LLM 提升转换精度
            force_ocr: 是否强制对所有内容进行 OCR
            disable_image_extraction: 是否禁用图片提取
            output_format: 输出格式 (markdown, json, html, chunks)
            llm_service: LLM 服务类路径 (如 marker.services.openai.OpenAIService)
            llm_api_key: LLM API 密钥
            llm_base_url: LLM API 基础 URL
            llm_model: LLM 模型名称
        """
        self.use_llm = use_llm
        self.force_ocr = force_ocr
        self.disable_image_extraction = disable_image_extraction
        self.output_format = output_format
        
        # 构建配置字典
        self.config = {
            "output_format": output_format,
            "use_llm": use_llm,
            "force_ocr": force_ocr,
            "disable_image_extraction": disable_image_extraction,
        }
        
        # 如果启用 LLM，添加 LLM 相关配置
        if use_llm and llm_service:
            self.config["llm_service"] = llm_service
            if llm_api_key:
                # 根据不同的 LLM 服务设置对应的 API key 参数
                if "openai" in llm_service.lower():
                    self.config["openai_api_key"] = llm_api_key
                    if llm_base_url:
                        self.config["openai_base_url"] = llm_base_url
                    if llm_model:
                        self.config["openai_model"] = llm_model
                elif "gemini" in llm_service.lower():
                    self.config["gemini_api_key"] = llm_api_key
                    if llm_model:
                        self.config["gemini_model"] = llm_model
                elif "claude" in llm_service.lower():
                    self.config["claude_api_key"] = llm_api_key
                    if llm_model:
                        self.config["claude_model_name"] = llm_model
        
        # 初始化转换器（延迟初始化，在实际转换时创建）
        self.converter: Optional[PdfConverter] = None
        
    def _initialize_converter(self) -> None:
        """初始化 marker 转换器（延迟导入）"""
        if self.converter is not None:
            return

        # 延迟导入 marker 模块（避免启动时下载模型）
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser

        # 创建配置解析器
        config_parser = ConfigParser(self.config)

        # 创建转换器
        self.converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service() if self.use_llm else None
        )
        
        print(f"✅ Markdown 转换器初始化成功！")
        print(f"   - 输出格式: {self.output_format}")
        print(f"   - 使用 LLM: {self.use_llm}")
        print(f"   - 强制 OCR: {self.force_ocr}")
        print(f"   - 禁用图片提取: {self.disable_image_extraction}")
    
    async def convert_file(
        self,
        file_path: str,
        page_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转换文件为 Markdown
        
        参数:
            file_path: 文件路径
            page_range: 页面范围 (例如: "0,5-10,20")
            
        返回:
            包含转换结果的字典:
            {
                "markdown": str,  # Markdown 文本
                "metadata": dict,  # 元数据
                "images": dict,   # 图片字典 (如果启用图片提取)
                "success": bool,
                "message": str
            }
        """
        try:
            # 确保转换器已初始化
            self._initialize_converter()
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"文件不存在: {file_path}",
                    "markdown": "",
                    "metadata": {},
                    "images": {}
                }
            
            # 如果指定了页面范围，更新配置
            if page_range:
                # 这里可以通过重新创建转换器来应用页面范围
                # 但为了简化，我们先不支持动态页面范围
                pass
            
            # 执行转换
            print(f"🔄 开始转换文件: {file_path}")
            rendered = self.converter(file_path)

            # 延迟导入 text_from_rendered
            from marker.output import text_from_rendered

            # 提取文本和图片
            text, metadata, images = text_from_rendered(rendered)

            # 如果禁用了图片提取，清空图片字典
            if self.disable_image_extraction:
                images = {}
            else:
                # 将 PIL Image 对象转换为 base64 字符串，以便序列化
                import base64
                from io import BytesIO
                serializable_images = {}
                for key, img in images.items():
                    if hasattr(img, 'save'):  # 检查是否是 PIL Image
                        buffer = BytesIO()
                        img.save(buffer, format='PNG')
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        serializable_images[key] = f"data:image/png;base64,{img_base64}"
                    else:
                        serializable_images[key] = img
                images = serializable_images

            print(f"✅ 文件转换成功！")
            print(f"   - 文本长度: {len(text)} 字符")
            print(f"   - 图片数量: {len(images)}")

            return {
                "success": True,
                "message": "转换成功",
                "markdown": text,
                "metadata": metadata,
                "images": images
            }
            
        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "markdown": "",
                "metadata": {},
                "images": {}
            }
    
    async def convert_file_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        page_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转换文件字节流为 Markdown
        
        参数:
            file_bytes: 文件字节流
            filename: 文件名（用于确定文件类型）
            page_range: 页面范围 (例如: "0,5-10,20")
            
        返回:
            包含转换结果的字典
        """
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)
        
        try:
            # 写入临时文件
            with open(temp_file_path, 'wb') as f:
                f.write(file_bytes)
            
            # 转换文件
            result = await self.convert_file(temp_file_path, page_range)
            
            return result
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"⚠️ 清理临时文件失败: {str(e)}")
    
    def get_supported_formats(self) -> list[str]:
        """
        获取支持的文件格式列表
        
        返回:
            支持的文件扩展名列表
        """
        return [
            ".pdf",
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff",
            ".pptx", ".ppt",
            ".docx", ".doc",
            ".xlsx", ".xls",
            ".html", ".htm",
            ".epub"
        ]
    
    def is_supported_file(self, filename: str) -> bool:
        """
        检查文件是否支持转换

        参数:
            filename: 文件名

        返回:
            是否支持
        """
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.get_supported_formats()

    async def convert_multiple_files(
        self,
        file_paths: list[str],
        page_range: Optional[str] = None,
        max_concurrent: int = 3
    ) -> list[Dict[str, Any]]:
        """
        并发转换多个文件

        参数:
            file_paths: 文件路径列表
            page_range: 页面范围 (例如: "0,5-10,20")
            max_concurrent: 最大并发数（默认: 3）

        返回:
            包含所有转换结果的列表
        """
        import asyncio

        # 创建信号量来限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def convert_with_semaphore(file_path: str) -> Dict[str, Any]:
            """带信号量控制的转换函数"""
            async with semaphore:
                print(f"🔄 开始转换: {file_path}")
                result = await self.convert_file(file_path, page_range)
                result["file_path"] = file_path  # 添加文件路径到结果中
                return result

        # 并发执行所有转换任务
        tasks = [convert_with_semaphore(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "message": f"转换失败: {str(result)}",
                    "markdown": "",
                    "metadata": {},
                    "images": {},
                    "file_path": file_paths[i]
                })
            else:
                processed_results.append(result)

        return processed_results

    async def convert_multiple_file_bytes(
        self,
        files_data: list[tuple[bytes, str]],
        page_range: Optional[str] = None,
        max_concurrent: int = 3
    ) -> list[Dict[str, Any]]:
        """
        并发转换多个文件字节流

        参数:
            files_data: 文件数据列表，每项为 (file_bytes, filename) 元组
            page_range: 页面范围 (例如: "0,5-10,20")
            max_concurrent: 最大并发数（默认: 3）

        返回:
            包含所有转换结果的列表
        """
        import asyncio

        # 创建信号量来限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def convert_with_semaphore(file_bytes: bytes, filename: str) -> Dict[str, Any]:
            """带信号量控制的转换函数"""
            async with semaphore:
                print(f"🔄 开始转换: {filename}")
                result = await self.convert_file_bytes(file_bytes, filename, page_range)
                result["filename"] = filename  # 添加文件名到结果中
                return result

        # 并发执行所有转换任务
        tasks = [convert_with_semaphore(fb, fn) for fb, fn in files_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "message": f"转换失败: {str(result)}",
                    "markdown": "",
                    "metadata": {},
                    "images": {},
                    "filename": files_data[i][1]
                })
            else:
                processed_results.append(result)

        return processed_results

