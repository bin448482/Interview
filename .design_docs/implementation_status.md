## 已实施

- **数据精简**：`latest_resumes/projects_summary.yaml` 与 `latest_resumes/projects_summary_en.yaml` 仅保留 “MySixth 塔罗牌智能应用”“NGSE（Next Generation Sales Engine）”“Remedium (BI)” 三个项目，保持原有字段与指标，确保多角色共用统一基线。
- **角色过滤停用**：`resume_docs/role_filter.py` 只做角色合法性校验，返回完整项目/工作列表，保证任意角色都会渲染这三段经历。
- **Persona 定义**：`resume_docs/role_config.py` 为既有角色补充 `persona` 描述，并新增 `ai_product_designer`、`ai_engineer`，提供中英文视角提示供 Polisher 使用。
- **CLI 透传 Persona**：`resume_docs/cli.py` 在解析 `--role` 时加载 persona，并在调用 `LLMPolisher` 时透传，未知角色会直接报错。
- **LLM 润色增强**：`resume_docs/llm_polisher.py` 支持 persona-aware prompt，在中/英文模板中插入“角色视角提示”，并新增 `_get_persona_hint` 帮助 LLM 输出遵循不同职业叙事。

## 计划实施

1. **文档同步**：更新 README / CLAUDE / AGENTS 等指南，声明当前角色主要用于视角控制，项目列表固定三条，并提供 persona 配置说明。
2. **规范校验**：按仓库流程运行 `yamllint latest_resumes/*.yaml` 与 loader 脚本，记录输出供后续提交引用，必要时补充自动化脚本。
3. **多角色验收**：使用 CLI 分别以 `ai_product_designer`、`ai_engineer`、`product_manager` 等角色生成中英简历（带/不带 LLM polishing），对比输出截图或摘要，确认 persona 生效且 DOCX 渲染正常。
