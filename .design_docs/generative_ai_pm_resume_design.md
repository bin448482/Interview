# Generative AI Product Manager Resume Plan

## 1. Background & Goals
- **Objective**: refresh the resume datasets in `latest_resumes/*.yaml` so they portray a senior/lead Generative AI Product Manager with verifiable AI commercialization, data governance, and cross-platform delivery results.
- **Drivers**: new interviews in Q4 2025 ask for concrete AI PM metrics (conversion, ARR, retention) and bilingual collateral. Existing YAML emphasizes engineering depth but not product strategy.
- **Success Criteria**:
  - Projects & experience narratives highlight roadmap ownership, user research signals, experimentation, and monetization outcomes.
  - Role responsibilities and skills clearly distinguish "Generative AI PM" from "AI application developer".
  - CN & EN YAML stay schema-compliant (`schema_version 1.1`, enums from `.design_docs/role_mapping_guidelines.md`) and pass repo linters.

## 2. Stakeholders & Consumers
- **Primary**: Interview panelists for PM/AI leadership roles in US/CN; internal recruiters needing structured YAML for downstream rendering.
- **Secondary**: Automation scripts under `scripts/` that ingest YAML to generate PDF/Markdown outputs; review bots enforcing `yamllint` and safe-load checks.
- **Success signal**: reviewers can lift a project block directly into JD-aligned talking points without extra editing.

## 3. Scope
- **In scope**:
  - Update `projects_summary.yaml` & `_en` twin with PM-focused metrics, decision ownership, generative AI governance language.
  - Extend `work_experience_summary*.yaml` role responsibilities to include Generative AI PM behaviors (prompt governance, experiment backlog, AI risk review).
  - Add/refresh relevant categories in `skills_summary*.yaml` (e.g., "Generative AI Product Strategy", "Multi-agent orchestration").
  - Maintain `personal_info_summary*.yaml` textual consistency (certifications, contact info) but verify translation & formatting.
- **Out of scope**:
  - Structural schema changes (no enum edits without `.design_docs` approval).
  - Updates to historical archived folders (`.backup/`, `.snapshots/`).
  - Automation or export scripts beyond describing hooks in plan.

## 4. Current State Snapshot (Nov 28, 2025)
- `projects_summary.yaml` already lists three flagship initiatives:
  1. **MySixth TarotAI**: strong AI infra + commercialization, missing explicit user research loop and roadmap artifacts.
  2. **NGSE**: showcases platform governance & exec reporting but lacks generative AI narrative.
  3. **AI增强智能简历投递系统**: rich LangChain/RAG detail but limited product-market framing.
- `role_responsibilities` include "产品经理" but without generative AI focus (no prompt lifecycle, A/B testing, AI risk logs).
- Skills emphasize engineering stacks; product analytics (north star metrics, funnel diagnostics) absent.
- English YAMLs lag behind CN versions and may not mirror latest data once edits begin.

## 5. Requirements Breakdown
1. **Narrative Shift**: each project must state the problem hypothesis, AI feature strategy, commercialization approach, and measurable outcomes (conversion %, ARR impact, retention uplift).
2. **Governance Signals**: reference guardrails like prompt QA, cost dashboards, abuse mitigation, fairness review.
3. **Stakeholder Coverage**: ensure `management_scope.stakeholder_tiers` includes exec/product/ops and `decision_accountability` contains `commercial_strategy` and `risk_governance` where applicable.
4. **Localization**: deliver CN + EN versions with consistent numerical data and ISO dates; highlight timezone-specific labels (e.g., "2025.10 – 至今" vs "Oct 2025 – Present").
5. **Validation**: `yamllint` + Python safe-load script must pass; include commands in final PR body.

## 6. Implementation Plan & Timeline (est. 2 days)
| Phase | Time | Key Tasks |
| --- | --- | --- |
| Discovery | 0.5d | Collect 2–3 target JD excerpts, map desired competencies to existing projects, confirm schema constraints in `.design_docs/role_mapping_guidelines.md`. |
| Content Design | 0.5d | Draft per-project deltas (problem, AI solution, metrics, governance); define new skill categories & role responsibility text. |
| YAML Edits (CN) | 0.5d | Update `latest_resumes/projects_summary.yaml`, `work_experience_summary.yaml`, `skills_summary.yaml` following two-space indent. Run `yamllint` + loader. |
| YAML Edits (EN) | 0.5d | Mirror updates into `_en` files. Ensure translation keeps product tone, adjust timeframe labels to English month abbreviations. |
| Validation & Review | 0.25d | Rerun validation commands, `rg` spot checks on `role_perspective`, capture before/after snippets for reviewers. |
| Packaging | 0.25d | Draft PR summary (intent, impacted files, validation output). Optionally export Markdown/PDF excerpt via existing scripts. |

## 7. Data & Content Guidelines
- Keep lists in narrative order (newest project first). Do not alphabetize.
- Use double quotes for strings containing punctuation or mixed-language text.
- Quantify impact with concrete numbers (ARR, retention %, latency). If only directional data exists, annotate with time period (e.g., "Q3 2025 付费转化 +18%").
- `management_scope.team_size` stays integer or null; avoid textual descriptions there.
- For any new governance artifact (e.g., "prompt_playbook"), confirm enumeration or document rationale in PR description.

## 8. Risk & Mitigation
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Enum mismatch when adding new decision_accountability values | Linter failure, downstream parser crash | Cross-check `.design_docs/role_mapping_guidelines.md`, reuse existing enums only. |
| Metric credibility questioned | Interview panel loses trust | Cite data source in `notes` when metric derived from experiments; keep ratios realistic (<3x unless justified). |
| English/Chinese drift | Recruiters see inconsistent facts | After CN edits, immediately port to `_en` files; use diff tools to align sequences. |
| Sensitive PII leakage | Compliance issues | Verify no new tokens/URLs beyond approved GitHub link; anonymize user data references. |

## 9. Validation Checklist
1. `source .venv/bin/activate`
2. `yamllint latest_resumes/*.yaml`
3. ```bash
python - <<'PY'
import yaml, pathlib
for path in pathlib.Path('latest_resumes').glob('*.yaml'):
    yaml.safe_load(path.read_text(encoding='utf-8'))
print('YAML loads \u2713')
PY
```
4. `rg -n "role_perspective" latest_resumes/projects_summary.yaml`
5. Manual bilingual spot-check (projects & work experience).

## 10. Deliverables
- Updated CN/EN YAML datasets with PM-focused narratives.
- This design plan stored at `docs/generative_ai_pm_resume_design.md` for reviewer sign-off.
- Optional: summary snippet or slide for interview rehearsal referencing new metrics.
