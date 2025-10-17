# Playwright 快速开始指南

## 🚀 5 分钟快速上手

### 步骤 1: 激活虚拟环境

```bash
# macOS/Linux
source backend/venv/bin/activate

# Windows
backend\venv\Scripts\activate
```

### 步骤 2: 验证安装

```bash
python playwright_tests/scripts/verify_installation.py
```

你应该看到所有检查项都显示 ✅

### 步骤 3: 运行第一个示例

```bash
python playwright_tests/scripts/example_basic.py
```

这个脚本会：
- 启动 Chromium 浏览器
- 访问 Playwright 官网
- 截取页面截图
- 点击 "Get started" 链接

### 步骤 4: 运行测试

```bash
cd playwright_tests
pytest -v
```

## 📝 常用命令

### 运行示例脚本

```bash
# 基础示例
python playwright_tests/scripts/example_basic.py

# 表单交互示例
python playwright_tests/scripts/example_form_interaction.py
```

### 运行测试

```bash
# 运行所有测试
cd playwright_tests && pytest

# 运行特定测试文件
pytest tests/test_example.py

# 运行特定测试类
pytest tests/test_example.py::TestPlaywrightBasic

# 运行特定测试方法
pytest tests/test_example.py::TestPlaywrightBasic::test_page_title

# 使用标记运行测试
pytest -m smoke          # 冒烟测试
pytest -m ui             # UI 测试
pytest -m slow           # 慢速测试
```

### 浏览器选项

```bash
# 使用不同浏览器
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# 使用多个浏览器
pytest --browser chromium --browser firefox

# 无头模式
pytest --headless

# 有头模式（默认）
pytest --headed

# 慢速模式（方便观察）
pytest --slowmo 1000
```

### 生成报告

```bash
# HTML 报告
pytest --html=reports/report.html --self-contained-html

# JUnit XML 报告
pytest --junitxml=reports/junit.xml

# 详细输出
pytest -v

# 显示打印输出
pytest -s
```

## 🎯 编写你的第一个测试

### 1. 创建测试文件

在 `playwright_tests/tests/` 目录下创建 `test_my_first.py`:

```python
import pytest
from playwright.sync_api import Page, expect


class TestMyFirst:
    """我的第一个测试"""
    
    @pytest.mark.smoke
    def test_visit_website(self, page: Page):
        """访问网站测试"""
        # 访问网页
        page.goto('https://example.com')
        
        # 验证标题
        expect(page).to_have_title('Example Domain')
        
        # 验证内容
        heading = page.locator('h1')
        expect(heading).to_have_text('Example Domain')
```

### 2. 运行测试

```bash
cd playwright_tests
pytest tests/test_my_first.py -v
```

## 🛠️ 编写你的第一个脚本

### 1. 创建脚本文件

在 `playwright_tests/scripts/` 目录下创建 `my_first_script.py`:

```python
from playwright.sync_api import sync_playwright
import os


def run():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # 访问网页
        page.goto('https://example.com')
        
        # 截图
        os.makedirs('playwright_tests/reports/screenshots', exist_ok=True)
        page.screenshot(
            path='playwright_tests/reports/screenshots/my_first.png',
            full_page=True
        )
        
        print(f"✅ 页面标题: {page.title()}")
        print("✅ 截图已保存")
        
        # 关闭浏览器
        browser.close()


if __name__ == '__main__':
    run()
```

### 2. 运行脚本

```bash
python playwright_tests/scripts/my_first_script.py
```

## 📚 使用工具函数

### 使用辅助函数

```python
from playwright.sync_api import sync_playwright
from playwright_tests.utils.helpers import (
    wait_for_element,
    take_screenshot,
    fill_form_field,
)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    
    # 等待元素
    wait_for_element(page, 'h1')
    
    # 截图
    screenshot_path = take_screenshot(page, 'my_page')
    print(f"截图保存在: {screenshot_path}")
    
    browser.close()
```

### 使用页面对象模型

```python
from playwright.sync_api import sync_playwright
from playwright_tests.utils.page_objects import BasePage


class MyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = 'https://example.com'
    
    def open(self):
        self.navigate(self.url)
    
    def get_heading(self):
        return self.get_text('h1')


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    my_page = MyPage(page)
    my_page.open()
    heading = my_page.get_heading()
    print(f"标题: {heading}")
    
    browser.close()
```

## 🔧 常见问题

### Q: 浏览器未安装？

```bash
playwright install
```

### Q: 测试运行太快看不清？

```bash
pytest --headed --slowmo 1000
```

### Q: 想要录制视频？

在测试中添加 fixture:

```python
@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        'record_video_dir': 'playwright_tests/reports/videos',
    }
```

### Q: 想要调试测试？

```bash
# 使用 pytest 调试
pytest --pdb

# 使用 Playwright Inspector
PWDEBUG=1 pytest
```

## 📖 下一步

1. 阅读完整文档: `playwright_tests/README.md`
2. 查看更多示例: `playwright_tests/scripts/`
3. 学习测试用例: `playwright_tests/tests/`
4. 访问官方文档: https://playwright.dev/python/

## 🎉 开始你的自动化之旅！

现在你已经准备好使用 Playwright 进行浏览器自动化测试了！

有任何问题，请查看:
- 项目 README: `playwright_tests/README.md`
- 安装总结: `PLAYWRIGHT_SETUP_SUMMARY.md`
- Playwright 官方文档: https://playwright.dev/

