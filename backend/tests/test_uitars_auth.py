"""
测试 UI-TARS API 认证
"""
import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 加载环境变量
load_dotenv()

async def test_uitars_auth():
    """测试 UI-TARS API 认证"""
    
    # 从环境变量读取配置
    api_key = os.getenv("UITARS_API_KEY")
    base_url = os.getenv("UITARS_BASE_URL")
    model = os.getenv("UITARS_MODEL")
    
    print("=" * 80)
    print("🔍 UI-TARS API 配置信息")
    print("=" * 80)
    print(f"模型: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key (前20字符): {api_key[:20] if api_key else 'None'}...")
    print(f"API Key (后10字符): ...{api_key[-10:] if api_key else 'None'}")
    print(f"API Key 长度: {len(api_key) if api_key else 0}")
    print(f"API Key 完整: {api_key}")
    print("=" * 80)
    
    # 创建客户端
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    
    # 测试请求
    print("\n📤 发送测试请求...")
    print(f"请求 URL: {base_url}/chat/completions")
    print(f"请求头:")
    print(f"  Authorization: Bearer {api_key[:20]}...{api_key[-10:]}")
    print(f"  Content-Type: application/json")
    
    try:
        # 简单的文本请求（不带图片）
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "你好，请简单介绍一下你自己。"
                }
            ],
            max_tokens=100,
        )
        
        print("\n✅ 请求成功！")
        print(f"响应: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n❌ 请求失败！")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 打印详细错误
        if hasattr(e, 'response'):
            print(f"\n响应状态码: {e.response.status_code}")
            print(f"响应头: {dict(e.response.headers)}")
            print(f"响应体: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(test_uitars_auth())

