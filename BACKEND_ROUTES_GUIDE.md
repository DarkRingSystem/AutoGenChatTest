# 后端路由重构指南

## 📋 新路由结构

### 路由组织原则

按**一级路径**进行模块化管理，每个功能模块有独立的路由文件。

```
backend/api/
├── __init__.py                  # 主路由整合
├── routes_home.py               # 首页相关路由
├── routes_chat_normal.py        # 普通对话路由
├── routes_chat_testcase.py      # 测试用例生成路由
├── routes_image_analysis.py     # 图片分析路由
├── routes_files.py              # 文件相关路由
└── utils.py                     # 工具函数
```

---

## 🗺️ 完整路由映射

### 1. 首页相关 (`/api/home/*`)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/home/` | GET | 获取首页信息和模式列表 |
| `/api/home/stats` | GET | 获取应用统计信息 |

**文件**: `backend/api/routes_home.py`

---

### 2. 普通对话 (`/api/chat/normal/*`)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/chat/normal/stream` | POST | 流式对话 |
| `/api/chat/normal/` | POST | 非流式对话 |
| `/api/chat/normal/session/{id}` | GET | 获取会话信息 |
| `/api/chat/normal/session/{id}` | DELETE | 删除会话 |
| `/api/chat/normal/sessions` | GET | 列出所有会话 |

**文件**: `backend/api/routes_chat_normal.py`

**前端路径**: `/chat/normal`

---

### 3. 测试用例生成 (`/api/chat/testcase/*`)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/chat/testcase/stream` | POST | 流式生成测试用例 |
| `/api/chat/testcase/session/{id}` | GET | 获取会话信息 |
| `/api/chat/testcase/session/{id}` | DELETE | 删除会话 |
| `/api/chat/testcase/sessions` | GET | 列出所有会话 |
| `/api/chat/testcase/clear-all` | POST | 清除所有会话 |

**文件**: `backend/api/routes_chat_testcase.py`

**前端路径**: `/chat/testcase`

---

### 4. 图片分析 (`/api/image-analysis/*`)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/image-analysis/stream` | POST | 流式图片分析 |
| `/api/image-analysis/` | POST | 非流式图片分析 |
| `/api/image-analysis/health` | GET | 服务健康检查 |

**文件**: `backend/api/routes_image_analysis.py`

**前端路径**: `/image-analysis`

---

### 5. 文件管理 (`/api/files/*`)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/files/parse` | POST | 批量解析文件 |
| `/api/files/convert` | POST | 单文件转换 |
| `/api/files/storage/{id}` | GET | 获取文件内容 |
| `/api/files/storage/{id}` | DELETE | 删除文件 |
| `/api/files/storage` | GET | 列出所有文件 |
| `/api/files/storage` | DELETE | 清除所有文件 |

**文件**: `backend/api/routes_files.py`

---

### 6. 通用路由

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 根端点 |
| `/health` | GET | 健康检查 |

**文件**: `backend/api/__init__.py`

---

## 🔄 前后端路径对应

### 前端路由 → 后端 API

```
前端路径                    后端 API
/home                   →  /api/home/
/chat/normal            →  /api/chat/normal/*
/chat/testcase          →  /api/chat/testcase/*
/image-analysis         →  /api/image-analysis/*
```

### 示例

**前端**: 用户访问 `/chat/normal`
**后端**: 前端调用 `/api/chat/normal/stream`

---

## 📝 API 使用示例

### 1. 获取首页信息

```bash
curl http://localhost:8000/api/home/
```

**响应**:
```json
{
  "message": "AutoGen Chat Application",
  "version": "1.0.0",
  "modes": [
    {
      "id": "normal",
      "name": "普通对话",
      "description": "与 AI 进行自然对话，支持文件上传",
      "path": "/chat/normal",
      "icon": "message"
    },
    ...
  ]
}
```

---

### 2. 普通对话（流式）

```bash
curl -X POST http://localhost:8000/api/chat/normal/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "conversation_id": null
  }'
```

**响应**: SSE 流式数据

---

### 3. 测试用例生成（流式）

```bash
curl -X POST http://localhost:8000/api/chat/testcase/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "为登录接口生成测试用例",
    "conversation_id": null
  }'
```

---

### 4. 图片分析（流式）

```bash
curl -X POST http://localhost:8000/api/image-analysis/stream \
  -F "image=@screenshot.png" \
  -F "prompt=分析这张 UI 界面"
```

---

### 5. 文件解析

```bash
curl -X POST http://localhost:8000/api/files/parse \
  -F "files=@document.pdf" \
  -F "files=@code.py"
```

**响应**:
```json
{
  "results": [
    {
      "filename": "document.pdf",
      "success": true,
      "markdown": "...",
      "file_id": "uuid-xxx"
    }
  ],
  "total": 2,
  "success_count": 2,
  "failed_count": 0
}
```

---

## 🎯 路由设计优势

### 1. 清晰的模块划分

```
/api/home/*           # 首页相关
/api/chat/normal/*    # 普通对话
/api/chat/testcase/*  # 测试用例
/api/image-analysis/* # 图片分析
/api/files/*          # 文件管理
```

### 2. 易于维护

- 每个功能模块独立文件
- 修改某个功能不影响其他模块
- 代码职责清晰

### 3. 易于扩展

添加新功能只需：
1. 创建新的路由文件 `routes_xxx.py`
2. 在 `__init__.py` 中注册
3. 不影响现有代码

### 4. RESTful 风格

```
GET    /api/chat/normal/sessions      # 列出资源
GET    /api/chat/normal/session/{id}  # 获取资源
POST   /api/chat/normal/stream        # 创建资源
DELETE /api/chat/normal/session/{id}  # 删除资源
```

---

## 🔧 开发指南

### 添加新路由模块

**步骤 1**: 创建路由文件

```python
# backend/api/routes_new_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

@router.get("/")
async def get_feature():
    return {"message": "New feature"}
```

**步骤 2**: 注册到主路由

```python
# backend/api/__init__.py
from api import routes_new_feature

router.include_router(routes_new_feature.router)
```

**步骤 3**: 测试

```bash
curl http://localhost:8000/api/new-feature/
```

---

## 📊 路由统计

```
总路由数: 27

按模块分布:
- 首页: 2 个
- 普通对话: 5 个
- 测试用例: 5 个
- 图片分析: 3 个
- 文件管理: 8 个
- 通用: 2 个
- 系统: 2 个 (OpenAPI, Docs)
```

---

## 🚀 迁移说明

### 旧路由 → 新路由

| 旧路径 | 新路径 | 状态 |
|--------|--------|------|
| `/api/chat/stream` | `/api/chat/normal/stream` | ✅ 已迁移 |
| `/api/chat` | `/api/chat/normal/` | ✅ 已迁移 |
| `/api/testcases/stream` | `/api/chat/testcase/stream` | ✅ 已迁移 |
| `/api/image-analysis/stream` | `/api/image-analysis/stream` | ✅ 保持不变 |
| `/api/parse-files` | `/api/files/parse` | ✅ 已迁移 |

### 兼容性

- ✅ 所有功能保持不变
- ✅ API 响应格式不变
- ✅ 前端需要更新 API 路径

---

## 📚 相关文档

- **前端路由规划**: `FRONTEND_ROUTING_PLAN.md`
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## ✅ 验收标准

- [x] 所有路由按一级路径组织
- [x] 每个功能模块独立文件
- [x] 路由命名清晰规范
- [x] 支持 RESTful 风格
- [x] 应用正常启动（27 个路由）
- [x] 所有功能正常工作

