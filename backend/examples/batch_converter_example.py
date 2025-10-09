"""
批量 Markdown 转换示例

演示如何使用 MarkdownConverterService 并发转换多个文件
"""
import asyncio
import os
import time
from pathlib import Path

from services.markdown_converter_service import MarkdownConverterService


async def example_batch_convert_files():
    """示例 1: 批量转换本地文件"""
    print("\n" + "="*80)
    print("示例 1: 批量转换本地文件（并发处理）")
    print("="*80)
    
    # 创建转换服务
    converter = MarkdownConverterService(
        use_llm=False,
        force_ocr=False,
        disable_image_extraction=False,
        output_format="markdown"
    )
    
    # 准备要转换的文件列表
    # 注意：请根据实际情况修改文件路径
    file_paths = [
        "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png",
        # 添加更多文件路径...
    ]
    
    # 过滤存在的文件
    existing_files = [fp for fp in file_paths if os.path.exists(fp)]
    
    if not existing_files:
        print("⚠️ 没有找到可转换的文件")
        print("💡 提示: 请修改 file_paths 列表，添加实际存在的文件路径")
        return
    
    print(f"\n📋 准备转换 {len(existing_files)} 个文件:")
    for fp in existing_files:
        print(f"   • {Path(fp).name}")
    
    # 记录开始时间
    start_time = time.time()
    
    # 批量转换（并发处理，最大并发数为 3）
    print(f"\n🔄 开始批量转换（最大并发数: 3）...")
    results = await converter.convert_multiple_files(
        file_paths=existing_files,
        max_concurrent=3
    )
    
    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n✅ 批量转换完成！")
    print(f"   - 总文件数: {len(results)}")
    print(f"   - 成功: {success_count}")
    print(f"   - 失败: {failed_count}")
    print(f"   - 总耗时: {elapsed_time:.2f} 秒")
    print(f"   - 平均耗时: {elapsed_time/len(results):.2f} 秒/文件")
    
    # 显示每个文件的结果
    print("\n📄 转换结果详情:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        filename = Path(result.get("file_path", "unknown")).name
        if result["success"]:
            markdown_len = len(result["markdown"])
            image_count = len(result["images"])
            print(f"{i}. ✅ {filename}")
            print(f"   - Markdown 长度: {markdown_len} 字符")
            print(f"   - 图片数量: {image_count}")
        else:
            print(f"{i}. ❌ {filename}")
            print(f"   - 错误: {result['message']}")
    print("-" * 80)


async def example_batch_convert_bytes():
    """示例 2: 批量转换文件字节流"""
    print("\n" + "="*80)
    print("示例 2: 批量转换文件字节流（模拟文件上传）")
    print("="*80)
    
    # 创建转换服务
    converter = MarkdownConverterService()
    
    # 准备文件列表
    file_paths = [
        "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png",
        # 添加更多文件...
    ]
    
    # 读取文件为字节流
    files_data = []
    for fp in file_paths:
        if os.path.exists(fp):
            with open(fp, 'rb') as f:
                file_bytes = f.read()
            files_data.append((file_bytes, Path(fp).name))
    
    if not files_data:
        print("⚠️ 没有找到可转换的文件")
        return
    
    print(f"\n📋 准备转换 {len(files_data)} 个文件:")
    for _, filename in files_data:
        print(f"   • {filename}")
    
    # 记录开始时间
    start_time = time.time()
    
    # 批量转换
    print(f"\n🔄 开始批量转换（最大并发数: 3）...")
    results = await converter.convert_multiple_file_bytes(
        files_data=files_data,
        max_concurrent=3
    )
    
    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    
    print(f"\n✅ 批量转换完成！")
    print(f"   - 总文件数: {len(results)}")
    print(f"   - 成功: {success_count}")
    print(f"   - 总耗时: {elapsed_time:.2f} 秒")


async def example_batch_convert_with_different_concurrency():
    """示例 3: 测试不同并发数的性能"""
    print("\n" + "="*80)
    print("示例 3: 测试不同并发数的性能")
    print("="*80)
    
    # 准备测试文件
    file_paths = [
        "/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png",
    ] * 6  # 复制 6 次，模拟 6 个文件
    
    existing_files = [fp for fp in file_paths if os.path.exists(fp)]
    
    if not existing_files:
        print("⚠️ 测试文件不存在")
        return
    
    # 测试不同的并发数
    concurrency_levels = [1, 2, 3, 5]
    
    print(f"\n📊 测试文件数: {len(existing_files)}")
    print("\n性能对比:")
    print("-" * 80)
    
    for max_concurrent in concurrency_levels:
        converter = MarkdownConverterService()
        
        start_time = time.time()
        results = await converter.convert_multiple_files(
            file_paths=existing_files,
            max_concurrent=max_concurrent
        )
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        success_count = sum(1 for r in results if r["success"])
        
        print(f"并发数 {max_concurrent}: {elapsed_time:.2f} 秒 (成功: {success_count}/{len(results)})")
    
    print("-" * 80)


async def example_batch_convert_folder():
    """示例 4: 批量转换文件夹中的所有文件"""
    print("\n" + "="*80)
    print("示例 4: 批量转换文件夹中的所有文件")
    print("="*80)
    
    # 指定文件夹路径
    folder_path = "/Users/darkringsystem/PycharmProjects/autogenTest"
    
    if not os.path.exists(folder_path):
        print(f"⚠️ 文件夹不存在: {folder_path}")
        return
    
    # 创建转换服务
    converter = MarkdownConverterService()
    
    # 获取文件夹中所有支持的文件
    all_files = []
    for ext in converter.get_supported_formats():
        all_files.extend(Path(folder_path).glob(f"*{ext}"))
    
    if not all_files:
        print(f"⚠️ 文件夹中没有支持的文件")
        return
    
    file_paths = [str(fp) for fp in all_files]
    
    print(f"\n📋 找到 {len(file_paths)} 个可转换的文件:")
    for fp in file_paths[:10]:  # 只显示前 10 个
        print(f"   • {Path(fp).name}")
    if len(file_paths) > 10:
        print(f"   ... 还有 {len(file_paths) - 10} 个文件")
    
    # 批量转换
    print(f"\n🔄 开始批量转换...")
    start_time = time.time()
    
    results = await converter.convert_multiple_files(
        file_paths=file_paths,
        max_concurrent=3
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    
    print(f"\n✅ 批量转换完成！")
    print(f"   - 总文件数: {len(results)}")
    print(f"   - 成功: {success_count}")
    print(f"   - 失败: {len(results) - success_count}")
    print(f"   - 总耗时: {elapsed_time:.2f} 秒")
    
    # 保存结果到文件
    output_folder = Path(folder_path) / "markdown_output"
    output_folder.mkdir(exist_ok=True)
    
    for result in results:
        if result["success"]:
            filename = Path(result["file_path"]).stem + ".md"
            output_path = output_folder / filename
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["markdown"])
    
    print(f"\n💾 Markdown 文件已保存到: {output_folder}")


async def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("批量 Markdown 转换示例")
    print("="*80)
    
    # 运行示例
    await example_batch_convert_files()
    # await example_batch_convert_bytes()
    # await example_batch_convert_with_different_concurrency()
    # await example_batch_convert_folder()
    
    print("\n" + "="*80)
    print("所有示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

