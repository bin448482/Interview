# Persona-Aware LLM Prompting 实施计划

## 现状分析

### 已完成的部分
1. ✅ **Role Configuration System** - 6 个角色已定义，每个角色有 `persona` 和 `field_visibility` 配置
2. ✅ **CLI Integration** - `--role` 参数已集成，persona 信息已传递到 llm_polisher
3. ✅ **Field-Level Filtering** - role_filter 已激活，对项目字段进行可见性过滤
4. ✅ **Basic Persona Injection** - llm_polisher 已接收 persona，并在 LLM 提示中注入

### 存在的问题
1. ❌ **Project-Level Filtering 未激活** - role_filter 中的 `include_projects` 和 `exclude_projects` 规则未被使用，所有项目都被保留
2. ⚠️ **Persona 影响力有限** - Persona 提示被插入在 LLM 提示的中间，而不是系统级别的角色定义
3. ⚠️ **Prompt 结构不够角色感知** - 所有角色使用相同的 6 部分输出结构，不区分产品经理 vs 工程师的不同需求
4. ⚠️ **代码重复** - 中英文 prompt 完全独立，难以维护

## 改造目标

### 核心目标
设计和实现**角色特定的 LLM Prompt 系统**，使得不同角色的简历在 LLM 润色时能够体现出不同的视角、指标和表述方式。

### 具体目标
1. **激活项目级过滤** - 所有角色只看到 3 个核心项目（MySixth、NGSE、Remedium BI），但每个角色看到项目中不同的属性
2. **实现完全不同的 Prompt 结构** - 产品经理、工程师、数据工程师各有独特的 6 部分输出结构
3. **强化 Persona 在 Prompt 中的地位** - 从补充提示升级为系统级角色定义
4. **使用 YAML 配置驱动 Prompt** - 便于非开发者编辑和维护 prompt 配置

## 实施方案

### Phase 1: 激活 Project-Level Filtering（1-2 小时）

**目标**：完成 role_filter.py 中的项目级过滤逻辑

**任务**：
1. 在 `role_filter.py` 中实现 `_filter_and_sort_projects()` 方法
   - 支持 `include_projects` 规则匹配（pattern、contains、exact、value）
   - 支持 `exclude_projects` 规则匹配
   - 计算每个项目的相关性分数（匹配的 include 规则数）
   - 按相关性分数 + 时间排序

2. 修改 `filter_resume()` 方法调用新的过滤方法

3. 测试每个角色的过滤结果

**关键文件**：
- `resume_docs/role_filter.py` - 实现过滤逻辑
- `resume_docs/role_config.py` - 已有规则定义，无需修改

**验证方式**：
```bash
python -m resume_docs.cli --role product_manager --dry-run
# 验证输出中只包含符合 include_projects 规则的项目
```

---

### Phase 2: 重构 LLM Prompt 系统（2-3 小时）

**目标**：设计和实现角色特定的 prompt 系统

**设计决策**：

#### 2.1 Prompt 结构设计

**新的 Prompt 架构**：
```
1. 系统角色定义（System Role）
   - 基础角色：资深技术招聘官 + 简历优化专家
   - 角色视角：从 persona.label 中提取（如"AI 产品经理视角"）

2. 角色特定的任务说明（Role-Specific Task）
   - 产品经理：强调商业价值、用户洞察、干系人对齐
   - 工程师：强调技术深度、架构演进、可扩展性
   - 数据工程师：强调数据可靠性、治理、性能

3. 输出结构（Role-Aware Output Structure）
   - 产品经理：项目名称 → 角色 → 商业背景 → 用户问题 → 解决方案 → 商业成果
   - 工程师：项目名称 → 角色 → 技术背景 → 技术挑战 → 架构方案 → 技术成果
   - 数据工程师：项目名称 → 角色 → 数据背景 → 数据问题 → 数据方案 → 数据成果

4. 角色特定的指标指导（Role-Specific Metrics Guidance）
   - 从 impact_metrics 中提取相关指标类别
   - 根据角色类型生成指标范围建议

5. 原始项目内容（已过滤的字段）

6. 最后指示
```

#### 2.2 Prompt 模板化（YAML 配置驱动）

**方案**：创建 `.design_docs/prompt_config.yaml` 配置文件，定义：
- 基础 prompt 模板（中英文）
- 角色特定的任务说明
- 角色特定的输出结构（6 部分）
- 角色特定的指标指导

**示例结构**：
```yaml
# .design_docs/prompt_config.yaml
base_templates:
  zh:
    system_role: "资深技术招聘官与简历优化专家"
    task_intro: "生成可直接放入简历的项目经验"
  en:
    system_role: "Senior technical recruiter and resume optimization expert"
    task_intro: "Generate project experience section"

roles:
  product_manager:
    label: "AI 产品经理视角"
    task_focus:
      zh: "商业价值与用户洞察"
      en: "Business value and user insights"
    output_structure:
      - "项目名称"
      - "角色"
      - "商业背景"
      - "用户问题"
      - "解决方案"
      - "商业成果"
    metrics_categories: ["business_metrics", "operational_metrics"]
    tone: "strategic, user-centric, metrics-driven"

  ai_development:
    label: "AI 工程师视角"
    task_focus:
      zh: "技术深度与架构演进"
      en: "Technical depth and architecture evolution"
    output_structure:
      - "项目名称"
      - "角色"
      - "技术背景"
      - "技术挑战"
      - "架构方案"
      - "技术成果"
    metrics_categories: ["technical_metrics"]
    tone: "technical, detailed, scalability-focused"

  # ... 其他角色
```

#### 2.2.1 完整示例：基于 _build_polish_prompt 的实际 Prompt 生成

本节展示当前 `llm_polisher.py` 中 `_build_polish_prompt()` 方法如何为不同角色生成角色感知的 prompt。

**原始项目输入（project_overview）：**
```
TarotAI 全渠道套件：Expo React Native 客户端 + FastAPI 后端 + Next.js 管理台 + AI 内容生成工具，叠加产品遥测、Cohort 仪表盘与提示治理，面向匿名用户提供四步塔罗体验与付费 AI 解读。
```

**示例 1：产品经理视角（product_manager）**

Persona 配置（来自 `role_config.py`）：
```python
"persona": {
    "label": "AI 产品设计/策略视角",
    "instructions": {
        "zh": "以 AI 产品设计师或产品经理的身份撰写，强调用户洞察、商业化假设、干系人对齐与实验节奏，把技术亮点转译为产品价值。"
    }
}
```

生成的 Prompt（由 `_build_polish_prompt()` 构建）：
```
你是一名资深技术招聘官与简历优化专家，擅长根据候选人提供的项目内容，重写为结构清晰、量化明确、对招聘方友好的项目经验。

请根据以下项目内容，生成一段可以直接放入简历的【项目经验】内容。

要求：
1. 按照以下结构输出：
   - 项目名称 | 所属公司/个人 | 起止时间
   - 角色 Role
   - 技术栈 Tech Stack
   - 项目背景（严格控制在800-1000字以内，综合以下信息组织）：
     * 项目的核心目标与用户群体
     * 主要挑战与技术难点
     * 采用的架构方案与技术选型
     * 交付的核心产品与功能
   - 主要职责（4~6 条，每条以动词开头）
   - 成果产出（1~4 条；原文有数据则忠实引用，缺少数据时可基于行业通用区间补写保守指标，例如：Day1留存约20%~30%、Day30留存约5%~12%、DAU/MAU约20%~30%。务必使用"约""保持在"等措辞，严禁超出这些区间或给出明显夸张的用户规模。）

2. 项目背景部分应该：
   - 从用户需求出发，说明为什么要做这个项目
   - 阐述面临的主要技术挑战
   - 介绍采用的解决方案与架构设计
   - 突出交付的核心价值与影响
   - 字数严格控制在800-1000字以内，不要超过1000字

3. 风格要求：
   - 简洁、专业、重点突出
   - 避免列表式堆砌，用段落形式组织
   - 尽量使用动词开头
   - 原文缺少数据时，可以引用上述行业区间生成保守指标，并注明这是区间表现；严禁出现夸张数字（例如：超大用户量、远高于行业均值的增长率）。

4. 重要：只输出上述6个部分的内容，不要包含任何其他信息（如Business、Technical、Challenges、Responsibilities、Solution、Deliverables、Impact等原始数据）；可以在成果部分使用前述行业区间，但不要超出这些范围，更不要虚构庞大里程碑、收入或用户规模。

角色视角提示（必须体现在措辞、指标与优先级中）：以 AI 产品设计师或产品经理的身份撰写，强调用户洞察、商业化假设、干系人对齐与实验节奏，把技术亮点转译为产品价值。

原始项目内容：
TarotAI 全渠道套件：Expo React Native 客户端 + FastAPI 后端 + Next.js 管理台 + AI 内容生成工具，叠加产品遥测、Cohort 仪表盘与提示治理，面向匿名用户提供四步塔罗体验与付费 AI 解读。

请直接返回结构化的项目经验内容，不要添加任何前缀或解释。
```

**预期 LLM 输出（产品经理视角）：**
```
MySixth 塔罗牌智能应用 | 个人独立开发者 | 2025.10 - 至今
独立开发者
Expo React Native、FastAPI、Next.js、GLM-4/OpenAI、PostHog

面向匿名用户的 AI 塔罗占卜平台，通过四步体验与付费解读实现商业化。核心挑战是在单人团队下同时交付移动端、后端、管理后台与 AI 生成工具，并将用户访谈与漏斗数据沉淀到产品决策。通过设计北极星指标（付费率/留存）、建立实验待办与用户反馈闭环，确保每周迭代周期 < 2 天。采用 Expo 移动端 + FastAPI 单体 + Next.js Admin 的分层架构，支持 Google Play IAP、兑换码、Stripe 多渠道充值，并通过 Cohort 仪表盘与 A/B 实验矩阵驱动产品决策。

- 梳理北极星指标（付费率/留存），沉淀实验待办、用户访谈与需求优先级
- 设计匿名安装 ID + JWT 认证、四步占卜流程与端到端 API 契约
- 实现 Google Play IAP/兑换码/Stripe 的充值路由、分账报表与风控策略
- 搭建 Cohort 仪表盘与 A/B 实验矩阵，支撑提示/付费实验决策
- 撰写多语言 README/CLAUDE 指南与产品遥测 SOP，固化开发 + 运营流程

- Q4 2025 付费转化率约 18%，较行业均值 +50%，日活分层付费率约 6%
- 上线 60 天锁定约 6 万人民币 ARR 的订阅/兑换码流水，形成复购漏斗
- A/B 实验迭代周期 < 2 天，用户反馈闭环 48 小时内完成
```

---

**示例 2：AI 工程师视角（ai_development）**

Persona 配置（来自 `role_config.py`）：
```python
"persona": {
    "label": "AI 应用工程视角",
    "instructions": {
        "zh": "以 AI 工程负责人身份描述建模、推理性能、PromptOps 与成本治理等实现细节。"
    }
}
```

生成的 Prompt（仅展示 persona 注入部分的差异）：
```
... [前面的 6 部分结构要求相同] ...

角色视角提示（必须体现在措辞、指标与优先级中）：以 AI 工程负责人身份描述建模、推理性能、PromptOps 与成本治理等实现细节。

原始项目内容：
TarotAI 全渠道套件：...
```

**预期 LLM 输出（AI 工程师视角）：**
```
MySixth 塔罗牌智能应用 | 个人独立开发者 | 2025.10 - 至今
独立开发者
Expo React Native、FastAPI、Next.js、GLM-4/OpenAI、Ollama、Docker

构建双阶段 AI 流水线与多 LLM 路由系统，实现成本与性能的平衡。核心技术挑战包括：(1) 设计 `/readings/analyze` 推荐维度与 `/readings/generate` 付费解读的双阶段 API，并挂载提示治理清单；(2) 实现多 LLM 路由（GLM-4/OpenAI/Ollama）与成本看板，将推理成本降低 60%；(3) 构建事件总线 + Cohort 仪表盘，在 24 小时内可视化实验指标。采用 FastAPI 单体 + Python AI Generator 的架构，支持批量维度文案生成与成本监控。

- 主导双阶段 AI API 设计与多 LLM 路由实现，支持 GLM-4/OpenAI/Ollama 动态切换
- 搭建 LLM 工厂 + 成本看板，实现推理成本监控与告警
- 实现提示治理清单与风险评审节奏，确保 AI 输出质量
- 设计 Docker Compose + Nginx 部署拓扑，支持单台云服务器部署
- 构建事件总线 + Cohort 仪表盘，支撑 A/B 实验与提示优化

- 统一 LLM 工厂 + 成本看板让 AI 调用成本降低 60%，高峰期 TP99 < 1.2s
- 事件总线 + Cohort 仪表盘将实验指标在 24 小时内可视化，支撑提示/付费实验
- 单台云服务器部署将月运营成本控制在 500 元以内
```

---

**示例 3：数据平台视角（data_development）**

Persona 配置（来自 `role_config.py`）：
```python
"persona": {
    "label": "数据平台负责人视角",
    "instructions": {
        "zh": "以数据平台/湖仓负责人的身份撰写，突出数据可靠性、治理指标、性能优化与跨区域复制价值。"
    }
}
```

**预期 LLM 输出（数据平台视角）：**
```
MySixth 塔罗牌智能应用 | 个人独立开发者 | 2025.10 - 至今
独立开发者
Expo React Native、FastAPI、Next.js、SQLite、PostHog、Cohort

构建离线优先的数据架构与产品遥测系统，确保数据可靠性与实验驱动决策。核心数据挑战包括：(1) 设计匿名身份体系（`installation_id` + 可选邮箱绑定）与离线同步策略，支持 Expo SQLite `tarot_config.db` 预置与后台持久化；(2) 构建 PostHog/Amplitude 事件采集 → Cohort 分群 → 留存看板的完整数据链路；(3) 实现 A/B 实验矩阵与成本/收益对账报表，支撑数据驱动的产品决策。采用 SQLite 版本控制 + Docker volume 备份策略，确保数据持久化与灾难恢复。

- 设计匿名安装 ID + JWT 认证体系，支持离线同步与会话留资
- 构建 PostHog/Amplitude 事件采集与 Cohort 仪表盘，实现用户分群与留存分析
- 实现 A/B 实验矩阵与成本/收益对账报表，支撑数据驱动决策
- 搭建 SQLite 版本控制 + Docker volume 备份策略，确保数据持久化
- 撰写数据治理 SOP 与产品遥测文档，固化数据采集与分析流程

- 漏斗分析显示付费转化率约 18%，日活分层付费率约 6%，较行业均值 +50%
- 留存看板显示 Day1 留存约 25%、Day30 留存约 8%，支撑产品优化方向
- 实验矩阵追踪 A/B 实验迭代周期 < 2 天，用户反馈闭环 48 小时内完成
```

---

**关键观察：**

1. **Persona 注入机制**：`_build_polish_prompt()` 在 persona_hint 参数中注入角色视角提示，位置在主要要求之后、原始项目内容之前（见 `llm_polisher.py` 第 114 行）。

2. **6 部分输出结构**：所有角色共享相同的 6 部分结构（项目名称、角色、技术栈、项目背景、主要职责、成果产出），但 LLM 根据 persona 提示调整措辞、指标与优先级。

3. **指标范围**：Prompt 明确指导 LLM 使用保守指标范围（Day1 留存 20-30%、Day30 留存 5-12%、DAU/MAU 20-30%），避免虚构数据。

4. **实际应用**：当调用 `polish_projects()` 时，系统会：
   - 从 `role_config.py` 中获取角色的 persona 配置
   - 调用 `_get_persona_hint()` 提取语言特定的 persona 指导文本
   - 将其传递给 `_build_polish_prompt()`，生成角色感知的 prompt
   - 发送给 LLM 进行润色

**Python 端**：创建 `resume_docs/prompt_loader.py` 加载和解析 YAML 配置

#### 2.3 Persona 在 Prompt 中的位置

**改进**：
- 将 persona 提示从 prompt 中间移到开头（系统级别）
- 格式：`You are a [persona.label]. [persona.instructions[lang]]`
- 确保 persona 影响整个 prompt 的语气和重点

#### 2.4 字段级过滤的 Prompt 集成

**改进**：
- 在调用 LLM 前，根据 `field_visibility` 过滤项目字段
- 只将相关字段传递给 LLM（减少噪音，提高 prompt 效率）
- 例如：product_manager 不需要看 `tech_stack` 和 `architecture_or_solution`

### Phase 3: 实现 Prompt 系统（2-3 小时）

**任务**：

1. **创建 `.design_docs/prompt_config.yaml`**
   - 定义基础 prompt 模板（中英文）
   - 为每个角色定义：task_focus、output_structure、metrics_categories、tone

2. **创建 `resume_docs/prompt_loader.py`**
   - 实现 `load_prompt_config()` 函数加载 YAML
   - 实现 `build_role_aware_prompt()` 函数
     - 接收 role、project、language 参数
     - 从 YAML 配置中获取角色特定的结构
     - 构建完整的 LLM prompt

3. **修改 `llm_polisher.py`**
   - 导入 `prompt_loader`
   - 修改 `polish_projects()` 方法
     - 接收 `role` 参数
   - 修改 `_polish_single_project()` 方法
     - 接收 `role` 参数
     - 调用 `prompt_loader.build_role_aware_prompt()` 构建 prompt
     - 在调用 LLM 前过滤项目字段（根据 field_visibility）

4. **修改 `cli.py`**
   - 在调用 `polish_projects()` 时传递 `role` 参数

5. **修改 `role_filter.py`**
   - 实现 `_filter_and_sort_projects()` 方法（激活项目级过滤）
   - 在 `polish_projects()` 调用时传递 `role` 参数

**关键文件**：
- `.design_docs/prompt_config.yaml` - 新建
- `resume_docs/prompt_loader.py` - 新建
- `resume_docs/llm_polisher.py` - 修改
- `resume_docs/cli.py` - 修改
- `resume_docs/role_filter.py` - 修改

---

### Phase 4: 测试与验证（1-2 小时）

**任务**：

1. **单元测试**
   - 测试 `_filter_and_sort_projects()` 的过滤逻辑
   - 测试 `build_role_aware_prompt()` 的 prompt 生成

2. **集成测试**
   - 为每个角色生成一份简历（无 LLM 润色）
   - 验证项目级过滤是否正确
   - 验证字段级过滤是否正确

3. **LLM 润色测试**
   - 为 2-3 个角色生成简历（有 LLM 润色）
   - 验证 prompt 中的 persona 是否被正确注入
   - 验证输出是否体现了角色特定的视角

4. **YAML 验证**
   - 运行 `yamllint latest_resumes/*.yaml`
   - 运行 Python safe-load 验证

**验证命令**：
```bash
# 无 LLM 润色
.venv\Scripts\python -m resume_docs.cli --role product_manager --template modern --locale zh-CN --skip-polish

# 有 LLM 润色
.venv\Scripts\python -m resume_docs.cli --role product_manager --template modern --locale zh-CN --model glm-4

# 验证 YAML
yamllint latest_resumes/*.yaml
```

---

### Phase 5: 文档与 PR（1 小时）

**任务**：

1. **更新 `CLAUDE.md`**
   - 解释新的 persona-aware prompt 系统
   - 说明如何为新角色添加 prompt 配置

2. **创建 `resume_docs/ROLE_FILTERS.md`**
   - 文档化每个角色的过滤规则
   - 文档化每个角色的 prompt 配置

3. **创建 PR**
   - 标题：`feat: implement persona-aware LLM prompting with role-specific output structures`
   - 描述：
     - 激活项目级过滤
     - 实现角色特定的 prompt 系统
     - 强化 persona 在 prompt 中的地位
   - 包含验证输出和测试结果

---

## 关键设计决策

### 1. Prompt 模板化 vs 硬编码
- **选择**：模板化（`prompt_templates.py`）
- **理由**：便于维护、扩展新角色、减少代码重复

### 2. Persona 位置
- **选择**：系统级别（prompt 开头）
- **理由**：提高 persona 对 LLM 输出的影响力

### 3. 字段过滤时机
- **选择**：在调用 LLM 前过滤
- **理由**：减少 prompt 长度、提高 LLM 效率、避免噪音

### 4. Role 参数传递
- **选择**：从 CLI 一路传递到 llm_polisher
- **理由**：保持数据流清晰，便于调试

---

## 文件修改清单

| 文件 | 操作 | 优先级 |
|------|------|--------|
| `resume_docs/role_filter.py` | 实现 `_filter_and_sort_projects()` 激活项目级过滤 | P0 |
| `.design_docs/prompt_config.yaml` | 新建，定义角色特定的 prompt 配置 | P0 |
| `resume_docs/prompt_loader.py` | 新建，加载 YAML 并构建角色感知 prompt | P0 |
| `resume_docs/llm_polisher.py` | 修改 prompt 构建逻辑，集成 prompt_loader | P0 |
| `resume_docs/cli.py` | 传递 role 参数到 llm_polisher | P0 |
| `CLAUDE.md` | 更新文档，解释新的 prompt 系统 | P1 |
| `resume_docs/ROLE_FILTERS.md` | 新建，文档化过滤规则和 prompt 配置 | P1 |

---

## 预期成果

### 功能成果
1. ✅ 项目级过滤激活 - 所有角色只看到 3 个核心项目
2. ✅ 字段级过滤激活 - 每个角色看到项目中不同的属性
3. ✅ 角色特定的 prompt 结构 - 产品经理、工程师、数据工程师各有独特的 6 部分结构
4. ✅ 强化的 persona 影响 - persona 作为系统级角色定义，影响整个 prompt
5. ✅ YAML 配置驱动 - 非开发者可编辑 prompt 配置

### 质量成果
1. ✅ 代码可维护性提升 - prompt 配置外部化，易于扩展
2. ✅ 测试覆盖 - 单元测试 + 集成测试
3. ✅ 文档完整 - CLAUDE.md + ROLE_FILTERS.md

### 用户体验成果
1. ✅ 简历更贴切 - 不同角色的简历体现完全不同的视角和结构
2. ✅ 指标更相关 - 产品经理看到商业指标，工程师看到技术指标
3. ✅ 表述更专业 - LLM 根据角色生成专业的表述

---

## 时间估计

| Phase | 任务 | 时间 |
|-------|------|------|
| 1 | 激活 Project-Level Filtering | 1-2 小时 |
| 2 | 设计 Prompt 系统（YAML 配置） | 1-2 小时 |
| 3 | 实现 Prompt 系统 | 2-3 小时 |
| 4 | 测试与验证 | 1-2 小时 |
| 5 | 文档与 PR | 1 小时 |
| **总计** | | **6-10 小时** |

---

## 风险与缓解

| 风险 | 影响 | 缓解方案 |
|------|------|---------|
| LLM 不遵循 prompt 指导 | 输出不符合预期 | 在 prompt 中明确强调关键要求，使用 few-shot 示例 |
| Prompt 过长导致 token 超限 | API 调用失败 | 严格控制字段过滤，避免传递不相关字段 |
| 新 prompt 结构破坏现有功能 | 回归问题 | 保留原有 prompt 作为 fallback，逐步迁移 |
| 多语言 prompt 维护复杂 | 维护成本高 | 使用模板化方案，提取公共部分 |

