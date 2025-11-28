# resume_docs 模块

核心简历生成管道，将 YAML 数据转换为 DOCX 文档和 LLM 提示。

## 模块结构

**数据流：**
```
latest_resumes/*.yaml
    ↓
loader.py (验证 YAML)
    ↓
models.py (数据模型)
    ↓
role_filter.py (职位过滤)
    ↓
llm_polisher.py (LLM 润色)
    ↓
docx_renderer.py (生成 DOCX)
    ↓
docs/output/{locale}/{template}/
```

## 核心模块

| 模块 | 功能 |
|------|------|
| `loader.py` | 加载和验证 YAML 文件，确保枚举合规 |
| `models.py` | 数据类定义：PersonalInfo、Project、WorkExperience 等 |
| `role_config.py` | 职位过滤规则定义 |
| `role_filter.py` | 实现职位过滤和排序逻辑 |
| `llm_polisher.py` | 使用 LLM 润色项目描述 |
| `langchain_clients.py` | LangChain LLM 客户端（OpenAI、Zhipu、Ollama） |
| `docx_renderer.py` | 应用 DOCX 模板，注入排版和指标 |
| `cli.py` | Argparse CLI 入口，支持职位过滤和 LLM 润色 |
| `config.py` | 配置合并（CLI 参数 > config.yaml > 默认值） |
| `constants.py` | 主题定义、地区映射、输出路径 |

## 职位过滤

支持基于职位的字段级内容过滤。每个角色根据其视角看到不同的 Project 字段子集。

**过滤机制：**
- `role_config.py` 中每个角色定义 `field_visibility` 字典，指定哪些字段对该角色可见
- `role_filter.py` 在渲染前应用字段过滤，隐藏字段设为 None 或空列表
- 项目列表保持不变，只有字段级别的可见性改变

**可用职位及其字段焦点：**
- `data_development` - 数据平台视角：governance_artifacts、decision_accountability、impact_metrics、tech_stack
- `full_stack` - 全栈工程视角：responsibility_focus、architecture_or_solution、tech_stack、process_or_methodology
- `ai_development` - AI 工程视角：ai_component_flag、architecture_or_solution、tech_stack、governance_artifacts
- `product_manager` - 产品经理视角：decision_accountability、responsibility_focus、impact_metrics、governance_artifacts
- `ai_product_designer` - 产品设计视角：impact_metrics、deliverables_or_features、metrics_or_impact
- `ai_engineer` - AI 工程师视角：ai_component_flag、architecture_or_solution、tech_stack、governance_artifacts

**使用示例：**
```bash
python3 -m resume_docs.cli --role data_development --template modern --locale zh-CN
python3 -m resume_docs.cli --role product_manager --template modern --locale zh-CN
```

## 常用命令

**注意：**
- 所有命令需要使用虚拟环境中的 Python。在 Windows 上使用 `.venv\Scripts\python`，在 macOS/Linux 上使用 `.venv/bin/python`
- LLM 润色需要在 `.env` 文件中设置 API Key：
  ```
  OPENAI_API_KEY=sk-xxx...
  ZHIPU_API_KEY=xxx...
  OLLAMA_HOST=http://localhost:11434
  ```

**验证 YAML：**
```bash
yamllint latest_resumes/*.yaml
.venv\Scripts\python -m resume_docs.cli --dry-run --role data_development
```

**生成 DOCX（无 LLM 润色）：**
```bash
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --include-contact --skip-polish
```

**生成 DOCX（使用 LLM 润色，需要 .env 配置）：**
```bash
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --include-contact --model glm-4
```

**使用不同 LLM 模型（需要 .env 配置）：**
```bash
# OpenAI
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --model gpt-4o

# Zhipu GLM
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --model glm-4

# Ollama (本地)
.venv\Scripts\python -m resume_docs.cli --role data_development --template modern --locale zh-CN --model ollama
```

## 关键设计

- **单一数据源：** `latest_resumes/*.yaml` 是唯一真实来源
- **字段级过滤：** 按职位动态过滤 Project 字段，保持项目列表不变
  - 每个角色在 `role_config.py` 中定义 `field_visibility` 字典
  - `role_filter.py` 在渲染前应用过滤，隐藏字段设为 None 或空列表
  - Renderer 和 Polisher 自动适应可见字段
- **LLM 润色：** 可选使用 LLM 润色项目描述，支持多语言和角色视角
- **模板驱动：** DOCX 基于模板生成
- **环境变量：** API 密钥通过环境变量管理，不提交到仓库
- **语言感知：** 根据 locale 参数自动选择润色语言
