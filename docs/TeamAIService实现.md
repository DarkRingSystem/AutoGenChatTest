# 🤝 TeamAIService 实现文档

## 📋 概述

基于 `team_ai_agents.py` 的结构，在 `ai_service.py` 中创建了一个新的 `TeamAIService` 类，用于管理多个智能体协作的团队。

---

## 🏗️ 架构设计

### 类结构

```python
class TeamAIService:
    """AI 团队服务类，管理多个智能体协作的团队"""
    
    def __init__(self, settings: Settings)
    async def initialize(self) -> None
    async def cleanup(self) -> None
    async def run(self, message: str)
    async def run_stream(self, message: str)
    
    # 私有方法
    def _create_team_agents(self) -> None
    def _create_team(self) -> None
    def _create_model_info(self) -> ModelInfo
    def _get_model_family(self) -> str
```

---

## 🎯 核心功能

### 1. **团队智能体创建**

团队包含 3 个智能体，各司其职：

#### Primary Agent（主要智能体）
- **角色**: 任务生成者
- **职责**: 生成初步的回答和方案
- **系统消息**: "你是一个主要的 AI 助手，负责生成初步的回答和方案。请提供详细、全面的回答。"

#### Critic Agent（评审智能体）
- **角色**: 质量检查者
- **职责**: 审查和改进主要智能体的回答
- **系统消息**: "你是一个评审专家，负责审查和改进主要智能体的回答。请提供建设性的反馈。如果回答已经足够好，请回复 'APPROVE'。"

#### Optimizer Agent（优化智能体）
- **角色**: 改进者
- **职责**: 根据评审意见改进回答
- **系统消息**: "你是一个优化专家，负责根据评审意见改进回答。请确保回答清晰、准确、易懂。"

---

### 2. **团队协作模式**

使用 **RoundRobinGroupChat**（轮询式团队聊天）：

```python
self.team = RoundRobinGroupChat(
    participants=self.agents,
    termination_condition=text_termination | max_message_termination,
)
```

#### 工作流程
1. **Primary Agent** 生成初步回答
2. **Critic Agent** 评审回答，提供反馈
3. **Optimizer Agent** 根据反馈改进回答
4. 循环往复，直到满足终止条件

---

### 3. **终止条件**

#### 文本终止条件
```python
text_termination = TextMentionTermination("APPROVE")
```
- 当 Critic Agent 回复 "APPROVE" 时停止

#### 最大消息数终止条件
```python
max_message_termination = MaxMessageTermination(max_messages=10)
```
- 防止无限循环，最多 10 条消息后强制停止

#### 组合终止条件
```python
termination_condition = text_termination | max_message_termination
```
- 满足任一条件即停止

---

## 📝 代码实现

### 完整代码

<augment_code_snippet path="backend/services/ai_service.py" mode="EXCERPT">
````python
class TeamAIService:
    """AI 团队服务类，管理多个智能体协作的团队"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        self.agents: List[AssistantAgent] = []
        self.team: Optional[RoundRobinGroupChat] = None
    
    async def initialize(self) -> None:
        """初始化 AI 团队"""
        # 创建模型客户端
        # 创建团队智能体
        # 创建团队
        ...
````
</augment_code_snippet>

---

## 🔧 使用方法

### 1. **初始化团队服务**

```python
from config import settings
from services.ai_service import TeamAIService

# 创建团队服务
team_service = TeamAIService(settings)

# 初始化
await team_service.initialize()
```

### 2. **运行团队（非流式）**

```python
# 发送任务给团队
result = await team_service.run("请帮我分析量子计算的发展趋势")

# 获取最终结果
print(result)
```

### 3. **运行团队（流式）**

```python
# 流式获取团队协作过程
async for event in team_service.run_stream("请帮我分析量子计算的发展趋势"):
    print(event)
```

### 4. **清理资源**

```python
await team_service.cleanup()
```

---

## 🆚 与 AIService 的对比

| 特性 | AIService | TeamAIService |
|------|-----------|---------------|
| **智能体数量** | 1 个 | 3 个 |
| **协作模式** | 单一智能体 | 轮询式团队协作 |
| **质量保证** | 无 | 有评审和优化流程 |
| **终止条件** | 单次回答 | 文本终止 + 最大消息数 |
| **适用场景** | 简单问答 | 复杂任务、需要多轮优化 |
| **响应时间** | 快 | 较慢（多轮协作） |
| **回答质量** | 标准 | 更高（经过评审和优化） |

---

## 📊 工作流程图

```
用户消息
   ↓
Primary Agent（生成初步回答）
   ↓
Critic Agent（评审回答）
   ↓
   ├─→ 回复 "APPROVE" → 结束
   └─→ 提供反馈
       ↓
   Optimizer Agent（改进回答）
       ↓
   Primary Agent（生成新回答）
       ↓
   （循环，直到 APPROVE 或达到最大消息数）
```

---

## 🎯 应用场景

### 适合使用 TeamAIService 的场景

1. **复杂问题分析**
   - 需要多角度思考
   - 需要反复推敲

2. **内容创作**
   - 文章写作
   - 代码生成
   - 方案设计

3. **质量要求高**
   - 需要评审流程
   - 需要多轮优化

### 适合使用 AIService 的场景

1. **简单问答**
   - 快速响应
   - 单次回答即可

2. **实时对话**
   - 聊天场景
   - 即时反馈

---

## 🔌 集成到现有系统

### 方式 1: 替换现有 AIService

```python
# 在 main.py 中
from services.ai_service import TeamAIService

# 替换
# ai_service = AIService(settings)
team_service = TeamAIService(settings)
await team_service.initialize()
```

### 方式 2: 并行使用

```python
# 同时提供两种服务
ai_service = AIService(settings)
team_service = TeamAIService(settings)

await ai_service.initialize()
await team_service.initialize()

# 根据需求选择使用
if task_is_complex:
    result = await team_service.run(message)
else:
    result = await ai_service.run(message)
```

### 方式 3: 添加新的 API 端点

```python
# 在 routes.py 中添加
@router.post("/api/team-chat")
async def team_chat(request: ChatRequest):
    """团队协作聊天端点"""
    team_service = get_team_service()
    result = await team_service.run(request.message)
    return ChatResponse(message=result)
```

---

## 📦 依赖项

### 新增导入

```python
from typing import List
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
```

### 已有依赖

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._model_info import ModelInfo
from config import Settings
```

---

## 🎨 自定义团队

### 修改智能体数量

```python
def _create_team_agents(self) -> None:
    """创建团队中的多个智能体"""
    # 添加更多智能体
    agent1 = AssistantAgent(...)
    agent2 = AssistantAgent(...)
    agent3 = AssistantAgent(...)
    agent4 = AssistantAgent(...)  # 新增
    
    self.agents = [agent1, agent2, agent3, agent4]
```

### 修改系统消息

```python
primary_agent = AssistantAgent(
    name="Primary_Agent",
    model_client=self.model_client,
    system_message="你的自定义系统消息",  # 修改这里
    model_client_stream=self.settings.enable_streaming,
)
```

### 修改终止条件

```python
# 使用不同的关键词
text_termination = TextMentionTermination("完成")

# 修改最大消息数
max_message_termination = MaxMessageTermination(max_messages=20)
```

---

## 🚀 性能优化

### 1. **共享模型客户端**
- 所有智能体共享同一个 `model_client`
- 减少连接开销

### 2. **流式传输**
- 支持 `run_stream` 方法
- 实时获取协作过程

### 3. **终止条件优化**
- 设置合理的最大消息数
- 避免无限循环

---

## 🐛 常见问题

### Q1: 团队运行时间过长？
**A**: 减少 `max_messages` 或优化智能体的系统消息，让评审更快通过。

### Q2: 智能体之间循环争论？
**A**: 调整系统消息，明确各智能体的职责，避免重复讨论。

### Q3: 如何查看团队协作过程？
**A**: 使用 `run_stream` 方法，实时查看每个智能体的输出。

---

## 📚 参考资料

- **原始文件**: `backend/services/team_ai_agents.py`
- **AutoGen 文档**: https://microsoft.github.io/autogen/
- **RoundRobinGroupChat**: https://microsoft.github.io/autogen/docs/reference/agentchat/teams

---

**TeamAIService 已成功实现！现在可以使用多智能体协作来处理复杂任务了！** 🎉🤝

