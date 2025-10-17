"""
Page Object Model (POM) 基类
提供页面对象模型的基础实现
"""

from playwright.sync_api import Page
from typing import Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from playwright_tests.playwright_config import PlaywrightConfig


class BasePage:
    """页面对象基类"""
    
    def __init__(self, page: Page):
        """
        初始化页面对象
        
        Args:
            page: Playwright 页面对象
        """
        self.page = page
        self.timeout = PlaywrightConfig.TIMEOUTS['default']
    
    def navigate(self, url: str) -> None:
        """
        导航到指定 URL
        
        Args:
            url: 目标 URL
        """
        self.page.goto(url, timeout=PlaywrightConfig.TIMEOUTS['navigation'])
        self.page.wait_for_load_state('networkidle')
    
    def get_title(self) -> str:
        """
        获取页面标题
        
        Returns:
            str: 页面标题
        """
        return self.page.title()
    
    def get_url(self) -> str:
        """
        获取当前 URL
        
        Returns:
            str: 当前 URL
        """
        return self.page.url
    
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self.timeout
        self.page.click(selector, timeout=timeout)
    
    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """
        填写输入框
        
        Args:
            selector: 元素选择器
            value: 要填写的值
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self.timeout
        self.page.fill(selector, value, timeout=timeout)
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            str: 元素文本内容
        """
        timeout = timeout or self.timeout
        return self.page.locator(selector).text_content(timeout=timeout) or ''
    
    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 元素是否可见
        """
        timeout = timeout or self.timeout
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except:
            return False
    
    def wait_for_selector(
        self,
        selector: str,
        state: str = 'visible',
        timeout: Optional[int] = None
    ) -> None:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            state: 元素状态
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self.timeout
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    def screenshot(
        self,
        path: str,
        full_page: bool = True
    ) -> None:
        """
        截取页面截图
        
        Args:
            path: 截图保存路径
            full_page: 是否截取整个页面
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.screenshot(path=path, full_page=full_page)
    
    def scroll_to_element(self, selector: str) -> None:
        """
        滚动到指定元素
        
        Args:
            selector: 元素选择器
        """
        self.page.locator(selector).scroll_into_view_if_needed()
    
    def execute_script(self, script: str, *args) -> any:
        """
        执行 JavaScript 代码
        
        Args:
            script: JavaScript 代码
            *args: 传递给脚本的参数
        
        Returns:
            any: 脚本执行结果
        """
        return self.page.evaluate(script, *args)
    
    def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """
        等待页面导航完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or PlaywrightConfig.TIMEOUTS['navigation']
        self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    def reload(self) -> None:
        """刷新页面"""
        self.page.reload()
        self.wait_for_navigation()
    
    def go_back(self) -> None:
        """返回上一页"""
        self.page.go_back()
        self.wait_for_navigation()
    
    def go_forward(self) -> None:
        """前进到下一页"""
        self.page.go_forward()
        self.wait_for_navigation()


class LoginPage(BasePage):
    """登录页面示例"""
    
    # 页面元素选择器
    USERNAME_INPUT = 'input[name="username"]'
    PASSWORD_INPUT = 'input[name="password"]'
    LOGIN_BUTTON = 'button[type="submit"]'
    ERROR_MESSAGE = '.error-message'
    
    def __init__(self, page: Page, url: str):
        """
        初始化登录页面
        
        Args:
            page: Playwright 页面对象
            url: 登录页面 URL
        """
        super().__init__(page)
        self.url = url
    
    def open(self) -> None:
        """打开登录页面"""
        self.navigate(self.url)
    
    def login(self, username: str, password: str) -> None:
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
        """
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
    
    def get_error_message(self) -> str:
        """
        获取错误消息
        
        Returns:
            str: 错误消息文本
        """
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ''

