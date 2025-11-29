# 角色视角字段填写指南

## role_perspective 判定
- `developer`：描述聚焦编码实现、模块交付、性能/技术难题，团队规模<=5 且无明显管理权。
- `architect`：强调架构设计、技术决策、跨系统方案、技术治理但未直接管理大团队。
- `project_manager`：负责项目计划、预算、干系人/风险管理，强调交付/沟通指标。
- `product_owner`：描述需求定义、价值验证、路线图或商业策略的优先级。
- `hybrid`：同一项目中既有深入编码又承担管理/架构职责且无法拆分时使用，并在 `notes` 说明。

## management_scope 填写
- `team_size`：核心交付团队上限（未知时填 null）。
- `budget_level`：
  - `<100k`：个人或小型内训项目。
  - `100k-1m`：典型企业项目、部门级预算。
  - `>1m`：跨区域或多年度计划。
- `stakeholder_tiers`：根据描述列举接触层级，如 `exec`(CxO/VP)、`director`, `ops`, `vendor`, `regulator`。

## decision_accountability 选项释义
- `delivery_owner`：对整体交付/进度负责。
- `technical_strategy`：主导架构蓝图、技术路线或选型。
- `people_management`：直线管理或重组团队。
- `hands_on_build`：主要贡献在编码/系统实现。
- `commercial_strategy`：负责商业模式、成本控制或ROI。
- `risk_governance`：负责风险登记、合规/安全汇报。

## responsibility_focus 标签
为项目的重点职责选 2-3 个：`planning`, `architecture`, `implementation`, `operations`, `commercialization`, `stakeholder_management`, `compliance`。

## impact_metrics 分类
- `business_metrics`：收入、成本、转化率、预算、ROI。
- `technical_metrics`：性能、吞吐、延迟、可用性、AI准确率。
- `operational_metrics`：交付周期、部署效率、自动化覆盖率、团队效率。

## governance_artifacts 示例
`exec_dashboard`, `roadmap`, `risk_register`, `RACI`, `jira_board`, `runbook`, `playbook`, `SOP`, `training_plan`。仅列出确实交付或维护的治理产出。

> 建议在填充 `projects_summary.yaml` 时先确定 `role_perspective`，然后根据上表逐项补足字段，确保后续 LLM 提取时可以按角色过滤。

## 项目级 LLM 角色字段

为支持“项目级角色视角”的 LLM 改写，每个项目可以选择性配置：

- `llm_primary_role`：项目最推荐的 LLM 改写视角。
  - 取值必须是 `ROLE_FILTERS` 的 key 之一（如 `data_development`, `ai_development`, `full_stack`, `product_manager`, `ai_product_designer`, `ai_engineer`）。
  - Tarot / AI 应用类项目通常使用 `ai_development` 或 `full_stack`。
  - 数据平台 / 湖仓类项目（如 NGSE、Remedium）通常使用 `data_development`。
- `llm_secondary_roles`：可接受的备选视角列表。
  - 同样必须来自 `ROLE_FILTERS` 的 key 集；
  - 当 CLI 的整体 `--role` 落在该列表内时，会优先采用整体视角进行改写。

语义说明：

- 这两个字段只影响 LLM 改写时选用的角色 prompt；
- 不影响 `RoleFilter` 的项目过滤/排序规则；
- 不影响字段可见性（仍由 `ROLE_FILTERS[role]['field_visibility']` 控制）。

迁移建议：

- 旧项目可以暂不填写 `llm_primary_role` / `llm_secondary_roles`，系统会自动退回整体角色或基础 polish prompt；
- 为关键项目补齐这两个字段，可以显著减少“强行带错角色视角”导致的技术栈幻觉。
