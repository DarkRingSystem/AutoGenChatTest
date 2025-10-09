"""
GraphFlow 工作流测试脚本
验证 UI 图片分析团队的并行工作流是否正常工作
"""
import asyncio
import time
from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam


async def test_graphflow_basic():
    """测试基本的 GraphFlow 工作流"""
    print("="*70)
    print("测试 1: 基本 GraphFlow 工作流")
    print("="*70)
    
    # 1. 创建配置
    settings = Settings.from_env()
    
    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 3. 初始化团队
    print("\n📦 初始化团队...")
    await analyzer_team.initialize()
    
    # 4. 验证团队结构
    print("\n✅ 团队初始化成功！")
    print(f"   - UI_Expert: {analyzer_team.ui_expert.name}")
    print(f"   - Interaction_Analyst: {analyzer_team.interaction_analyst.name}")
    print(f"   - Test_Scenario_Expert: {analyzer_team.test_scenario_expert.name}")
    print(f"   - 工作流类型: {type(analyzer_team.team).__name__}")
    
    # 5. 验证 GraphFlow
    if type(analyzer_team.team).__name__ == "GraphFlow":
        print("\n✅ GraphFlow 工作流创建成功！")
    else:
        print(f"\n❌ 错误：期望 GraphFlow，实际是 {type(analyzer_team.team).__name__}")
        return False
    
    return True


async def test_graphflow_execution():
    """测试 GraphFlow 执行流程"""
    print("\n" + "="*70)
    print("测试 2: GraphFlow 执行流程")
    print("="*70)
    
    # 1. 创建配置
    settings = Settings.from_env()
    
    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 3. 初始化团队
    await analyzer_team.initialize()
    
    # 4. 准备测试图片（使用示例路径）
    # 注意：这里使用一个示例路径，实际使用时请替换为真实图片路径
    image_path = "https://example.com/ui_screenshot.png"
    
    print(f"\n🔍 开始分析图片: {image_path}")
    print("   注意：这是一个示例路径，实际使用时请替换为真实图片")
    
    # 5. 记录开始时间
    start_time = time.time()
    
    try:
        # 6. 执行分析（使用流式输出观察并行执行）
        print("\n📊 执行流式分析（观察并行执行）...")
        print("-" * 70)
        
        agent_start_times = {}
        agent_end_times = {}
        current_agent = None
        
        async for event in analyzer_team.analyze_image_stream(image_path=image_path):
            # 记录智能体开始和结束时间
            if hasattr(event, 'source'):
                source = event.source
                
                # 检测智能体切换
                if source != current_agent and source != 'user':
                    if current_agent and current_agent not in agent_end_times:
                        agent_end_times[current_agent] = time.time()
                    
                    if source not in agent_start_times:
                        agent_start_times[source] = time.time()
                        print(f"\n[{source}] 开始执行...")
                    
                    current_agent = source
                
                # 打印消息（简化输出）
                if hasattr(event, 'content') and event.content:
                    content_preview = event.content[:100] + "..." if len(event.content) > 100 else event.content
                    print(f"[{source}] {content_preview}")
        
        # 记录最后一个智能体的结束时间
        if current_agent and current_agent not in agent_end_times:
            agent_end_times[current_agent] = time.time()
        
        # 7. 计算执行时间
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "-" * 70)
        print(f"✅ 分析完成！总耗时: {total_time:.2f} 秒")
        
        # 8. 分析并行执行情况
        print("\n📈 智能体执行时间分析:")
        for agent_name in ['UI_Expert', 'Interaction_Analyst', 'Test_Scenario_Expert']:
            if agent_name in agent_start_times and agent_name in agent_end_times:
                duration = agent_end_times[agent_name] - agent_start_times[agent_name]
                relative_start = agent_start_times[agent_name] - start_time
                print(f"   {agent_name}:")
                print(f"     - 开始时间: +{relative_start:.2f}s")
                print(f"     - 执行时长: {duration:.2f}s")
        
        # 9. 验证并行执行
        if 'UI_Expert' in agent_start_times and 'Interaction_Analyst' in agent_start_times:
            ui_start = agent_start_times['UI_Expert']
            ia_start = agent_start_times['Interaction_Analyst']
            time_diff = abs(ui_start - ia_start)
            
            print(f"\n🔍 并行执行验证:")
            print(f"   UI_Expert 和 Interaction_Analyst 开始时间差: {time_diff:.2f}s")
            
            if time_diff < 1.0:  # 如果开始时间差小于1秒，认为是并行执行
                print(f"   ✅ 确认并行执行！")
            else:
                print(f"   ⚠️  可能不是并行执行（时间差较大）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_graphflow_result_structure():
    """测试 GraphFlow 结果结构"""
    print("\n" + "="*70)
    print("测试 3: GraphFlow 结果结构")
    print("="*70)
    
    # 1. 创建配置
    settings = Settings.from_env()
    
    # 2. 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 3. 初始化团队
    await analyzer_team.initialize()
    
    # 4. 准备测试图片
    image_path = "https://example.com/ui_screenshot.png"
    
    print(f"\n🔍 分析图片并验证结果结构...")
    
    try:
        # 5. 执行分析
        results = await analyzer_team.analyze_image(
            image_path=image_path,
            user_requirements="测试 GraphFlow 结果结构"
        )
        
        # 6. 验证结果结构
        print("\n📋 验证结果结构:")
        
        expected_keys = ['ui_analysis', 'interaction_analysis', 'test_scenarios', 'chat_history', 'summary']
        for key in expected_keys:
            if key in results:
                print(f"   ✅ {key}: {type(results[key]).__name__}")
                if isinstance(results[key], list):
                    print(f"      - 包含 {len(results[key])} 项")
            else:
                print(f"   ❌ 缺少 {key}")
        
        # 7. 验证对话历史
        print("\n📜 对话历史:")
        for i, msg in enumerate(results['chat_history'], 1):
            source = msg.get('source', 'unknown')
            content_preview = msg.get('content', '')[:50] + "..."
            print(f"   {i}. [{source}] {content_preview}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("GraphFlow 工作流测试套件")
    print("="*70)
    
    tests = [
        ("基本工作流", test_graphflow_basic),
        ("执行流程", test_graphflow_execution),
        ("结果结构", test_graphflow_result_structure),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 失败: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！GraphFlow 工作流运行正常。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("GraphFlow 工作流测试")
    print("="*70)
    print("\n请选择测试模式：")
    print("1. 运行所有测试")
    print("2. 仅测试基本工作流")
    print("3. 仅测试执行流程")
    print("4. 仅测试结果结构")
    print("="*70)
    
    choice = input("\n请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        asyncio.run(run_all_tests())
    elif choice == "2":
        asyncio.run(test_graphflow_basic())
    elif choice == "3":
        asyncio.run(test_graphflow_execution())
    elif choice == "4":
        asyncio.run(test_graphflow_result_structure())
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()

