"""
Markdown 转换服务使用示例

演示如何使用 MarkdownConverterService 将各种文件转换为 Markdown 格式
基于 marker 官方库: https://github.com/datalab-to/marker
"""
import asyncio
import os
from pathlib import Path

from services.markdown_converter_service import MarkdownConverterService


async def example_basic_conversion():
    """示例 1: 基础转换 - 不使用 LLM"""
    print("\n" + "="*80)
    print("示例 1: 基础 PDF 转换（不使用 LLM）")
    print("="*80)
    
    # 创建转换服务
    converter = MarkdownConverterService(
        use_llm=False,
        force_ocr=False,
        disable_image_extraction=False,
        output_format="markdown"
    )
    
    # 转换文件
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if os.path.exists(file_path):
        result = await converter.convert_file(file_path)
        
        if result["success"]:
            print(f"\n✅ 转换成功！")
            print(f"Markdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result["markdown"][:500])
            print("-" * 80)
            print(f"\n元数据: {result['metadata']}")
            print(f"图片数量: {len(result['images'])}")
        else:
            print(f"\n❌ 转换失败: {result['message']}")
    else:
        print(f"\n⚠️ 文件不存在: {file_path}")


async def example_llm_enhanced_conversion():
    """示例 2: 使用 LLM 增强转换精度"""
    print("\n" + "="*80)
    print("示例 2: 使用 LLM 增强的 PDF 转换")
    print("="*80)
    
    # 创建转换服务（使用 LLM）
    converter = MarkdownConverterService(
        use_llm=True,
        force_ocr=False,
        disable_image_extraction=False,
        output_format="markdown",
        llm_service="marker.services.openai.OpenAIService",
        llm_api_key="sk-65417eb6629a4102858a35f3484878e5",  # 替换为你的 API key
        llm_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        llm_model="qwen-vl-max-latest"
    )
    
    # 转换文件
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if os.path.exists(file_path):
        result = await converter.convert_file(file_path)
        
        if result["success"]:
            print(f"\n✅ 转换成功！")
            print(f"Markdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result["markdown"][:500])
            print("-" * 80)
            print(f"\n元数据: {result['metadata']}")
            print(f"图片数量: {len(result['images'])}")
        else:
            print(f"\n❌ 转换失败: {result['message']}")
    else:
        print(f"\n⚠️ 文件不存在: {file_path}")


async def example_force_ocr_conversion():
    """示例 3: 强制 OCR 转换"""
    print("\n" + "="*80)
    print("示例 3: 强制 OCR 转换（适用于扫描版 PDF 或图片）")
    print("="*80)
    
    # 创建转换服务（强制 OCR）
    converter = MarkdownConverterService(
        use_llm=False,
        force_ocr=True,  # 强制 OCR
        disable_image_extraction=False,
        output_format="markdown"
    )
    
    # 转换图片文件
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if os.path.exists(file_path):
        result = await converter.convert_file(file_path)
        
        if result["success"]:
            print(f"\n✅ 转换成功！")
            print(f"Markdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result["markdown"][:500])
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
    else:
        print(f"\n⚠️ 文件不存在: {file_path}")


async def example_json_output():
    """示例 4: JSON 格式输出"""
    print("\n" + "="*80)
    print("示例 4: JSON 格式输出（包含结构化信息）")
    print("="*80)
    
    # 创建转换服务（JSON 输出）
    converter = MarkdownConverterService(
        use_llm=False,
        force_ocr=False,
        disable_image_extraction=False,
        output_format="json"  # JSON 格式
    )
    
    # 转换文件
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if os.path.exists(file_path):
        result = await converter.convert_file(file_path)
        
        if result["success"]:
            print(f"\n✅ 转换成功！")
            print(f"JSON 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result["markdown"][:500])  # JSON 格式也存储在 markdown 字段中
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
    else:
        print(f"\n⚠️ 文件不存在: {file_path}")


async def example_check_supported_formats():
    """示例 5: 检查支持的文件格式"""
    print("\n" + "="*80)
    print("示例 5: 检查支持的文件格式")
    print("="*80)
    
    converter = MarkdownConverterService()
    
    supported_formats = converter.get_supported_formats()
    print(f"\n支持的文件格式 ({len(supported_formats)} 种):")
    print("-" * 80)
    for fmt in supported_formats:
        print(f"  • {fmt}")
    print("-" * 80)
    
    # 测试文件格式检查
    test_files = [
        "document.pdf",
        "image.png",
        "presentation.pptx",
        "spreadsheet.xlsx",
        "unsupported.txt"
    ]
    
    print("\n文件格式检查:")
    for filename in test_files:
        is_supported = converter.is_supported_file(filename)
        status = "✅ 支持" if is_supported else "❌ 不支持"
        print(f"  {filename}: {status}")


async def example_convert_bytes():
    """示例 6: 从字节流转换"""
    print("\n" + "="*80)
    print("示例 6: 从字节流转换（模拟文件上传）")
    print("="*80)
    
    # 创建转换服务
    converter = MarkdownConverterService(
        use_llm=False,
        force_ocr=False,
        disable_image_extraction=False,
        output_format="markdown"
    )
    
    # 读取文件为字节流
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        # 从字节流转换
        result = await converter.convert_file_bytes(
            file_bytes=file_bytes,
            filename="avatr.png"
        )
        
        if result["success"]:
            print(f"\n✅ 转换成功！")
            print(f"Markdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result["markdown"][:500])
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
    else:
        print(f"\n⚠️ 文件不存在: {file_path}")


async def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("Markdown 转换服务示例")
    print("基于 marker 官方库: https://github.com/datalab-to/marker")
    print("="*80)
    
    # 运行示例
    await example_check_supported_formats()
    await example_basic_conversion()
    # await example_llm_enhanced_conversion()  # 需要配置 LLM API key
    await example_force_ocr_conversion()
    # await example_json_output()
    await example_convert_bytes()
    
    print("\n" + "="*80)
    print("所有示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

