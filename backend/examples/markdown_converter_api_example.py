"""
Markdown 转换 API 使用示例

演示如何通过 HTTP API 调用 Markdown 转换服务
"""
import requests
import json
from pathlib import Path


# API 基础 URL
BASE_URL = "http://localhost:8000"


def example_get_supported_formats():
    """示例 1: 获取支持的文件格式"""
    print("\n" + "="*80)
    print("示例 1: 获取支持的文件格式")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/supported-formats"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✅ 请求成功！")
        print(f"支持的文件格式 ({data['total']} 种):")
        print("-" * 80)
        for fmt in data['supported_formats']:
            print(f"  • {fmt}")
        print("-" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")


def example_convert_pdf_basic():
    """示例 2: 基础 PDF 转换"""
    print("\n" + "="*80)
    print("示例 2: 基础 PDF 转换（不使用 LLM）")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown"
    
    # 文件路径
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if not Path(file_path).exists():
        print(f"\n⚠️ 文件不存在: {file_path}")
        return
    
    try:
        # 准备文件和表单数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/octet-stream')
            }
            
            data = {
                'use_llm': 'false',
                'force_ocr': 'false',
                'disable_image_extraction': 'false',
                'output_format': 'markdown'
            }
            
            # 发送请求
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print(f"\n✅ 转换成功！")
            print(f"消息: {result['message']}")
            print(f"\nMarkdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result['markdown'][:500])
            print("-" * 80)
            print(f"\n元数据: {json.dumps(result['metadata'], indent=2, ensure_ascii=False)}")
            print(f"图片数量: {len(result['images'])}")
        else:
            print(f"\n❌ 转换失败: {result['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def example_convert_with_llm():
    """示例 3: 使用 LLM 增强的转换"""
    print("\n" + "="*80)
    print("示例 3: 使用 LLM 增强的转换")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown"
    
    # 文件路径
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if not Path(file_path).exists():
        print(f"\n⚠️ 文件不存在: {file_path}")
        return
    
    try:
        # 准备文件和表单数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/octet-stream')
            }
            
            data = {
                'use_llm': 'true',
                'force_ocr': 'false',
                'disable_image_extraction': 'false',
                'output_format': 'markdown',
                'llm_api_key': 'sk-65417eb6629a4102858a35f3484878e5',  # 替换为你的 API key
                'llm_base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'llm_model': 'qwen-vl-max-latest'
            }
            
            # 发送请求
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print(f"\n✅ 转换成功！")
            print(f"消息: {result['message']}")
            print(f"\nMarkdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result['markdown'][:500])
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def example_convert_with_force_ocr():
    """示例 4: 强制 OCR 转换"""
    print("\n" + "="*80)
    print("示例 4: 强制 OCR 转换")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown"
    
    # 文件路径
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if not Path(file_path).exists():
        print(f"\n⚠️ 文件不存在: {file_path}")
        return
    
    try:
        # 准备文件和表单数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/octet-stream')
            }
            
            data = {
                'use_llm': 'false',
                'force_ocr': 'true',  # 强制 OCR
                'disable_image_extraction': 'false',
                'output_format': 'markdown'
            }
            
            # 发送请求
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print(f"\n✅ 转换成功！")
            print(f"消息: {result['message']}")
            print(f"\nMarkdown 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result['markdown'][:500])
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def example_convert_to_json():
    """示例 5: 转换为 JSON 格式"""
    print("\n" + "="*80)
    print("示例 5: 转换为 JSON 格式")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown"
    
    # 文件路径
    file_path = "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png"
    
    if not Path(file_path).exists():
        print(f"\n⚠️ 文件不存在: {file_path}")
        return
    
    try:
        # 准备文件和表单数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/octet-stream')
            }
            
            data = {
                'use_llm': 'false',
                'force_ocr': 'false',
                'disable_image_extraction': 'false',
                'output_format': 'json'  # JSON 格式
            }
            
            # 发送请求
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print(f"\n✅ 转换成功！")
            print(f"消息: {result['message']}")
            print(f"\nJSON 内容预览（前 500 字符）:")
            print("-" * 80)
            print(result['markdown'][:500])
            print("-" * 80)
        else:
            print(f"\n❌ 转换失败: {result['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("Markdown 转换 API 使用示例")
    print(f"API 地址: {BASE_URL}")
    print("="*80)
    print("\n⚠️ 请确保后端服务已启动: python backend/main.py")
    
    # 运行示例
    example_get_supported_formats()
    example_convert_pdf_basic()
    # example_convert_with_llm()  # 需要配置 LLM API key
    example_convert_with_force_ocr()
    # example_convert_to_json()
    
    print("\n" + "="*80)
    print("所有示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    main()

