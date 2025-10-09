# Git 使用指南

## ✅ Git 仓库已配置完成

### 当前配置

- **用户名**：DarkRingSystem
- **邮箱**：493557094@qq.com
- **主分支**：main
- **首次提交**：d710c5a - Initial commit - AutoGen Chat Application

### 提交统计

- **文件数量**：160 个文件
- **代码行数**：51,532 行
- **提交状态**：✅ 工作区干净

---

## 📚 常用 Git 命令

### 1. 查看状态

```bash
# 查看当前状态
git status

# 查看提交历史
git log

# 查看简洁的提交历史
git log --oneline

# 查看图形化提交历史
git log --graph --oneline --all
```

### 2. 添加和提交

```bash
# 添加所有修改的文件
git add .

# 添加特定文件
git add backend/api/routes.py

# 提交更改
git commit -m "描述你的更改"

# 添加并提交（快捷方式）
git commit -am "描述你的更改"
```

### 3. 分支管理

```bash
# 查看所有分支
git branch

# 创建新分支
git branch feature/new-feature

# 切换分支
git checkout feature/new-feature

# 创建并切换到新分支（快捷方式）
git checkout -b feature/new-feature

# 合并分支
git checkout main
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

### 4. 远程仓库

```bash
# 添加远程仓库
git remote add origin https://github.com/DarkRingSystem/autogenTest.git

# 查看远程仓库
git remote -v

# 推送到远程仓库
git push -u origin main

# 拉取远程更新
git pull origin main

# 克隆远程仓库
git clone https://github.com/DarkRingSystem/autogenTest.git
```

### 5. 撤销操作

```bash
# 撤销工作区的修改
git checkout -- filename

# 撤销暂存区的文件
git reset HEAD filename

# 撤销最后一次提交（保留更改）
git reset --soft HEAD^

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD^

# 查看某个文件的历史版本
git log -- filename
```

### 6. 查看差异

```bash
# 查看工作区和暂存区的差异
git diff

# 查看暂存区和最后一次提交的差异
git diff --staged

# 查看两次提交之间的差异
git diff commit1 commit2
```

---

## 🔄 推荐的工作流程

### 日常开发流程

```bash
# 1. 开始新功能前，确保在最新的 main 分支
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 进行开发，定期提交
git add .
git commit -m "feat: 添加新功能描述"

# 4. 功能完成后，合并到 main
git checkout main
git merge feature/your-feature-name

# 5. 推送到远程仓库
git push origin main

# 6. 删除功能分支
git branch -d feature/your-feature-name
```

### 提交信息规范

使用语义化的提交信息：

```bash
# 新功能
git commit -m "feat: 添加图片分析功能"

# 修复 bug
git commit -m "fix: 修复会话管理的内存泄漏问题"

# 文档更新
git commit -m "docs: 更新 API 使用文档"

# 代码重构
git commit -m "refactor: 重构路由模块结构"

# 性能优化
git commit -m "perf: 优化流式传输性能"

# 测试
git commit -m "test: 添加图片分析单元测试"

# 构建/依赖
git commit -m "build: 更新 AutoGen 到 0.7.5"

# 样式调整
git commit -m "style: 统一代码格式"
```

---

## 🌐 关联 GitHub 远程仓库

### 步骤 1：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`autogenTest`（或其他名称）
3. 选择 Public 或 Private
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 步骤 2：关联本地仓库

```bash
# 添加远程仓库
git remote add origin https://github.com/DarkRingSystem/autogenTest.git

# 推送到远程仓库
git push -u origin main
```

### 步骤 3：后续推送

```bash
# 之后只需要
git push
```

---

## 🔧 .gitignore 说明

当前 `.gitignore` 已配置，会自动忽略：

- ✅ Python 缓存文件（`__pycache__/`, `*.pyc`）
- ✅ 虚拟环境（`venv/`, `env/`）
- ✅ 环境变量文件（`.env`）
- ✅ IDE 配置（`.vscode/`, `.idea/`）
- ✅ Node.js 依赖（`node_modules/`）
- ✅ 前端构建产物（`frontend/dist/`）
- ✅ 日志文件（`*.log`）
- ✅ 临时文件

---

## 📊 查看项目统计

```bash
# 查看代码统计
git log --stat

# 查看贡献者统计
git shortlog -sn

# 查看文件修改次数
git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -10
```

---

## 🆘 常见问题

### 1. 如何撤销刚才的提交？

```bash
# 撤销提交但保留更改
git reset --soft HEAD^

# 撤销提交并丢弃更改
git reset --hard HEAD^
```

### 2. 如何修改最后一次提交信息？

```bash
git commit --amend -m "新的提交信息"
```

### 3. 如何暂存当前工作？

```bash
# 暂存当前更改
git stash

# 查看暂存列表
git stash list

# 恢复暂存的更改
git stash pop
```

### 4. 如何查看某个文件的修改历史？

```bash
git log -p filename
```

### 5. 如何忽略已经提交的文件？

```bash
# 1. 添加到 .gitignore
echo "filename" >> .gitignore

# 2. 从 Git 中移除（但保留本地文件）
git rm --cached filename

# 3. 提交更改
git commit -m "chore: 忽略 filename"
```

---

## 🎯 下一步

1. **创建 GitHub 仓库**（可选）
   - 访问 https://github.com/new
   - 创建新仓库并关联

2. **设置分支保护**（推荐）
   - 在 GitHub 仓库设置中启用分支保护
   - 要求 Pull Request 审查

3. **配置 CI/CD**（可选）
   - 使用 GitHub Actions 自动化测试和部署

4. **编写 CONTRIBUTING.md**
   - 为其他贡献者提供指南

---

## 📖 学习资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 指南](https://guides.github.com/)
- [Git 可视化学习](https://learngitbranching.js.org/)
- [Pro Git 中文版](https://git-scm.com/book/zh/v2)

---

## ✅ 总结

你的项目现在已经完全纳入 Git 版本控制！

- ✅ Git 仓库已初始化
- ✅ 用户信息已配置
- ✅ 首次提交已完成
- ✅ .gitignore 已配置
- ✅ 160 个文件已纳入版本控制

现在你可以：
- 📝 定期提交代码更改
- 🌿 创建分支进行功能开发
- 🔄 与团队协作
- 🌐 推送到远程仓库（GitHub/GitLab/Gitee）

祝你开发愉快！🚀

