# NGSE 数据平台架构设计（面试版）

> Project: NGSE (Next Generation Sales Engine)  
> Role: Data Platform Engineer / Architect  
> Tech Stack: ADF, Azure Data Lake, Databricks, SQL Server, Web API  
> Purpose: 面试展示数据平台架构能力

---

## 1. Project Overview（项目背景）

### Background

NGSE 是一个销售数据平台项目，目标是统一企业销售数据来源，构建可扩展、可治理的数据中台，为销售管理与绩效分析提供可靠的数据基础。

主要背景问题：

- 多源系统（CRM, SQL Server, Excel, Web API）
- 数据分散、口径不统一
- 报表高度依赖人工维护
- 缺乏统一的数据平台

---

### Goal

项目建设目标：

- 建立统一数据平台（Single Source of Truth）
- 提供数据服务能力
- 支持销售运营分析
- 降低数据运维成本

---

## 2. Architecture Overview（总体架构说明）

整体架构基于 Azure 云平台，采用典型 Data Lake + Compute + Service 分层设计。

### Architecture Layers

```
Source Layer
    |
    v
Ingestion (ADF)
    |
    v
Storage (Azure Data Lake)
    |
    v
Compute (Databricks)
    |
    v
Serving Layer (Power BI / Web API)
```

---

### Components

| Layer       | Technology |
|--------------|------------|
| Source       | SQL Server, Excel, Web API |
| Ingestion    | Azure Data Factory |
| Storage      | Azure Data Lake Storage |
| Compute      | Databricks |
| Serving      | Power BI, REST API |

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

### Model Layering

| Layer | Description |
|-------|-------------|
| ODS   | 原始同步层 |
| DWD   | 明细层 |
| DM    | 汇总指标层 |

---

### Core Tables

- Fact_Sales
- Dim_Product
- Dim_Customer
- Dim_Time

---

### Model Design Principles

- High cohesion
- Low coupling
- Standardized metrics
- BI friendly model

---

## 5. Pipeline & Scheduling Architecture

- 所有 pipeline 由 ADF 统一管理
- Databricks 负责数据处理与回写
- 支持失败重试
- 调度依赖关系清晰

---

## 6. Performance Optimization

### Techniques

- Delta Lake
- Partitioning
- Z-order
- Cache
- Broadcast Join

---

### Optimization Result

Query latency significantly reduced.

---

## 7. Governance & Security

- Azure AD 权限管理
- Table-level Access Control
- 审计日志
- Pipeline 监控

---

## 8. Challenges & Solutions

| Challenge | Solution |
|----------|----------|
| Data inconsistency | Unified data model |
| Slow query | Partition & Z-order |
| Pipeline failures | Retry & alert |
| Governance | Logging & access control |

---

## 9. Achievements

- Improved data latency
- Unified model
- Stable daily pipeline

---

## 10. Personal Contributions（个人职责）

本人负责：

- 数据平台架构设计
- Databricks Pipeline 开发
- 模型设计
- 性能调优
- 权限与治理

---

## 11. Summary

NGSE 项目成功搭建企业级数据平台，实现基础数据到业务智能的完整链路。
