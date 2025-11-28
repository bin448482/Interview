# Role-Based Field Filtering Redesign

## 目标
重新设计 `resume_docs/role_filter.py`，实现基于角色的字段级过滤。不同角色将根据其视角看到 Project 对象中不同的字段子集，同时保持项目列表不变。

## 当前状态
- `role_filter.py` 目前禁用了所有过滤逻辑，所有角色返回完整的 ResumeDocument
- `role_config.py` 为每个角色定义了 `include_projects`、`exclude_projects` 和 `persona`
- Project 模型有 20+ 个字段，包括 governance_artifacts、decision_accountability、responsibility_focus 等

## 设计方案

### 1. 字段可见性映射策略
- **真实来源**：`role_config.py` 中的 include/exclude 规则决定了哪些字段与每个角色相关
- **逻辑**：如果角色的 include 规则引用了 `decision_accountability` 或 `governance_artifacts` 等字段，这些字段应该可见；其他字段隐藏
- **实现**：为每个角色配置添加 `field_visibility` 字典，将字段名称映射到可见性（True/False）

### 2. 字段可见性定义

在 `role_config.py` 中，为每个角色添加 `field_visibility` 部分，明确列出 Project 的哪些字段应该可见：

```python
"field_visibility": {
    "governance_artifacts": True,
    "decision_accountability": True,
    "responsibility_focus": True,
    "impact_metrics": True,
    "management_scope": True,
    "role_perspective": True,
    "project_overview": True,
    "challenges_or_objectives": True,
    "responsibilities": True,
    "architecture_or_solution": True,
    "deliverables_or_features": True,
    "metrics_or_impact": True,
    "tech_stack": True,
    # 其他字段设为 False
}
```

### 3. role_filter.py 实现

修改 `RoleFilter.filter_resume()` 以：
1. 验证角色存在于 ROLE_FILTERS 中
2. 获取该角色的 field_visibility 配置
3. 对于 resume.projects 中的每个项目：
   - 创建一个新的 Project 实例，仅包含可见字段
   - 将隐藏字段设置为 None 或空默认值
4. 返回修改后的 ResumeDocument，其中包含过滤后的项目

**关键方法**：
- `_get_field_visibility(role: str) -> dict`：从角色配置中提取 field_visibility
- `_filter_project_fields(project: Project, visibility: dict) -> Project`：创建仅包含可见字段的新 Project
- `_filter_projects(projects: List[Project], visibility: dict) -> List[Project]`：对所有项目应用过滤

### 4. 处理字段默认值

当字段被隐藏时：
- 字符串字段 → None
- 列表字段 → 空列表 []
- 对象字段（ManagementScope、ImpactMetrics、Timeframe）→ 空实例或 None
- 布尔字段 → None

### 5. 集成点

- **docx_renderer.py**：已经能够优雅地处理 None/空字段（跳过渲染）
- **llm_polisher.py**：只会看到可见字段，自然适应角色视角
- **CLI**：无需更改；过滤在 role_filter.py 中透明进行

## 实施步骤

### 步骤 1：更新 role_config.py
为每个现有角色添加 `field_visibility` 字典：
- data_development
- full_stack
- ai_development
- product_manager
- ai_product_designer
- ai_engineer

### 步骤 2：重构 role_filter.py
- 实现 `_get_field_visibility()` 方法
- 实现 `_filter_project_fields()` 方法以创建过滤后的 Project 实例
- 更新 `filter_resume()` 以应用字段过滤
- 移除或保留禁用的过滤方法供将来使用

### 步骤 3：验证
- 确保所有 Project 字段都在 field_visibility 配置中被考虑
- 测试过滤后的项目在 DOCX 中正确渲染
- 验证 LLM 润色适用于过滤后的字段

## 修改的文件
1. `resume_docs/role_config.py` - 为每个角色添加 field_visibility
2. `resume_docs/role_filter.py` - 实现字段级过滤逻辑
3. `resume_docs/claude.md` - 更新文档说明新的过滤行为

## 预期结果
- 每个角色只看到与其视角相关的字段
- 项目列表保持不变（无项目级过滤）
- Renderer 和 polisher 自动适应可见字段
- 每个角色的简历输出更清晰、更专注
