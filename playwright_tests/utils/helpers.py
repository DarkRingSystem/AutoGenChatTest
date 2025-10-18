"""
Playwright 辅助函数
提供常用的工具函数
"""

from playwright.sync_api import Page, Locator
from typing import Optional, Union
import os
from datetime import datetime


def wait_for_element(
    page: Page,
    selector: str,
    timeout: int = 30000,
    state: str = 'visible'
) -> Locator:
    """
    等待元素出现
    
    Args:
        page: Playwright 页面对象
        selector: 元素选择器
        timeout: 超时时间（毫秒）
        state: 元素状态 ('visible', 'hidden', 'attached', 'detached')
    
    Returns:
        Locator: 元素定位器
    """
    locator = page.locator(selector)
    locator.wait_for(state=state, timeout=timeout)
    return locator


def take_screenshot(
    page: Page,
    name: str,
    full_page: bool = True,
    path: Optional[str] = None
) -> str:
    """
    截取页面截图
    
    Args:
        page: Playwright 页面对象
        name: 截图文件名
        full_page: 是否截取整个页面
        path: 保存路径（可选）
    
    Returns:
        str: 截图文件路径
    """
    if path is None:
        path = 'playwright_tests/reports/screenshots'
    
    os.makedirs(path, exist_ok=True)
    
    # 添加时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join(path, filename)
    
    page.screenshot(path=filepath, full_page=full_page)
    return filepath


def scroll_to_element(page: Page, selector: str) -> None:
    """
    滚动到指定元素
    
    Args:
        page: Playwright 页面对象
        selector: 元素选择器
    """
    element = page.locator(selector)
    element.scroll_into_view_if_needed()


def get_element_text(page: Page, selector: str) -> str:
    """
    获取元素文本内容
    
    Args:
        page: Playwright 页面对象
        selector: 元素选择器
    
    Returns:
        str: 元素文本内容
    """
    return page.locator(selector).text_content() or ''


def wait_for_navigation(
    page: Page,
    url_pattern: Optional[str] = None,
    timeout: int = 30000
) -> None:
    """
    等待页面导航完成
    
    Args:
        page: Playwright 页面对象
        url_pattern: URL 匹配模式（可选）
        timeout: 超时时间（毫秒）
    """
    if url_pattern:
        page.wait_for_url(url_pattern, timeout=timeout)
    else:
        page.wait_for_load_state('networkidle', timeout=timeout)


def fill_form_field(
    page: Page,
    selector: str,
    value: str,
    clear_first: bool = True
) -> None:
    """
    填写表单字段
    
    Args:
        page: Playwright 页面对象
        selector: 元素选择器
        value: 要填写的值
        clear_first: 是否先清空字段
    """
    if clear_first:
        page.fill(selector, '')
    page.fill(selector, value)


def select_dropdown_option(
    page: Page,
    selector: str,
    value: Optional[str] = None,
    label: Optional[str] = None,
    index: Optional[int] = None
) -> None:
    """
    选择下拉框选项
    
    Args:
        page: Playwright 页面对象
        selector: 下拉框选择器
        value: 选项值
        label: 选项标签
        index: 选项索引
    """
    if value:
        page.select_option(selector, value=value)
    elif label:
        page.select_option(selector, label=label)
    elif index is not None:
        page.select_option(selector, index=index)
    else:
        raise ValueError("必须提供 value、label 或 index 之一")


def check_checkbox(page: Page, selector: str, checked: bool = True) -> None:
    """
    选中或取消选中复选框
    
    Args:
        page: Playwright 页面对象
        selector: 复选框选择器
        checked: True 为选中，False 为取消选中
    """
    if checked:
        page.check(selector)
    else:
        page.uncheck(selector)


def get_current_url(page: Page) -> str:
    """
    获取当前页面 URL
    
    Args:
        page: Playwright 页面对象
    
    Returns:
        str: 当前 URL
    """
    return page.url


def execute_javascript(page: Page, script: str, *args) -> any:
    """
    执行 JavaScript 代码
    
    Args:
        page: Playwright 页面对象
        script: JavaScript 代码
        *args: 传递给脚本的参数
    
    Returns:
        any: 脚本执行结果
    """
    return page.evaluate(script, *args)


def wait_for_timeout(page: Page, timeout: int) -> None:
    """
    等待指定时间
    
    Args:
        page: Playwright 页面对象
        timeout: 等待时间（毫秒）
    """
    page.wait_for_timeout(timeout)

