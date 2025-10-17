# Playwright 自动化测试框架

本目录包含基于 Playwright 的浏览器自动化测试框架，使用最新版本的 Playwright (v1.55.0)。

## 📁 目录结构

```
playwright_tests/
├── scripts/              # 自动化脚本
│   ├── example_basic.py              # 基础示例
│   └── example_form_interaction.py   # 表单交互示例
├── tests/               # 测试用例
│   └── test_example.py              # 示例测试
├── utils/               # 工具模块
│   ├── __init__.py
│   ├── helpers.py                   # 辅助函数
│   └── page_objects.py              # 页面对象模型
├── reports/             # 测试报告
│   ├── screenshots/                 # 截图
│   └── videos/                      # 视频录制
├── pytest.ini           # Pytest 配置
├── playwright.config.py # Playwright 配置
└── README.md           # 本文件
```

## 🚀 快速开始

### 1. 环境准备

确保已激活虚拟环境：

```bash
# macOS/Linux
source backend/venv/bin/activate

# Windows
backend\venv\Scripts\activate
```

### 2. 验证安装

检查 Playwright 是否正确安装：

```bash
playwright --version
```

### 3. 运行示例脚本

#### 基础示例

```bash
python playwright_tests/scripts/example_basic.py
```

这个脚本会：
- 启动 Chromium 浏览器
- 访问 Playwright 官网
- 截取页面截图
- 点击 "Get started" 链接

#### 表单交互示例

```bash
python playwright_tests/scripts/example_form_interaction.py
```

这个脚本会：
- 访问示例表单页面
- 填写各种表单字段
- 提交表单
- 验证提交结果

### 4. 运行测试

#### 运行所有测试

```bash
cd playwright_tests
pytest
```

#### 运行特定测试

```bash
# 运行特定测试文件
pytest tests/test_example.py

# 运行特定测试类
pytest tests/test_example.py::TestPlaywrightBasic

# 运行特定测试方法
pytest tests/test_example.py::TestPlaywrightBasic::test_page_title
```

#### 使用标记运行测试

```bash
# 运行冒烟测试
pytest -m smoke

# 运行 UI 测试
pytest -m ui

# 运行慢速测试
pytest -m slow
```

#### 指定浏览器

```bash
# 使用 Chromium（默认）
pytest --browser chromium

# 使用 Firefox
pytest --browser firefox

# 使用 WebKit
pytest --browser webkit

# 使用多个浏览器
pytest --browser chromium --browser firefox
```

#### 无头模式

```bash
# 无头模式运行
pytest --headless

# 有头模式运行（默认）
pytest --headed
```

## 📝 配置说明

### pytest.ini

Pytest 配置文件，包含：
- 测试文件匹配模式
- 测试标记定义
- 日志配置
- 默认参数

### playwright.config.py

Playwright 配置类，包含：
- 浏览器配置（Chromium、Firefox、WebKit）
- 超时设置
- 视口大小
- 截图和视频录制配置
- 追踪配置

## 🛠️ 工具模块

### helpers.py

提供常用的辅助函数：

```python
from playwright_tests.utils.helpers import (
    wait_for_element,
    take_screenshot,
    scroll_to_element,
    get_element_text,
    fill_form_field,
    select_dropdown_option,
    check_checkbox,
)

# 使用示例
wait_for_element(page, '.my-element')
take_screenshot(page, 'my_screenshot')
fill_form_field(page, '#username', 'testuser')
```

### page_objects.py

提供页面对象模型基类：

```python
from playwright_tests.utils.page_objects import BasePage

class MyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = 'https://example.com'
    
    def open(self):
        self.navigate(self.url)
    
    def click_button(self):
        self.click('#my-button')
```

## 📊 测试报告

### 截图

测试过程中的截图保存在 `playwright_tests/reports/screenshots/` 目录。

### 视频录制

测试视频保存在 `playwright_tests/reports/videos/` 目录。

要启用视频录制，在测试中配置：

```python
@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        'record_video_dir': 'playwright_tests/reports/videos',
    }
```

### HTML 报告

生成 HTML 测试报告：

```bash
pytest --html=playwright_tests/reports/report.html --self-contained-html
```

## 🎯 最佳实践

### 1. 使用 Page Object Model

将页面元素和操作封装到页面对象中：

```python
class LoginPage(BasePage):
    USERNAME = '#username'
    PASSWORD = '#password'
    SUBMIT = 'button[type="submit"]'
    
    def login(self, username, password):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)
```

### 2. 使用显式等待

避免使用固定延迟，使用显式等待：

```python
# ❌ 不推荐
page.wait_for_timeout(5000)

# ✅ 推荐
page.wait_for_selector('.element', state='visible')
```

### 3. 使用有意义的选择器

优先使用语义化选择器：

```python
# ✅ 推荐
page.get_by_role('button', name='Submit')
page.get_by_label('Username')
page.get_by_text('Welcome')

# ⚠️ 次选
page.locator('#submit-btn')
page.locator('.username-input')
```

### 4. 错误处理和截图

在测试失败时自动截图：

```python
@pytest.fixture(autouse=True)
def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f'error_{request.node.name}.png')
```

### 5. 使用测试标记

合理使用测试标记组织测试：

```python
@pytest.mark.smoke
def test_critical_feature():
    pass

@pytest.mark.slow
def test_long_running():
    pass
```

## 🔧 常见问题

### 浏览器未安装

如果遇到浏览器未安装的错误：

```bash
playwright install
```

### 权限问题

如果遇到权限问题，确保虚拟环境已激活：

```bash
source backend/venv/bin/activate
```

### 超时问题

如果测试经常超时，可以增加超时时间：

```python
# 在 playwright.config.py 中调整
TIMEOUTS = {
    'default': 60000,  # 60 秒
}
```

## 📚 参考资源

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright Python API](https://playwright.dev/python/docs/intro)
- [pytest-playwright 文档](https://playwright.dev/python/docs/test-runners)
- [最佳实践指南](https://playwright.dev/docs/best-practices)

## 🤝 贡献

欢迎提交问题和改进建议！

---

**版本信息**
- Playwright: v1.55.0
- pytest-playwright: v0.7.1
- Python: 3.11+

