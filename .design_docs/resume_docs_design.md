# Resume Docs Generation Design

## 1. Background & Goals
- `latest_resumes/*.yaml` is the single source of truth and must stay schema-compliant with `.design_docs/role_mapping_guidelines.md`.
- We need a pipeline that renders a visually appealing DOCX resume and produces prompt text tailored to multiple LLM providers, without mutating the YAML inputs.
- Outputs must be reproducible offline (template-based rendering) and optionally integrate online model calls when credentials exist.

Success will be measured by:
1. Generating DOCX + prompt artifacts in under 30s on a laptop without network calls.
2. Passing `yamllint latest_resumes/*.yaml` plus the loader smoke test before rendering.
3. Supporting at least two visual themes and three model families via configuration.

## 2. Scope & Non-Goals
In scope:
- CLI/automation entry point to orchestrate loading, rendering, and prompt generation.
- Themeable DOCX templates (colors, fonts, layout) stored under `templates/docx/`.
- Prompt templates per model family + locale under `templates/prompts/`.
- Optional model invocation with caching for dry-run/offline use.

Out of scope for this iteration:
- Web UI or collaborative editor.
- Persisting generated artifacts in git (`docs/output/` will be ignored).
- Editing or reformatting the YAML data.

## 3. System Overview
```
latest_resumes/*.yaml
        │
 resume_loader  ──>  resume_view_model  ──┬── docx_renderer ──> DOCX artifacts
        │                                 └── prompt_orchestrator ──> prompt files / model calls
```
Key modules (Python 3.10):
- `resume_loader`: combines YAML files, ensures ordering, validates enums defined in `role_mapping_guidelines.md`.
- `resume_view_model`: normalized dataclasses/Pydantic models for personal info, skills, projects, work experience.
- `docx_renderer`: applies templates via `python-docx`, injects typography, sections, metrics, bilingual labels.
- `prompt_orchestrator`: renders Jinja2 prompt templates and optionally invokes model clients.
- `model_clients`: adapters for OpenAI-compatible, Zhipu GLM, and Ollama/local endpoints with shared retry/backoff.
- `cli.py`: Typer-based CLI controlling themes, locale, dry-run, and model selection.

## 4. Templates & Presentation Strategy
### DOCX Themes
- **Modern**: deep blue + gray palette, Inter + Source Han Sans fonts, two-column layout (left sidebar for contact/skills, right for narrative sections).
- **Minimal**: monochrome palette, increased whitespace, single-column stacked sections.

Template resources: `templates/docx/modern.docx`, `templates/docx/minimal.docx`. Each template documents style name mappings (Heading 1→name block, Heading 2→section headers, List Bullet→responsibilities, Custom Style→metrics chips).

Rendering rules:
- Respect YAML order for projects/work entries to preserve narrative chronology.
- Group metadata (role, timeframe, impact metrics) before descriptive bullets.
- Highlight metrics via inline labels (Business/Technical/Operational) and bold key figures.
- Provide toggle for including/redacting sensitive contact data.

### Prompt Templates
- Directory structure: `templates/prompts/{model_family}/{locale}/{use_case}.j2` (e.g., `gpt/zh-CN/summary.j2`).
- Template variables: persona, tone, formatting instructions, YAML excerpt, safety tags.
- Output artifacts: Markdown preview (`docs/output/prompts/{model}.md`) and JSON descriptors with metadata (model_id, locale, max_tokens).

## 5. Model Strategy
Supported families:
1. **OpenAI-compatible** (`gpt-4o`, `o4-mini`): uses shared OpenAI client.
2. **Zhipu GLM** (`glm-4`, `glm-4-plus`): REST client with signature + env var `ZHIPU_API_KEY`.
3. **Local/Ollama** (`qwen2`, `mixtral` or any `ollama list` model): HTTP localhost adapter.

`prompt_orchestrator` workflow per model:
- Render prompt text via Jinja2.
- If `--invoke` set and credentials exist, send to client, store response plus prompt hash under `artifacts/model_runs/{timestamp}.json`.
- Without invoke, only emit prompt text for manual use.

## 6. CLI & Configuration
- Entry command: `python -m resume_docs.cli --template modern --locale zh-CN --models gpt-4o glm-4 --include-contact`.
- Configuration precedence: CLI args > `resume_docs/config.yaml` > defaults.
- Generated outputs under `docs/output/{locale}/{template}/` (ignored by git via `.gitignore`).
- Cache key = SHA256(latest_resumes contents + template + locale + prompt config); cache metadata stored in `artifacts/cache_index.json`.

## 7. Validation & Testing
- Pre-flight: `yamllint latest_resumes/*.yaml` and loader smoke test (existing snippet in AGENTS.md).
- Unit tests (pytest):
  - Loader schema + ordering.
  - Prompt render snapshots (use `syrupy`).
  - DOCX verification by re-reading with `python-docx` to assert presence of headers/metrics.
- End-to-end dry run: `python -m resume_docs.cli --dry-run --models gpt-4o --template modern` generates fixtures for review.
- CI target `make validate-resume-docs` chaining lint → unit → dry-run.

## 8. Security & Operations
- Treat PII carefully: redact contact info by default; require `--include-contact` for full details.
- Environment secrets via `.env` + `.venv` activation, never stored in repo.
- Handle missing templates or failed model calls with clear error messages and fallback to dry-run textual prompts.
- `docs/output/` and `artifacts/` added to `.gitignore` to avoid leaking generated content.

## 9. Milestones
1. Data modeling + loader (0.5 day).
2. DOCX renderer MVP with Modern theme (1 day).
3. Prompt templates + multi-model adapters (1 day).
4. CLI integration + testing harness (0.5 day).
5. Visual polish + documentation updates (0.5 day).

Next steps: review this document, adjust requirements if needed, then proceed with module scaffolding.
