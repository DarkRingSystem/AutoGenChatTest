"""
测试图片分析 API 的脚本
用于验证后端 API 是否正常工作
"""
import asyncio
import aiohttp
import json


async def test_image_analysis_stream():
    """测试流式图片分析 API"""
    
    print("\n" + "="*60)
    print("测试图片分析流式 API")
    print("="*60)
    
    # API 端点
    url = "http://localhost:8000/api/image-analysis/stream"
    
    # 准备测试数据
    data = aiohttp.FormData()
    data.add_field('image_url', 'https://example.com/login-screenshot.png')
    data.add_field('web_url', 'https://example.com/login')
    data.add_field('test_description', '登录页面 UI 测试')
    data.add_field('additional_context', '需要重点关注表单验证和错误提示')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                print(f"\n状态码: {response.status}")
                print(f"会话 ID: {response.headers.get('X-Session-ID', 'N/A')}")
                print("\n开始接收 SSE 事件...\n")
                
                # 读取 SSE 流
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_str = line[6:]  # 去掉 'data: ' 前缀
                        
                        if data_str == '[DONE]':
                            print("\n✅ 分析完成！")
                            break
                        
                        try:
                            event = json.loads(data_str)
                            handle_sse_event(event)
                        except json.JSONDecodeError:
                            print(f"⚠️ 无法解析 JSON: {data_str}")
                
    except aiohttp.ClientError as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def handle_sse_event(event):
    """处理 SSE 事件"""
    event_type = event.get('type', 'unknown')
    content = event.get('content', '')
    
    if event_type == 'status':
        print(f"📊 状态: {content}")
    
    elif event_type == 'agent_start':
        agent_role = event.get('agent_role', 'Unknown')
        print(f"\n{'='*60}")
        print(f"🚀 {agent_role} 开始工作")
        print(f"{'='*60}")
    
    elif event_type == 'agent_message':
        agent_role = event.get('agent_role', 'Unknown')
        print(f"\n💬 {agent_role}:")
        print(f"{'-'*60}")
        # 只显示前 200 个字符，避免输出过长
        if len(content) > 200:
            print(f"{content[:200]}...")
        else:
            print(content)
    
    elif event_type == 'agent_done':
        agent_role = event.get('agent_role', 'Unknown')
        print(f"\n✅ {agent_role} 完成")
    
    elif event_type == 'done':
        print(f"\n🎉 {content}")
    
    elif event_type == 'token_usage':
        token_info = event.get('token_usage', {})
        total_tokens = token_info.get('total_tokens', 0)
        message_count = token_info.get('message_count', 0)
        print(f"\n📊 Token 使用统计:")
        print(f"   总 Tokens: {total_tokens}")
        print(f"   消息数量: {message_count}")
    
    elif event_type == 'error':
        print(f"\n❌ 错误: {content}")


async def test_image_analysis_non_stream():
    """测试非流式图片分析 API"""
    
    print("\n" + "="*60)
    print("测试图片分析非流式 API")
    print("="*60)
    
    # API 端点
    url = "http://localhost:8000/api/image-analysis"
    
    # 准备测试数据
    data = aiohttp.FormData()
    data.add_field('image_url', 'https://example.com/dashboard-screenshot.png')
    data.add_field('web_url', 'https://example.com/dashboard')
    data.add_field('test_description', '仪表板页面 UI 测试')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                print(f"\n状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    
                    print(f"\n会话 ID: {result.get('session_id', 'N/A')}")
                    print(f"状态: {result.get('status', 'N/A')}")
                    
                    print(f"\n📊 分析结果摘要:")
                    print(f"{'-'*60}")
                    
                    # UI 分析
                    ui_analysis = result.get('ui_analysis', [])
                    print(f"\n🎨 UI 专家分析 ({len(ui_analysis)} 条):")
                    for i, analysis in enumerate(ui_analysis[:2], 1):  # 只显示前 2 条
                        print(f"  {i}. {analysis[:100]}...")
                    
                    # 交互分析
                    interaction_analysis = result.get('interaction_analysis', [])
                    print(f"\n🔄 交互分析师分析 ({len(interaction_analysis)} 条):")
                    for i, analysis in enumerate(interaction_analysis[:2], 1):
                        print(f"  {i}. {analysis[:100]}...")
                    
                    # 测试场景
                    test_scenarios = result.get('test_scenarios', [])
                    print(f"\n📋 测试场景 ({len(test_scenarios)} 条):")
                    for i, scenario in enumerate(test_scenarios[:2], 1):
                        print(f"  {i}. {scenario[:100]}...")
                    
                    # 摘要
                    summary = result.get('summary', '')
                    print(f"\n📝 摘要:")
                    print(f"{summary[:200]}...")
                    
                    print(f"\n✅ 分析完成！")
                else:
                    error_text = await response.text()
                    print(f"❌ 请求失败: {error_text}")
                
    except aiohttp.ClientError as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🧪 图片分析 API 测试")
    print("="*60)
    print("\n⚠️ 注意：")
    print("1. 确保后端服务已启动 (python backend/main.py)")
    print("2. 确保已配置 LLM API 密钥")
    print("3. 本测试使用示例 URL，实际测试时请替换为真实图片")
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 流式 API 测试")
    print("2. 非流式 API 测试")
    print("3. 两者都测试")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == '1':
        await test_image_analysis_stream()
    elif choice == '2':
        await test_image_analysis_non_stream()
    elif choice == '3':
        await test_image_analysis_stream()
        print("\n" + "="*60)
        await asyncio.sleep(2)  # 等待 2 秒
        await test_image_analysis_non_stream()
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

