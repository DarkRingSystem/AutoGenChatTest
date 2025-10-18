"""
Playwright 表单交互示例
演示如何使用 Playwright 进行表单填写和交互
"""

from playwright.sync_api import sync_playwright
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from playwright_tests.playwright_config import PlaywrightConfig


def run_form_example():
    """运行表单交互示例"""
    print("🚀 启动 Playwright 表单交互示例...")
    
    with sync_playwright() as p:
        # 启动浏览器
        launch_options = PlaywrightConfig.get_launch_options()
        browser = p.chromium.launch(**launch_options)
        
        # 创建浏览器上下文
        context = browser.new_context(**PlaywrightConfig.get_context_options())
        page = context.new_page()
        
        try:
            # 访问示例表单页面
            print("🌐 访问示例表单页面...")
            page.goto('https://www.selenium.dev/selenium/web/web-form.html')
            page.wait_for_load_state('networkidle')
            
            print(f"📄 页面标题: {page.title()}")
            
            # 填写文本输入框
            print("✍️  填写文本输入框...")
            page.fill('input[name="my-text"]', 'Hello Playwright!')
            
            # 填写密码框
            print("🔒 填写密码框...")
            page.fill('input[name="my-password"]', 'SecurePassword123')
            
            # 填写文本域
            print("📝 填写文本域...")
            page.fill('textarea[name="my-textarea"]', 'This is a test message from Playwright automation.')
            
            # 选择下拉框
            print("📋 选择下拉框选项...")
            page.select_option('select[name="my-select"]', label='Two')
            
            # 选择单选按钮
            print("🔘 选择单选按钮...")
            page.check('input[value="1"]')
            
            # 选择复选框
            print("☑️  选择复选框...")
            page.check('input[name="my-check"]')
            
            # 选择日期
            print("📅 选择日期...")
            page.fill('input[name="my-date"]', '2025-10-17')
            
            # 截图 - 填写后的表单
            screenshot_path = os.path.join(
                'playwright_tests/reports/screenshots',
                'form_filled.png'
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 表单填写截图已保存: {screenshot_path}")
            
            # 提交表单
            print("🚀 提交表单...")
            page.click('button[type="submit"]')
            
            # 等待页面跳转或响应
            page.wait_for_load_state('networkidle')
            
            # 验证提交结果
            print("✅ 验证提交结果...")
            success_message = page.locator('.display-6')
            if success_message.is_visible():
                print(f"✅ 成功消息: {success_message.text_content()}")
            
            # 截图 - 提交后的页面
            result_screenshot = os.path.join(
                'playwright_tests/reports/screenshots',
                'form_submitted.png'
            )
            page.screenshot(path=result_screenshot, full_page=True)
            print(f"📸 提交结果截图已保存: {result_screenshot}")
            
            # 等待用户观察
            print("\n⏸️  按 Enter 键继续...")
            input()
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            error_screenshot = os.path.join(
                'playwright_tests/reports/screenshots',
                'error_form.png'
            )
            os.makedirs(os.path.dirname(error_screenshot), exist_ok=True)
            page.screenshot(path=error_screenshot)
            print(f"📸 错误截图已保存: {error_screenshot}")
            
        finally:
            print("🔚 关闭浏览器...")
            context.close()
            browser.close()
            print("✅ 示例完成！")


if __name__ == '__main__':
    run_form_example()

