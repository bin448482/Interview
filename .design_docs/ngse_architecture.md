# NGSE 数据平台架构设计（面试版）

> Project: NGSE (Next Generation Sales Engine)  
> Role: Data Platform Engineer / Architect  
> Tech Stack: ADF, Azure Data Lake, Databricks, SQL Server, Web API  
> Purpose: 面试展示数据平台架构能力

---

## 1. Project Overview（项目背景）

### Background

为 Zoetis 全球 NGSE（Next Generation Sales Engine）在中国落地提供合规的 AI 引擎与湖仓底座，解决数据出入境限制、模型口径差异与推荐算法设计难题，让本地销售团队可复用全球剧本并量化商业化收益。

主要背景问题：

- 在中国数据进出口法规下，为全球 NGSE 构建可审计的本地数据管线与 AI 引擎
- 对齐 Zoetis 全球标准模型与国内经销/销售业务模型的字段、粒度与指标定义
- 验证国内销售/库存数据对 AI 训练、提示工程与推荐算法的适配性与质量
- 设计兼顾合规、可解释性的推荐算法与 Prompt 治理策略，支撑销售剧本复用

---

### Goal

项目建设目标：

- 建立中国区 DDP（统一数据平台 / Single Source of Truth），沉淀销售、库存等镜像数据资产
– 提供标准化数据服务能力，支撑 Sales Copilot、Power BI 等下游应用与多市场复用
- 通过统一模型与口径支撑销售运营分析与 AI 推荐，减少人工报表与口径对账成本
- 在中国数据出入境法规约束下，为全球 NGSE 构建可审计、可回溯的本地数据管线与 AI 引擎
- 对齐 Zoetis 全球标准模型与国内经销/销售模型，统一字段、粒度与指标定义，保障全球销售剧本在中国可落地
- 通过 Inbox→Raw→Transform→Governed 的四层 DDP 架构，形成公司级湖仓规范并支持后续市场复制
- 为 AI 训练、Prompt 工程与推荐算法提供高质量训练/测试/验证数据集，支撑 Sales Copilot 的摘要、下一步建议与风险提示能力
- 建立 PromptOps + 风险治理闭环（LLM 审核、Prompt QA、告警与复盘），在合规前提下安全推广生成式 AI
- 达成明确的数据与 AI 目标：数据准确率保持 ~99.5%，AI 推荐命中率约 70%，销售人员每周节省约 6 小时线索整理时间

---

## 2. Architecture Overview（总体架构说明）

整体架构基于 Azure 云平台，围绕 NGSE 中国区 DDP 与 AI 引擎展开，采用「多源接入 → DDP 分层存储 → DNA 特征层 → NGSE 应用数据库」的分层设计。

### Architecture Layers

```
Source Layer (CRM / SAP / 其它外部系统)
    |
    v
Ingestion (ADF / Aliyun OSS→ADLS Gen2)
    |
    v
DDP Storage
  ├─ Raw        （标准化 / 命名规范）
  ├─ Transform  （清洗 / 关联 / 聚合）
  └─ Governed   （治理 / 血缘 / 权限 / 发布）
    |
    v
DNA Feature Layer（为 AI 设计的可配置特征层）
    |
    v
NGSE Application DB & Serving（应用数据库 / Power BI / Web API）
```

---

### Components

| Layer                | Technology / Systems                                  |
|----------------------|-------------------------------------------------------|
| Source               | CRM, SAP, SQL Server, Excel, Web API, Aliyun OSS 等   |
| Ingestion            | Azure Data Factory（Pipeline, Integration Runtime）   |
| DDP Storage (Raw/Transform/Governed) | Azure Data Lake Storage Gen2, Delta Lake          |
| Compute & DNA Feature Layer | Databricks (Spark SQL / PySpark, DNA 特征表、方法注册) |
| NGSE Application DB & Serving | SQL Server（NGSE 应用库）、Power BI 报表、REST API       |

---

## 3. Data Flow Design（数据流转设计）

### Step 1: Data Acquisition

- 使用 ADF 从 SQL Server 和 Web API 拉取数据
- 支持 Full / Increment
- Pipeline 参数化控制

### Step 2: Raw Storage

- 数据写入 Azure Data Lake 的 Raw 层
- 保留完整原始数据用于审计和回溯

### Step 3: Data Processing

在 Databricks：

- 清洗
- 关联
- 去重
- 建模
- 汇总

### Step 4: Data Serving

- Power BI 报表
- Web API 提供销售指标

---

## 4. Data Model Design（建模设计）

### 4.1 DDP 分层数据模型

围绕中国区 DDP，我们采用「Inbox → Raw → Transform → Governed」的分层建模，而不是传统 ODS/DWD/DM 命名，更贴近项目实际交付：

- Inbox：多源接入缓冲层  
  - 承接 Aliyun OSS、CRM、SAP、SQL Server、Excel 等原始文件/接口落地  
  - 保留原始结构用于审计与重放，不直接对下游开放
- Raw（标准化 / 命名规范）  
  - 对字段命名、数据类型、编码做统一标准化（如客户、产品、区域、渠道等维度）  
  - 维持与源系统一一映射，便于定位问题与比对
- Transform（清洗 / 关联 / 聚合）  
  - 通过 Databricks 进行清洗、去重、主数据对齐与业务口径聚合  
  - 产出销售流向宽表、产品流向宽表、库存快照宽表等业务语义模型  
  - 支撑 Power BI 报表与下游 AI 特征抽取
- Governed（治理 / 血缘 / 权限 / 发布）  
  - 对外发布的「受治理数据集」，带有血缘、质量校验结果与权限标签  
  - 针对不同角色（exec/ops/market）发布不同的数据视图和访问策略

典型核心对象包括：

- 销售流向宽表：按客户/产品/区域/时间汇总的销售事实，作为 Exec 与 Sales Copilot 的共同基线  
- 库存快照宽表：按仓库/产品/时间的库存状态，支撑补货分析与推荐过滤  
- 维度表：客户、产品、区域、渠道、时间等维度，统一指标口径

---

### 4.2 DNA 特征模型（Feature Layer）

DNA 层是为 AI 设计的特征层，用于灵活配置与复用「客户 / 产品 / 区域」等维度的特征表，支撑推荐算法与 LLM 能力：

- 特征组织方式  
  - 按主体拆分：Customer DNA、Product DNA、Territory DNA 等  
  - 每个主体下可配置一组特征列，例如：历史销量、增长率、库存周转、拜访频次、履约率等
- 特征来源  
  - 主要从 Transform/Governed 宽表中聚合而来，确保与 DDP 口径一致  
  - 同时引入部分应用侧信号（例如推荐结果反馈、点击/采纳情况）
- 使用方式  
  - 作为 AI 训练和推理的数据输入，支撑 Sales Copilot 的排序与过滤逻辑  
  - 通过方法注册机制与 Notebook 模板，支持快速增加/下线特征，实现可插拔维度与事实表

通过 DNA 层，模型可以在不扰动 DDP 核心模型的前提下，快速演进特征组合，满足不同 AI 实验与市场需求。

---

### 4.3 NGSE 应用数据库模型

在 NGSE 应用数据库中，我们围绕「销售机会管理 + AI 推荐结果」构建了面向应用的轻量模型：

- 机会与账户模型  
  - 机会表：承载每个销售机会的状态、阶段、预计收益等  
  - 账户/客户表：与 DDP 客户维度打通，增强业务字段（例如负责人、覆盖区域）
- 推荐与任务模型  
  - 推荐结果表：记录 Sales Copilot 给出的推荐（推荐对象、得分、理由、使用的特征快照）  
  - 任务/待办表：将部分推荐落地为销售行动项，便于跟进与闭环
- 审计与监控模型  
  - 日志表：记录每次 AI 调用、输入输出摘要、模型版本、执行延迟  
  - 审计视图：面向合规/风险团队提供的透明视图，查看推荐分布与采纳情况

应用库的数据主要来源于 Governed 层与 DNA 特征层，通过 Databricks 作业或存储过程定期回写，既保证与数仓的一致性，又满足在线应用对查询性能与结构简洁性的要求。

---

## 5. Pipeline & Scheduling Architecture

NGSE 的调度体系以 ADF + Databricks Workflows + Azure Functions 为核心，贯通「跨云传输 → DDP 分层作业 → DNA 特征刷新 → 应用回写」全链路。

- ADF 统一编排  
  - 由 ADF 管理 Linked Services / Integration Runtime，负责 Aliyun OSS→ADLS Gen2 文件传输  
  - 调度 Databricks Notebook / Jobs，实现 Inbox→Raw→Transform→Governed 四层管道的每日/每小时运行  
  - 对关键 Pipeline 配置重试策略与失败告警，保障批处理稳定性
- Databricks Workflows 模块化拆分  
  - 将 ingestion / cleansing / join / aggregation 拆成原子作业，通过依赖配置与 global_temp/temp/intermediate 表衔接  
  - 利用 Delta 版本回溯与调试宽表，加速问题定位与回放
- Azure Functions 事件驱动  
  - 承接数据质量校验结果（Schema Drift、字段完整性、空值/重复等），触发邮件/Teams 告警  
  - 根据业务事件或验证结果调用 Databricks REST API，按需触发补数、重跑或下游任务
- 应用与 AI 侧刷新  
  - 定期刷新 DNA 特征表，为 Sales Copilot 提供最新特征快照  
  - 通过批量回写或 API，将聚合结果与推荐结果同步到 NGSE 应用数据库与 Power BI 语义层

整体上形成了「定时 + 事件」结合的调度体系：常规批处理走 ADF/Workflows，异常与业务触发由 Azure Functions 补充闭环。

---

## 6. Performance Optimization

性能优化主要围绕湖仓架构与 Delta Lake 特性展开，目标是同时满足 AI 训练与 BI 查询的 SLA。

- Delta Lake 版本与事务管理  
  - 利用 Delta 支持批处理回溯、全量/增量切换  
  - 结合 T-1 全量+增量差异校验，保证销售/产品流向等大表在高吞吐场景下仍保持 99.5% 数据准确率
- 分区与 Z-Order  
  - 针对销量、库存等宽表按日期/区域/产品进行合理分区  
  - 对高频过滤字段（如 market、product_id）使用 Z-Order，提高扫描效率
- 宽表与双通道消费  
  - 在 Transform/Governed 层构建统一宽表，一份数据同时支撑 AI 训练与 Power BI 实时查询  
  - 减少多套模型重复聚合，降低 IO 与维护成本
- 计算路径优化  
  - 公共 ETL 模块（加密/脱敏/路径解析/动态参数）统一封装，减少重复开发与算子冗余  
  - 在 DNA 层集中生成特征，避免在应用侧重复计算

效果上，关键库存/销售报表的运行时间提升约 2–3 倍，既满足 Exec 看板的实时性要求，也为 AI 训练窗口留出充足弹性。

---

## 7. Governance & Security

治理与安全方面，NGSE 通过「湖仓一体 + PromptOps + 数据出入境合规」三轨并行，覆盖数据与 AI 两个维度。

- 数据治理  
  - DDP 分层（Inbox/Raw/Transform/Governed）配合元数据目录与方法注册机制，记录数据血缘与方法依赖  
  - 自动化数据质量校验：Schema Drift、字段完整性、空值/重复率等，由 Databricks 作业+Azure Functions 告警闭环  
  - T-1 差异校验覆盖销售流向、产品流向等关键表，作为日常质量红线
- 权限与合规  
  - 基于 Azure AD 的角色/组管理，按 Exec/Director/Ops/Vendor 等角色配置访问级别  
  - 利用 Governed 层的脱敏视图与授权策略控制跨区域、跨团队访问  
  - 在中国数据出入境法规前提下，明确哪些数据可以用于 AI 训练，哪些只能在本地使用
- PromptOps 与 AI 治理  
  - 为 Sales Copilot 建立 Prompt 模板、版本与 Owner 管理，纳入变更流程  
  - 定义 LLM 使用边界、敏感场景禁用策略，并通过 Prompt QA、人工抽检与关键词告警管控风险  
  - 所有 AI 调用记录输入/输出摘要与模型版本，支持审计与回溯

---

## 8. Challenges & Solutions

| Challenge                                                 | Solution                                                                                          |
|-----------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| 中国数据进出口法规限制下，如何落地全球 NGSE 数据与 AI 能力 | 在中国区搭建本地 DDP 与 AI 引擎，只同步合规字段，严格区分本地/全球数据与模型边界                          |
| 全球标准模型与国内经销/销售模型在字段、粒度、指标上的差异 | 通过 DDP 分层建模与字段映射矩阵，对齐口径并在 Governed 层输出统一语义宽表                              |
| AI 训练/推荐对数据质量与时效的高要求                        | 引入 Delta + T-1 差异校验 + 自动化质量规则，保障 99.5% 准确率，并优化 Pipeline 满足训练/查询窗口       |
| 推荐算法与 Prompt 在合规场景下的可解释性与风险控制        | 构建 Sales Copilot 推荐算法 + PromptOps 体系，增加 Prompt QA、审计日志与高风险关键词告警              |
| 多市场、多团队对数仓规范与管道的复用诉求                  | 模块化 Notebook/ETL/方法注册规范与 DNA 架构，沉淀可复用蓝图，支持后续 4 个市场复制                     |

---

## 9. Achievements

- 性能与质量  
  - 关键库存/销售报表运行时间提升 2–3 倍，满足 AI 训练与 BI 查询 SLA  
  - T-1 差异校验覆盖核心宽表，数据准确率保持在约 99.5%
- AI 效能  
  - Sales Copilot 推荐命中率约 70%，帮助销售人员每周节省约 6 小时线索整理与准备时间  
  - 建立训练/测试/验证数据集资产包，支撑模型回归与监管抽检
- 组织与复用  
  - 形成公司级湖仓 + Prompt 治理规范，在 4 个市场复用，风险事件零高危升级  
  - NGSE 中国区实践被纳入全球销售数字化参考蓝本

---

## 10. Personal Contributions（个人职责）

本人负责：

- 路线图与架构  
  - 主导中国区 NGSE DDP + AI 引擎架构设计，定义 Inbox→Raw→Transform→Governed + DNA 特征层整体蓝图  
  - 参与全球/本地团队路线图讨论，将数据出入境合规与业务需求落实到技术方案
- 管道与建模  
  - 搭建跨云 Pipeline（Aliyun OSS→ADLS Gen2），拆解 ingestion/cleansing/join/aggregation 流程  
  - 设计并实现销售/库存等宽表与 DNA 特征表，支撑 BI 与 AI 双通道消费
- 质量与治理  
  - 设计并落地 Delta + T-1 差异校验机制与自动化质量规则（Schema Drift、字段完整性、空值/重复）  
  - 统一元数据/方法注册规范，串联 DDP 层与应用层的血缘与权限
- AI 与 PromptOps  
  - 定义 Sales Copilot 推荐算法与 PromptOps 流程，组织 Prompt QA、风险评审与复盘  
  - 协调 Exec/风险/业务团队，对齐合规边界与可解释性要求
- 复制与赋能  
  - 梳理可复用的 Notebook 模板、ETL 模块与 DNA 架构，支持后续市场快速复制  
  - 赋能本地数据工程与分析团队，建立日常运维与优化节奏

---

## 11. Summary

NGSE 项目在中国区落地了一套兼顾「湖仓一体、AI 能力与合规治理」的数据平台：  
既为全球销售引擎提供本地 DDP 镜像与高质量训练数据，又通过 Sales Copilot 等应用将推荐能力交付到一线销售手中，并以可复制的架构与规范支撑多市场扩展。
