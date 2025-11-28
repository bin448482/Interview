# 职位过滤规则文档

本文档描述 `role_config.py` 中定义的职位过滤规则。

## 数据开发 (data_development)

**包含项目规则：**
- `data_domain` 包含 "数据" 或 "BI"
- `ai_component_flag` 为 True

**排除项目规则：**
- 项目名称为 "Move To HP Cloud"
- `data_domain` 包含 "基础设施"

**包含工作经历规则：**
- `role_title` 包含 "数据"
- 公司为 "Zoetis"

**排序方式：** 按相关度 + 时间排序（新项目优先）

---

## 全栈开发 (full_stack)

**包含项目规则：**
- `responsibility_focus` 包含 "implementation" 或 "architecture"

**排除项目规则：**
- `data_domain` 包含 "爬虫"

**排序方式：** 按相关度 + 时间排序（新项目优先）

---

## AI应用开发 (ai_development)

**包含项目规则：**
- `ai_component_flag` 为 True

**排除项目规则：** 无

**排序方式：** 按相关度 + 时间排序（新项目优先）

---

## Generative AI 产品经理 (product_manager)

**包含项目规则：**
- `responsibility_focus` 包含 "commercialization" 或 "stakeholder_management"
- 或 `decision_accountability` 包含 "commercial_strategy"/"risk_governance"
- 或 `role_title` 文本包含 “产品”/"Product"

**排除项目规则：**
- `role_title` 包含 “测试” 或 “运维”

**排序方式：** 按相关度 + 时间排序（新项目优先）

---

## 过滤规则类型

- `exact`: 精确匹配字符串
- `pattern`: 正则表达式匹配
- `contains`: 列表包含任意指定值
- `value`: 直接值匹配
