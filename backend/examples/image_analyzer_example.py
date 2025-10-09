"""
UI 图片分析示例
演示如何使用 ImageAnalyzerTeam 分析 UI 界面图片
使用 GraphFlow 实现并行分析工作流
"""
import asyncio
from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam


async def analyze_ui_image_example():
    """UI 图片分析示例 - 使用 GraphFlow 并行分析"""

    # 1. 创建配置
    settings = Settings.from_env()

    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)

    # 3. 初始化团队（使用 GraphFlow）
    await analyzer_team.initialize()

    # 4. 分析图片（示例图片路径，请替换为实际路径）
    image_path = "path/to/your/ui_screenshot.png"
    user_requirements = "请重点关注登录表单的交互流程和验证逻辑"

    print("\n" + "="*60)
    print("开始分析 UI 图片（GraphFlow 并行模式）")
    print("="*60)
    print("工作流程：")
    print("  1. UI_Expert 和 Interaction_Analyst 并行分析")
    print("  2. Test_Scenario_Expert 综合分析结果")
    print("="*60)
    
    # 5. 执行分析（使用新的参数格式）
    results = await analyzer_team.analyze_image(
        session_id="example_session_001",
        image_url=image_path,
        web_url="https://example.com/login",
        test_description=user_requirements,
        additional_context="这是一个登录页面的 UI 分析示例"
    )
    
    # 6. 输出分析结果
    print("\n" + "="*60)
    print("分析结果")
    print("="*60)
    
    print("\n【UI 专家分析】")
    print("-" * 60)
    for i, analysis in enumerate(results["ui_analysis"], 1):
        print(f"\n第 {i} 条分析：")
        print(analysis)
    
    print("\n【交互分析师分析】")
    print("-" * 60)
    for i, analysis in enumerate(results["interaction_analysis"], 1):
        print(f"\n第 {i} 条分析：")
        print(analysis)
    
    print("\n【测试场景专家分析】")
    print("-" * 60)
    for i, scenario in enumerate(results["test_scenarios"], 1):
        print(f"\n第 {i} 条场景：")
        print(scenario)
    
    print("\n【分析摘要】")
    print("-" * 60)
    print(results["summary"])
    
    return results


async def analyze_ui_image_stream_example():
    """UI 图片流式分析示例 - GraphFlow 并行模式"""

    # 1. 创建配置
    settings = Settings.from_env()

    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)

    # 3. 初始化团队（使用 GraphFlow）
    await analyzer_team.initialize()

    # 4. 分析图片（流式输出）
    image_path = "path/to/your/ui_screenshot.png"

    print("\n" + "="*60)
    print("开始流式分析 UI 图片（GraphFlow 并行模式）")
    print("="*60)
    print("注意：UI_Expert 和 Interaction_Analyst 将并行输出")
    print("="*60)
    
    # 5. 执行流式分析（使用新的参数格式）
    async for event in analyzer_team.analyze_image_stream(
        session_id="stream_session_001",
        image_url=image_path,
        web_url="https://example.com/dashboard",
        test_description="流式分析仪表板页面"
    ):
        # 处理流式事件
        print(f"\n[事件] {type(event).__name__}")

        # 根据事件类型处理
        if hasattr(event, 'content'):
            print(f"内容: {event.content}")

        if hasattr(event, 'source'):
            print(f"来源: {event.source}")


async def batch_analyze_example():
    """批量分析多个 UI 图片示例"""
    
    # 1. 创建配置
    settings = Settings.from_env()
    
    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 3. 初始化团队
    await analyzer_team.initialize()
    
    # 4. 批量分析多个图片
    image_paths = [
        "path/to/login_page.png",
        "path/to/dashboard.png",
        "path/to/settings_page.png",
    ]
    
    all_results = []
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n{'='*60}")
        print(f"分析第 {i}/{len(image_paths)} 个图片")
        print(f"{'='*60}")
        
        results = await analyzer_team.analyze_image(
            session_id=f"batch_session_{i:03d}",
            image_url=image_path,
            test_description=f"批量分析第 {i} 个图片"
        )
        all_results.append({
            "image_path": image_path,
            "results": results,
        })
        
        print(f"\n✅ 第 {i} 个图片分析完成")
    
    # 5. 输出汇总
    print(f"\n{'='*60}")
    print("批量分析完成")
    print(f"{'='*60}")
    print(f"总共分析了 {len(all_results)} 个图片")
    
    return all_results


def main():
    """主函数"""
    print("UI 图片分析示例")
    print("="*60)
    print("请选择示例：")
    print("1. 单个图片分析")
    print("2. 流式分析")
    print("3. 批量分析")
    print("="*60)
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(analyze_ui_image_example())
    elif choice == "2":
        asyncio.run(analyze_ui_image_stream_example())
    elif choice == "3":
        asyncio.run(batch_analyze_example())
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()

