# UI 图片分析智能体团队 - 快速开始

## 5 分钟快速上手（GraphFlow 并行模式）

### 1. 配置环境变量

创建或编辑 `.env` 文件：

```bash
# 必需配置
API_KEY=your_api_key_here

# 推荐配置（用于图像分析）
VISION_MODEL=gpt-4o
VISION_API_KEY=your_openai_api_key
VISION_BASE_URL=https://api.openai.com/v1
```

### 2. 最简单的使用示例（自动并行执行）

```python
import asyncio
from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam

async def main():
    # 创建并初始化团队（使用 GraphFlow）
    team = ImageAnalyzerTeam()
    await team.initialize()

    # 分析图片（UI_Expert 和 Interaction_Analyst 自动并行执行）
    results = await team.analyze_image("your_screenshot.png")

    # 查看结果
    print(results["summary"])

asyncio.run(main())
```

**注意**：UI_Expert 和 Interaction_Analyst 会并行执行，显著提高分析速度！

### 3. 运行示例

```bash
cd backend/examples
python image_analyzer_example.py
```

### 4. 测试 GraphFlow 工作流

```bash
cd backend/examples
python test_graphflow.py
```

## 常用代码片段

### 分析单个图片

```python
from backend.examples.image_analyzer import ImageAnalyzerTeam

team = ImageAnalyzerTeam()
await team.initialize()

results = await team.analyze_image(
    image_path="login_page.png",
    user_requirements="重点分析表单验证逻辑"
)
```

### 流式分析（实时输出）

```python
async for event in team.analyze_image_stream("dashboard.png"):
    if hasattr(event, 'content'):
        print(event.content)
```

### 批量分析

```python
images = ["page1.png", "page2.png", "page3.png"]

for image in images:
    result = await team.analyze_image(image)
    print(f"{image}: {result['summary']}")
```

## 结果结构

```python
{
    "ui_analysis": [
        "UI 专家的分析内容..."
    ],
    "interaction_analysis": [
        "交互分析师的分析内容..."
    ],
    "test_scenarios": [
        "测试场景专家的场景设计..."
    ],
    "chat_history": [
        {"source": "UI_Expert", "content": "..."},
        {"source": "Interaction_Analyst", "content": "..."},
        {"source": "Test_Scenario_Expert", "content": "..."}
    ],
    "summary": "分析摘要..."
}
```

## 常见问题

### Q: 如何指定特定的分析需求？

```python
results = await team.analyze_image(
    image_path="checkout.png",
    user_requirements="""
    请重点分析：
    1. 支付表单的验证
    2. 错误提示的显示
    3. 按钮状态变化
    """
)
```

### Q: 如何使用不同的模型？

在 `.env` 文件中配置：

```bash
# 使用 Claude 进行图像分析
VISION_MODEL=claude-3-5-sonnet-20241022
VISION_API_KEY=your_anthropic_key
VISION_BASE_URL=https://api.anthropic.com
```

### Q: 如何查看详细的分析过程？

使用流式分析：

```python
async for event in team.analyze_image_stream("page.png"):
    print(f"[{type(event).__name__}]")
    if hasattr(event, 'source'):
        print(f"来源: {event.source}")
    if hasattr(event, 'content'):
        print(f"内容: {event.content}")
```

### Q: 如何控制分析的详细程度？

修改提示词文件：
- `backend/prompts/ui_expert.txt`
- `backend/prompts/interaction_analyst.txt`
- `backend/prompts/test_scenario_expert.txt`

## 团队成员职责

| 成员 | 职责 | 输出 |
|------|------|------|
| UI 专家 | 视觉和布局分析 | UI 元素清单、布局结构 |
| 交互分析师 | 交互行为分析 | 交互流程、用户路径 |
| 测试场景专家 | 测试场景设计 | 测试用例、自动化建议 |

## 下一步

- 📖 阅读 [完整文档](README_IMAGE_ANALYZER.md)
- 🧪 运行 [测试脚本](test_image_analyzer.py)
- 🎯 查看 [示例代码](image_analyzer_example.py)
- 📚 了解 [实现细节](../../docs/UI_IMAGE_ANALYZER_IMPLEMENTATION.md)

## 获取帮助

如果遇到问题：
1. 检查 `.env` 配置是否正确
2. 确认使用的模型支持视觉输入
3. 查看错误日志和堆栈跟踪
4. 参考完整文档

## 示例输出

```
🚀 正在初始化 UI 图片分析团队...
✅ UI-TARS 模型客户端已创建: gpt-4o
   ✓ 已创建 3 个团队成员
     - UI_Expert
     - Interaction_Analyst
     - Test_Scenario_Expert
   ✓ 团队协作机制已建立（RoundRobinGroupChat）
✅ UI 图片分析团队初始化成功！

🔍 开始分析 UI 图片...
   图片: login_page.png
   需求: 重点关注表单验证

✅ UI 图片分析完成！
   消息总数: 12

=== UI 图片分析摘要 ===

UI 分析条目数: 3
交互分析条目数: 2
测试场景条目数: 4
总消息数: 12

分析已完成，可用于后续的测试脚本生成。
```

