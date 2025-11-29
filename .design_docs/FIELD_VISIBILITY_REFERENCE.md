# 字段可见性参考指南

## 快速查询表

| 字段 | data_dev | full_stack | ai_dev | pm | designer | engineer |
|------|----------|-----------|--------|----|---------|----|
| project_name | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| company_or_context | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| timeframe | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| role_title | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| role_perspective | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| management_scope | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **decision_accountability** | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **responsibility_focus** | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| impact_metrics | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **governance_artifacts** | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ |
| project_overview | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| challenges_or_objectives | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| responsibilities | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **architecture_or_solution** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| deliverables_or_features | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| metrics_or_impact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **tech_stack** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| **tools_platforms** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| **process_or_methodology** | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| team_info | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| notes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **data_domain** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **ai_component_flag** | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |

**图例：** ✓ = 可见，✗ = 隐藏，**粗体** = 角色特定字段

## 角色字段焦点

### data_development (数据平台)
**核心字段：** governance_artifacts, decision_accountability, data_domain, tech_stack
**用途：** 强调数据可靠性、治理指标、性能优化

### full_stack (全栈工程)
**核心字段：** responsibility_focus, architecture_or_solution, tech_stack, process_or_methodology
**用途：** 强调端到端交付、前后端协同、上线速度

### ai_development (AI 工程)
**核心字段：** ai_component_flag, architecture_or_solution, tech_stack, governance_artifacts
**用途：** 强调建模、推理性能、PromptOps、成本治理

### product_manager (产品经理)
**核心字段：** decision_accountability, responsibility_focus, impact_metrics, governance_artifacts
**用途：** 强调用户洞察、商业化、干系人对齐、实验节奏

### ai_product_designer (产品设计)
**核心字段：** impact_metrics, deliverables_or_features, metrics_or_impact
**用途：** 强调用户旅程、体验策略、变现模型、设计系统

### ai_engineer (AI 工程师)
**核心字段：** ai_component_flag, architecture_or_solution, tech_stack, governance_artifacts
**用途：** 强调架构演进、模型优化、灰度与监控、可扩展性

## 添加新角色

在 `resume_docs/role_config.py` 中添加新角色时，必须包含 `field_visibility` 字典：

```python
"new_role": {
    "name": "新角色名称",
    "include_projects": [...],
    "exclude_projects": [...],
    "sort_by": "relevance_then_time",
    "persona": {...},
    "field_visibility": {
        "project_name": True,
        "company_or_context": True,
        # ... 其他字段
    },
}
```

## 隐藏字段的默认值

- **列表字段** (challenges_or_objectives, responsibilities 等) → `[]`
- **其他字段** (project_overview, role_title 等) → `None`

## 验证字段可见性

```bash
# 运行测试脚本
python test_role_filter.py

# 检查特定角色的可见性
python -c "from resume_docs.role_config import ROLE_FILTERS; print(ROLE_FILTERS['product_manager']['field_visibility'])"
```
