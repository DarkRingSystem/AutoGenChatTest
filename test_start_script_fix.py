#!/usr/bin/env python3
"""
测试 start.bat 修复 - 验证虚拟环境路径修复是否有效
"""

import requests
import time
import subprocess
import os
import sys

def test_backend_with_correct_venv():
    """测试后端是否使用了正确的虚拟环境和代码"""
    print("🔍 测试后端虚拟环境和编排模式...")
    
    try:
        # 等待后端启动
        print("⏳ 等待后端服务启动...")
        time.sleep(3)
        
        # 测试健康检查端点
        print("🏥 测试健康检查端点...")
        response = requests.get("http://localhost:8000/api/v1/normal_chat/message_health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 健康检查成功: {health_data}")
            
            # 检查是否是编排模式的服务
            if health_data.get("service") == "normal_chat_message_aitest":
                print("✅ 确认使用编排模式后端服务")
                return True
            else:
                print(f"❌ 后端服务不正确: {health_data.get('service')}")
                return False
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接后端失败: {str(e)}")
        return False

def test_orchestration_endpoint():
    """测试编排模式端点是否可用"""
    print("\n🚀 测试编排模式端点...")
    
    try:
        data = {
            "message": "测试编排模式是否正常工作",
            "session_id": None,
            "file_ids": [],
            "is_feedback": False
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/normal_chat/stream_aitest",
            json=data,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 编排模式端点响应正常")
            
            # 检查会话ID
            session_id = response.headers.get('X-Session-ID')
            if session_id:
                print(f"✅ 会话ID正常: {session_id[:30]}...")
            
            # 读取一些流式响应
            message_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    message_count += 1
                    if message_count >= 5:  # 只读取前5条消息
                        break
                    
                    data_content = line[6:]
                    if data_content == "[DONE]":
                        break
                        
                    try:
                        import json
                        event_data = json.loads(data_content)
                        event_type = event_data.get("type", "unknown")
                        print(f"  📝 收到事件: {event_type}")
                    except:
                        pass
            
            print(f"✅ 编排模式流式响应正常，收到 {message_count} 条消息")
            return True
        else:
            print(f"❌ 编排模式端点失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 编排模式测试异常: {str(e)}")
        return False

def check_virtual_environment():
    """检查当前使用的虚拟环境"""
    print("\n🔍 检查虚拟环境状态...")
    
    # 检查Python路径
    python_path = sys.executable
    print(f"Python路径: {python_path}")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 当前在虚拟环境中")
        
        # 检查虚拟环境路径
        if ".venv" in python_path:
            print("✅ 使用正确的 .venv 虚拟环境")
            return True
        else:
            print(f"⚠️ 虚拟环境路径可能不正确: {python_path}")
            return False
    else:
        print("❌ 当前不在虚拟环境中")
        return False

def main():
    """主测试函数"""
    print("🔧 start.bat 修复验证测试")
    print("=" * 60)
    
    # 检查虚拟环境
    venv_ok = check_virtual_environment()
    
    # 测试后端健康状态
    backend_ok = test_backend_with_correct_venv()
    
    # 测试编排模式
    orchestration_ok = test_orchestration_endpoint()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 start.bat 修复验证总结:")
    print(f"  虚拟环境: {'✅ 正确' if venv_ok else '❌ 错误'}")
    print(f"  后端服务: {'✅ 编排模式' if backend_ok else '❌ 异常'}")
    print(f"  编排端点: {'✅ 正常' if orchestration_ok else '❌ 失败'}")
    
    if venv_ok and backend_ok and orchestration_ok:
        print("\n🎉 start.bat 修复成功！")
        print("💡 现在使用 start.bat 启动会正确加载编排模式")
        print("🌐 前端'普通对话模式'将使用编排模式后端")
    else:
        print("\n⚠️ start.bat 可能仍有问题，请检查:")
        if not venv_ok:
            print("  - 虚拟环境路径不正确")
        if not backend_ok:
            print("  - 后端服务异常")
        if not orchestration_ok:
            print("  - 编排模式端点不可用")

if __name__ == "__main__":
    main()
