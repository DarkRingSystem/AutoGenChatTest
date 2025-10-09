"""
测试文件上下文功能
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import get_file_storage
from api.utils import build_message_with_file_context


def test_file_context():
    """测试文件上下文构建功能"""
    
    print("🧪 测试文件上下文功能...\n")
    
    # 获取文件存储
    file_storage = get_file_storage()
    
    # 测试1: 没有文件 ID
    print("📝 测试1: 没有文件 ID")
    message = "你好"
    result = build_message_with_file_context(message, None)
    assert result == message, "应该返回原始消息"
    print(f"   ✅ 通过: 返回原始消息\n")
    
    # 测试2: 空文件 ID 列表
    print("📝 测试2: 空文件 ID 列表")
    result = build_message_with_file_context(message, [])
    assert result == message, "应该返回原始消息"
    print(f"   ✅ 通过: 返回原始消息\n")
    
    # 测试3: 文件 ID 不存在
    print("📝 测试3: 文件 ID 不存在")
    result = build_message_with_file_context(message, ["non_existent_id"])
    assert result == message, "应该返回原始消息"
    print(f"   ✅ 通过: 返回原始消息\n")
    
    # 测试4: 添加文件到存储
    print("📝 测试4: 添加文件到存储并构建上下文")
    file_id = "test_file_123"
    file_storage[file_id] = {
        "filename": "test.py",
        "markdown": "```python\ndef hello():\n    print('Hello, World!')\n```",
        "metadata": {}
    }
    
    result = build_message_with_file_context("解释这段代码", [file_id])
    
    # 验证结果包含文件内容
    assert "test.py" in result, "应该包含文件名"
    assert "def hello()" in result, "应该包含文件内容"
    assert "解释这段代码" in result, "应该包含用户问题"
    assert "请结合以下文件内容和用户问题进行解答" in result, "应该包含提示文本"
    
    print(f"   ✅ 通过: 正确构建文件上下文")
    print(f"   📄 生成的消息:\n")
    print("   " + "\n   ".join(result.split("\n")[:10]))
    print("   ...\n")
    
    # 测试5: 多个文件
    print("📝 测试5: 多个文件")
    file_id2 = "test_file_456"
    file_storage[file_id2] = {
        "filename": "config.json",
        "markdown": '```json\n{\n  "name": "test",\n  "version": "1.0.0"\n}\n```',
        "metadata": {}
    }
    
    result = build_message_with_file_context("分析这些文件", [file_id, file_id2])
    
    assert "test.py" in result, "应该包含第一个文件名"
    assert "config.json" in result, "应该包含第二个文件名"
    assert "def hello()" in result, "应该包含第一个文件内容"
    assert '"name": "test"' in result, "应该包含第二个文件内容"
    
    print(f"   ✅ 通过: 正确处理多个文件")
    print(f"   📄 包含文件: test.py, config.json\n")
    
    # 清理
    file_storage.clear()
    
    print("✅ 所有测试通过！")
    print("✅ 文件上下文功能正常工作")


if __name__ == "__main__":
    test_file_context()

