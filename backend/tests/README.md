# Backend 测试目录

本目录包含后端的单元测试和集成测试。

## 📁 目录结构

```
backend/tests/
├── README.md                          # 本文件
├── test_markdown_converter.py         # Markdown 转换器测试
├── test_uitars_auth.py                # UI-TARS 认证测试
├── test_uitars_vision.py              # UI-TARS 视觉模型测试
├── test_graphflow.py                  # GraphFlow 工作流测试
├── test_image_analyzer.py             # 图片分析器测试
└── test_image_analyzer_api.py         # 图片分析 API 测试
```

## 🧪 测试说明

### Markdown 转换器测试
- **文件**: `test_markdown_converter.py`
- **功能**: 测试 Markdown 转换服务
- **运行**: `python -m pytest test_markdown_converter.py`

### UI-TARS 模型测试
- **文件**: `test_uitars_auth.py`, `test_uitars_vision.py`
- **功能**: 测试 UI-TARS 模型的认证和视觉分析功能
- **运行**: `python test_uitars_auth.py` 或 `python test_uitars_vision.py`

### GraphFlow 测试
- **文件**: `test_graphflow.py`
- **功能**: 测试 AutoGen GraphFlow 工作流
- **运行**: `python test_graphflow.py`

### 图片分析器测试
- **文件**: `test_image_analyzer.py`, `test_image_analyzer_api.py`
- **功能**: 测试图片分析智能体团队和 API
- **运行**: `python test_image_analyzer.py` 或 `python test_image_analyzer_api.py`

## 🚀 运行所有测试

```bash
# 进入 backend 目录
cd backend

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 运行所有 pytest 测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_markdown_converter.py -v
```

## 📝 编写测试

### 测试文件命名规范
- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 测试类以 `Test` 开头

### 示例测试

```python
import pytest
from services.my_service import MyService

class TestMyService:
    def test_basic_functionality(self):
        service = MyService()
        result = service.do_something()
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        service = MyService()
        result = await service.do_async_something()
        assert result is not None
```

## 🔗 相关文档

- [项目测试指南](../../docs/TROUBLESHOOTING.md)
- [集成测试](../../tests/README.md)
- [API 文档](../../docs/ARCHITECTURE.md)

