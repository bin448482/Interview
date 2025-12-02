# NGSE 数据平台架构（面试版）PPT 大纲

## 1. 封面

- 标题：NGSE 中国区数据平台 & AI 架构实践  
- 副标题：在合规约束下落地全球销售引擎  
- 个人信息：姓名 \| Data Platform Engineer / Architect  

---

## 2. 项目背景 & 业务痛点

- 背景：为 Zoetis 全球 NGSE 在中国落地，解决本地合规与全球复用  
- 痛点 1：数据出入境法规限制，需本地可审计数据管线与 AI 引擎  
- 痛点 2：全球标准模型 vs 国内经销/销售模型口径不一致  
- 痛点 3：销售分析与推荐高度依赖人工报表与经验  

---

## 3. 项目目标 & 关键指标

- 搭建中国区 DDP（统一数据平台 / Single Source of Truth）  
- 支撑 Sales Copilot、Power BI 等下游应用与多市场复制  
- 对齐全球/本地字段、粒度与指标，统一销售与库存视图  
- 数据准确率 ~99.5%，AI 推荐命中率 ~70%  
- 每位销售每周节省 ~6 小时线索整理时间  

---

## 4. 总体架构概览

- 基于 Azure：ADF + ADLS Gen2 + Databricks + SQL Server + Power BI  
- 分层架构：Source → Ingestion → DDP（Inbox/Raw/Transform/Governed）  
- AI 特征层：DNA Feature Layer（Customer / Product / Territory DNA）  
- 应用层：NGSE Application DB & Rest API，为 Sales Copilot 和报表服务  

---

## 5. 数据流转设计（E2E 流程）

- Step 1：多源采集（CRM / SAP / SQL Server / Web API / Aliyun OSS）  
- Step 2：Inbox / Raw 层落地，保留原始结构用于审计与重放  
- Step 3：Databricks 清洗、关联、聚合，生成销售/库存宽表  
- Step 4：Governed 层发布治理数据集与视图  
- Step 5：回写 NGSE 应用库 & 提供 Power BI / API 查询  

---

## 6. 数据模型 & DNA 特征层

- DDP 分层模型：Inbox / Raw / Transform / Governed  
- 核心宽表：销售流向、产品流向、库存快照 + 客户/产品/区域等维度  
- DNA 特征层：Customer / Product / Territory DNA  
- 特征示例：历史销量、增长率、库存周转、拜访频次、履约率等  
- 用途：统一支撑 AI 训练、推理与排序/过滤逻辑  

---

## 7. 调度架构 & 性能优化

- 调度体系：ADF（跨云传输 & 主控）+ Databricks Workflows + Azure Functions  
- 策略：定时批处理 + 事件驱动（质量告警、补数、重跑）  
- 性能优化：Delta Lake 版本回溯、分区 + Z-Order、统一宽表双通道消费  
- 效果：核心报表性能提升 2–3 倍，满足 BI 与 AI 同时 SLA  

---

## 8. 治理、安全与 PromptOps

- 数据治理：分层建模 + 元数据目录 + 自动化质量规则（Schema Drift 等）  
- 权限与合规：基于 Azure AD 的角色访问控制 + 脱敏视图  
- 出入境合规：清晰划分本地/全球数据与模型边界  
- PromptOps：Prompt 模板与版本管理、Prompt QA、关键词告警与审计日志  

---

## 9. 挑战与解决方案（精简版）

- 合规 vs 全球复用：本地 DDP + AI 引擎，只同步合规字段  
- 模型口径不一致：字段映射矩阵 + Governed 层统一语义宽表  
- AI 质量要求高：Delta + T-1 差异校验 + 自动化质量规则  
- 风险与可解释性：Sales Copilot 推荐算法 + PromptOps 全链路审计  

---

## 10. 成果与业务价值

- 数据侧：关键宽表准确率 ~99.5%，报表性能提升 2–3 倍  
- AI 侧：推荐命中率 ~70%，销售每周节省 ~6 小时准备时间  
- 组织侧：形成湖仓 + Prompt 治理蓝本，在多个市场复用，零高危风险升级  

---

## 11. 个人贡献 & 升级点

- 架构：主导中国区 DDP + AI 整体架构（Inbox→Governed + DNA 特征层）  
- 实施：设计并实现跨云 Pipeline、宽表模型与 DNA 特征表  
- 治理：提出并落地 Delta + T-1 差异校验与质量告警机制  
- AI & PromptOps：定义 Sales Copilot 推荐策略与 PromptOps 流程  
- 复制：沉淀可复用 Notebook/ETL 模板，支持后续市场快速复制  

