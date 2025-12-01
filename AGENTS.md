# Repository Guidelines

## Project Structure & Module Organization
The repo is data-first: `latest_resumes/` holds the four canonical YAML summaries (personal info, skills, projects, work experience) and is the only folder that should change in feature branches. `.design_docs/role_mapping_guidelines.md` defines every enum used in `projects_summary.yaml`; treat it as the contract for schema choices before editing any project block. Archive folders such as `.backup/` and `.snapshots/` keep raw pulls for provenance, while `.venv/` and `.vscode/` exist purely for local tooling and should not be versioned differently.

## Build, Test, and Development Commands
- Activate the shared interpreter with `source .venv/bin/activate` (or `.venv\\Scripts\\activate` on Windows) so everyone runs identical tooling.
- Install validation helpers when needed: `pip install -U yamllint ruamel.yaml`.
- Run `yamllint latest_resumes/*.yaml` to catch spacing or quoting drift, then spot-check fields with `rg -n "role_perspective" latest_resumes/projects_summary.yaml`.
- Sanity-check structure with a quick loader:
```bash
python - <<'PY'
import yaml, pathlib
for path in pathlib.Path('latest_resumes').glob('*.yaml'):
    yaml.safe_load(path.read_text(encoding='utf-8'))
print('YAML loads ✓')
PY
```
- Runtime secrets (OpenAI/Zhipu/Ollama endpoints、Token 等) 统一放在 `latest_resumes/runtime_config.yaml`，不要依赖 `.env`。复制 `latest_resumes/runtime_config.example.yaml` 并填写后，本地 CLI/脚本会自动加载；该文件已经加入 `.gitignore`，请勿提交。

## Coding Style & Naming Conventions
Use two-space indentation, double quotes around mixed-language strings, and `snake_case` keys (see `schema_version`, `role_perspective`). Keep narrative order for lists—projects stay chronologically relevant rather than alphabetized—and group metadata keys before narrative text. URLs or repo references belong in clearly prefixed fields such as `git_like` and must stay quoted.

### Project-level role fields (do not remove)

For every project entry in `latest_resumes/projects_summary*.yaml`, the following
fields are part of the stable schema contract:

- `role_perspective`:
  - Allowed values: `developer`, `architect`, `project_manager`, `product_owner`, `hybrid`.
  - Describes the main perspective for this project (implementation, architecture,
    delivery/governance, or product). Use `hybrid` only when responsibilities truly
    cannot be separated and explain nuance in `notes`.
- `llm_primary_role`:
  - Optional; when present, must be one of the `ROLE_FILTERS` keys
    (e.g. `data_development`, `ai_development`, `full_stack`, `product_manager`,
    `project_manager`, `ai_product_designer`, `ai_engineer`).
  - Used only by `llm_polisher` to choose the default role-aware prompt.
- `llm_secondary_roles`:
  - Optional list of additional `ROLE_FILTERS` keys that are also acceptable
    polishing perspectives for this project.
  - If the CLI `--role` is in this list, the polisher prefers that global role;
    otherwise it falls back to `llm_primary_role`.

These rules apply uniformly for all contributors and tools:
- Do not delete these fields from YAML once introduced; if a project does not need
  them, leave them empty/null instead of removing the keys.
- Do not remove this section from the docs; downstream agents rely on this contract
  when interpreting and editing projects.

## Design Docs Directory

All design documents should be placed in the `.design_docs/` directory.

**Document Types:**
- `*_design.md` - Feature design documents
- `*_plan.md` - Implementation plan documents
- `*_guidelines.md` - Guidelines and standards documents

**Current Design Docs:**
- `.design_docs/merry-painting-sonnet.md` - Persona-Aware LLM Prompting implementation plan
- `.design_docs/role_mapping_guidelines.md` - Role mapping standards

## YAML Configuration Files

All YAML configuration files should be placed in the `latest_resumes/` directory.

**Configuration File Types:**
- `*_config.yaml` - System configuration files
- `*_summary.yaml` - Data summary files

**Current Configuration Files:**
- `latest_resumes/prompt_config.yaml` - Role-aware prompt configuration

## Scripts & Automation

All helper scripts should be placed in the `scripts/` directory.

**Script Naming Convention:**
- Use `snake_case` naming
- Prefix indicates script type:
  - `test_*.py` - Test scripts
  - `generate_*.py` - Generation scripts
  - `validate_*.py` - Validation scripts
  - `migrate_*.py` - Migration scripts

**Script Structure:**
```python
"""Script description

Functionality: ...
Usage: python scripts/xxx.py
Output: ...
Dependencies: ...
"""

# Imports
# Constants
# Main function

if __name__ == "__main__":
    main()
```

**Current Scripts:**
- `scripts/generate_prompts.py` - Generate prompts for different roles
- `scripts/test_role_prompts.py` - Test prompt generation (venv version)

See `scripts/README.md` for details.

## Testing Guidelines
Treat `yamllint` plus the loader script as the minimum pre-commit bar and re-run them after resolving merge conflicts. If you add automation scripts later, co-locate pytest files under `tests/` and wire them into CI before relying on the output. Reviewers should reject any project entry that omits `decision_accountability`, metric blocks, or `management_scope` because downstream agents require them for filtering.

## Commit & Pull Request Guidelines
History favors short imperative messages with a type prefix (e.g., `chore: checkpoint current resume updates`). Follow the same `type[:scope]: summary` shape, reference the primary YAML file in the body, and include validation output snippets. PRs must describe the intent, list touched files, attach screenshots or rendered excerpts if content meaning changes, and tag stakeholders who consume that slice of data.

## Security & Data Handling
These files store personally identifiable information. Only store anonymized samples in `.design_docs/` when illustrating patterns, never push secrets or private URLs, and confirm redaction before sharing excerpts outside the repo. Use encrypted channels for certification evidence and rotate or remove any accidentally committed tokens immediately.
