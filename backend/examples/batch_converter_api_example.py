"""
批量 Markdown 转换 API 使用示例

演示如何通过 HTTP API 批量转换多个文件
"""
import requests
import json
import time
from pathlib import Path


# API 基础 URL
BASE_URL = "http://localhost:8000"


def example_batch_convert_api():
    """示例 1: 批量转换多个文件"""
    print("\n" + "="*80)
    print("示例 1: 批量转换多个文件（HTTP API）")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown/batch"
    
    # 准备要转换的文件列表
    file_paths = [
        "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png",
        # 添加更多文件路径...
    ]
    
    # 过滤存在的文件
    existing_files = [fp for fp in file_paths if Path(fp).exists()]
    
    if not existing_files:
        print("⚠️ 没有找到可转换的文件")
        print("💡 提示: 请修改 file_paths 列表，添加实际存在的文件路径")
        return
    
    print(f"\n📋 准备转换 {len(existing_files)} 个文件:")
    for fp in existing_files:
        print(f"   • {Path(fp).name}")
    
    try:
        # 准备文件和表单数据
        files = []
        for fp in existing_files:
            with open(fp, 'rb') as f:
                file_content = f.read()
            files.append(('files', (Path(fp).name, file_content, 'application/octet-stream')))
        
        data = {
            'use_llm': 'false',
            'force_ocr': 'false',
            'disable_image_extraction': 'false',
            'output_format': 'markdown',
            'max_concurrent': '3'  # 最大并发数
        }
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送请求
        print(f"\n🔄 开始批量转换（最大并发数: 3）...")
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        result = response.json()
        
        print(f"\n✅ 批量转换完成！")
        print(f"   - 总文件数: {result['total']}")
        print(f"   - 成功: {result['success_count']}")
        print(f"   - 失败: {result['failed_count']}")
        print(f"   - 总耗时: {elapsed_time:.2f} 秒")
        print(f"   - 平均耗时: {elapsed_time/result['total']:.2f} 秒/文件")
        
        # 显示每个文件的结果
        print("\n📄 转换结果详情:")
        print("-" * 80)
        for i, file_result in enumerate(result['results'], 1):
            filename = file_result.get('filename', 'unknown')
            if file_result.get('success', False):
                markdown_len = len(file_result.get('markdown', ''))
                image_count = len(file_result.get('images', {}))
                print(f"{i}. ✅ {filename}")
                print(f"   - Markdown 长度: {markdown_len} 字符")
                print(f"   - 图片数量: {image_count}")
                
                # 显示 Markdown 预览
                if markdown_len > 0:
                    preview = file_result['markdown'][:100]
                    print(f"   - 预览: {preview}...")
            else:
                print(f"{i}. ❌ {filename}")
                print(f"   - 错误: {file_result.get('message', '未知错误')}")
        print("-" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def example_batch_convert_with_llm():
    """示例 2: 使用 LLM 增强的批量转换"""
    print("\n" + "="*80)
    print("示例 2: 使用 LLM 增强的批量转换")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown/batch"
    
    # 准备文件
    file_paths = [
        "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png",
    ]
    
    existing_files = [fp for fp in file_paths if Path(fp).exists()]
    
    if not existing_files:
        print("⚠️ 没有找到可转换的文件")
        return
    
    try:
        # 准备文件
        files = []
        for fp in existing_files:
            with open(fp, 'rb') as f:
                file_content = f.read()
            files.append(('files', (Path(fp).name, file_content, 'application/octet-stream')))
        
        data = {
            'use_llm': 'true',
            'force_ocr': 'false',
            'output_format': 'markdown',
            'max_concurrent': '2',  # LLM 模式建议降低并发数
            'llm_api_key': 'sk-65417eb6629a4102858a35f3484878e5',  # 替换为你的 API key
            'llm_base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'llm_model': 'qwen-vl-max-latest'
        }
        
        print(f"\n🔄 开始批量转换（使用 LLM 增强）...")
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n✅ 批量转换完成！")
        print(f"   - 总文件数: {result['total']}")
        print(f"   - 成功: {result['success_count']}")
        print(f"   - 失败: {result['failed_count']}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")


def example_batch_convert_folder():
    """示例 3: 批量转换文件夹中的所有文件"""
    print("\n" + "="*80)
    print("示例 3: 批量转换文件夹中的所有文件")
    print("="*80)
    
    url = f"{BASE_URL}/api/convert/markdown/batch"
    
    # 指定文件夹
    folder_path = "/Users/darkringsystem/PycharmProjects/autogenTest"
    
    if not Path(folder_path).exists():
        print(f"⚠️ 文件夹不存在: {folder_path}")
        return
    
    # 获取支持的文件格式
    supported_formats_url = f"{BASE_URL}/api/convert/supported-formats"
    formats_response = requests.get(supported_formats_url)
    supported_formats = formats_response.json()['supported_formats']
    
    # 查找所有支持的文件
    all_files = []
    for ext in supported_formats:
        all_files.extend(Path(folder_path).glob(f"*{ext}"))
    
    if not all_files:
        print(f"⚠️ 文件夹中没有支持的文件")
        return
    
    # 限制文件数量（API 限制最多 20 个）
    all_files = all_files[:20]
    
    print(f"\n📋 找到 {len(all_files)} 个可转换的文件:")
    for fp in all_files[:10]:
        print(f"   • {fp.name}")
    if len(all_files) > 10:
        print(f"   ... 还有 {len(all_files) - 10} 个文件")
    
    try:
        # 准备文件
        files = []
        for fp in all_files:
            with open(fp, 'rb') as f:
                file_content = f.read()
            files.append(('files', (fp.name, file_content, 'application/octet-stream')))
        
        data = {
            'use_llm': 'false',
            'force_ocr': 'false',
            'output_format': 'markdown',
            'max_concurrent': '5'
        }
        
        print(f"\n🔄 开始批量转换...")
        start_time = time.time()
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        result = response.json()
        
        print(f"\n✅ 批量转换完成！")
        print(f"   - 总文件数: {result['total']}")
        print(f"   - 成功: {result['success_count']}")
        print(f"   - 失败: {result['failed_count']}")
        print(f"   - 总耗时: {elapsed_time:.2f} 秒")
        
        # 保存结果
        output_folder = Path(folder_path) / "markdown_output"
        output_folder.mkdir(exist_ok=True)
        
        saved_count = 0
        for file_result in result['results']:
            if file_result.get('success', False):
                filename = Path(file_result['filename']).stem + ".md"
                output_path = output_folder / filename
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(file_result['markdown'])
                saved_count += 1
        
        print(f"\n💾 已保存 {saved_count} 个 Markdown 文件到: {output_folder}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("批量 Markdown 转换 API 使用示例")
    print(f"API 地址: {BASE_URL}")
    print("="*80)
    print("\n⚠️ 请确保后端服务已启动: python backend/main.py")
    
    # 运行示例
    example_batch_convert_api()
    # example_batch_convert_with_llm()  # 需要配置 LLM API key
    # example_batch_convert_folder()
    
    print("\n" + "="*80)
    print("所有示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    main()

