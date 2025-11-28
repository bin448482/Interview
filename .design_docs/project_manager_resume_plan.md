# Project Manager Resume Plan

## 1. Background & Problem Statement
Current CLI generation (`resume_docs/cli.py`) exposes only three role filters (`data_development`, `full_stack`, `ai_development`). Resume data already stores some `role_perspective: project_manager` entries (e.g., `latest_resumes/projects_summary.yaml:543`), but these are not surfaced because:
- No `project_manager` role exists inside `resume_docs/role_config.py` / `ROLE_FILTERS.md`.
- Only one legacy project (`LMS`) is tagged as `project_manager`; other PM-centric efforts stay labeled `hybrid`.
- `role_filter.RoleFilter` lacks include rules for PM-specific work experiences, so CLI output mixes engineering-heavy history.

We need a repeatable plan to expose a dedicated project manager resume while respecting the data-first contract in `AGENTS.md`.

## 2. Goals & Non-Goals
- **Goals**
  - Define filtering heuristics and documentation for a new `project_manager` role.
  - Ensure PM resumes highlight governance/delivery achievements, not deep-dive engineering tasks.
  - Keep zh-CN and en-US data in sync.
- **Non-Goals**
  - Building new rendering templates or locales.
  - Modifying LLM polishing prompts beyond ensuring they work with the new role.

## 3. Scope Overview
| Area | Required Changes |
| --- | --- |
| YAML data (`latest_resumes/*.yaml`) | Expand/retag projects & work entries with PM metadata; ensure schema fields complete (`management_scope`, `decision_accountability`, `governance_artifacts`). |
| Role config (`resume_docs/role_config.py`, `ROLE_FILTERS.md`) | Add `project_manager` block, include/exclude rules, optional work filters. |
| CLI docs (`README.md`, `resume_docs/claude.md`) | Advertise new role and usage examples. |
| Validation | `yamllint`, loader smoke test, CLI dry-run outputs for zh-CN/en-US. |

## 4. Data Workstream (Single Source of Truth)
1. **Project Inventory**
   - Review every `projects_summary*.yaml` block for PM signals: `role_title` contains PM/Lead/Scrum Master, `decision_accountability` lists `delivery_owner`, `risk_governance`, `commercial_strategy`, or `management_scope.team_size >= 5`.
   - Where a project mixes engineering + PM, either (a) split into separate records or (b) keep `role_perspective: hybrid` with a note, but create at least 3–4 pure PM entries spanning 2023–2014 for narrative depth.
2. **Field Completion**
   - Enforce `management_scope.stakeholder_tiers` to include `exec/director/ops/vendor` when applicable.
   - Populate `governance_artifacts` (e.g., `roadmap`, `risk_register`, `exec_dashboard`) so filters can key off them.
   - Ensure `impact_metrics.business_metrics` mention on-time %, budget variance, stakeholder NPS, etc.
3. **Work History & Responsibilities**
   - For `work_experience_summary*.yaml`, augment durations/titles to surface PM roles clearly (Zoetis PM, HP Scrum Master, etc.).
   - Curate `role_responsibilities` for "项目经理" / "Project Manager" with quantifiable outcomes that align with project data.
4. **Validation**
   - Run `yamllint latest_resumes/*.yaml`.
   - Execute loader smoke test from `AGENTS.md` to guarantee schema correctness.

## 5. Role Filter & Code Changes
1. **New Role Entry** (`resume_docs/role_config.py`)
   ```python
   "project_manager": {
       "name": "项目经理",
       "include_projects": [
           {"field": "role_perspective", "exact": "project_manager"},
           {"field": "responsibility_focus", "contains": ["planning", "stakeholder_management", "compliance"]},
           {"field": "decision_accountability", "contains": ["delivery_owner", "risk_governance"]},
       ],
       "exclude_projects": [
           {"field": "role_perspective", "exact": "developer"},
           {"field": "ai_component_flag", "value": True, "requires_governance": False}  # see note below
       ],
       "include_work_roles": [
           {"field": "title", "pattern": ".*(项目经理|Scrum Master|Program Manager).*"}
       ],
       "sort_by": "relevance_then_time",
   }
   ```
   - Implement `contains` handling for list fields already present (`role_filter._match_field_rule`).
   - Optional: extend rule syntax to support `any_governance_artifacts` for future filtering—validate necessity before coding.
2. **Work Experience Filtering**
   - `role_filter._filter_work_experience` already accepts `include_work_roles`; wire it in for `project_manager`.
   - Consider trimming `work.role_responsibilities` to only PM-related entries when role config requests it.
3. **Documentation Sync**
   - Update `resume_docs/ROLE_FILTERS.md`, `README.md` ("Available roles" + command snippets), and `resume_docs/claude.md` quick commands.
   - Mention PM role in `.design_docs/resume_docs_design.md` if that document enumerates supported roles.
4. **Optional Enhancements**
   - Wire `_calculate_relevance_score` into `_filter_and_sort_projects` when `sort_by == "relevance_then_time"` so projects matching multiple PM rules rank higher.

## 6. Testing & Validation Plan
1. **Static Checks**
   - `yamllint latest_resumes/*.yaml`
   - Python loader smoke test from `README.md`.
2. **Role-specific Dry Runs**
   - `python -m resume_docs.cli --template modern --locale zh-CN --role project_manager --dry-run`
   - `python -m resume_docs.cli --template modern --locale en-US --role project_manager --dry-run`
3. **DOCX Sanity**
   - With `.venv` activated, run `python -m resume_docs.cli --role project_manager --locale zh-CN --template modern --skip-polish --include-contact` and manually inspect the produced DOCX in `docs/output/zh-CN/modern/`.
4. **Regression**
   - Re-run one existing role (e.g., `data_development`) to confirm filtering logic didn’t regress.

## 7. Milestones & Timeline (estimate)
| Day | Deliverable |
| --- | --- |
| Day 0 | Finalize this design, confirm acceptance criteria with stakeholders. |
| Day 1 | Update/expand YAML data for PM projects + work; run validation scripts. |
| Day 2 | Implement role config, doc updates, dry-run verification. |
| Day 3 | Optional DOCX polish, prepare PR with summary + validator output. |

## 8. Risks & Mitigations
- **Insufficient PM-labeled data**: Mitigate by duplicating hybrid projects with PM-specific narrative; document rationale in `notes`.
- **Filter overfitting**: Avoid regex patterns that miss English entries; prefer enums (`role_perspective`) where possible.
- **Doc drift**: Fail CI if README/ROLE_FILTERS doesn’t list new role (consider adding a unit test or linters later).

## 9. Open Questions
1. Should PM resumes include select technical achievements (e.g., AI governance) or strictly managerial content?
2. Do we need localized role keys (e.g., `project_manager_cn`) for future segmentation, or is a single role sufficient?
3. Is there appetite for additional PM subtypes (program/portfolio) that would change filtering logic soon?
