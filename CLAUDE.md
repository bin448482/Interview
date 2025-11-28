# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume Docs Generator is a data-driven pipeline that transforms YAML resume data into:
- Themeable DOCX documents (Modern/Minimal layouts)
- LLM-polished content using LangChain (OpenAI, Zhipu GLM, Ollama)

The system filters resumes by role, optionally polishes project descriptions using LLMs, and generates DOCX documents. All data flows from `latest_resumes/*.yaml` (the single source of truth) through a normalized view model to renderers.

## Architecture

See `resume_docs/claude.md` for detailed module documentation and data flow diagram.

**Quick Reference:**
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
- Reviewers reject entries missing `decision_accountability`, metric blocks, or `management_scope`

## Common Commands

**Setup:**
```bash
python3 -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Validate YAML before any changes:**
```bash
yamllint latest_resumes/*.yaml
python3 - <<'PY'
from resume_docs import loader
loader.load_resume_data()
print('Resume YAML OK')
PY
```

**Dry-run validation:**
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --dry-run
```

**Generate DOCX without LLM polishing:**
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --skip-polish
```

**Generate DOCX with LLM polishing (requires .env configuration):**
```bash
# Zhipu GLM
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model glm-4

# OpenAI
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model gpt-4o

# Ollama (local)
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model ollama
```

**Available roles:**
- `data_development`: Data platform, lakehouse, AI data engineering
- `full_stack`: Full-stack development (frontend + backend)
- `ai_development`: AI/ML application development

**Available locales:**
- `zh-CN`: Chinese (default)
- `en-US`: English

**Output location:**
- DOCX: `docs/output/{locale}/{template}/resume-YYYYMMDD-HHMMSS.docx`

## Multi-Locale Support (English Resume Generation)

The system supports generating resumes in multiple languages via the `--locale` flag.

### English Resume Generation

**Generate English resume:**
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale en-US --role data_development --include-contact --skip-polish
```

**Generate English resume with LLM polishing:**
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale en-US --role data_development --include-contact --model glm-4-flash
```

**Output location:**
- English DOCX: `docs/output/en-US/modern/resume-YYYYMMDD-HHMMSS.docx`

### Data Files Structure

The system uses locale-aware file loading:
- **Chinese (default):** `latest_resumes/personal_info_summary.yaml`, `skills_summary.yaml`, `projects_summary.yaml`, `work_experience_summary.yaml`
- **English:** `latest_resumes/personal_info_summary_en.yaml`, `skills_summary_en.yaml`, `projects_summary_en.yaml`, `work_experience_summary_en.yaml`

When `--locale en-US` is specified, the loader automatically looks for `*_en.yaml` files. If not found, it falls back to Chinese files.

### Implementation Details

**Locale-aware loading in `loader.py`:**
```python
def load_resume_data(base_dir: Path | None = None, locale: str = "zh-CN") -> models.ResumeDocument:
    base_path = Path(base_dir or constants.LATEST_RESUMES_DIR)
    suffix = "_en" if locale == "en-US" else ""
    personal_file = f"personal_info_summary{suffix}.yaml"
    # ... load files with locale-specific suffix
```

**CLI integration in `cli.py`:**
```python
resume_data = loader.load_resume_data(locale=args.locale)
```

### Adding New Locales

To add support for a new locale (e.g., `es-ES` for Spanish):

1. Create Spanish YAML files in `latest_resumes/`:
   - `personal_info_summary_es.yaml`
   - `skills_summary_es.yaml`
   - `projects_summary_es.yaml`
   - `work_experience_summary_es.yaml`

2. Add Spanish translations to `SECTION_LABELS` in `docx_renderer.py`:
   ```python
   "es-ES": {
       "skills": "Habilidades",
       "projects": "Proyectos",
       "work": "Experiencia",
       # ... other labels
   }
   ```

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

**Template Extension:**
- DOCX themes: Add `.docx` files to `templates/docx/`, update `constants.py` THEMES dict

**LLM Client Pattern:**
- LangChain clients in `langchain_clients.py` inherit from `LangChainLLMClient`
- Implement `invoke(prompt: str) -> str` method
- Environment variable precedence: `OPENAI_API_KEY`, `ZHIPU_API_KEY`, `OLLAMA_HOST` (defaults to `http://localhost:11434`)
- Automatic model detection based on model name (gpt* → OpenAI, glm* → Zhipu, etc.)

## Testing & Validation

- Pre-commit: `yamllint latest_resumes/*.yaml` + loader smoke test
- Unit tests: pytest under `tests/` (if added)
- End-to-end: `--dry-run` generates fixtures for manual review
- CI target: `make validate-resume-docs` (chains lint → unit → dry-run)

### Testing GitHub Link Preservation in LLM Polishing

**Requirement:** Ensure GitHub links in `project_overview` are preserved during LLM polishing.

**Setup (.env file):**
```env
ZHIPU_API_KEY=your-api-key-here
```

**Test Command (Zhipu GLM-4):**
```bash
.venv\Scripts\python -m resume_docs.cli --template modern --locale zh-CN --role data_development --include-contact --model glm-4
```

**Verification Steps:**
1. Check the generated DOCX files (timestamped): `docs/output/zh-CN/modern/resume-*.docx`
2. Open it in Word/Google Docs
3. Find the "MySixth 塔罗牌智能应用" project section
4. Verify that the project overview contains both:
   - LLM-polished content
   - GitHub link: `GitHub: https://github.com/bin448482/tarotAI`

**Expected Output Format:**
```
MySixth 塔罗牌智能应用 | Zoetis / 个人独立开发者 (2025.10 - 至今)
独立开发者 | hybrid | 消费级塔罗占卜 / AI内容运营
[LLM-polished project description spanning multiple sentences...]
GitHub: https://github.com/bin448482/tarotAI
```

**Automated Test (no API call needed):**
```bash
python -c "
from resume_docs import llm_polisher

polisher = llm_polisher.LLMPolisher()
test_text = 'TarotAI application. GitHub: https://github.com/bin448482/tarotAI'
link = polisher._extract_github_link(test_text)
assert link == 'https://github.com/bin448482/tarotAI', f'Expected GitHub link, got {link}'
print('✓ GitHub link extraction test passed')
"
```

**Key Implementation Details:**
- `llm_polisher.py`: `_polish_single_project()` method preserves GitHub links by:
  1. Checking if original `project_overview` contains "github.com"
  2. Checking if LLM output already contains "github.com" (avoid duplication)
  3. Extracting GitHub URL using regex pattern: `https://github\.com/[\w\-]+/[\w\-]+`
  4. Appending preserved link to polished content if needed

## Role-Based Filtering

See `resume_docs/ROLE_FILTERS.md` for current role definitions and filtering rules.

**Available roles:**
- `data_development`: Data platform, lakehouse, AI data engineering
- `full_stack`: Full-stack development (frontend + backend)
- `ai_development`: AI/ML application development

To add new roles, edit `resume_docs/role_config.py` and add entry to `ROLE_FILTERS` dict with `include_projects`, `exclude_projects`, and `sort_by` keys.

## Git Workflow

- Commit messages: `type[:scope]: summary` (e.g., `chore: checkpoint current resume updates`)
- Reference primary YAML file in body, include validation output snippets
- PRs must describe intent, list touched files, attach rendered excerpts if content meaning changes
- Tag stakeholders consuming that data slice

## Generative AI PM Resume Refresh (2025-11-28)

### TODO & Status (source: `.design_docs/generative_ai_pm_resume_design.md`)
1. **Reframe CN 项目**（MySixth/NGSE/AI增强投递系统）以突出 Generative AI PM 叙事、指标、治理 —— ✅ 已加入北极星指标、PromptOps、商业化与治理字段。
2. **镜像 EN 项目数据**，保持指标与治理语言完全对齐 —— ✅ 使用人工翻译 + 术语同步完成。
3. **扩展 work_experience role_responsibilities**，补充 Generative AI 产品经理职责（实验待办、风险审查、Responsible AI）—— ✅。
4. **刷新 skills_summary / skills_summary_en**，新增 “Generative AI 产品策略与指标” 与 “多代理编排与提示治理” 类别 —— ✅。
5. **验证 + 记录**：运行 `yamllint latest_resumes/*.yaml`（仍有既有行宽/缩进告警，需结构性改造才能清零）以及 Python safe-load —— ✅。

### Notes for Future Contributors
- 所有更新限定在 `latest_resumes/*.yaml` + 文档本身，符合 schema_version 1.1。新增的治理 artifact（`prompt_playbook`, `cost_dashboard`, `ai_policy`, `experiment_log` 等）均已与 `.design_docs/role_mapping_guidelines.md` 校对。
- 角色职责与技能条目已偏向产品指标、PromptOps、商业化语言，便于 downstream 渲染区分 “Generative AI PM” 与 “AI 开发者”。
- 若继续迭代，优先补充 `.yamllint` 配置或脚本化格式化，避免固定的行宽/缩进告警干扰验证记录。

### Validation Commands (Nov 28, 2025)
- `source .venv/bin/activate && yamllint latest_resumes/*.yaml` → 仍报历史性的 document-start/line-length/缩进入口；本次更改未新增独立错误。
- `source .venv/bin/activate && python - <<'PY' ...`（safe-load 脚本）→ `YAML loads ✓`。

## Product Manager 简历生成实验 (2025-11-28)

**TODO**
1. 在 `resume_docs/role_config.py` 添加 `product_manager` 角色过滤规则，使其优先选择包含商业化/治理职责的项目。
2. 更新 `resume_docs/ROLE_FILTERS.md` 文档，向协作者说明新的过滤逻辑与适用场景。
3. 运行 CLI 生成一次 `Generative AI 产品经理` 简历，确认文档可以正确落地到 `docs/output/`。

**Implementation Notes**
- `resume_docs/role_config.py`: 通过 `responsibility_focus`、`decision_accountability` 与 `role_title` 模式匹配筛出 Generative AI PM 叙事，排除带“测试/运维”标签的条目，仍沿用 `relevance_then_time` 排序。
- `resume_docs/ROLE_FILTERS.md`: 新增章节解释筛选条件，提醒 reviewer 该角色偏重商业指标与 PromptOps/治理描述。

**Validation / Command Log**
- `.venv/bin/python -m resume_docs.cli --template modern --locale zh-CN --role product_manager --include-contact --skip-polish`
  - 输出：`docs/output/zh-CN/modern/resume-20251128-193537.docx`
- `.venv/bin/python -m resume_docs.cli --template modern --locale zh-CN --role product_manager --include-contact --model gpt-5`
  - 结果：LLM polishing 调用失败（401 无效令牌，request id 2025112819395536795863232866264）。待刷新 OPENAI_API_KEY 或代理配置后重试。
