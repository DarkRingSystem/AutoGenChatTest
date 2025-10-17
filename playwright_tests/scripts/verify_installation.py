"""
Playwright 安装验证脚本
验证 Playwright 是否正确安装并可以正常运行
"""

import sys
import os


def verify_installation():
    """验证 Playwright 安装"""
    print("=" * 60)
    print("🔍 Playwright 安装验证")
    print("=" * 60)
    print()
    
    # 1. 检查 Playwright 导入
    print("1️⃣  检查 Playwright 导入...")
    try:
        from playwright.sync_api import sync_playwright
        print("   ✅ Playwright 导入成功")
    except ImportError as e:
        print(f"   ❌ Playwright 导入失败: {e}")
        return False
    
    # 2. 检查 pytest-playwright
    print("\n2️⃣  检查 pytest-playwright...")
    try:
        import pytest_playwright
        print("   ✅ pytest-playwright 导入成功")
    except ImportError as e:
        print(f"   ❌ pytest-playwright 导入失败: {e}")
        return False
    
    # 3. 检查配置文件
    print("\n3️⃣  检查配置文件...")
    config_files = [
        'playwright_tests/pytest.ini',
        'playwright_tests/playwright.config.py',
    ]
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file} 存在")
        else:
            print(f"   ❌ {config_file} 不存在")
            return False
    
    # 4. 检查目录结构
    print("\n4️⃣  检查目录结构...")
    directories = [
        'playwright_tests/scripts',
        'playwright_tests/tests',
        'playwright_tests/utils',
        'playwright_tests/reports/screenshots',
        'playwright_tests/reports/videos',
    ]
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ 存在")
        else:
            print(f"   ❌ {directory}/ 不存在")
            return False
    
    # 5. 测试浏览器启动
    print("\n5️⃣  测试浏览器启动...")
    try:
        with sync_playwright() as p:
            # 测试 Chromium
            print("   🌐 启动 Chromium...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://playwright.dev/')
            title = page.title()
            browser.close()
            print(f"   ✅ Chromium 启动成功，访问页面标题: {title[:50]}...")
            
    except Exception as e:
        print(f"   ❌ 浏览器启动失败: {e}")
        return False
    
    # 6. 检查浏览器安装
    print("\n6️⃣  检查已安装的浏览器...")
    try:
        import subprocess
        result = subprocess.run(
            ['playwright', 'install', '--dry-run'],
            capture_output=True,
            text=True
        )
        if 'chromium' in result.stdout.lower():
            print("   ✅ Chromium 已安装")
        if 'firefox' in result.stdout.lower():
            print("   ✅ Firefox 已安装")
        if 'webkit' in result.stdout.lower():
            print("   ✅ WebKit 已安装")
    except Exception as e:
        print(f"   ⚠️  无法检查浏览器安装状态: {e}")
    
    # 7. 检查示例文件
    print("\n7️⃣  检查示例文件...")
    example_files = [
        'playwright_tests/scripts/example_basic.py',
        'playwright_tests/scripts/example_form_interaction.py',
        'playwright_tests/tests/test_example.py',
    ]
    for example_file in example_files:
        if os.path.exists(example_file):
            print(f"   ✅ {example_file} 存在")
        else:
            print(f"   ❌ {example_file} 不存在")
    
    # 8. 检查工具模块
    print("\n8️⃣  检查工具模块...")
    try:
        sys.path.insert(0, os.path.abspath('.'))
        from playwright_tests.playwright_config import PlaywrightConfig
        print("   ✅ PlaywrightConfig 导入成功")
        print(f"   📝 默认浏览器: {PlaywrightConfig.DEFAULT_BROWSER}")
        print(f"   📝 默认超时: {PlaywrightConfig.TIMEOUTS['default']}ms")
    except Exception as e:
        print(f"   ❌ 配置模块导入失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Playwright 安装验证完成！")
    print("=" * 60)
    print()
    print("📚 下一步:")
    print("   1. 运行示例脚本: python playwright_tests/scripts/example_basic.py")
    print("   2. 运行测试: cd playwright_tests && pytest")
    print("   3. 查看文档: cat playwright_tests/README.md")
    print()
    
    return True


if __name__ == '__main__':
    success = verify_installation()
    sys.exit(0 if success else 1)

