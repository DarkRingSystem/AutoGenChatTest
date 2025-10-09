# AutoGen Chat Application - 架构设计文档

## 📋 文档信息

- **项目名称**: AutoGen Chat Application
- **版本**: v0.2
- **最后更新**: 2025-10-09
- **架构类型**: 分层智能体工厂架构

---

## 🎯 架构目标

1. **高可维护性**: 清晰的分层结构，低耦合高内聚
2. **高可扩展性**: 方便添加新的智能体和业务功能
3. **高可测试性**: 工厂模式支持依赖注入和单元测试
4. **统一管理**: 集中管理智能体的创建、注册和生命周期
5. **性能优化**: 智能体缓存机制，减少重复创建

---

## 🏗️ 整体架构

### 四层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                       │
│                    React + Ant Design                       │
│              用户界面、交互、状态管理                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
┌────────────────────────▼────────────────────────────────────┐
│                    1️⃣ API 接口层 (API Layer)                 │
│                   FastAPI Routes                            │
│          接收前端请求，参数验证，启动业务流程                   │
│                                                             │
│  • /api/chat - 普通对话                                      │
│  • /api/testcases/team - 测试用例生成                        │
│  • /api/webui/analyze - 图片分析                            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    2️⃣ 服务层 (Service Layer)                │
│          AIService, TestCasesTeamAIService                  │
│          业务流程编排，调用智能体工厂                          │
│                                                             │
│  • 初始化智能体                                              │
│  • 管理会话状态                                              │
│  • 处理流式响应                                              │
│  • 资源清理                                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 3️⃣ 智能体工厂层 (Factory Layer)              │
│              AgentFactory, AgentRegistry                    │
│      创建、注册、管理智能体，提供智能体缓存                     │
│                                                             │
│  • 智能体类型注册                                            │
│  • 智能体实例创建                                            │
│  • 智能体缓存管理                                            │
│  • 生命周期管理                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  4️⃣ 智能体层 (Agent Layer)                   │
│    ChatAgent, TestCaseTeamAgent, ImageAnalyzerTeam          │
│          具体智能体实现，完成各自的业务逻辑                     │
│                                                             │
│  • 单智能体 (BaseAgent)                                      │
│  • 团队智能体 (BaseTeamAgent)                                │
│  • 工作流编排 (RoundRobin, GraphFlow)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 核心模块详解

### 1. API 接口层 (`backend/api/`)

**职责**: 接收前端请求，参数验证，启动业务流程

**主要文件**:
- `routes.py`: 所有 API 路由定义

**主要端点**:

| 端点 | 方法 | 功能 | 响应类型 |
|------|------|------|----------|
| `/api/chat` | POST | 普通对话 | JSON |
| `/api/chat/stream` | POST | 流式对话 | SSE |
| `/api/testcases/team` | POST | 测试用例生成 | JSON |
| `/api/testcases/team/stream` | POST | 流式测试用例生成 | SSE |
| `/api/webui/analyze` | POST | 图片分析 | JSON |
| `/api/webui/analyze/stream` | POST | 流式图片分析 | SSE |

**设计原则**:
- 薄接口层，只负责参数验证和响应格式化
- 业务逻辑委托给服务层
- 统一的错误处理
- 支持 CORS 跨域

---

### 2. 服务层 (`backend/services/`)

**职责**: 业务流程编排，调用智能体工厂

**主要文件**:
- `ai_service.py`: AI 服务类
  - `AIService`: 普通对话服务
  - `TestCasesTeamAIService`: 测试用例团队服务

**核心方法**:

```python
class AIService:
    async def initialize() -> None
        """初始化服务，创建智能体"""
    
    async def run(message: str)
        """运行对话（非流式）"""
    
    async def run_stream(message: str)
        """运行对话（流式）"""
    
    async def cleanup() -> None
        """清理资源"""
```

**设计原则**:
- 使用工厂创建智能体
- 管理智能体生命周期
- 提供统一的运行接口
- 支持流式和非流式

---

### 3. 智能体工厂层 (`backend/agents/factory.py`)

**职责**: 创建、注册、管理智能体

**核心类**:

#### AgentType (枚举)
```python
class AgentType(str, Enum):
    CHAT = "chat"
    TESTCASE_TEAM = "testcase_team"
    IMAGE_ANALYSIS_TEAM = "image_analysis_team"
```

#### AgentRegistry (注册表)
```python
class AgentRegistry:
    def register(agent_type: str, agent_class: Type)
        """注册智能体类型"""
    
    def get(agent_type: str) -> Type
        """获取智能体类"""
```

#### AgentFactory (工厂)
```python
class AgentFactory:
    async def create_agent(
        agent_type: AgentType,
        name: str,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> BaseAgent
        """创建智能体实例"""
    
    def get_cached_agent(cache_key: str) -> Optional[BaseAgent]
        """获取缓存的智能体"""
    
    async def cleanup_agent(cache_key: str) -> None
        """清理智能体"""
    
    async def cleanup_all() -> None
        """清理所有缓存的智能体"""
```

**设计原则**:
- 单例模式：全局唯一工厂实例
- 注册机制：支持动态注册新智能体类型
- 缓存机制：复用智能体实例
- 生命周期管理：统一的资源清理

---

### 4. 智能体层 (`backend/agents/`)

**职责**: 具体智能体实现

#### 基类设计

**BaseAgent** (单智能体基类):
```python
class BaseAgent(ABC):
    @abstractmethod
    async def initialize() -> None
        """初始化智能体"""
    
    @abstractmethod
    def get_agent_type() -> str
        """获取智能体类型"""
    
    def get_agent() -> Optional[AssistantAgent]
        """获取智能体实例"""
    
    async def cleanup() -> None
        """清理资源"""
```

**BaseTeamAgent** (团队智能体基类):
```python
class BaseTeamAgent(BaseAgent):
    @abstractmethod
    def create_team_members() -> List[AssistantAgent]
        """创建团队成员"""
    
    @abstractmethod
    def create_team_workflow() -> Union[RoundRobinGroupChat, GraphFlow]
        """创建团队工作流"""
    
    def get_team() -> Optional[Union[RoundRobinGroupChat, GraphFlow]]
        """获取团队实例"""
    
    def get_team_members() -> List[AssistantAgent]
        """获取团队成员列表"""
```

#### 具体智能体

**1. ChatAgent** (普通对话智能体)
- 继承自 `BaseAgent`
- 使用 DeepSeek 模型
- 支持流式和非流式对话

**2. TestCaseTeamAgent** (测试用例团队)
- 继承自 `BaseTeamAgent`
- 三个智能体：Generator、Reviewer、Optimizer
- 使用 `RoundRobinGroupChat` 工作流
- 支持三种模式：
  - 默认模式：Generator + Reviewer
  - 单智能体模式：只运行指定智能体
  - 优化模式：Generator + Reviewer + Optimizer

**3. ImageAnalyzerTeam** (图片分析团队)
- 继承自 `BaseTeamAgent`
- 三个智能体：UI_Expert、Interaction_Analyst、Test_Scenario_Expert
- 使用 `GraphFlow` 工作流（并行执行）
- 支持多模态输入（图片 + 文本）

---

## 🔄 工作流程

### 普通对话流程

```
用户输入
   │
   ▼
API 接口层 (/api/chat)
   │
   ▼
AIService.initialize()
   │
   ▼
AgentFactory.create_agent(CHAT)
   │
   ▼
ChatAgent.initialize()
   │
   ▼
AIService.run(message)
   │
   ▼
ChatAgent.run(message)
   │
   ▼
返回响应
```

### 测试用例生成流程

```
用户输入
   │
   ▼
API 接口层 (/api/testcases/team)
   │
   ▼
TestCasesTeamAIService.initialize()
   │
   ▼
AgentFactory.create_agent(TESTCASE_TEAM)
   │
   ▼
TestCaseTeamAgent.initialize()
   ├─ create_team_members()
   │  ├─ TestCase_Generator
   │  ├─ TestCase_Reviewer
   │  └─ TestCase_Optimizer (可选)
   └─ create_team_workflow()
      └─ RoundRobinGroupChat
   │
   ▼
TestCasesTeamAIService.run(message)
   │
   ▼
TestCaseTeamAgent.run(message)
   │
   ▼
RoundRobinGroupChat 执行
   ├─ Generator 生成测试用例
   ├─ Reviewer 评审
   └─ Optimizer 优化 (可选)
   │
   ▼
返回响应
```

### 图片分析流程

```
用户上传图片
   │
   ▼
API 接口层 (/api/webui/analyze)
   │
   ▼
AgentFactory.create_agent(IMAGE_ANALYSIS_TEAM)
   │
   ▼
ImageAnalyzerTeam.initialize()
   ├─ create_team_members()
   │  ├─ UI_Expert (UI-TARS)
   │  ├─ Interaction_Analyst (UI-TARS)
   │  └─ Test_Scenario_Expert (DeepSeek)
   └─ create_team_workflow()
      └─ GraphFlow (并行执行)
   │
   ▼
ImageAnalyzerTeam.analyze_image()
   │
   ▼
GraphFlow 执行
   ├─ UI_Expert 分析 ────┐
   │                    │
   ├─ Interaction_Analyst 分析 ─┤
   │                    │
   └─────────────────────▼
              Test_Scenario_Expert
                  综合分析
   │
   ▼
返回分析结果
```

---

## 🔧 技术栈

### 后端
- **框架**: FastAPI 0.115.6
- **AI 框架**: AutoGen 0.7.5
- **LLM**: 
  - DeepSeek Chat (对话、测试用例)
  - UI-TARS (图片分析)
- **Python**: 3.13+

### 前端
- **框架**: React 18
- **UI 库**: Ant Design
- **状态管理**: React Hooks
- **HTTP 客户端**: Axios
- **SSE**: EventSource

---

## 📊 数据流

### 请求流
```
Frontend → API Layer → Service Layer → Factory Layer → Agent Layer
```

### 响应流
```
Agent Layer → Service Layer → API Layer → Frontend
```

### 流式响应流
```
Agent Layer (stream) → Service Layer (SSE) → API Layer (SSE) → Frontend (EventSource)
```

---

## 🔐 安全设计

1. **API 密钥管理**: 使用环境变量存储敏感信息
2. **CORS 配置**: 限制允许的来源
3. **输入验证**: Pydantic 模型验证所有输入
4. **错误处理**: 统一的异常处理，不暴露内部信息
5. **资源清理**: 确保所有资源正确释放

---

## 🚀 性能优化

1. **智能体缓存**: 复用智能体实例，减少创建开销
2. **流式响应**: SSE 实时传输，提升用户体验
3. **异步处理**: 全异步架构，提高并发能力
4. **连接池**: 复用 HTTP 连接
5. **GraphFlow 并行**: 图片分析智能体并行执行

---

## 📈 可扩展性

### 添加新智能体

1. 创建智能体类（继承 BaseAgent 或 BaseTeamAgent）
2. 在 AgentType 中添加类型
3. 注册到工厂
4. 在服务层调用

### 添加新 API 端点

1. 在 routes.py 中添加路由
2. 创建对应的服务类（可选）
3. 调用工厂创建智能体
4. 返回响应

---

## 🧪 测试策略

1. **单元测试**: 测试每个智能体的功能
2. **集成测试**: 测试完整的业务流程
3. **工厂测试**: 测试智能体创建和缓存
4. **API 测试**: 测试所有 API 端点

---

## 📝 最佳实践

1. **使用工厂模式**: 集中管理对象创建
2. **基类继承**: 定义通用接口，减少重复代码
3. **延迟导入**: 避免循环依赖
4. **资源清理**: 实现 cleanup 方法
5. **异步优先**: 使用 async/await
6. **类型提示**: 使用 Type Hints 提高代码可读性

---

## 🔮 未来规划

1. **UserProxy 支持**: 添加用户交互智能体
2. **更多工作流**: 支持 DAG、条件分支
3. **智能体监控**: 添加运行状态监控
4. **配置化**: 支持从配置文件加载智能体
5. **插件系统**: 支持第三方智能体插件

---

**文档版本**: v1.0  
**最后更新**: 2025-10-09  
**维护者**: DarkRingSystem

