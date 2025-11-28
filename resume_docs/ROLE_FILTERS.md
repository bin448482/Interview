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

## 过滤规则类型

- `exact`: 精确匹配字符串
- `pattern`: 正则表达式匹配
- `contains`: 列表包含任意指定值
- `value`: 直接值匹配
