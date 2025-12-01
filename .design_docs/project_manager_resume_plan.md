# Project Manager / Product Manager Resume Plan

> 状态校准（2025-12）：在 2025-11 版本中，CLI 仅提供 `product_manager` 代码角色。根据最新面试需求，需要 **新增独立的 `project_manager` 代码角色**，强调项目管理与技术决策评估视角。  
> 本文档更新为：在保持 `latest_resumes/*.yaml` 为单一数据真实来源的前提下，**同时规划代码侧与数据侧改动**，让 `--role project_manager` 与 `--role product_manager` 各自输出清晰区分的简历版本。

## 1. Background & Problem Statement
当前仓库已经完成简历数据收敛与角色配置重构：
- `latest_resumes/projects_summary*.yaml` 只保留 3 个旗舰项目（TarotAI、NGSE、Remedium），字段包含 `management_scope`、`decision_accountability`、`governance_artifacts` 等 PM 相关枚举。
- `resume_docs/role_config.py` 中存在 `product_manager` 角色及 persona，`latest_resumes/prompt_config.yaml` 也为该角色定义了专门的输出结构与语气。
- `work_experience_summary*.yaml` 的 `experiences` 和 `role_responsibilities` 已经出现 “项目经理 / Project Manager”“产品经理 / Product Manager” 等角色描述。

但当前叙事与角色配置仍存在问题：
- 项目段落仍然偏重工程实现细节，对 roadmap ownership、干系人对齐、风险治理与预算/范围控制的“项目经理视角”不够集中。
- 中英文数据在 Generative AI PM 能力的体现上不完全对齐，尤其是商业化与 AI 风险治理描述。
- 技能矩阵中 PM/AI PM 能力已经存在（如 “Generative AI 产品策略与指标”），但排序与组织方式仍然偏工程导向。
- CLI 侧只有 `product_manager` 角色，没有将“项目经理（交付/治理，评估技术决策）”与“产品经理（用户/商业化）”明确区分。

目标是在 **引入新的 `project_manager` 代码角色但保持 schema 不变** 的前提下，通过少量代码 + YAML 更新，分别产出：
- 面向项目交付/治理与技术决策评估的 `--role project_manager` 简历输出；
- 面向产品策略/商业化与用户洞察的 `--role product_manager` 简历输出。

## 2. Goals & Non-Goals
- **Goals**
  - 让 `project_manager` 角色生成的简历自然呈现“项目交付负责人”的叙事：业务/技术背景 → 目标与范围 → 计划与干系人 → 技术选型评估 → 风险/变更管理 → 指标结果。
  - 让 `product_manager` 角色保持“Generative AI 产品经理/产品设计师”的叙事：用户洞察 → 问题假设 → AI 方案 → 商业化路径 → 实验与指标。
  - 强化项目与工作经历中对 roadmap ownership、干系人管理、AI 治理与商业化指标的描述，并在 `project_manager` 视角下更多展示对技术决策的评估与取舍。
  - 保持 zh-CN / en-US YAML 数据在数字、时间线和关键表述上的严格对齐。
- **Non-Goals**
  - 不修改现有 schema（`schema_version`、字段名与枚举值保持不变）。
  - 不调整 `llm_role_resolver` 的整体算法，仅在 `ROLE_FILTERS` / `prompt_config` 中扩充分支。
  - 不引入新的模板或导出形式，只复用现有 DOCX 流程。

## 3. Scope Overview
| Area | Required Changes |
| --- | --- |
| YAML data (`latest_resumes/*.yaml`) | 按 PM 视角补写/重构项目、工作经历与技能描述，强调决策与指标，保证中英文对齐。 |
| Role usage | 设计并实现新的 `--role project_manager` 代码角色，与现有 `product_manager` 并存，并在 persona 与字段可见性上做明确区分。 |
| Design docs | 与 `.design_docs/generative_ai_pm_resume_design.md`、`.design_docs/role_mapping_guidelines.md` 和 `.design_docs/project_level_role_prompt_design.md` 保持一致，将本计划作为落地执行清单。 |
| Validation | 运行 `yamllint`、loader 脚本及 CLI dry-run（zh-CN/en-US，role=product_manager）。 |

## 4. Data Workstream（Single Source of Truth）

### 4.1 项目层（projects_summary*.yaml）
1. **CN 项目差分设计**
   - 针对 3 个项目（TarotAI、NGSE、Remedium），对照 `.design_docs/generative_ai_pm_resume_design.md`：
     - 每个项目在 `project_overview` / `challenges_or_objectives` 中明确：业务问题/假设、AI 方案、商业化路径。
     - 在 `impact_metrics.business_metrics` 中补强 ARR、转化率、留存/NPS 等 PM 指标，保持数值可信且与现有叙事一致。
     - 核对并补全 `management_scope.stakeholder_tiers`、`decision_accountability`、`responsibility_focus`、`governance_artifacts`，确保体现 exec/product/ops、commercial_strategy、risk_governance 等枚举。
     - 根据 `.design_docs/role_mapping_guidelines.md` 中 `role_perspective` 定义，区分项目的主视角：
       - 对项目管理/交付主导的项目（如 NGSE）优先考虑设置为 `project_manager` 或 `hybrid`；
       - 对以技术架构为主的项目（如 Remedium）保持 `architect`，但在 `decision_accountability` 中体现“评估/把关技术决策”的责任。
     - 适度“收缩”过深的纯技术 bullet，把空间让给 roadmap、stakeholder、实验节奏（OKR、A/B、Cohort 等）描述。
2. **EN 项目镜像更新**
   - 在 CN 调整完成后，同步更新 `projects_summary_en.yaml`：
     - 数字、时间、项目顺序、字段存在性与中文完全一致。
     - 采用更标准的 PM 用语（problem / hypothesis / user insights / experiments / outcomes）。
     - 校准 `role_title` 与 `notes` 的翻译，使其明确传达 Generative AI PM/项目负责人角色。

### 4.2 工作经历层（work_experience_summary*.yaml）
3. **Experiences 标题与时间线**
   - 审核 `experiences` 段：
     - Zoetis/PWC/HP 等经历的 `title` 是否清晰表达 PM/项目负责人身份（如 “Project Manager & Data Architect & AI Application Developer” 的顺序与重点）。
     - 确认 CN/EN 的时间区间一致，必要时在英文版本中加上 “(China)” 等上下文以支撑叙事。
4. **Role responsibilities 对齐**
   - 对 `role_responsibilities` 中 “项目经理”“产品经理”“AI应用开发”等角色进行职责梳理：
     - 保留“项目经理”“产品经理”中关于范围/进度/成本控制、干系人管理、风险与变更、AI 治理与实验节奏的条目。
     - 确保这些职责与项目中的 `decision_accountability` / `governance_artifacts` / `impact_metrics` 一一呼应。
     - 英文 responsibilities 调整为更 JD 友好的表达（roadmap ownership, stakeholder alignment, AI risk reviews, experimentation backlog）。

### 4.3 技能层（skills_summary*.yaml）
5. **技能矩阵重排与补充**
   - 在 `skills_summary.yaml` / `_en` 中：
     - 将 “项目/项目群管理与指标”“Generative AI 产品策略与指标”“多代理编排与提示治理”“独立开发能力”等 PM/AI PM 相关 category 适度前置。
     - 对纯底层工程栈（CV 模型列表、细粒度框架清单等）进行收拢，合并到 1–2 个更概括的 bullet，避免盖过 PM 能力。
     - 如有必要新增 “项目/产品管理 & 指标” 类别，将 KPI/SLA、roadmap、风险矩阵、跨团队协作集中描述。

### 4.4 校验
6. **结构与枚举校验**
   - 严格遵循 `.design_docs/role_mapping_guidelines.md` 中枚举取值，不增删自定义枚举。
   - 使用 `rg -n "role_perspective" latest_resumes/projects_summary.yaml` 等命令 spot-check 字段是否符合 schema 与预期。

## 5. Role & Persona Usage（project_manager vs product_manager）

本节列出为了支持新的 `project_manager` 代码角色，在代码与配置层面需要完成的改动清单。

### 5.1 语义区分
- `project_manager`：
  - 关注范围：项目计划、范围与里程碑、预算与资源、风险/问题/变更管理；
  - 对技术决策的角色：评估备选技术方案的风险/成本/可落地性，做出或推动决策，并在简历中体现“评审 + 取舍”；
  - 重点字段：`management_scope`、`decision_accountability`（尤其是 `delivery_owner`, `risk_governance`, `technical_strategy`）、`governance_artifacts`（如 `risk_register`, `roadmap`, `RACI`）、`impact_metrics` 中的交付/效率类指标。
- `product_manager`：
  - 关注范围：用户问题、价值假设、商业化路径、实验与指标；
  - 对技术决策的角色：主要从产品价值与用户体验角度提出约束和优先级；
  - 重点字段：`impact_metrics.business_metrics`、用户/商业背景、实验与 A/B 流程。

### 5.2 代码与配置改动列表

1. `resume_docs/role_config.py`
   - 在 `ROLE_FILTERS` 中新增 `project_manager` 条目，示例规则：
     - `include_projects`：
       - `responsibility_focus` 包含 `planning`、`stakeholder_management` 或 `compliance`；
       - 或 `decision_accountability` 包含 `delivery_owner` 或 `risk_governance`；
       - 或 `role_title` 文本包含 “项目经理”/`Project Manager`；
     - `exclude_projects`：
       - `role_title` 包含 “测试”/“运维” 等与项目管理无关的角色；
     - `persona`（草案）：
       - `label`: "项目交付与技术决策视角"
       - `instructions.zh`: 强调范围/进度/成本控制、跨团队协作、风险治理，以及对关键技术决策的评估与把关；
       - `instructions.en`: 强调 scope/schedule/budget, cross-team delivery, risk governance, and evaluation of major technical decisions;
     - `field_visibility`：
       - 强制展示：`management_scope`, `decision_accountability`, `governance_artifacts`, `impact_metrics`, `role_perspective`, `project_overview`, `challenges_or_objectives`, `responsibilities`, `timeframe`, `company_or_context`, `role_title`;
       - 仅保留必要的技术上下文：`architecture_or_solution`、`tech_stack`、`tools_platforms` 设为 True 但简洁呈现；
       - 可隐藏：与底层实现强相关、对项目经理视角噪声较大的字段（如过细的 `process_or_methodology` 细节）。

2. `resume_docs/ROLE_FILTERS.md`
   - 新增 “项目经理 (project_manager)” 小节，文档化上述过滤规则：
     - 列出包含/排除项目条件；
     - 简要说明适用场景（例如“项目/项目群交付负责人、技术项目经理 TPM、Program Manager”）。

3. `latest_resumes/prompt_config.yaml`
   - 在 `roles:` 下新增 `project_manager` 配置：
     - `label`: "项目交付/技术决策视角"；
     - `output_structure.zh`（草案）：
       - "项目名称 | 所属公司/个人 | 起止时间"
       - "角色 Role"
       - "项目背景 & 范围"
       - "关键干系人与依赖"
       - "关键决策 & 风险/问题管理"
       - "交付成果 & 指标"
     - `output_structure.en`：
       - "Project Name | Company/Organization | Duration"
       - "Role"
       - "Project Context & Scope"
       - "Stakeholders & Dependencies"
       - "Key Decisions, Risks & Issues"
       - "Delivery Outcomes & Metrics"
     - `task_focus`：强调范围管理、跨团队交付、风险治理与对关键技术决策的评估；
     - `metrics_categories`：优先 `operational_metrics` + `business_metrics`，必要时引用 `technical_metrics` 支撑“决策质量”。

4. CLI 使用与文档
   - 在 `resume_docs/ROLE_FILTERS.md`、`CLAUDE.md` 或相关 README 中补充：
     - 支持的角色列表中新增 `project_manager`；
     - 简要示例：`python -m resume_docs.cli --role project_manager --locale zh-CN --template modern --dry-run`。
   - 若有针对 role 的自动化脚本或测试（如 `scripts/test_role_prompts.py`），补充 `project_manager` 的回归用例。

## 6. Testing & Validation Plan
1. **静态检查**
   - `yamllint latest_resumes/*.yaml`
   - Python safe-load 脚本（见 `AGENTS.md`）：
     - 遍历 `latest_resumes/*.yaml` 并 `yaml.safe_load`，确认全部可解析。
2. **角色视角 Dry Run**
   - `python -m resume_docs.cli --template modern --locale zh-CN --role project_manager --dry-run`
   - `python -m resume_docs.cli --template modern --locale en-US --role project_manager --dry-run`
   - `python -m resume_docs.cli --template modern --locale zh-CN --role product_manager --dry-run`
   - `python -m resume_docs.cli --template modern --locale en-US --role product_manager --dry-run`
3. **DOCX 生成与人工检查（可选）**
   - 激活 `.venv` 并配置好 `latest_resumes/runtime_config.yaml` 后执行：
     - `python -m resume_docs.cli --role project_manager --locale zh-CN --template modern --skip-polish --include-contact`
     - `python -m resume_docs.cli --role project_manager --locale en-US --template modern --skip-polish --include-contact`
     - `python -m resume_docs.cli --role product_manager --locale zh-CN --template modern --skip-polish --include-contact`
     - `python -m resume_docs.cli --role product_manager --locale en-US --template modern --skip-polish --include-contact`
   - 打开 `docs/output/<locale>/modern/` 下的 DOCX，手工确认：
     - 项目顺序、字段展示是否符合 PM 预期。
     - PM/AI PM 能力是否被突出，而不是被纯工程细节淹没。

## 7. Milestones & Timeline（estimate）
| Day | Deliverable |
| --- | --- |
| Day 0 | 确认 `project_manager` 与 `product_manager` 的角色边界与验收标准。 |
| Day 1 | 完成 `resume_docs/role_config.py`、`resume_docs/ROLE_FILTERS.md`、`latest_resumes/prompt_config.yaml` 中 `project_manager` 相关代码与配置改动；本地跑通 dry-run。 |
| Day 2 | 完成 CN 项目/工作/技能 YAML 更新并通过 `yamllint` + loader 校验；确保 `role_perspective`、`management_scope`、`decision_accountability` 等字段符合新角色语义。 |
| Day 3 | 完成 EN YAML 镜像更新，dry-run 验证 `--role project_manager` 与 `--role product_manager` 下的 zh-CN/en-US 输出。 |
| Day 4 | 可选：DOCX 视觉检查与打磨，准备 PR（包含变更摘要与校验命令输出）。 |

## 8. Risks & Mitigations
- **PM 叙事不够集中**：如果技术细节仍然过多，优先在 projects 的 `responsibilities`、`architecture_or_solution` 中做裁剪，将 PM 行为前置。
- **中英文漂移**：每次修改 CN 后立即更新 EN，对比 diff 确认项目顺序与数值完全一致。
- **枚举或 schema 变更风险**：不新增枚举值，必要时在 PR 描述中解释某些取值选择的理由。
- **可信度质疑**：对来源于实验或估算的指标，在 `notes` 中简要注明依据，数字保持保守区间。

## 9. Open Questions
1. `project_manager` 与 `product_manager` 的典型 JD 场景边界是否需要进一步量化（例如是否新增 “Program Manager / TPM” 子 persona）？
2. 是否需要为未来的更细分画像（如 `ai_program_manager`、`ai_portfolio_lead`）预留数据结构或文案空间？
3. 在实际生成简历时，是否需要额外输出 Markdown/PDF 版本供快速投递，还是 DOCX 足够覆盖目前需求？
