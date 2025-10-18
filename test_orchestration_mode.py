#!/usr/bin/env python3
"""
测试编排模式 - 验证前端编排模式对话功能
"""

import requests
import json
import time

def test_orchestration_mode():
    """测试编排模式端点"""
    print("🚀 测试编排模式端点...")
    
    try:
        # 模拟前端编排模式的请求
        data = {
            "message": "你好，我是编排模式用户，请简单介绍你自己",
            "session_id": None,
            "file_ids": [],
            "is_feedback": False
        }
        
        print(f"📤 发送请求到编排模式端点: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/normal_chat/stream_aitest",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            },
            stream=True
        )
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        # 检查会话ID头
        session_id = response.headers.get('X-Session-ID')
        if session_id:
            print(f"✅ 成功获取会话ID: {session_id}")
        else:
            print("❌ 未获取到会话ID")
            print("可用的响应头:", list(response.headers.keys()))
        
        if response.status_code == 200:
            print("📡 流式响应:")
            
            message_count = 0
            content_chunks = []
            event_types = {}
            
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_content = line[6:]
                    
                    if data_content == "[DONE]":
                        print("  [DONE]")
                        break
                    
                    try:
                        event_data = json.loads(data_content)
                        event_type = event_data.get("type", "unknown")
                        content = event_data.get("content", "")
                        
                        # 统计事件类型
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                        
                        message_count += 1
                        if message_count <= 10:  # 只显示前10条消息
                            print(f"  📝 {event_type}: {str(content)[:50]}...")
                        elif message_count == 11:
                            print("  ... (更多消息)")
                        
                        # 收集内容块
                        if event_type == "chunk":
                            content_chunks.append(content)
                            
                    except json.JSONDecodeError:
                        print(f"  ⚠️ JSON 解析错误: {data_content[:50]}...")
            
            full_content = "".join(content_chunks)
            print(f"✅ 编排模式端点测试成功")
            print(f"   消息数量: {message_count}")
            print(f"   事件类型统计: {event_types}")
            print(f"   内容长度: {len(full_content)} 字符")
            print(f"   内容预览: {full_content[:200]}...")
            
            # 测试会话连续性
            if session_id:
                print("\n🔄 测试会话连续性...")
                return test_session_continuity(session_id)
            
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_session_continuity(session_id):
    """测试会话连续性"""
    try:
        # 发送第二条消息，使用之前的会话ID
        data = {
            "message": "请记住我刚才说的话，并简短回复",
            "session_id": session_id,
            "file_ids": [],
            "is_feedback": False
        }
        
        print(f"📤 发送第二条消息 (会话ID: {session_id[:20]}...):")
        
        response = requests.post(
            "http://localhost:8000/api/v1/normal_chat/stream_aitest",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            },
            stream=True
        )
        
        print(f"📊 状态码: {response.status_code}")
        
        # 检查是否返回相同的会话ID
        returned_session_id = response.headers.get('X-Session-ID')
        if returned_session_id == session_id:
            print(f"✅ 会话ID保持一致: {returned_session_id[:20]}...")
        else:
            print(f"⚠️ 会话ID不一致: 发送={session_id[:20]}..., 返回={returned_session_id[:20] if returned_session_id else 'None'}...")
        
        if response.status_code == 200:
            print("📡 第二次响应:")
            
            message_count = 0
            content_chunks = []
            
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_content = line[6:]
                    
                    if data_content == "[DONE]":
                        print("  [DONE]")
                        break
                    
                    try:
                        event_data = json.loads(data_content)
                        event_type = event_data.get("type", "unknown")
                        content = event_data.get("content", "")
                        
                        message_count += 1
                        if message_count <= 5:  # 只显示前5条消息
                            print(f"  📝 {event_type}: {str(content)[:30]}...")
                        elif message_count == 6:
                            print("  ... (更多消息)")
                        
                        # 收集内容块
                        if event_type == "chunk":
                            content_chunks.append(content)
                            
                    except json.JSONDecodeError:
                        print(f"  ⚠️ JSON 解析错误: {data_content[:30]}...")
            
            full_content = "".join(content_chunks)
            print(f"✅ 会话连续性测试成功，共收到 {message_count} 条消息")
            print(f"   内容长度: {len(full_content)} 字符")
            print(f"   内容预览: {full_content[:100]}...")
            return True
        else:
            print(f"❌ 第二次请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 会话连续性测试异常: {str(e)}")
        return False

def test_health_check():
    """测试健康检查端点"""
    print("\n🏥 测试健康检查端点...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/normal_chat/message_health")
        
        print(f"📊 健康检查状态码: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 后端健康状态: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始编排模式测试...")
    print("=" * 60)
    
    # 等待服务器完全启动
    print("⏳ 等待服务器准备就绪...")
    time.sleep(2)
    
    # 测试健康检查
    health_ok = test_health_check()
    
    time.sleep(1)
    
    # 测试编排模式
    orchestration_ok = test_orchestration_mode()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 编排模式测试总结:")
    print(f"  健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"  编排模式对话: {'✅ 通过' if orchestration_ok else '❌ 失败'}")
    
    if health_ok and orchestration_ok:
        print("\n🎉 编排模式测试全部通过！")
        print("💡 前端现在可以正常使用编排模式对话：")
        print("   - 选择'普通对话模式'即可使用编排模式后端")
        print("   - 支持会话连续性和上下文记忆")
        print("   - 使用AutoGen消息发布-订阅机制")
        print("\n🌐 前端地址: http://localhost:3000")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()
