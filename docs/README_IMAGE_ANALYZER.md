# UI 图片分析智能体团队

## 概述

UI 图片分析智能体团队是一个基于 AutoGen 0.7.5 **GraphFlow** 的并行多智能体协作系统，专门用于深度分析 UI 界面图片，并生成全面的测试场景和自动化测试建议。

### 核心特性

- ✅ **GraphFlow 并行工作流** - UI_Expert 和 Interaction_Analyst 并行分析，提高效率
- ✅ **智能结果汇总** - Test_Scenario_Expert 综合并行分析结果
- ✅ **视觉分析** - 支持多模态输入，可直接分析图片
- ✅ **专业分工** - 三个专业智能体各司其职
- ✅ **流式输出** - 支持实时查看分析过程
- ✅ **结构化结果** - 提供清晰的分析结果结构

## 团队成员

### 1. UI 专家 (UI_Expert)
- **职责**：并行分析界面的视觉元素和布局结构
- **能力**：
  - 识别所有可见的 UI 元素
  - 分析元素的视觉属性和位置
  - 评估设计规范和一致性
  - 提供元素定位信息

### 2. 交互分析师 (Interaction_Analyst)
- **职责**：并行分析界面的交互行为和用户流程
- **能力**：
  - 识别可交互元素
  - 分析用户操作路径
  - 识别交互模式和反馈机制
  - 提出测试场景建议

### 3. 测试场景专家 (Test_Scenario_Expert)
- **职责**：综合前两位专家的并行分析结果，设计测试场景
- **能力**：
  - 整合 UI 和交互分析结果
  - 设计全面的测试场景
  - 提供自动化测试建议
  - 定义测试数据和预期结果

## 工作流程（GraphFlow）

```
┌─────────────┐
│  用户输入    │
│  (图片路径)  │
└──────┬──────┘
       │
┌──────┴──────┐
│             │
▼             ▼
UI_Expert   Interaction_Analyst
(并行分析)   (并行分析)
│             │
└──────┬──────┘
       │
       ▼
Test_Scenario_Expert
(综合分析)
       │
       ▼
┌─────────────┐
│  分析结果    │
└─────────────┘
```

**优势**：
- UI_Expert 和 Interaction_Analyst 并行执行，节省时间
- Test_Scenario_Expert 等待两者完成后再综合分析
- 充分利用多智能体并行能力

## 快速开始

### 1. 环境配置

在 `.env` 文件中配置模型信息：

```bash
# 基础配置
API_KEY=your_api_key_here
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1

# 视觉模型配置（可选，用于图像分析）
VISION_MODEL=gpt-4o
VISION_API_KEY=your_openai_api_key
VISION_BASE_URL=https://api.openai.com/v1

# UI-TARS 模型配置（可选，用于 UI 自动化）
UITARS_MODEL=gpt-4o
UITARS_API_KEY=your_openai_api_key
UITARS_BASE_URL=https://api.openai.com/v1
```

### 2. 基本使用

```python
import asyncio
from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam

async def main():
    # 创建配置
    settings = Settings.from_env()
    
    # 创建图片分析团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 初始化团队
    await analyzer_team.initialize()
    
    # 分析图片
    results = await analyzer_team.analyze_image(
        image_path="path/to/your/ui_screenshot.png",
        user_requirements="请重点关注登录表单的交互流程"
    )
    
    # 输出结果
    print("UI 分析:", results["ui_analysis"])
    print("交互分析:", results["interaction_analysis"])
    print("测试场景:", results["test_scenarios"])

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 流式分析

```python
async def stream_example():
    analyzer_team = ImageAnalyzerTeam()
    await analyzer_team.initialize()
    
    # 流式分析
    async for event in analyzer_team.analyze_image_stream(
        image_path="path/to/ui_screenshot.png"
    ):
        # 实时处理分析事件
        print(f"事件: {type(event).__name__}")
        if hasattr(event, 'content'):
            print(f"内容: {event.content}")
```

## 分析结果结构

```python
{
    "ui_analysis": [
        "UI 专家的第一条分析...",
        "UI 专家的第二条分析...",
    ],
    "interaction_analysis": [
        "交互分析师的第一条分析...",
        "交互分析师的第二条分析...",
    ],
    "test_scenarios": [
        "测试场景专家的第一个场景...",
        "测试场景专家的第二个场景...",
    ],
    "chat_history": [
        {
            "source": "UI_Expert",
            "content": "..."
        },
        {
            "source": "Interaction_Analyst",
            "content": "..."
        },
        {
            "source": "Test_Scenario_Expert",
            "content": "..."
        }
    ],
    "summary": "分析摘要..."
}
```

## 高级功能

### 批量分析

```python
async def batch_analyze():
    analyzer_team = ImageAnalyzerTeam()
    await analyzer_team.initialize()
    
    image_paths = [
        "login_page.png",
        "dashboard.png",
        "settings.png",
    ]
    
    results = []
    for image_path in image_paths:
        result = await analyzer_team.analyze_image(image_path)
        results.append(result)
    
    return results
```

### 自定义需求

```python
# 指定特定的分析需求
results = await analyzer_team.analyze_image(
    image_path="checkout_page.png",
    user_requirements="""
    请重点分析：
    1. 支付表单的验证逻辑
    2. 错误提示的显示方式
    3. 支付按钮的状态变化
    4. 敏感信息的安全处理
    """
)
```

## 配置说明

### 模型选择

- **默认模型**：使用 `MODEL_NAME` 配置的模型
- **视觉模型**：使用 `VISION_MODEL` 配置的模型（需要支持图像输入）
- **UI-TARS 模型**：使用 `UITARS_MODEL` 配置的模型（专门用于 UI 自动化）

### 推荐配置

| 场景 | 推荐模型 | 说明 |
|------|---------|------|
| 图像分析 | GPT-4o, Claude 3.5 Sonnet | 支持视觉输入 |
| 文本分析 | DeepSeek-Chat, GPT-4 | 高质量文本理解 |
| UI 自动化 | GPT-4o | 支持视觉和函数调用 |

## 提示词管理

团队使用的提示词文件位于 `backend/prompts/` 目录：

- `ui_expert.txt` - UI 专家的系统提示词
- `interaction_analyst.txt` - 交互分析师的系统提示词
- `test_scenario_expert.txt` - 测试场景专家的系统提示词

可以根据需要自定义这些提示词以优化分析效果。

## 终止条件

团队分析会在以下情况下终止：

1. 测试场景专家在回复中包含 `ANALYSIS_COMPLETE` 标记
2. 达到最大消息数（默认 15 条）

可以通过修改 `_create_team()` 方法中的终止条件来调整。

## 示例脚本

运行示例脚本：

```bash
cd backend/examples
python image_analyzer_example.py
```

选择不同的示例模式：
1. 单个图片分析
2. 流式分析
3. 批量分析

## 注意事项

1. **图片格式**：支持常见的图片格式（PNG, JPG, JPEG 等）
2. **图片大小**：建议图片大小不超过 20MB
3. **API 限制**：注意 API 的速率限制和 token 限制
4. **成本控制**：视觉模型的调用成本较高，建议合理使用

## 故障排除

### 问题：团队未初始化

```
RuntimeError: 团队未初始化，请先调用 initialize()
```

**解决方案**：在使用前调用 `await analyzer_team.initialize()`

### 问题：模型不支持视觉输入

```
Error: Model does not support vision
```

**解决方案**：配置支持视觉输入的模型（如 GPT-4o, Claude 3.5 Sonnet）

### 问题：API 密钥错误

```
Error: Invalid API key
```

**解决方案**：检查 `.env` 文件中的 API 密钥配置

## 扩展开发

### 添加新的团队成员

```python
# 在 _create_team_members() 方法中添加
new_agent = AssistantAgent(
    name="New_Agent",
    model_client=self.vision_model_client,
    system_message="新智能体的系统提示词",
    model_client_stream=self.settings.enable_streaming,
)

self.agents.append(new_agent)
```

### 自定义工作流

可以修改 `_create_team()` 方法来使用不同的团队协作模式：

- `RoundRobinGroupChat` - 轮流发言
- `SelectorGroupChat` - 选择器模式
- `Swarm` - 群体智能模式

## 相关文档

- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [提示词管理系统](../prompts/README.md)
- [配置指南](../../docs/CONFIGURATION_GUIDE.md)

## 许可证

本项目遵循 MIT 许可证。

