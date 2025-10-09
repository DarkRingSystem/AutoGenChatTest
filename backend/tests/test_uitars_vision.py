"""
测试 UI-TARS 视觉模型
"""
import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 加载环境变量
load_dotenv()

async def test_uitars_vision():
    """测试 UI-TARS 视觉模型"""
    
    # 从环境变量读取配置
    api_key = os.getenv("UITARS_API_KEY")
    base_url = os.getenv("UITARS_BASE_URL")
    model = os.getenv("UITARS_MODEL")
    
    print("=" * 80)
    print("🔍 UI-TARS 视觉模型测试")
    print("=" * 80)
    print(f"模型: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print("=" * 80)
    
    # 创建客户端
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    
    # 测试图片 URL（使用一个公开的测试图片）
    test_image_url = "https://picsum.photos/400/300"
    
    print(f"\n📤 发送视觉分析请求...")
    print(f"图片 URL: {test_image_url}")
    
    try:
        # 带图片的请求
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请描述这张图片中的内容。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": test_image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
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
    asyncio.run(test_uitars_vision())

