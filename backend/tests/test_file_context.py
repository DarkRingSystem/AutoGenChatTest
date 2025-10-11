"""
测试文件上下文功能
验证文件解析后的内容是否正确传递给大模型
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.routes import get_file_storage, _build_message_with_file_context


def test_file_storage():
    """测试文件存储功能"""
    print("\n" + "="*60)
    print("测试 1: 文件存储功能")
    print("="*60)
    
    # 获取文件存储
    storage = get_file_storage()
    print(f"✓ 获取文件存储成功，当前存储的文件数: {len(storage)}")
    
    # 模拟添加文件
    test_file_id = "test_file_001"
    storage[test_file_id] = {
        "filename": "test_requirements.txt",
        "markdown": "# 测试需求文档\n\n## 功能描述\n这是一个测试功能",
        "metadata": {"page_count": 1}
    }
    print(f"✓ 添加测试文件: {test_file_id}")
    
    # 验证文件是否存储成功
    if test_file_id in storage:
        file_data = storage[test_file_id]
        print(f"✓ 文件存储成功:")
        print(f"  - 文件名: {file_data['filename']}")
        print(f"  - Markdown长度: {len(file_data['markdown'])} 字符")
        print(f"  - 元数据: {file_data['metadata']}")
        return True
    else:
        print("✗ 文件存储失败")
        return False


def test_build_message_with_context():
    """测试构建包含文件上下文的消息"""
    print("\n" + "="*60)
    print("测试 2: 构建包含文件上下文的消息")
    print("="*60)
    
    # 获取文件存储
    storage = get_file_storage()
    
    # 添加测试文件
    file_id_1 = "test_file_001"
    file_id_2 = "test_file_002"
    
    storage[file_id_1] = {
        "filename": "需求文档.txt",
        "markdown": "# 用户登录功能需求\n\n## 功能描述\n用户可以通过用户名和密码登录系统",
        "metadata": {}
    }
    
    storage[file_id_2] = {
        "filename": "设计文档.txt",
        "markdown": "# 登录页面设计\n\n## UI 设计\n包含用户名输入框、密码输入框和登录按钮",
        "metadata": {}
    }
    
    print(f"✓ 添加了 2 个测试文件")
    
    # 测试构建消息
    user_message = "请根据需求文档和设计文档，生成登录功能的测试用例"
    file_ids = [file_id_1, file_id_2]
    
    message_with_context = _build_message_with_file_context(user_message, file_ids)
    
    print(f"\n原始消息:")
    print(f"  {user_message}")
    print(f"\n包含文件上下文的消息:")
    print("-" * 60)
    print(message_with_context)
    print("-" * 60)
    
    # 验证消息是否包含文件内容
    if "需求文档.txt" in message_with_context and "设计文档.txt" in message_with_context:
        print("\n✓ 消息成功包含文件上下文")
        return True
    else:
        print("\n✗ 消息未包含文件上下文")
        return False


def test_empty_file_ids():
    """测试空文件 ID 列表"""
    print("\n" + "="*60)
    print("测试 3: 空文件 ID 列表")
    print("="*60)
    
    user_message = "请生成测试用例"
    file_ids = []
    
    message_with_context = _build_message_with_file_context(user_message, file_ids)
    
    if message_with_context == user_message:
        print("✓ 空文件 ID 列表时，返回原始消息")
        return True
    else:
        print("✗ 空文件 ID 列表时，消息被错误修改")
        return False


def test_nonexistent_file_ids():
    """测试不存在的文件 ID"""
    print("\n" + "="*60)
    print("测试 4: 不存在的文件 ID")
    print("="*60)
    
    user_message = "请生成测试用例"
    file_ids = ["nonexistent_file_001", "nonexistent_file_002"]
    
    message_with_context = _build_message_with_file_context(user_message, file_ids)
    
    if message_with_context == user_message:
        print("✓ 不存在的文件 ID 时，返回原始消息")
        return True
    else:
        print("✗ 不存在的文件 ID 时，消息被错误修改")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("文件上下文功能测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("文件存储功能", test_file_storage()))
    results.append(("构建包含文件上下文的消息", test_build_message_with_context()))
    results.append(("空文件 ID 列表", test_empty_file_ids()))
    results.append(("不存在的文件 ID", test_nonexistent_file_ids()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())

