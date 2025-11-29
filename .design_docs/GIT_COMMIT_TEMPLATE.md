# Git 提交模板

## 提交信息

```
feat: implement role-based field-level filtering for resume generation

## 详细说明

重新设计 resume_docs/role_filter.py，实现基于角色的字段级过滤机制。

### 修改内容

- **resume_docs/role_config.py**: 为每个角色添加 field_visibility 字典，定义 22 个字段的可见性
  - data_development: 强调数据平台视角
  - full_stack: 强调全栈工程视角
  - ai_development: 强调 AI 工程视角
  - product_manager: 强调产品经理视角
  - ai_product_designer: 强调产品设计视角
  - ai_engineer: 强调 AI 工程师视角

- **resume_docs/role_filter.py**: 完全重构过滤逻辑
  - 实现 filter_resume() 主入口方法
  - 实现 _get_field_visibility() 获取可见性配置
  - 实现 _filter_projects() 批量过滤
  - 实现 _filter_project_fields() 单个项目过滤
  - 使用 dataclasses.replace() 创建过滤后的 Project 实例

- **resume_docs/claude.md**: 更新文档说明
  - 解释字段级过滤机制
  - 列出每个角色的字段焦点
  - 更新关键设计部分

### 新增文档

- .design_docs/role_filter_redesign.md - 详细设计文档
- .design_docs/IMPLEMENTATION_SUMMARY.md - 实施总结
- .design_docs/FIELD_VISIBILITY_REFERENCE.md - 字段可见性参考
- test_role_filter.py - 测试脚本

### 核心特性

- 字段级过滤：每个角色看到不同的字段子集
- 项目列表不变：所有角色看到相同的项目
- 显式配置：在 role_config.py 中明确定义可见性
- 最小化代码：简洁的过滤实现（~60 行）
- 透明集成：Renderer 和 Polisher 自动适应可见字段

### 验证

✓ 所有 6 个角色都定义了 field_visibility（22 个字段）
✓ Python 语法检查通过
✓ 字段过滤功能测试通过
✓ 错误处理测试通过
✓ CLI 集成验证通过

### 使用示例

```bash
# 生成数据平台视角的简历
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --include-contact --skip-polish

# 生成产品经理视角的简历
.venv\Scripts\python -m resume_docs.cli --role product_manager --template modern --locale zh-CN --include-contact --skip-polish

# 生成 AI 工程师视角的简历（带 LLM 润色）
.venv\Scripts\python -m resume_docs.cli --role ai_engineer --template modern --locale zh-CN --include-contact --model glm-4
```

### 相关文档

- 设计文档：.design_docs/role_filter_redesign.md
- 实施总结：.design_docs/IMPLEMENTATION_SUMMARY.md
- 字段参考：.design_docs/FIELD_VISIBILITY_REFERENCE.md

### 后续改进

- 在 ROLE_FILTERS.md 中添加详细的字段可见性文档
- 为每个角色添加单元测试
- 考虑添加字段可见性的验证脚本
- 在 CI/CD 中集成字段可见性检查
```

## 提交前检查清单

```bash
# 1. 运行测试
python test_role_filter.py

# 2. 验证语法
python -m py_compile resume_docs/role_config.py
python -m py_compile resume_docs/role_filter.py

# 3. 检查修改的文件
git status

# 4. 查看 diff
git diff resume_docs/role_config.py
git diff resume_docs/role_filter.py
git diff resume_docs/claude.md

# 5. 提交
git add resume_docs/role_config.py resume_docs/role_filter.py resume_docs/claude.md
git add .design_docs/role_filter_redesign.md
git add .design_docs/IMPLEMENTATION_SUMMARY.md
git add .design_docs/FIELD_VISIBILITY_REFERENCE.md
git add test_role_filter.py

git commit -m "feat: implement role-based field-level filtering for resume generation"
```

## 提交后验证

```bash
# 1. 查看提交日志
git log -1 --stat

# 2. 生成各角色的简历进行手动测试
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --dry-run
.venv\Scripts\python -m resume_docs.cli --role product_manager --template modern --locale zh-CN --dry-run
.venv\Scripts\python -m resume_docs.cli --role ai_engineer --template modern --locale zh-CN --dry-run

# 3. 运行完整的 CI/CD 测试（如果有）
make validate-resume-docs
```
