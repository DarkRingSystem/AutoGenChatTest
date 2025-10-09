# UI 图片分析智能体团队实现文档

## 概述

本文档描述了 UI 图片分析智能体团队的完整实现，包括架构设计、核心功能、使用方法和扩展指南。

## 实现时间

2025-10-08

## 核心文件

### 1. 模型客户端管理 (`backend/examples/llms.py`)

**功能**：
- 提供统一的 LLM 模型客户端管理
- 支持多种模型类型（默认模型、视觉模型、UI-TARS 模型）
- 实现客户端缓存机制，提高性能

**主要函数**：
```python
# 获取 UI-TARS 模型客户端（用于 UI 自动化）
get_uitars_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient

# 获取视觉模型客户端（用于图像理解）
get_vision_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient

# 获取默认模型客户端（用于通用对话）
get_default_model_client(settings: Optional[Settings] = None) -> OpenAIChatCompletionClient

# 重置所有模型客户端缓存
reset_model_clients() -> None
```

**特性**：
- 自动推断模型家族（DeepSeek、OpenAI、Anthropic、Google、Qwen）
- 支持自定义模型配置
- 全局缓存机制，避免重复创建客户端

### 2. 图片分析团队 (`backend/examples/image_analyzer.py`)

**功能**：
- 实现基于 AutoGen 的多智能体协作系统
- 支持 UI 界面图片的深度分析
- 生成测试场景和自动化测试建议

**核心类**：
```python
class ImageAnalyzerTeam:
    """UI 图片分析智能体团队"""
    
    async def initialize(self) -> None:
        """初始化团队"""
    
    async def analyze_image(
        self, 
        image_path: str, 
        user_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析 UI 图片"""
    
    async def analyze_image_stream(
        self, 
        image_path: str, 
        user_requirements: Optional[str] = None
    ):
        """流式分析 UI 图片"""
```

**团队成员**：

1. **UI 专家 (UI_Expert)**
   - 分析视觉元素和布局结构
   - 识别 UI 组件和设计模式
   - 提供元素定位信息

2. **交互分析师 (Interaction_Analyst)**
   - 分析交互行为和用户流程
   - 识别可交互元素
   - 提出测试场景建议

3. **测试场景专家 (Test_Scenario_Expert)**
   - 综合前两位专家的分析
   - 设计全面的测试场景
   - 提供自动化测试建议

**工作流程**：
```
用户提交图片 → UI 专家分析 → 交互分析师分析 → 测试场景专家综合 → 输出结果
```

### 3. 配置管理 (`backend/config.py`)

**新增配置项**：
```python
# UI-TARS 模型配置
uitars_model: str = "gpt-4o"
uitars_api_key: Optional[str] = None
uitars_base_url: Optional[str] = None

# 视觉模型配置
vision_model: Optional[str] = None
vision_api_key: Optional[str] = None
vision_base_url: Optional[str] = None
```

### 4. 提示词文件

**新增提示词**：
- `backend/prompts/ui_expert.txt` - UI 专家系统提示词
- `backend/prompts/interaction_analyst.txt` - 交互分析师系统提示词
- `backend/prompts/test_scenario_expert.txt` - 测试场景专家系统提示词

**提示词管理**：
```python
# backend/prompts/prompt_loader.py
class PromptNames:
    UI_EXPERT = "ui_expert"
    INTERACTION_ANALYST = "interaction_analyst"
    TEST_SCENARIO_EXPERT = "test_scenario_expert"
```

## 架构设计

### 多智能体协作模式

使用 **RoundRobinGroupChat** 模式：
- 智能体按顺序轮流发言
- 每个智能体基于前面的分析结果进行工作
- 测试场景专家完成后发送终止信号

### 终止条件

```python
termination_condition = (
    TextMentionTermination("ANALYSIS_COMPLETE") |  # 文本终止
    MaxMessageTermination(15)                       # 最大消息数
)
```

### 数据流

```
输入: 图片路径 + 用户需求
  ↓
任务消息构建
  ↓
团队协作分析
  ↓
结果解析和分类
  ↓
输出: 结构化分析结果
```

## 使用示例

### 基本使用

```python
import asyncio
from backend.config import Settings
from backend.examples.image_analyzer import ImageAnalyzerTeam

async def main():
    # 1. 创建配置
    settings = Settings.from_env()
    
    # 2. 创建团队
    analyzer_team = ImageAnalyzerTeam(settings)
    
    # 3. 初始化
    await analyzer_team.initialize()
    
    # 4. 分析图片
    results = await analyzer_team.analyze_image(
        image_path="screenshot.png",
        user_requirements="重点关注表单验证"
    )
    
    # 5. 使用结果
    print("UI 分析:", results["ui_analysis"])
    print("交互分析:", results["interaction_analysis"])
    print("测试场景:", results["test_scenarios"])

asyncio.run(main())
```

### 流式分析

```python
async def stream_analysis():
    analyzer_team = ImageAnalyzerTeam()
    await analyzer_team.initialize()
    
    async for event in analyzer_team.analyze_image_stream("screenshot.png"):
        # 实时处理事件
        print(f"事件: {type(event).__name__}")
```

### 批量分析

```python
async def batch_analysis():
    analyzer_team = ImageAnalyzerTeam()
    await analyzer_team.initialize()
    
    images = ["page1.png", "page2.png", "page3.png"]
    results = []
    
    for image in images:
        result = await analyzer_team.analyze_image(image)
        results.append(result)
    
    return results
```

## 配置指南

### 环境变量配置

在 `.env` 文件中配置：

```bash
# 基础配置
API_KEY=your_api_key
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1

# 视觉模型（推荐使用支持图像的模型）
VISION_MODEL=gpt-4o
VISION_API_KEY=your_openai_key
VISION_BASE_URL=https://api.openai.com/v1

# UI-TARS 模型（可选）
UITARS_MODEL=gpt-4o
UITARS_API_KEY=your_openai_key
UITARS_BASE_URL=https://api.openai.com/v1
```

### 推荐模型

| 用途 | 推荐模型 | 原因 |
|------|---------|------|
| 图像分析 | GPT-4o, Claude 3.5 Sonnet | 强大的视觉理解能力 |
| 文本分析 | DeepSeek-Chat, GPT-4 | 高质量文本生成 |
| UI 自动化 | GPT-4o | 支持视觉和函数调用 |

## 测试

### 运行测试

```bash
cd backend/examples
python test_image_analyzer.py
```

### 测试覆盖

- ✓ 团队初始化
- ✓ 任务消息构建
- ✓ 结果解析
- ✓ 模型客户端管理

## 扩展指南

### 添加新的团队成员

1. 创建提示词文件：
```bash
touch backend/prompts/new_agent.txt
```

2. 在 `PromptNames` 中添加常量：
```python
class PromptNames:
    NEW_AGENT = "new_agent"
```

3. 在 `_create_team_members()` 中添加智能体：
```python
new_agent = AssistantAgent(
    name="New_Agent",
    model_client=self.vision_model_client,
    system_message=load_prompt(PromptNames.NEW_AGENT),
    model_client_stream=self.settings.enable_streaming,
)
self.agents.append(new_agent)
```

### 自定义工作流

修改 `_create_team()` 方法以使用不同的协作模式：

```python
# 使用选择器模式
from autogen_agentchat.teams import SelectorGroupChat

self.team = SelectorGroupChat(
    participants=self.agents,
    model_client=self.vision_model_client,
    termination_condition=termination_condition,
)
```

### 自定义终止条件

```python
from autogen_agentchat.conditions import (
    TextMentionTermination,
    MaxMessageTermination,
    TimeoutTermination
)

# 组合多个终止条件
termination_condition = (
    TextMentionTermination("DONE") |
    MaxMessageTermination(20) |
    TimeoutTermination(300)  # 5 分钟超时
)
```

## 性能优化

### 1. 客户端缓存

模型客户端使用全局缓存，避免重复创建：
```python
# 第一次调用创建客户端
client1 = get_vision_model_client()

# 后续调用返回缓存的客户端
client2 = get_vision_model_client()  # 返回 client1
```

### 2. 流式输出

使用流式分析可以更快地获得初步结果：
```python
async for event in analyzer_team.analyze_image_stream(image_path):
    # 实时处理事件，无需等待全部完成
    process_event(event)
```

### 3. 批量处理

批量分析时重用同一个团队实例：
```python
analyzer_team = ImageAnalyzerTeam()
await analyzer_team.initialize()  # 只初始化一次

for image in images:
    result = await analyzer_team.analyze_image(image)
```

## 注意事项

1. **API 成本**：视觉模型的调用成本较高，建议合理使用
2. **图片大小**：建议图片大小不超过 20MB
3. **速率限制**：注意 API 的速率限制
4. **模型选择**：确保使用支持视觉输入的模型

## 相关文档

- [README_IMAGE_ANALYZER.md](../backend/examples/README_IMAGE_ANALYZER.md) - 详细使用指南
- [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md) - 配置指南
- [AutoGen 官方文档](https://microsoft.github.io/autogen/)

## 更新日志

### 2025-10-08
- ✅ 实现 `llms.py` 模型客户端管理
- ✅ 实现 `image_analyzer.py` 图片分析团队
- ✅ 添加配置项到 `config.py`
- ✅ 创建三个提示词文件
- ✅ 更新 `prompt_loader.py`
- ✅ 创建示例脚本和测试脚本
- ✅ 编写完整文档

## 总结

UI 图片分析智能体团队是一个功能完整、易于扩展的多智能体协作系统。通过三个专业智能体的协作，可以对 UI 界面图片进行深度分析，并生成高质量的测试场景和自动化测试建议。

系统采用模块化设计，支持自定义配置、扩展团队成员和调整工作流程，适合各种 UI 测试自动化场景。

