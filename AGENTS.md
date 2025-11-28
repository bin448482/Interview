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

## Coding Style & Naming Conventions
Use two-space indentation, double quotes around mixed-language strings, and `snake_case` keys (see `schema_version`, `role_perspective`). Keep narrative order for lists—projects stay chronologically relevant rather than alphabetized—and group metadata keys before narrative text. URLs or repo references belong in clearly prefixed fields such as `git_like` and must stay quoted.

## Testing Guidelines
Treat `yamllint` plus the loader script as the minimum pre-commit bar and re-run them after resolving merge conflicts. If you add automation scripts later, co-locate pytest files under `tests/` and wire them into CI before relying on the output. Reviewers should reject any project entry that omits `decision_accountability`, metric blocks, or `management_scope` because downstream agents require them for filtering.

## Commit & Pull Request Guidelines
History favors short imperative messages with a type prefix (e.g., `chore: checkpoint current resume updates`). Follow the same `type[:scope]: summary` shape, reference the primary YAML file in the body, and include validation output snippets. PRs must describe the intent, list touched files, attach screenshots or rendered excerpts if content meaning changes, and tag stakeholders who consume that slice of data.

## Security & Data Handling
These files store personally identifiable information. Only store anonymized samples in `.design_docs/` when illustrating patterns, never push secrets or private URLs, and confirm redaction before sharing excerpts outside the repo. Use encrypted channels for certification evidence and rotate or remove any accidentally committed tokens immediately.
