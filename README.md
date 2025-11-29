# Resume Docs Generator / 履历文档生成器

Data-driven pipeline transforming YAML resume data into themeable DOCX documents with LLM-polished content using LangChain (OpenAI, Zhipu GLM, Ollama).

## Project Overview

Resume Docs Generator is a data-driven pipeline that transforms YAML resume data into:
- Themeable DOCX documents (Modern/Minimal layouts)
- LLM-polished content using LangChain (OpenAI, Zhipu GLM, Ollama)

All data flows from `latest_resumes/*.yaml` (the single source of truth) through a normalized view model to renderers. Role-aware filters decide which projects/fields stay visible for a target role before the LLM polisher and DOCX renderer run.

## Quickstart 快速开始
1. 创建并激活虚拟环境
   ```bash
   python3 -m venv .venv && source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. 运行解析 & 渲染（多模型 Prompt）
   ```bash
   python3 -m resume_docs.cli --template modern --locale zh-CN --include-contact --models gpt-4o glm-4
   ```
   - 生成的 DOCX 位于 `docs/output/zh-CN/modern/`
   - Prompt 文件写入同路径下的 `prompts/` 目录

> 提示：根目录可添加 `resume_docs/config.yaml` 配置文件，CLI 参数优先生效。

## Architecture & Data Flow

```
latest_resumes/*.yaml
    ↓
loader.py (验证 & 枚举检查)
    ↓
models.py (数据模型)
    ↓
role_filter.py (项目/字段级过滤)
    ↓
llm_polisher.py (可选 LLM 润色)
    ↓
docx_renderer.py (DOCX 渲染)
    ↓
docs/output/{locale}/{template}/
```

**Core Modules:**
- `loader.py`: Loads and validates YAML files
- `models.py`: Data model definitions
- `role_config.py` & `role_filter.py`: Role-based filtering logic (project + field visibility)
- `prompt_loader.py`: 构建角色感知 Prompt，定义六段式结构
- `llm_polisher.py`: LLM-based content polishing using LangChain
- `langchain_clients.py`: LangChain LLM clients (OpenAI, Zhipu, Ollama)
- `docx_renderer.py`: DOCX generation
- `cli.py`: CLI entry point
- `config.py` & `constants.py`: 默认配置、主题、语言映射

**Schema Contract:**
- `.design_docs/role_mapping_guidelines.md` defines all enums used in `projects_summary.yaml`
- Fields like `role_perspective`, `decision_accountability`, `responsibility_focus`, `impact_metrics`, `management_scope` must match this contract

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

## CLI Usage

### Key Flags
- `--template`：`modern`、`minimal` 等主题
- `--locale`：`zh-CN`（默认）、`en-US`，支持扩展
- `--include-contact`：在页眉展示电话/地址
- `--models`：生成多模型 Prompt 列表（如 `gpt-4o glm-4`）
- `--prompt-use-case`：`summary`（默认）等用途
- `--invoke-models`：渲染 Prompt 后立即调用模型（需已配置 API Key）
- `--skip-docx` / `--skip-prompts`：按需跳过阶段
- `--dry-run`：仅解析 YAML 不写文件

### Optional Config File
`resume_docs/config.yaml` 示例：
```yaml
template: modern
locale: zh-CN
include_contact: false
models:
  - gpt-4o
  - glm-4
output_dir: docs/output
```

CLI 参数 > `config.yaml` > 默认值。

## Runtime Configuration

为避免 `.env` 被外部环境覆盖，所有 LLM/API 凭证统一写入 `latest_resumes/runtime_config.yaml`：

1. 在 `latest_resumes/` 中复制 `runtime_config.example.yaml` 为 `runtime_config.yaml`（该文件已写入 `.gitignore`，不会被提交）。
2. 根据需要填写 `openai.api_key`、`openai.base_url`、`zhipu.api_key`、`ollama.host` 等字段；`env` 区块可映射其他环境变量（如 `MODEL_NAME`）。
3. CLI 与脚本会在启动时自动调用 `load_runtime_config()`，并用 YAML 中的值覆盖进程内的相关环境变量，确保调用链始终使用同一组凭证。

> 若 `runtime_config.yaml` 缺失，则保持现有环境变量不变，可用于 CI 或容器化场景。

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

### Prompt review for all roles
```bash
python scripts/generate_prompts.py  # 输出写入 artifacts/role_prompts_review.txt
```

### Available roles
- `data_development`: Data platform, lakehouse, AI data engineering
- `full_stack`: Full-stack development (frontend + backend)
- `ai_development`: AI/ML application development

### Available locales
- `zh-CN`: Chinese (default)
- `en-US`: English

### Output location
- DOCX: `docs/output/{locale}/{template}/resume-YYYYMMDD-HHMMSS.docx` (timestamped per run)

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

## Template & Prompt Extensions

- DOCX 主题：在 `templates/docx/` 中添加 Word 模板，并在 `resume_docs/constants.py` 的 `THEMES` 中注册。
- Prompt 模板：位于 `templates/prompts/{family}/{locale}/{use_case}.j2`，支持 `{{ resume | tojson }}` 注入；通过 `--prompt-use-case` 或配置切换。
- CLI 渲染既可生成 DOCX 也可单独输出 Prompt，可使用 `--skip-docx` 或 `--skip-prompts` 精确控制。
- `resume_docs/constants.py` 还存放 `SUPPORTED_LOCALES`，`docx_renderer.py` 需要在 `SECTION_LABELS` 中补齐新语言字段标题。

## Data Handling & Security

- `latest_resumes/` contains PII; never commit unredacted samples outside `.design_docs/`
- Use `--include-contact` flag to toggle phone/address in DOCX output
- Model API keys via environment variables (`.env` + `.venv` activation), never in repo
- `docs/output/` and `artifacts/` are git-ignored to prevent leaking generated content

## Repository Layout & Guidelines

- `latest_resumes/`: canonical YAML summaries (personal info, skills, projects, work). **Only folder expected to change** in feature branches.
- `.design_docs/`: feature specs + schema contracts (`*_design.md`, `*_plan.md`, `*_guidelines.md`).
- `.backup/`, `.snapshots/`: archived pulls for provenance—do not edit.
- `.venv/`, `.vscode/`: local tooling, keep untracked differences out of commits.
- `scripts/`: helper automation in `snake_case` with descriptive prefixes (`generate_*`, `validate_*`, `test_*`, `migrate_*`).

### Key Patterns
- Two-space indentation, double quotes for mixed-language strings.
- `snake_case` keys (`role_perspective`, `decision_accountability`, `management_scope`).
- Keep lists chronologically relevant rather than alphabetized; metadata keys precede narrative content.
- URLs/repos live in explicit quoted fields such as `git_like`.

### LLM Client Pattern
- Clients in `langchain_clients.py` inherit `LangChainLLMClient` and implement `invoke(prompt: str) -> str`.
- Environment variable precedence: `OPENAI_API_KEY`, `ZHIPU_API_KEY`, `OLLAMA_HOST` (default `http://localhost:11434`).
- Model auto-detection: `gpt*` → OpenAI, `glm*` → Zhipu, others fallback to Ollama/local clients.

## Testing & Validation

- Minimum bar: `yamllint latest_resumes/*.yaml` + loader smoke test (see snippet above)
- Role smoke tests: `.venv\Scripts\python -m resume_docs.cli --role <role> --dry-run`
- Prompt review: `python scripts/generate_prompts.py` → `artifacts/role_prompts_review.txt`
- Optional regression: add pytest suites under `tests/` and wire them into CI before depending on output
- Verify GitHub link preservation whenever LLM polishing is enabled

## Role-Based Filtering & Prompts

- Roles: `data_development`, `full_stack`, `ai_development`, `product_manager`, `ai_product_designer`, `ai_engineer`
- `role_config.py` describes which projects to include/exclude and per-field visibility via `field_visibility`
- `prompt_loader.py` builds role-specific six-part structures（背景、问题/挑战、方案、成果等）供 `llm_polisher.py` 使用
- Add a role by updating `role_config.py` (filters + visibility) and `prompt_loader.py` (prompt blocks)

## Git Workflow

- Commit messages: `type[:scope]: summary` (e.g., `chore: checkpoint current resume updates`)
- Reference primary YAML file in body, include validation output snippets
- PRs must describe intent, list touched files, attach rendered excerpts if content meaning changes
