# `latest_resumes` YAML Authoring Guide

## 1. Repository Boundary & Workflow
- Only edit files under `latest_resumes/` when updating resume content; other folders (code, docs, backups) stay immutable in feature branches per `AGENTS.md`.
- Source data (notebooks, long-form resumes) lives elsewhere. Reference the source in each YAML via `source_file` to keep provenance.
- Always produce both Chinese (`*_summary.yaml`) and English (`*_summary_en.yaml`) versions using identical structure. Update the Chinese file first, then translate field-by-field to the English twin.
- Maintain two-space indentation, double-quoted strings for text with punctuation or colons, and `snake_case` keys. Preserve list order to keep narrative flow (newest projects first, etc.).
- Validation checklist after every edit:
  1. `yamllint latest_resumes/*.yaml`
  2. Run the loader snippet from `AGENTS.md` to ensure every YAML parses.
  3. `rg -n "role_perspective" latest_resumes/projects_summary.yaml` to confirm schema alignment.

## 2. Shared Metadata Fields
Many files reuse the following keys:
- `schema_version`: Numeric contract (currently `1.1` for project data); bump only when `.design_docs/role_mapping_guidelines.md` changes enumerations.
- `generated_at`: ISO 8601 timestamp (e.g., `2025-11-28T10:40:46.354834`) or date-only (`YYYY-MM-DD`) if time unknown; stay UTC when possible.
- `source_file`: The markdown/Docs filename that fed the summary (e.g., `Resume_Data_Engineer_CN_20250529.md`).
- `ai_component_flag`: Boolean telling downstream agents whether AI/ML components exist in the described project.

## 3. File-by-File Data Model
### 3.1 `personal_info_summary*.yaml`
Top-level scalar fields:
- `name`, `phone`, `email`, `address`, `hukou`, `gender`, `github`.
Collections:
- `education`: list of `{description}` entries. Keep most recent degree first.
- `certifications`: list of `{name, url?}`. Use a public verification URL when available.
Guidelines:
- Normalize phone numbers and emails; redact anything private per security policy.
- If multiple GitHub/portfolio links exist, add extra keys such as `git_like` later, but keep them quoted.

### 3.2 `skills_summary*.yaml`
Structure:
```yaml
skills:
  - category: "Programming Languages & Frameworks"
    items:
      - "Proficient in C#"
```
Rules:
- Each `category` groups 4–8 bullet sentences ordered by business relevance.
- Use verb-leading statements (“Design…”, “Build…”) to help LLM scorers.
- Keep terminology bilingual per file language; do not mix languages in a single item.

### 3.3 `work_experience_summary*.yaml`
Two sections:
1. `experiences`: chronological list of `{company, duration, title}`. Duration stays as the human-readable label already used in resumes.
2. `role_responsibilities`: list of role profiles. Each entry carries `role` and a `responsibilities` array with 4–5 outcome-focused sentences.
Guidelines:
- Treat `experiences` as the canonical employment timeline used by downstream filtering agents.
- `role_responsibilities` should cover every role referenced in `projects_summary`. Reuse wording between languages but keep tone localized.

### 3.4 `projects_summary*.yaml`
This is the richest schema. Follow `.design_docs/role_mapping_guidelines.md` before editing enums.

Top-level metadata:
- `schema_version`, `generated_at`, `source_file` as described above.
- `projects`: ordered list (reverse chronological) of project dictionaries.

Every project entry must include:
- `project_name`: Plain-text label.
- `company_or_context`: Employer, client, or “个人独立开发者”.
- `timeframe`: object with `label` (human string), machine-readable `start`/`end` (`YYYY-MM` or `null`).
- `role_title`: Resume-friendly title.
- `role_perspective`: One of `developer|architect|project_manager|product_owner|hybrid`. Decide using the guideline doc; add clarifying note in `notes` if `hybrid`.
- `management_scope`: object with `team_size` (int or `null`), `budget_level` (`lt_100k|bt_100k_1m|gt_1m|null`), and `stakeholder_tiers` (ordered array such as `exec`, `director`, `ops`, `vendor`, `customer`).
- `decision_accountability`: non-empty subset of `[delivery_owner, technical_strategy, people_management, hands_on_build, commercial_strategy, risk_governance]` describing accountable areas.
- `responsibility_focus`: choose 2–3 tags from `[planning, architecture, implementation, operations, commercialization, stakeholder_management, compliance]`.
- `impact_metrics`: object with `business_metrics`, `technical_metrics`, `operational_metrics` lists. Keep sentences quantitative (e.g., “RAG吞吐 >50 职位/分钟”).
- `governance_artifacts`: artifacts you actually delivered (e.g., `runbook`, `exec_dashboard`, `risk_register`). Use empty list if none.
- Narrative blocks: `project_overview`, `data_domain`, `ai_component_flag` (bool), `challenges_or_objectives`, `responsibilities`, `architecture_or_solution`, `process_or_methodology`, `deliverables_or_features`, `metrics_or_impact`, `tech_stack`, `tools_platforms`.
- `team_info`: object with `team_size` and optional `description` summarizing team composition.
- `notes`: optional free-form clarifier or external link.

Authoring tips:
- Keep bullet arrays parallel between CN and EN versions to avoid downstream diff churn.
- When referencing URLs, embed inside the narrative string (e.g., `GitHub: https://github.com/...`) and keep them quoted.
- Use metric verbs first (“交付…”, “Built…”) to help filtering models detect achievements.
- When a project reuses subcomponents (e.g., multiple pipelines), describe them in `architecture_or_solution`; leave pricing/licensing info to `responsibilities`.

## 4. Creation Process
1. **Collect Inputs**: Gather latest resume draft, portfolio metrics, and approvals. Confirm sensitive data has been redacted.
2. **Update Chinese Files**:
   - Edit the relevant `*_summary.yaml` with new entries. Maintain chronological ordering.
   - Run the validation commands.
3. **Translate to English Files**:
   - Mirror the structure exactly. For numbers/dates keep the same formats; translate only prose.
   - Double-check comma/colon usage to satisfy YAML quoting rules.
4. **Cross-File Consistency Checks**:
   - Ensure every project’s `role_title` exists somewhere in `work_experience_summary*.yaml`.
   - Align skills keywords mentioned in `projects_summary` with at least one `skills_summary` item for searchability.
   - When `ai_component_flag: true`, mention supporting AI tech in `skills_summary` or `role_responsibilities`.
5. **Finalize & Commit**:
   - Run `yamllint` and the loader. Screenshot or copy results for PR descriptions per guidelines.
   - Commit using the `type[:scope]: summary` format (e.g., `feat: refresh resume YAMLs`). Reference the edited YAML file(s) in the message body.

## 5. Common Pitfalls & Safeguards
- **Missing required fields**: Downstream agents reject projects lacking `decision_accountability`, `impact_metrics`, or `management_scope`. Always populate them, even with `null`/empty lists if value truly unknown.
- **Enum drift**: Never invent new `role_perspective` or `budget_level` values without first updating `.design_docs/role_mapping_guidelines.md`.
- **Timeframe alignment**: `label` can be free-form (e.g., `2025.10 - 至今`), but `start`/`end` must remain machine-readable `YYYY-MM`. Use `null` for ongoing work.
- **Mixed languages**: Keep each file monolingual to prevent scoring noise. Use localized punctuation (`。` vs `.`) appropriately.
- **Security**: No raw PII beyond what’s already resume-ready. If a project references internal systems, abstract names (e.g., “某大型医药客户”).

Following this guide keeps the `latest_resumes/` dataset canonical, lint-clean, and ready for downstream automation.
