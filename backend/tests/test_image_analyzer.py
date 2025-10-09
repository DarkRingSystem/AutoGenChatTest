"""
UI 图片分析智能体团队测试脚本
用于验证 ImageAnalyzerTeam 的功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam


async def test_initialization():
    """测试团队初始化"""
    print("\n" + "="*60)
    print("测试 1: 团队初始化")
    print("="*60)
    
    try:
        settings = Settings.from_env()
        analyzer_team = ImageAnalyzerTeam(settings)
        
        # 检查初始状态
        assert not analyzer_team.is_initialized(), "团队不应该在初始化前就已初始化"
        print("✓ 初始状态检查通过")
        
        # 初始化团队
        await analyzer_team.initialize()
        
        # 检查初始化后状态
        assert analyzer_team.is_initialized(), "团队应该已经初始化"
        assert analyzer_team.vision_model_client is not None, "视觉模型客户端应该已创建"
        assert len(analyzer_team.agents) == 3, "应该有 3 个团队成员"
        assert analyzer_team.team is not None, "团队应该已创建"
        
        print("✓ 团队初始化成功")
        print(f"✓ 团队成员数量: {len(analyzer_team.agents)}")
        print(f"✓ 团队成员: {[agent.name for agent in analyzer_team.agents]}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_task_message_building():
    """测试任务消息构建"""
    print("\n" + "="*60)
    print("测试 2: 任务消息构建")
    print("="*60)
    
    try:
        settings = Settings.from_env()
        analyzer_team = ImageAnalyzerTeam(settings)
        
        # 测试基本任务消息
        task1 = analyzer_team._build_task_message("test_image.png")
        assert "test_image.png" in task1, "任务消息应包含图片路径"
        assert "UI 专家" in task1, "任务消息应包含 UI 专家的指示"
        assert "交互分析师" in task1, "任务消息应包含交互分析师的指示"
        assert "测试场景专家" in task1, "任务消息应包含测试场景专家的指示"
        print("✓ 基本任务消息构建成功")
        
        # 测试带用户需求的任务消息
        task2 = analyzer_team._build_task_message(
            "test_image.png",
            "请重点关注登录表单"
        )
        assert "请重点关注登录表单" in task2, "任务消息应包含用户需求"
        print("✓ 带用户需求的任务消息构建成功")
        
        print("\n任务消息示例:")
        print("-" * 60)
        print(task2)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_result_parsing():
    """测试结果解析"""
    print("\n" + "="*60)
    print("测试 3: 结果解析")
    print("="*60)
    
    try:
        from autogen_agentchat.base import TaskResult
        from autogen_agentchat.messages import TextMessage
        
        settings = Settings.from_env()
        analyzer_team = ImageAnalyzerTeam(settings)
        
        # 创建模拟的任务结果
        mock_messages = [
            TextMessage(content="UI 分析结果 1", source="UI_Expert"),
            TextMessage(content="UI 分析结果 2", source="UI_Expert"),
            TextMessage(content="交互分析结果 1", source="Interaction_Analyst"),
            TextMessage(content="测试场景 1", source="Test_Scenario_Expert"),
        ]
        
        mock_result = TaskResult(
            messages=mock_messages,
            stop_reason="Text mention termination"
        )
        
        # 解析结果
        parsed = analyzer_team._parse_analysis_results(mock_result)
        
        # 验证解析结果
        assert len(parsed["ui_analysis"]) == 2, "应该有 2 条 UI 分析"
        assert len(parsed["interaction_analysis"]) == 1, "应该有 1 条交互分析"
        assert len(parsed["test_scenarios"]) == 1, "应该有 1 条测试场景"
        assert len(parsed["chat_history"]) == 4, "应该有 4 条对话历史"
        assert parsed["summary"] != "", "应该有摘要"
        
        print("✓ 结果解析成功")
        print(f"✓ UI 分析数量: {len(parsed['ui_analysis'])}")
        print(f"✓ 交互分析数量: {len(parsed['interaction_analysis'])}")
        print(f"✓ 测试场景数量: {len(parsed['test_scenarios'])}")
        print(f"✓ 对话历史数量: {len(parsed['chat_history'])}")
        
        print("\n摘要:")
        print("-" * 60)
        print(parsed["summary"])
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_model_clients():
    """测试模型客户端"""
    print("\n" + "="*60)
    print("测试 4: 模型客户端")
    print("="*60)
    
    try:
        from backend.examples.llms import (
            get_default_model_client,
            get_vision_model_client,
            get_uitars_model_client,
            reset_model_clients
        )
        
        settings = Settings.from_env()
        
        # 测试默认模型客户端
        default_client = get_default_model_client(settings)
        assert default_client is not None, "默认模型客户端应该已创建"
        print("✓ 默认模型客户端创建成功")
        
        # 测试视觉模型客户端
        vision_client = get_vision_model_client(settings)
        assert vision_client is not None, "视觉模型客户端应该已创建"
        print("✓ 视觉模型客户端创建成功")
        
        # 测试 UI-TARS 模型客户端
        uitars_client = get_uitars_model_client(settings)
        assert uitars_client is not None, "UI-TARS 模型客户端应该已创建"
        print("✓ UI-TARS 模型客户端创建成功")
        
        # 测试客户端缓存
        default_client2 = get_default_model_client(settings)
        assert default_client is default_client2, "应该返回缓存的客户端"
        print("✓ 客户端缓存机制正常")
        
        # 测试重置
        reset_model_clients()
        print("✓ 客户端重置成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("UI 图片分析智能体团队 - 测试套件")
    print("="*60)
    
    tests = [
        ("团队初始化", test_initialization),
        ("任务消息构建", test_task_message_building),
        ("结果解析", test_result_parsing),
        ("模型客户端", test_model_clients),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 执行失败: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


def main():
    """主函数"""
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

