"""
TestCasesTeamAIService 使用示例
演示如何使用多智能体团队协作生成测试用例
"""
import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import TestCasesTeamAIService
from config import settings


async def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用 - 生成登录功能测试用例")
    print("=" * 60)

    # 创建测试用例团队服务
    team_service = TestCasesTeamAIService(settings)

    try:
        # 初始化
        await team_service.initialize()

        # 运行团队（非流式）
        print("\n📝 任务: 为用户登录功能生成测试用例\n")
        result = await team_service.run("为用户登录功能生成完整的测试用例，包括正常场景、边界条件和异常情况")

        print("\n✅ 最终结果:")
        print(result)

    finally:
        # 清理资源
        await team_service.cleanup()


async def example_stream_usage():
    """流式使用示例"""
    print("\n" + "=" * 60)
    print("示例 2: 流式使用（查看测试用例生成协作过程）")
    print("=" * 60)

    # 创建测试用例团队服务
    team_service = TestCasesTeamAIService(settings)

    try:
        # 初始化
        await team_service.initialize()

        # 运行团队（流式）
        print("\n📝 任务: 为购物车添加商品功能生成测试用例\n")

        async for event in team_service.run_stream("为购物车添加商品功能生成测试用例"):
            # 打印每个事件
            print(f"🔄 事件: {event}")
            print("-" * 60)

    finally:
        # 清理资源
        await team_service.cleanup()


async def example_complex_task():
    """复杂任务示例"""
    print("\n" + "=" * 60)
    print("示例 3: 复杂任务（为支付系统生成完整测试用例）")
    print("=" * 60)

    # 创建测试用例团队服务
    team_service = TestCasesTeamAIService(settings)

    try:
        # 初始化
        await team_service.initialize()

        # 复杂任务
        task = """
        为在线支付系统生成完整的测试用例，包括：
        1. 支付流程测试（微信支付、支付宝、银行卡）
        2. 金额验证测试（正常金额、边界值、异常金额）
        3. 安全性测试（加密、防重放攻击）
        4. 异常处理测试（网络超时、支付失败、退款）
        5. 性能测试（并发支付、大额支付）
        """

        print(f"\n📝 任务: {task}\n")
        result = await team_service.run(task)

        print("\n✅ 最终结果:")
        print(result)

    finally:
        # 清理资源
        await team_service.cleanup()


async def example_check_team_status():
    """检查团队状态示例"""
    print("\n" + "=" * 60)
    print("示例 4: 检查测试用例团队状态")
    print("=" * 60)

    # 创建测试用例团队服务
    team_service = TestCasesTeamAIService(settings)

    # 初始化前检查
    print(f"\n初始化前 - 团队是否已初始化: {team_service.is_initialized()}")
    print(f"初始化前 - 团队实例: {team_service.get_team()}")

    try:
        # 初始化
        await team_service.initialize()

        # 初始化后检查
        print(f"\n初始化后 - 团队是否已初始化: {team_service.is_initialized()}")
        print(f"初始化后 - 团队实例: {team_service.get_team()}")
        print(f"初始化后 - 智能体数量: {len(team_service.agents)}")
        print(f"初始化后 - 智能体列表:")
        for i, agent in enumerate(team_service.agents, 1):
            print(f"  {i}. {agent.name}")

    finally:
        # 清理资源
        await team_service.cleanup()


async def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例 5: 错误处理")
    print("=" * 60)

    # 创建测试用例团队服务
    team_service = TestCasesTeamAIService(settings)

    try:
        # 尝试在未初始化时运行
        print("\n❌ 尝试在未初始化时运行团队...")
        result = await team_service.run("生成测试用例")
    except RuntimeError as e:
        print(f"✅ 捕获到预期的错误: {e}")

    try:
        # 正确的使用方式
        print("\n✅ 正确的使用方式:")
        await team_service.initialize()
        result = await team_service.run("为用户注册功能生成简单的测试用例")
        print(f"结果: {result}")

    finally:
        # 清理资源
        await team_service.cleanup()


async def main():
    """主函数"""
    print("\n🧪 TestCasesTeamAIService 使用示例")
    print("=" * 60)
    
    # 运行所有示例
    examples = [
        ("基础使用", example_basic_usage),
        ("流式使用", example_stream_usage),
        ("复杂任务", example_complex_task),
        ("检查团队状态", example_check_team_status),
        ("错误处理", example_error_handling),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\n选择要运行的示例（输入数字，或按 Enter 运行所有示例）:")
    choice = input("> ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(examples):
        # 运行选定的示例
        name, func = examples[int(choice) - 1]
        print(f"\n运行示例: {name}")
        await func()
    else:
        # 运行所有示例
        print("\n运行所有示例...")
        for name, func in examples:
            try:
                await func()
                await asyncio.sleep(2)  # 示例之间暂停
            except Exception as e:
                print(f"\n❌ 示例 '{name}' 运行失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())

