# Resume Docs Generator / 履历文档生成器

Data-driven pipeline transforming YAML resume data into themeable DOCX documents with LLM-polished content using LangChain (OpenAI, Zhipu GLM, Ollama).

## Project Overview

Resume Docs Generator is a data-driven pipeline that transforms YAML resume data into:
- Themeable DOCX documents (Modern/Minimal layouts)
- LLM-polished content using LangChain (OpenAI, Zhipu GLM, Ollama)

The system filters resumes by role, optionally polishes project descriptions using LLMs, and generates DOCX documents. All data flows from `latest_resumes/*.yaml` (the single source of truth) through a normalized view model to renderers.

## Architecture

**Core Modules:**
- `loader.py`: Loads and validates YAML files
- `models.py`: Data model definitions
- `role_config.py` & `role_filter.py`: Role-based filtering logic
- `llm_polisher.py`: LLM-based content polishing using LangChain
- `langchain_clients.py`: LangChain LLM clients (OpenAI, Zhipu, Ollama)
- `docx_renderer.py`: DOCX generation
- `cli.py`: CLI entry point

**Schema Contract:**
- `.design_docs/role_mapping_guidelines.md` defines all enums used in `projects_summary.yaml`
- Fields like `role_perspective`, `decision_accountability`, `responsibility_focus`, `impact_metrics` must match this contract

## Tech Stack

- Language: Python 3.12
- Framework: argparse CLI, python-docx, LangChain, Jinja2
- Data: YAML files (`latest_resumes/`)
- LLM Support: OpenAI, Zhipu GLM, Ollama

## Installation & Setup

### Requirements
- Python >= 3.10
- Optional: Docker (for deployment)

### Setup
```bash
git clone <repo-url>
cd interview
python3 -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Validate YAML
```bash
yamllint latest_resumes/*.yaml
python3 - <<'PY'
from resume_docs import loader
loader.load_resume_data()
print('Resume YAML OK')
PY
```

## Common Commands

### Generate DOCX without LLM polishing
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --skip-polish
```

### Generate DOCX with LLM polishing
```bash
# Zhipu GLM
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model glm-4

# OpenAI
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model gpt-4o

# Ollama (local)
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model ollama
```

### Dry-run validation
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --dry-run
```

### Available roles
- `data_development`: Data platform, lakehouse, AI data engineering
- `full_stack`: Full-stack development (frontend + backend)
- `ai_development`: AI/ML application development

### Available locales
- `zh-CN`: Chinese (default)
- `en-US`: English

### Output location
- DOCX: `docs/output/{locale}/{template}/resume.docx`

## Multi-Locale Support

The system supports generating resumes in multiple languages via the `--locale` flag.

### English Resume Generation
```bash
# Without LLM polishing
.venv\Scripts\python -m resume_docs.cli --template modern --locale en-US --role data_development --include-contact --skip-polish

# With LLM polishing
.venv\Scripts\python -m resume_docs.cli --template modern --locale en-US --role data_development --include-contact --model glm-4-flash
```

### Data Files Structure
- **Chinese (default):** `latest_resumes/personal_info_summary.yaml`, `skills_summary.yaml`, `projects_summary.yaml`, `work_experience_summary.yaml`
- **English:** `latest_resumes/personal_info_summary_en.yaml`, `skills_summary_en.yaml`, `projects_summary_en.yaml`, `work_experience_summary_en.yaml`

When `--locale en-US` is specified, the loader automatically looks for `*_en.yaml` files. If not found, it falls back to Chinese files.

### Adding New Locales

To add support for a new locale (e.g., `es-ES` for Spanish):

1. Create locale-specific YAML files in `latest_resumes/`:
   - `personal_info_summary_es.yaml`
   - `skills_summary_es.yaml`
   - `projects_summary_es.yaml`
   - `work_experience_summary_es.yaml`

2. Add translations to `SECTION_LABELS` in `docx_renderer.py`

3. Update `constants.py` to include the new locale in `SUPPORTED_LOCALES`

4. Use the new locale:
   ```bash
   .venv\Scripts\python -m resume_docs.cli --template modern --locale es-ES --role data_development --include-contact
   ```

## Data Handling & Security

- `latest_resumes/` contains PII; never commit unredacted samples outside `.design_docs/`
- Use `--include-contact` flag to toggle phone/address in DOCX output
- Model API keys via environment variables (`.env` + `.venv` activation), never in repo
- `docs/output/` and `artifacts/` are git-ignored to prevent leaking generated content

## Key Patterns

**YAML Structure:**
- Two-space indentation, double quotes for mixed-language strings
- `snake_case` keys (e.g., `role_perspective`, `decision_accountability`)
- Preserve narrative order (chronological for projects/work, not alphabetized)
- Group metadata keys before narrative text

**LLM Client Pattern:**
- LangChain clients in `langchain_clients.py` inherit from `LangChainLLMClient`
- Implement `invoke(prompt: str) -> str` method
- Environment variable precedence: `OPENAI_API_KEY`, `ZHIPU_API_KEY`, `OLLAMA_HOST` (defaults to `http://localhost:11434`)
- Automatic model detection based on model name (gpt* → OpenAI, glm* → Zhipu, etc.)

## Testing & Validation

- Pre-commit: `yamllint latest_resumes/*.yaml` + loader smoke test
- End-to-end: `--dry-run` generates fixtures for manual review
- GitHub link preservation: Verified during LLM polishing to ensure links in `project_overview` are preserved

## Role-Based Filtering

**Available roles:**
- `data_development`: Data platform, lakehouse, AI data engineering
- `full_stack`: Full-stack development (frontend + backend)
- `ai_development`: AI/ML application development

To add new roles, edit `resume_docs/role_config.py` and add entry to `ROLE_FILTERS` dict with `include_projects`, `exclude_projects`, and `sort_by` keys.

## Git Workflow

- Commit messages: `type[:scope]: summary` (e.g., `chore: checkpoint current resume updates`)
- Reference primary YAML file in body, include validation output snippets
- PRs must describe intent, list touched files, attach rendered excerpts if content meaning changes
