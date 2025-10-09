# 提示词管理目录

这个目录用于集中管理所有智能体的系统提示词（system messages）。

## 📁 目录结构

```
prompts/
├── README.md                      # 本文件
├── prompt_loader.py               # 提示词加载器
├── assistant.txt                  # 通用助手提示词
├── test_case_generator.txt        # 测试用例生成专家提示词
├── test_case_reviewer.txt         # 测试用例评审专家提示词
└── test_case_optimizer.txt        # 测试用例优化专家提示词
```

## 🎯 设计目的

### 1. **集中管理**
- 所有提示词集中在一个目录中
- 便于查找和修改
- 避免提示词散落在代码各处

### 2. **易于维护**
- 修改提示词不需要改动代码
- 支持版本控制
- 可以快速迭代优化

### 3. **可读性强**
- 使用纯文本文件，易于阅读
- 支持多行格式，便于组织复杂提示词
- 可以添加注释和说明

### 4. **灵活性高**
- 支持热重载（开发模式）
- 支持缓存（生产模式）
- 可以动态切换不同的提示词

## 📝 提示词文件格式

每个提示词文件都是一个纯文本文件（`.txt`），内容为智能体的系统提示词。

### 示例：`test_case_generator.txt`

```
你是一个测试用例生成专家，负责根据需求生成全面、详细的测试用例。

## 职责
- 分析功能需求，识别测试场景
- 生成覆盖全面的测试用例
- 确保测试用例包含正常场景、边界条件和异常情况

## 测试用例格式
每个测试用例应包含：
- 用例编号
- 测试场景描述
- 前提条件
- 输入数据
- 操作步骤
- 预期结果
```

## 🔧 使用方法

### 1. 在代码中加载提示词

```python
from prompts.prompt_loader import load_prompt, PromptNames

# 方式 1: 使用便捷函数
system_message = load_prompt("test_case_generator")

# 方式 2: 使用常量
system_message = load_prompt(PromptNames.TEST_CASE_GENERATOR)

# 方式 3: 使用加载器实例
from prompts.prompt_loader import get_prompt_loader

loader = get_prompt_loader()
system_message = loader.load("test_case_generator")
```

### 2. 在智能体中使用

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from prompts.prompt_loader import load_prompt, PromptNames

# 创建智能体
agent = AssistantAgent(
    name="TestCase_Generator",
    model_client=model_client,
    system_message=load_prompt(PromptNames.TEST_CASE_GENERATOR),
    model_client_stream=True,
)
```

### 3. 重新加载提示词（开发模式）

```python
from prompts.prompt_loader import get_prompt_loader

loader = get_prompt_loader()

# 重新加载单个提示词
system_message = loader.reload("test_case_generator")

# 清除所有缓存
loader.clear_cache()
```

### 4. 列出所有可用提示词

```python
from prompts.prompt_loader import get_prompt_loader

loader = get_prompt_loader()
prompts = loader.list_prompts()
print(f"可用提示词: {prompts}")
# 输出: ['assistant', 'test_case_generator', 'test_case_optimizer', 'test_case_reviewer']
```

## 📋 提示词列表

| 文件名 | 智能体名称 | 用途 |
|--------|-----------|------|
| `assistant.txt` | Assistant | 通用 AI 助手 |
| `test_case_generator.txt` | TestCase_Generator | 生成测试用例 |
| `test_case_reviewer.txt` | TestCase_Reviewer | 评审测试用例 |
| `test_case_optimizer.txt` | TestCase_Optimizer | 优化测试用例 |

## ✏️ 编写提示词的最佳实践

### 1. **清晰的角色定义**
```
你是一个[角色名称]，负责[主要职责]。
```

### 2. **明确的职责说明**
```
## 职责
- 职责 1
- 职责 2
- 职责 3
```

### 3. **具体的输出要求**
```
## 输出格式
- 使用 Markdown 格式
- 包含标题和列表
- 提供具体示例
```

### 4. **必要的约束条件**
```
## 注意事项
- 不要做什么
- 必须做什么
- 特殊情况如何处理
```

### 5. **使用 Markdown 格式**
- 使用标题组织内容（`##`、`###`）
- 使用列表展示要点（`-`、`1.`）
- 使用代码块展示示例（` ``` `）
- 使用加粗强调重点（`**重点**`）

## 🔄 修改提示词的流程

### 1. **编辑提示词文件**
```bash
# 使用任何文本编辑器编辑
vim backend/prompts/test_case_generator.txt
```

### 2. **测试修改效果**
```python
# 在开发环境中重新加载
from prompts.prompt_loader import get_prompt_loader

loader = get_prompt_loader()
new_prompt = loader.reload("test_case_generator")
```

### 3. **提交版本控制**
```bash
git add backend/prompts/test_case_generator.txt
git commit -m "优化测试用例生成器提示词"
```

## 🚀 高级功能

### 1. **自定义提示词目录**
```python
from prompts.prompt_loader import PromptLoader

# 使用自定义目录
loader = PromptLoader("/path/to/custom/prompts")
system_message = loader.load("custom_prompt")
```

### 2. **禁用缓存（开发模式）**
```python
# 每次都从文件读取
system_message = loader.load("test_case_generator", use_cache=False)
```

### 3. **获取提示词文件路径**
```python
from prompts.prompt_loader import get_prompt_loader

loader = get_prompt_loader()
path = loader.get_prompt_path("test_case_generator")
print(f"提示词文件路径: {path}")
```

## 📊 提示词版本管理

建议使用 Git 管理提示词的版本：

```bash
# 查看提示词修改历史
git log backend/prompts/test_case_generator.txt

# 比较不同版本
git diff HEAD~1 backend/prompts/test_case_generator.txt

# 回退到之前的版本
git checkout HEAD~1 backend/prompts/test_case_generator.txt
```

## 🎨 提示词优化建议

### 1. **迭代优化**
- 从简单的提示词开始
- 根据实际效果逐步优化
- 记录每次修改的原因和效果

### 2. **A/B 测试**
- 创建不同版本的提示词
- 对比测试效果
- 选择最佳版本

### 3. **收集反馈**
- 观察智能体的输出质量
- 收集用户反馈
- 针对性地改进提示词

### 4. **保持简洁**
- 避免过长的提示词
- 突出重点信息
- 删除冗余内容

## 🔍 故障排查

### 问题 1: 提示词文件不存在
```
FileNotFoundError: 提示词文件不存在: /path/to/prompts/xxx.txt
```

**解决方案**：
- 检查文件名是否正确
- 确认文件是否存在于 `backend/prompts/` 目录
- 检查文件扩展名是否为 `.txt`

### 问题 2: 提示词内容为空
```
RuntimeError: 提示词内容为空
```

**解决方案**：
- 检查文件是否有内容
- 确认文件编码为 UTF-8
- 检查文件是否被正确保存

### 问题 3: 缓存未更新
**解决方案**：
```python
# 清除缓存并重新加载
loader.clear_cache()
system_message = loader.load("test_case_generator")
```

## 📚 相关文档

- [AutoGen 文档](https://microsoft.github.io/autogen/)
- [提示工程指南](https://www.promptingguide.ai/)
- [OpenAI 最佳实践](https://platform.openai.com/docs/guides/prompt-engineering)

---

**维护者**: AI Team  
**最后更新**: 2025-10-04

