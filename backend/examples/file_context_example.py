"""
文件上下文功能示例
演示如何使用文件上下文功能生成测试用例
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.routes import get_file_storage, _build_message_with_file_context


async def example_1_basic_usage():
    """示例 1: 基本使用"""
    print("\n" + "="*80)
    print("示例 1: 基本使用 - 单个文件")
    print("="*80)
    
    # 获取文件存储
    storage = get_file_storage()
    
    # 模拟文件上传和解析（实际使用中，这些数据来自 Markdown 转换 API）
    file_id = "example_file_001"
    storage[file_id] = {
        "filename": "登录功能需求.md",
        "markdown": """# 登录功能需求文档

## 功能描述
用户可以通过用户名和密码登录系统。

## 验收标准
1. 用户输入正确的用户名和密码，点击登录按钮，系统验证成功后跳转到首页
2. 用户输入错误的用户名或密码，系统显示错误提示
3. 用户名和密码输入框支持复制粘贴
4. 密码输入框显示为密文
5. 登录按钮在用户名和密码都不为空时才可点击

## 业务规则
- 用户名长度: 3-20 个字符
- 密码长度: 6-20 个字符
- 连续登录失败 5 次后，账号锁定 30 分钟
""",
        "metadata": {"page_count": 1}
    }
    
    print(f"✓ 模拟文件上传: {storage[file_id]['filename']}")
    print(f"✓ 文件 ID: {file_id}")
    
    # 构建包含文件上下文的消息
    user_message = "请根据需求文档，生成登录功能的测试用例"
    message_with_context = _build_message_with_file_context(user_message, [file_id])
    
    print(f"\n📝 发送给大模型的完整消息:")
    print("-" * 80)
    print(message_with_context)
    print("-" * 80)


async def example_2_multiple_files():
    """示例 2: 多个文件"""
    print("\n" + "="*80)
    print("示例 2: 多个文件 - 需求文档 + 设计文档")
    print("="*80)
    
    # 获取文件存储
    storage = get_file_storage()
    
    # 添加需求文档
    file_id_1 = "example_file_002"
    storage[file_id_1] = {
        "filename": "API网关需求.md",
        "markdown": """# API 网关 - 应用管理功能需求

## 功能描述
开发者可以创建应用，并为应用配置多种认证方式。

## 功能点
1. 创建应用：开发者可以创建新应用，填写应用名称、描述等信息
2. 编辑应用：开发者可以修改应用的基本信息
3. 删除应用：开发者可以删除不再使用的应用
4. 应用列表：开发者可以查看自己创建的所有应用

## 验收标准
- 应用名称不能为空，长度 1-50 个字符
- 应用描述可选，最大长度 200 个字符
- 删除应用时需要二次确认
- 应用列表支持分页，每页显示 10 条记录
""",
        "metadata": {}
    }
    
    # 添加设计文档
    file_id_2 = "example_file_003"
    storage[file_id_2] = {
        "filename": "应用管理UI设计.md",
        "markdown": """# 应用管理 UI 设计文档

## 页面布局
- 顶部：标题 "我的应用" + "创建应用" 按钮
- 中间：应用列表（表格形式）
- 底部：分页控件

## 应用列表表格
| 列名 | 说明 |
|------|------|
| 应用名称 | 显示应用名称，可点击查看详情 |
| 应用描述 | 显示应用描述，超过 50 字符显示省略号 |
| 创建时间 | 显示创建时间，格式: YYYY-MM-DD HH:mm:ss |
| 操作 | 编辑、删除按钮 |

## 创建应用弹窗
- 应用名称输入框（必填）
- 应用描述输入框（可选，多行文本）
- 确定、取消按钮
""",
        "metadata": {}
    }
    
    print(f"✓ 添加文件 1: {storage[file_id_1]['filename']}")
    print(f"✓ 添加文件 2: {storage[file_id_2]['filename']}")
    
    # 构建包含多个文件上下文的消息
    user_message = "请根据需求文档和设计文档，生成应用管理功能的完整测试用例"
    message_with_context = _build_message_with_file_context(
        user_message, 
        [file_id_1, file_id_2]
    )
    
    print(f"\n📝 发送给大模型的完整消息:")
    print("-" * 80)
    print(message_with_context)
    print("-" * 80)


async def example_3_no_files():
    """示例 3: 不使用文件上下文"""
    print("\n" + "="*80)
    print("示例 3: 不使用文件上下文")
    print("="*80)
    
    # 不传递文件 ID
    user_message = "请生成一个简单的登录功能测试用例"
    message_with_context = _build_message_with_file_context(user_message, None)
    
    print(f"📝 原始消息: {user_message}")
    print(f"📝 处理后消息: {message_with_context}")
    
    if user_message == message_with_context:
        print("✓ 没有文件时，消息保持不变")


async def example_4_file_not_found():
    """示例 4: 文件不存在的情况"""
    print("\n" + "="*80)
    print("示例 4: 文件不存在的情况")
    print("="*80)
    
    # 传递不存在的文件 ID
    user_message = "请生成测试用例"
    nonexistent_file_ids = ["nonexistent_001", "nonexistent_002"]
    
    print(f"⚠️ 尝试使用不存在的文件 ID: {nonexistent_file_ids}")
    
    message_with_context = _build_message_with_file_context(
        user_message, 
        nonexistent_file_ids
    )
    
    if user_message == message_with_context:
        print("✓ 文件不存在时，返回原始消息（不会报错）")


async def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("文件上下文功能示例")
    print("="*80)
    
    # 运行示例
    await example_1_basic_usage()
    await example_2_multiple_files()
    await example_3_no_files()
    await example_4_file_not_found()
    
    print("\n" + "="*80)
    print("示例运行完成")
    print("="*80)
    print("\n💡 提示:")
    print("  1. 在实际使用中，文件内容来自 Markdown 转换 API")
    print("  2. 文件 ID 由 API 自动生成并返回给前端")
    print("  3. 前端在发送测试用例生成请求时，携带 file_ids 参数")
    print("  4. 后端自动将文件内容添加到大模型的上下文中")
    print("\n📚 相关 API:")
    print("  - POST /api/convert/markdown/batch - 批量转换文件为 Markdown")
    print("  - POST /api/team/chat/stream - 测试用例团队流式对话")


if __name__ == "__main__":
    asyncio.run(main())

