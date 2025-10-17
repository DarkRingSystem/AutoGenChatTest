"""
Playwright 基础示例脚本
演示如何使用 Playwright 进行基本的浏览器自动化
"""

from playwright.sync_api import sync_playwright
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from playwright_tests.playwright_config import PlaywrightConfig


def run_basic_example():
    """运行基础示例"""
    print("🚀 启动 Playwright 基础示例...")
    
    with sync_playwright() as p:
        # 获取浏览器配置
        launch_options = PlaywrightConfig.get_launch_options()
        
        # 启动浏览器
        print(f"📦 启动 {PlaywrightConfig.DEFAULT_BROWSER} 浏览器...")
        browser = p.chromium.launch(**launch_options)
        
        # 创建浏览器上下文
        context_options = PlaywrightConfig.get_context_options()
        context = browser.new_context(**context_options)
        
        # 创建新页面
        page = context.new_page()
        
        try:
            # 访问网页
            print("🌐 访问 Playwright 官网...")
            page.goto('https://playwright.dev/', timeout=PlaywrightConfig.TIMEOUTS['navigation'])
            
            # 等待页面加载
            page.wait_for_load_state('networkidle')
            
            # 获取页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 截图
            screenshot_path = os.path.join(
                'playwright_tests/reports/screenshots',
                'example_basic.png'
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 截图已保存: {screenshot_path}")
            
            # 查找并点击元素
            print("🔍 查找 'Get started' 链接...")
            get_started = page.get_by_role('link', name='Get started')
            if get_started.is_visible():
                print("✅ 找到 'Get started' 链接")
                get_started.click()
                page.wait_for_load_state('networkidle')
                print(f"📄 新页面标题: {page.title()}")
            
            # 等待用户观察
            print("\n⏸️  按 Enter 键继续...")
            input()
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            # 错误时截图
            error_screenshot = os.path.join(
                'playwright_tests/reports/screenshots',
                'error_basic.png'
            )
            os.makedirs(os.path.dirname(error_screenshot), exist_ok=True)
            page.screenshot(path=error_screenshot)
            print(f"📸 错误截图已保存: {error_screenshot}")
            
        finally:
            # 关闭浏览器
            print("🔚 关闭浏览器...")
            context.close()
            browser.close()
            print("✅ 示例完成！")


if __name__ == '__main__':
    run_basic_example()

