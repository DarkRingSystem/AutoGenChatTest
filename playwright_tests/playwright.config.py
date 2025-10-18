"""
Playwright 配置文件
用于配置浏览器、超时、截图等选项
"""

from typing import Dict, Any


class PlaywrightConfig:
    """Playwright 配置类"""
    
    # 浏览器配置
    BROWSERS = {
        'chromium': {
            'headless': False,  # 是否无头模式
            'slow_mo': 500,     # 操作延迟（毫秒）
            'args': [
                '--start-maximized',  # 最大化窗口
            ]
        },
        'firefox': {
            'headless': False,
            'slow_mo': 500,
        },
        'webkit': {
            'headless': False,
            'slow_mo': 500,
        }
    }
    
    # 默认浏览器
    DEFAULT_BROWSER = 'chromium'
    
    # 超时配置（毫秒）
    TIMEOUTS = {
        'default': 30000,      # 默认超时 30 秒
        'navigation': 30000,   # 页面导航超时
        'action': 10000,       # 操作超时
        'wait': 5000,          # 等待超时
    }
    
    # 视口配置
    VIEWPORT = {
        'width': 1920,
        'height': 1080,
    }
    
    # 截图配置
    SCREENSHOT = {
        'path': 'playwright/reports/screenshots',
        'full_page': True,
        'type': 'png',
    }
    
    # 视频录制配置
    VIDEO = {
        'dir': 'playwright/reports/videos',
        'size': {'width': 1920, 'height': 1080},
    }
    
    # 追踪配置
    TRACE = {
        'screenshots': True,
        'snapshots': True,
        'sources': True,
    }
    
    # 重试配置
    RETRY = {
        'max_retries': 2,
        'retry_delay': 1000,  # 毫秒
    }
    
    @classmethod
    def get_browser_config(cls, browser_name: str = None) -> Dict[str, Any]:
        """获取浏览器配置"""
        browser = browser_name or cls.DEFAULT_BROWSER
        return cls.BROWSERS.get(browser, cls.BROWSERS[cls.DEFAULT_BROWSER])
    
    @classmethod
    def get_launch_options(cls, browser_name: str = None, **kwargs) -> Dict[str, Any]:
        """获取浏览器启动选项"""
        config = cls.get_browser_config(browser_name)
        config.update(kwargs)
        return config
    
    @classmethod
    def get_context_options(cls, **kwargs) -> Dict[str, Any]:
        """获取浏览器上下文选项"""
        options = {
            'viewport': cls.VIEWPORT,
            'record_video_dir': cls.VIDEO['dir'],
            'record_video_size': cls.VIDEO['size'],
        }
        options.update(kwargs)
        return options

