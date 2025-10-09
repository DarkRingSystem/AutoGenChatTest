# 测试脚本目录

本目录包含项目的集成测试和端到端测试脚本。

## 📁 目录结构

```
tests/
└── test_feedback_flow.sh          # 反馈流程端到端测试脚本
```

## 🧪 测试说明

### test_feedback_flow.sh
- **功能**: 测试完整的反馈流程
- **用途**: 端到端测试，验证反馈功能是否正常工作
- **运行方式**: `./tests/test_feedback_flow.sh`

## 📝 注意事项

- 运行测试前请确保后端服务已启动
- 某些测试可能需要配置环境变量
- 单元测试位于 `backend/tests/` 目录

## 🔗 相关文档

- [Backend 测试文档](../backend/tests/README.md)
- [测试指南](../docs/TROUBLESHOOTING.md)

