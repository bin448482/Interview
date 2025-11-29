# Project-Level Role-Aware Prompting Design

## 1. 背景与问题

当前行为：

- CLI 使用 `--role`（如 `data_development`）驱动三个层面：
  - `RoleFilter`：按角色过滤、排序项目；
  - 字段可见性：同一项目在不同角色下展示字段不同；
  - `LLMPolisher`：用对应角色的 prompt 改写项目的 `project_overview`。
- `PromptLoader` 读取 `latest_resumes/prompt_config.yaml` 中 `base_templates` 与 `roles` 配置，构建“角色感知 + 结构化输出”的长 prompt。
- 所有被过滤进来的项目，在有 `--role` 且有 `--model` 时，统一用同一个 role 的 prompt 改写。

暴露的问题：

- 有些项目天然是“数据平台视角”（如 NGSE / Remedium），适合 `data_development`；
- 有些项目天然更像“AI 应用 / 全栈”（如 TarotAI），用 `data_development` 强行改写时，模型会：
  - 过度补写“湖仓一体 + Kafka + Iceberg + ClickHouse + Great Expectations”等从未在原文出现的技术；
  - 把一个轻量级 AI 产品写成企业级数据平台，造成明显“专业型幻觉”。

核心矛盾：  
**简历整体角色视角需要一致，但单个项目更适合用不同角色视角去改写。**

---

## 2. 目标与非目标

### 2.1 目标

1. 支持“项目级角色选择”：
   - 每个项目可以声明自己“适配的 LLM 角色视角”（如 `ai_development` / `full_stack`）；
   - LLM 改写时按项目选择合适的角色 prompt，而不是所有项目强行用 global role。

2. 保持“简历整体角色视角”不变：
   - CLI `--role` 继续控制：项目过滤/排序 + 字段可见性；
   - 仅在 LLM 改写阶段引入“每个项目自己的 role 解析逻辑”。

3. 提供显式“防幻觉约束”：
   - 在 prompt 层明确禁止引入原文未出现的关键技术名/产品名/数据基础设施；
   - 特别是 `data_development` 这类“容易写爽”的角色。

4. 兼容现有数据与命令：
   - 不改 CLI 参数；
   - 旧的 YAML（没有新字段）仍然能跑，不改 schema 行为。

### 2.2 非目标

- 不改 `RoleFilter` 的 include/exclude 规则本身；
- 不做项目级“是否启用 LLM polishing”的开关（仍由 `--skip-polish` 全局控制）；
- 不在本轮调整 DOCX 模板或 resume 展示结构。

---

## 3. 方案概览

**核心改动点：**

1. YAML schema 增加项目级 LLM 角色 hint：
   - `llm_primary_role: str | null`
   - `llm_secondary_roles: list[str]`

2. 新增“项目级有效 role 解析算法”（`resolve_polish_role`）：
   - 输入：CLI `global_role` + `Project`；
   - 输出：该项目在 LLM 改写时用的 `effective_role`（或 `None`）。

3. Prompt 配置新增“防幻觉约束”文案：
   - 全局 `base_templates.*.hallucination_guard`；
   - 角色级（如 `roles.data_development.hallucination_guard`）可覆盖全局。

4. `LLMPolisher` 调整：
   - 不再直接使用 CLI 的 `role`；
   - 对每个项目调用 `resolve_polish_role`，决定是否使用角色感知 prompt；
   - 无合适角色时退回旧的基础 polish prompt。

---

## 4. 数据模型与配置变更

### 4.1 YAML：项目级 LLM 角色字段

在 `latest_resumes/projects_summary.yaml` / `_en.yaml` 每个项目下增加可选字段：

```yaml
projects:
  - project_name: "MySixth 塔罗牌智能应用"
    # ... 现有字段 ...
    llm_primary_role: "ai_development"
    llm_secondary_roles:
      - "full_stack"
      - "data_development"
```

```yaml
  - project_name: "Zoetis NGSE 中国湖仓项目"
    # ... 现有字段 ...
    llm_primary_role: "data_development"
    llm_secondary_roles:
      - "ai_development"
```

```yaml
  - project_name: "Remedium (BI)"
    # ... 现有字段 ...
    llm_primary_role: "data_development"
    llm_secondary_roles:
      - "full_stack"
```

语义约定：

- `llm_primary_role`：
  - 项目“最推荐”的 LLM 改写视角；
  - 必须是 `ROLE_FILTERS` 的 key 之一（如 `data_development`, `ai_development`, `full_stack`, `product_manager`, `ai_product_designer`, `ai_engineer`）。
- `llm_secondary_roles`：
  - “可接受的备选视角”，在整体角色与项目视角冲突时使用；
  - 同样必须是 `ROLE_FILTERS` 的 key 集。

约束：

- 字段可缺省：旧项目没有这两个字段也不报错；
- 对 TarotAI 这类项目，推荐配置为 `llm_primary_role = ai_development`；
- 对 NGSE/Remedium 等项目，推荐 `llm_primary_role = data_development`。

### 4.2 models / loader 层调整

在 `resume_docs/models.py` 的 `Project` dataclass 增加字段（示意）：

```python
@dataclass
class Project:
    # ... 现有字段 ...
    llm_primary_role: Optional[str] = None
    llm_secondary_roles: List[str] = field(default_factory=list)
```

`loader._parse_projects()` 中：

- 从 `raw` 读取这两个字段：
  - `llm_primary_role = raw.get("llm_primary_role") or None`
  - `llm_secondary_roles = list(raw.get("llm_secondary_roles", []) or [])`

`_validate_project_enums()` 中新增校验：

- 定义允许的 role 集合：`ALLOWED_ROLES = set(ROLE_FILTERS.keys())`；
- 若 `llm_primary_role` 非空且不在 `ALLOWED_ROLES`，抛出 `ValueError`，指明项目名；
- 若 `llm_secondary_roles` 中存在不在 `ALLOWED_ROLES` 的元素，同样抛错。

### 4.3 设计文档更新

在 `.design_docs/role_mapping_guidelines.md` 中新增一节：

- 描述：
  - `llm_primary_role` / `llm_secondary_roles` 的用途和合法取值；
  - 标注 Tarot / NGSE / Remedium 这类典型项目的推荐配置；
  - 明确这两个字段只影响 LLM 改写，不影响项目过滤或字段可见性。

---

## 5. 项目级角色解析算法

新增一个 helper（可以放 `resume_docs/llm_role_resolver.py` 或 `llm_polisher.py` 中）：

```python
from typing import Optional
from .role_config import ROLE_FILTERS
from .models import Project

def resolve_polish_role(global_role: Optional[str], project: Project) -> Optional[str]:
    """
    根据 CLI 全局角色和项目上的 llm_XXX 配置，决定该项目在 LLM 改写时使用的角色。
    返回值：
        - 有效角色名（传给 PromptLoader.build_role_aware_prompt）
        - 或 None（表示使用无角色的基础 polish prompt）
    """
    allowed_roles = set(ROLE_FILTERS.keys())

    # 1. 规范化输入
    if global_role not in allowed_roles:
        global_role = None

    primary = project.llm_primary_role if project.llm_primary_role in allowed_roles else None
    secondary = [r for r in (project.llm_secondary_roles or []) if r in allowed_roles]

    # 2. 优先使用“整体视角 + 项目声明兼容”的组合
    if global_role:
        if primary == global_role:
            return global_role
        if global_role in secondary:
            return global_role

    # 3. 退回项目自己的 primary 视角
    if primary:
        return primary

    # 4. 再退回整体角色（如果有），保证简历整体语气尽量一致
    if global_role:
        return global_role

    # 5. 无任何 hint，禁用角色感知，使用基础 prompt
    return None
```

行为举例：

- CLI `--role data_development`：
  - Tarot：`primary = ai_development`，`secondary` 包含或不包含 `data_development`：
    - 若包含：`effective_role = data_development`（整体视角优先）；
    - 若不包含：`effective_role = ai_development`（项目 primary）。
  - NGSE：`primary = data_development` ⇒ `effective_role = data_development`。
- CLI `--role ai_development`：
  - Tarot：`primary = ai_development` ⇒ `effective_role = ai_development`；
  - NGSE：`primary = data_development`，若 `secondary` 包含 `ai_development` ⇒ `effective_role = ai_development`，否则用 `data_development`。

这套策略满足两点：

1. “如果有合适的角色就用合适的角色来解析”（项目级视角）；
2. “如果没有，就用这个项目本来定位的角色来解析”（primary）；
3. 整体视角仍然优先（只要项目声明支持该视角）。

---

## 6. LLMPolisher 与 PromptLoader 调整

### 6.1 LLMPolisher：使用项目级 effective_role

当前逻辑（简化）：

```python
if role:
    prompt_loader = PromptLoader()
    prompt = prompt_loader.build_role_aware_prompt(
        project.project_overview, language, role, persona_hint
    )
else:
    prompt = self._build_polish_prompt(
        project.project_overview, language, persona_hint
    )
```

改为：

```python
from .llm_role_resolver import resolve_polish_role

effective_role = resolve_polish_role(role, project) if role else None

if effective_role:
    prompt_loader = PromptLoader()
    prompt = prompt_loader.build_role_aware_prompt(
        project.project_overview, language, effective_role, persona_hint
    )
else:
    # 无合适角色，回退到基础 polish prompt，降低“强行带角色”的风险
    prompt = self._build_polish_prompt(
        project.project_overview, language, persona_hint
    )
```

说明：

- `role` 仍然来自 CLI `--role`；
- `persona_hint` 仍使用 `ROLE_FILTERS[role]["persona"]`，目前暂不按项目覆盖；
- 对 Tarot 这类项目，当整体 role 与项目 primary 不兼容时，会自动选择 `ai_development` 等更合适的视角。

### 6.2 PromptLoader：新增防幻觉约束

在 `latest_resumes/prompt_config.yaml` 中扩展：

```yaml
base_templates:
  zh:
    # ... 现有字段 ...
    hallucination_guard: "严禁引入原文中未出现的技术栈名称、具体产品名或数据基础设施；可以在原有技术之上做抽象概括（如“事件总线架构”“实时处理链路”），但不得虚构新的云服务、数据库或监控产品名称。"

  en:
    # ... 现有字段 ...
    hallucination_guard: "You MUST NOT introduce any technology brands, databases, cloud services, or data infrastructure names that do not appear in the original text. You may describe them in abstract terms (e.g., 'event bus', 'real-time processing pipeline'), but do not fabricate concrete product names."
```

可选：针对 `data_development` 加更严格的 role 级别配置：

```yaml
roles:
  data_development:
    # ... 现有字段 ...
    hallucination_guard:
      zh: "特别注意：不得凭空补写未在原文提及的技术栈（如 Kafka、Iceberg、ClickHouse 等）。只能在已有技术之上做抽象总结。"
      en: "Do not invent lakehouse stacks (e.g. Kafka, Iceberg, ClickHouse) that are not explicitly present in the source text. Only abstract from existing technologies."
```

在 `PromptLoader.build_role_aware_prompt()` 中：

- 读取：

  ```python
  base_guard = base.get("hallucination_guard", "")
  role_guard_cfg = role_config.get("hallucination_guard", {})
  role_guard = role_guard_cfg.get(lang_key, "") if isinstance(role_guard_cfg, dict) else ""
  hallucination_guard = "\n".join(filter(None, [base_guard, role_guard]))
  ```

- 将 `hallucination_guard` 插入 prompt 文本（示意，中文）：

  ```python
  return f"""你是一名{base['system_role']}...
...
4. {base['important_note']}只输出上述结构中的内容，不要包含任何其他信息；可以在成果部分使用行业区间，但不要超出这些范围。

{base['metrics_guidance']}
{hallucination_guard}

任务焦点：{task_focus}
...
"""
  ```

这样在 Tarot + `data_development` 情况下，即便错误地选择了数据平台视角，prompt 也会强约束“不允许补写 Iceberg/ClickHouse/Great Expectations”。

---

## 7. 兼容性与迁移

- 旧 YAML：
  - 不含 `llm_primary_role` / `llm_secondary_roles` 时：
    - `resolve_polish_role` 会退回到 `global_role` 或 `None`；
    - 行为与当前版本等价或更保守（部分项目可能退回基础 prompt）。
- CLI：
  - 不新增参数；
  - `--role` 语义不变。
- 风险控制：
  - 枚举校验会在 YAML 加错角色名时提前 fail（而不是跑到 LLM 时才暴露问题）。

---

## 8. 后续扩展点（非本轮实现）

- 增加项目级开关 `llm_polish_enabled: bool`，允许对少数敏感项目禁用 LLM 改写；
- 为不同项目支持不同 `persona_hint` 或“子 persona”（例如“平台 owner vs pipeline engineer”）；
- 在 artifacts 中输出“effective_role audit log”，便于 review 哪个项目是用哪种视角改写的。

