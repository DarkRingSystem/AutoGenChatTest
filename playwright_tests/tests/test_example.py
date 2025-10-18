"""
Playwright 测试示例
使用 pytest-playwright 进行自动化测试
"""

import pytest
from playwright.sync_api import Page, expect
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestPlaywrightBasic:
    """基础 Playwright 测试"""
    
    @pytest.mark.smoke
    def test_page_title(self, page: Page):
        """测试页面标题"""
        page.goto('https://playwright.dev/')
        expect(page).to_have_title('Fast and reliable end-to-end testing for modern web apps | Playwright')
    
    @pytest.mark.smoke
    def test_get_started_link(self, page: Page):
        """测试 Get Started 链接"""
        page.goto('https://playwright.dev/')
        
        # 点击 Get Started 链接
        get_started = page.get_by_role('link', name='Get started')
        expect(get_started).to_be_visible()
        get_started.click()
        
        # 验证 URL 变化
        expect(page).to_have_url('https://playwright.dev/docs/intro')
    
    @pytest.mark.ui
    def test_search_functionality(self, page: Page):
        """测试搜索功能"""
        page.goto('https://playwright.dev/')
        
        # 查找搜索按钮
        search_button = page.get_by_label('Search')
        if search_button.is_visible():
            search_button.click()
            
            # 输入搜索内容
            search_input = page.get_by_placeholder('Search docs')
            search_input.fill('installation')
            
            # 等待搜索结果
            page.wait_for_timeout(1000)
            
            # 验证搜索结果存在
            results = page.locator('.DocSearch-Hits')
            expect(results).to_be_visible()


class TestPlaywrightForm:
    """表单测试"""
    
    @pytest.mark.ui
    def test_form_submission(self, page: Page):
        """测试表单提交"""
        page.goto('https://www.selenium.dev/selenium/web/web-form.html')
        
        # 填写表单
        page.fill('input[name="my-text"]', 'Test User')
        page.fill('input[name="my-password"]', 'password123')
        page.fill('textarea[name="my-textarea"]', 'Test message')
        
        # 提交表单
        page.click('button[type="submit"]')
        
        # 验证提交成功
        page.wait_for_load_state('networkidle')
        success_message = page.locator('.display-6')
        expect(success_message).to_be_visible()
        expect(success_message).to_contain_text('Received!')
    
    @pytest.mark.ui
    def test_dropdown_selection(self, page: Page):
        """测试下拉框选择"""
        page.goto('https://www.selenium.dev/selenium/web/web-form.html')
        
        # 选择下拉框选项
        page.select_option('select[name="my-select"]', label='Three')
        
        # 验证选择结果
        selected_value = page.locator('select[name="my-select"]').input_value()
        assert selected_value == '3'
    
    @pytest.mark.ui
    def test_checkbox_interaction(self, page: Page):
        """测试复选框交互"""
        page.goto('https://www.selenium.dev/selenium/web/web-form.html')
        
        checkbox = page.locator('input[name="my-check"]')
        
        # 验证初始状态
        expect(checkbox).not_to_be_checked()
        
        # 选中复选框
        checkbox.check()
        expect(checkbox).to_be_checked()
        
        # 取消选中
        checkbox.uncheck()
        expect(checkbox).not_to_be_checked()


class TestPlaywrightScreenshot:
    """截图测试"""
    
    @pytest.mark.ui
    def test_full_page_screenshot(self, page: Page):
        """测试全页面截图"""
        page.goto('https://playwright.dev/')
        
        # 创建截图目录
        screenshot_dir = 'playwright_tests/reports/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 截图
        screenshot_path = os.path.join(screenshot_dir, 'test_full_page.png')
        page.screenshot(path=screenshot_path, full_page=True)
        
        # 验证截图文件存在
        assert os.path.exists(screenshot_path)
    
    @pytest.mark.ui
    def test_element_screenshot(self, page: Page):
        """测试元素截图"""
        page.goto('https://playwright.dev/')
        
        # 创建截图目录
        screenshot_dir = 'playwright_tests/reports/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 截取特定元素
        header = page.locator('header')
        screenshot_path = os.path.join(screenshot_dir, 'test_header.png')
        header.screenshot(path=screenshot_path)
        
        # 验证截图文件存在
        assert os.path.exists(screenshot_path)


# Pytest fixtures
@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    """自定义浏览器上下文参数"""
    return {
        **browser_context_args,
        'viewport': {
            'width': 1920,
            'height': 1080,
        },
        'locale': 'zh-CN',
    }


@pytest.fixture(autouse=True)
def setup_teardown(page: Page):
    """每个测试的设置和清理"""
    # 设置默认超时
    page.set_default_timeout(30000)
    
    yield
    
    # 测试后清理（如果需要）
    pass

