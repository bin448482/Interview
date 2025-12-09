# 简历项目图数据库与 RAG 结构设计

本文档基于 `latest_resumes/projects_summary.yaml` 等配置文件，总结“图数据库 + RAG”在本仓库中的最小可用建模方案，并给出字段到图结构的映射规则，方便实现导入脚本和后续扩展。

## 1. 设计目标

- 把“结构化事实”（时间线、角色、公司、技能、治理产出）与“叙述性文本”（项目概述、难点、方案等）拆开建模；
- 图层负责精确筛选和多条件组合（who/what/when/where/relationship）；
- 向量检索层负责在候选项目集合中做语义相似度排序；
- 保持与 `role_perspective`、`management_scope`、`decision_accountability` 等既有字段契约对齐，不破坏现有 YAML schema。

简化心智模型：

- **节点**：稳定、可复用、会被多项目引用的“名词”（人、项目、公司、技能、领域、治理产出类型）；
- **边**：查询时会出现“同时满足 X 且与 Y 有关系”的那些关系；
- **文本属性**：不适合拆结构的长描述，放在节点属性中做向量/全文检索。

## 2. 图模型概览

### 2.1 节点类型

- `Person`
  - 描述候选人本人（通常就 1 个节点），从 `personal_info_summary*.yaml` 衍生。
- `Project`
  - 对应 `latest_resumes/projects_summary.yaml` 中的每个项目条目。
- `Company`
  - 公司或组织实体，用于跨项目聚合和过滤。
- `Domain`
  - 数据/业务域，例如“全球销售引擎 / 数据平台”“制药行业 BI”等。
- `Skill`
  - 技术能力或工具平台，统一承载 `tech_stack` 与 `tools_platforms` 中的条目。
- `GovernanceArtifact`
  - 治理类交付物，如 `runbook`、`exec_dashboard`、`risk_register` 等。

### 2.2 关系类型

- `(:Person)-[:WORKED_ON {…}]->(:Project)`
  - 代表“某人在某项目中以什么角色参与、管理多大盘、承担哪些责任”。
- `(:Project)-[:AT_COMPANY]->(:Company)`
  - 代表项目归属公司或业务上下文。
- `(:Project)-[:IN_DOMAIN]->(:Domain)`
  - 代表项目所属的数据/业务域。
- `(:Project)-[:USES_SKILL {source}]->(:Skill)`
  - 代表项目在技术栈或工具层面使用了某种能力。
- `(:Project)-[:HAS_ARTIFACT]->(:GovernanceArtifact)`
  - 代表项目交付或维护了特定治理产出。

长文本说明性内容一律挂在 `Project` 节点上，用于向量化和 RAG 上下文构造；图查询主要围绕上述节点和关系做结构过滤和多条件拼接。

## 3. YAML 字段到图结构映射

本节以 `latest_resumes/projects_summary.yaml` 为基准，说明每个项目下主要字段应如何映射到图节点/关系及其属性。

### 3.1 Project 节点主干

YAML 路径（单个项目内部） → 图结构：

- `project_name` → `Project.name`
- `company_or_context`
  - 简单版：原样保存为 `Project.company_or_context_raw`；
  - 进阶：解析出主要公司名，用于创建/关联 `Company` 节点（见 3.3）。
- `timeframe.start` / `timeframe.end` / `timeframe.label`
  - → `Project.start` / `Project.end` / `Project.time_label`
- `role_title` → `Project.role_title`
- `data_domain` → `Project.data_domain`（同时用于创建/关联 `Domain` 节点）
- `ai_component_flag` → `Project.ai_component_flag`（布尔）
- `project_overview` → `Project.overview`
- `notes` → `Project.notes`

文本列表类叙述字段全部保留在 `Project` 上，用于语义检索：

- `challenges_or_objectives` → `Project.challenges`（list\<string>）
- `responsibilities` → `Project.responsibilities`
- `architecture_or_solution` → `Project.architecture`
- `process_or_methodology` → `Project.process`
- `deliverables_or_features` → `Project.deliverables`
- `metrics_or_impact` → `Project.metrics_narrative`

指标字段保持三类拆分，方便后续做结构或文本检索：

- `impact_metrics.business_metrics` → `Project.business_metrics`（list\<string>）
- `impact_metrics.technical_metrics` → `Project.technical_metrics`
- `impact_metrics.operational_metrics` → `Project.operational_metrics`

项目级 LLM 视角字段直接挂在 `Project`：

- `llm_primary_role` → `Project.llm_primary_role`
- `llm_secondary_roles` → `Project.llm_secondary_roles`（list\<string>）

为了方便向量化，可以在导入时在 `Project` 上增加一个聚合字段：

- `Project.search_text`：
  - = `overview + challenges + responsibilities + architecture + process + deliverables + metrics_narrative` 拼接后的大文本；
  - 仅用于构建语义向量，不参与图查询。

### 3.2 Person–Project 关系：WORKED_ON

角色视角、管理范围和决策责任本质上是“我在该项目中的姿态”，适合作为人–项目关系的属性：

- `role_perspective` → `WORKED_ON.role_perspective`
- `management_scope.team_size` → `WORKED_ON.team_size_scope`
- `management_scope.budget_level` → `WORKED_ON.budget_level`
- `management_scope.stakeholder_tiers` → `WORKED_ON.stakeholder_tiers`（list\<string>）
- `decision_accountability` → `WORKED_ON.decision_accountability`（list\<string>）
- `responsibility_focus` → `WORKED_ON.responsibility_focus`（list\<string>）
- `team_info.team_size` → `WORKED_ON.team_size_overall`（可选）
- `team_info.description` → `WORKED_ON.team_description`

图层典型查询示例：

- “我在哪些项目里是 `architect` 且 `stakeholder_tiers` 包含 `exec`？”
- “预算 `gt_1m` 且 `decision_accountability` 含 `commercial_strategy` 的项目？”

### 3.3 公司与业务域：Company、Domain

**Company**

- 源字段：`company_or_context`
- 解析策略：
  - 简单情况可按约定取分隔符前半段作为公司名（例如 `"Zoetis / 个人独立开发者"` 取 `Zoetis`）；
  - 解析出的公司名 → `Company.name`。
- 关系：
  - `(:Project)-[:AT_COMPANY]->(:Company)`

**Domain**

- 源字段：`data_domain`
- 映射：
  - `Domain.name = data_domain`
- 关系：
  - `(:Project)-[:IN_DOMAIN]->(:Domain)`

### 3.4 技能与工具：Skill 节点与 USES_SKILL

技术栈与平台工具统一抽象为 `Skill`，通过关系属性区分来源：

- 源字段：
  - `tech_stack[]`
  - `tools_platforms[]`

映射规则：

- 每个字符串条目创建或复用一个 `Skill` 节点：
  - `Skill.name = item`
  - 可根据需要增加 `Skill.category`（如 `language` / `framework` / `cloud` / `tool`），也可以依赖全局技能表。
- 关系：
  - `(:Project)-[:USES_SKILL {source: "tech_stack"}]->(:Skill)`
  - `(:Project)-[:USES_SKILL {source: "tools_platforms"}]->(:Skill)`

典型图查询：

- “使用 Databricks 且 `role_perspective = architect` 的项目？”
- “同时用了 Azure Data Factory 和 Delta Lake 的项目？”

### 3.5 治理产出：GovernanceArtifact 节点与 HAS_ARTIFACT

治理产出字段 `governance_artifacts` 与 `role_mapping_guidelines.md` 中定义的枚举保持对齐，并拆为独立节点，方便按治理成熟度筛选项目。

- 源字段：`governance_artifacts[]`

映射规则：

- 每个字符串值对应一个 `GovernanceArtifact` 节点：
  - `GovernanceArtifact.code = item`（如 `runbook`、`exec_dashboard`）
- 关系：
  - `(:Project)-[:HAS_ARTIFACT]->(:GovernanceArtifact)`

典型图查询：

- “有 `exec_dashboard` 且 `ai_component_flag = true` 的项目？”
- “同时交付 `runbook` 与 `risk_register` 的项目？”

### 3.6 项目 ID 生成

当前 `projects_summary.yaml` 中没有显式 `project_id` 字段。为了在图中实现稳定引用和幂等导入，建议在导入脚本中派生一个项目 UID：

- 示例策略：
  - `project_uid = slugify(project_name + "_" + timeframe.start)`
- 存储位置：
  - `Project.uid = project_uid`
  - 关系上可冗余 `WORKED_ON.project_uid = project_uid`，方便排错或幂等更新。

如后续在 YAML 中引入显式 `project_id` 字段，应改用该字段作为 `Project.uid` 的源。

## 4. RAG 流程中的分工

在“Prompt + RAG”整体架构中，可以让图层与向量检索层分工合作：

1. **图层（Graph Retrieval）**
   - 根据结构化条件筛选候选项目集，例如：
     - 最近 3 年、`role_perspective = architect`、`ai_component_flag = true`；
     - 使用 Databricks 和 Azure Data Factory，且预算 `gt_1m`；
     - 有 `exec_dashboard` 和 `risk_register` 的全球项目。
   - 查询结果是若干 `Project` 节点及其关联结构信息（公司、域、技能、治理产出等）。

2. **向量层（Vector Retrieval）**
   - 在上述候选 `Project` 集合中，取 `Project.search_text` 向量做语义相似度排序；
   - 选出最相关若干个项目，将其长文本字段拼接为 RAG 上下文。

3. **Prompt 构造与生成**
   - 将用户问题 + 选中项目的结构化信息（角色、时间、公司、域、指标）+ 长文本描述，一起构成 prompt；
   - 明确告知 LLM 只基于给定项目内容作答，减少幻觉与角色错位。

## 5. 实现建议（导入脚本方向）

实际落地到 Neo4j / Arango / JanusGraph 等图数据库时，可以按照如下步骤实现导入脚本：

1. 解析 `latest_resumes/projects_summary.yaml`，为每个项目生成 `project_uid` 并构建中间数据结构；
2. 统一创建/更新：
   - 单一 `Person` 节点（如 `id = "me"`）；
   - 每个项目的 `Project` 节点及其文本属性；
   - 对应的 `Company`、`Domain`、`Skill`、`GovernanceArtifact` 节点；
3. 为每个项目创建/更新：
   - `(:Person)-[:WORKED_ON {…}]->(:Project)`；
   - `[:AT_COMPANY]`、`[:IN_DOMAIN]`、`[:USES_SKILL]`、`[:HAS_ARTIFACT]` 等关系；
4. 在 `Project` 节点上构建 `search_text` 聚合字段，并在向量索引层注册；
5. 在 CLI 或服务层实现：
   - 图查询 + 过滤 API；
   - 候选项目的向量检索与 RAG 上下文构造逻辑。

上述建模保持了与现有 YAML schema 的对齐，也让后续扩展（增加项目级枚举、细化技能分类等）可以通过增量字段与关系实现，而不需要频繁重构图结构。 

