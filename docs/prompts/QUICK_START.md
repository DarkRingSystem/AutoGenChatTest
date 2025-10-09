# 提示词管理快速开始

## 🚀 5 分钟快速上手

### 1. 查看可用提示词

```bash
ls backend/prompts/*.txt
```

输出：
```
assistant.txt
test_case_generator.txt
test_case_optimizer.txt
test_case_reviewer.txt
```

### 2. 在代码中使用

```python
from prompts.prompt_loader import load_prompt, PromptNames

# 加载提示词
system_message = load_prompt(PromptNames.TEST_CASE_GENERATOR)

# 创建智能体
agent = AssistantAgent(
    name="TestCase_Generator",
    model_client=model_client,
    system_message=system_message,
)
```

### 3. 修改提示词

```bash
# 编辑文件
vim backend/prompts/test_case_generator.txt

# 保存后重启服务
# 服务器会自动重新加载
```

## 📝 提示词文件位置

| 智能体 | 文件路径 |
|--------|---------|
| 通用助手 | `backend/prompts/assistant.txt` |
| 测试用例生成 | `backend/prompts/test_case_generator.txt` |
| 测试用例评审 | `backend/prompts/test_case_reviewer.txt` |
| 测试用例优化 | `backend/prompts/test_case_optimizer.txt` |

## 🔧 常用操作

### 查看提示词内容

```bash
cat backend/prompts/test_case_generator.txt
```

### 编辑提示词

```bash
# 使用你喜欢的编辑器
vim backend/prompts/test_case_generator.txt
# 或
code backend/prompts/test_case_generator.txt
# 或
nano backend/prompts/test_case_generator.txt
```

### 测试提示词

```python
# 在 Python 中测试
from prompts.prompt_loader import load_prompt

prompt = load_prompt("test_case_generator")
print(prompt)
```

## 💡 提示词编写技巧

### 1. 使用 Markdown 格式

```markdown
你是一个[角色]，负责[职责]。

## 职责
- 职责 1
- 职责 2

## 输出格式
- 格式要求

## 注意事项
- 注意事项
```

### 2. 清晰的结构

- ✅ 使用标题分组
- ✅ 使用列表展示要点
- ✅ 使用加粗强调重点
- ✅ 提供具体示例

### 3. 避免的问题

- ❌ 提示词过长
- ❌ 描述模糊
- ❌ 缺少具体要求
- ❌ 格式混乱

## 🎯 最佳实践

1. **从简单开始**：先写一个简单的提示词，然后逐步优化
2. **测试效果**：修改后立即测试，观察智能体的输出
3. **版本控制**：使用 Git 管理提示词的版本
4. **记录原因**：在 commit 消息中说明为什么修改

## 📚 更多信息

- 详细文档：`backend/prompts/README.md`
- 实现总结：`提示词管理系统实现完成.md`
- 代码示例：`backend/services/ai_service.py`

---

**快速开始完成！现在可以轻松管理提示词了！** 🎉

