# NGSE Data Platform Architecture Design (Interview Version)

> Project: NGSE (Next Generation Sales Engine)  
> Role: Data Platform Engineer / Architect  
> Tech Stack: ADF, Azure Data Lake, Databricks, SQL Server, Web API  
> Purpose: Showcase data platform architecture capabilities in interviews

---

## 1. Project Overview

### Background

Provide a compliant AI engine and lakehouse foundation to localize the global NGSE (Next Generation Sales Engine) in China, under Chinese data export/import regulations. The goal is to solve cross-border data restrictions, model definition mismatches, and recommendation algorithm design challenges so that the local sales team can reuse the global playbooks and quantify commercial impact.

Key background problems:

- Under Chinese data export/import regulations, build an auditable local data pipeline and AI engine for the global NGSE program in China
- Align Zoetis global standard models with local distributor/sales models in terms of fields, granularity, and metric definitions
- Validate how well domestic sales/inventory data fits AI training, prompt engineering, and recommendation algorithms, and assess its quality
- Design recommendation algorithms and prompt governance strategies that balance compliance and explainability, supporting reuse of global sales playbooks

---

### Goal

Project objectives:

- Build a China DDP (unified data platform / single source of truth) and consolidate mirrored data assets such as sales and inventory
- Provide standardized data services to support Sales Copilot, Power BI, and other downstream applications and facilitate reuse across markets
- Use unified models and definitions to support sales operations analytics and AI recommendations, reducing manual report work and metric reconciliation
- Under Chinese data export/import regulations, provide an auditable and traceable local data pipeline and AI engine for the global NGSE program
- Align Zoetis global standard models with domestic distributor/sales models, unifying fields, granularity, and metric definitions so global sales playbooks can be localized in China
- Establish a four-layer DDP architecture (Inbox → Raw → Transform → Governed) as a company-level lakehouse standard and support replication to future markets
- Provide high-quality training/test/validation datasets for AI training, prompt engineering, and recommendation algorithms, enabling Sales Copilot capabilities such as summarization, next-best-action, and risk alerts
- Build a closed loop of PromptOps and risk governance (LLM review, prompt QA, alerts, and postmortems) to safely roll out generative AI under compliance constraints
- Achieve clear data and AI targets: maintain ~99.5% data accuracy, achieve ~70% hit rate for AI recommendations, and save each salesperson ~6 hours per week on lead preparation

---

## 2. Architecture Overview

The overall architecture is built on Azure and centers on the NGSE China DDP and AI engine. It adopts a layered design of “multi-source ingestion → DDP layered storage → DNA feature layer → NGSE application database”.

### Architecture Layers

```
Source Layer (CRM / SAP / other external systems)
    |
    v
Ingestion (ADF / Aliyun OSS → ADLS Gen2)
    |
    v
DDP Storage
  ├─ Raw        (standardization / naming conventions)
  ├─ Transform  (cleansing / joining / aggregation)
  └─ Governed   (governance / lineage / permissions / publishing)
    |
    v
DNA Feature Layer (feature layer designed for AI)
    |
    v
NGSE Application DB & Serving (application DB / Power BI / Web API)
```

---

### Components

| Layer                         | Technology / Systems                                                     |
|-------------------------------|---------------------------------------------------------------------------|
| Source                        | CRM, SAP, SQL Server, Excel, Web API, Aliyun OSS, etc.                  |
| Ingestion                     | Azure Data Factory (Pipelines, Integration Runtime)                      |
| DDP Storage (Raw/Transform/Governed) | Azure Data Lake Storage Gen2, Delta Lake                                 |
| Compute & DNA Feature Layer   | Databricks (Spark SQL / PySpark, DNA feature tables, method registry)    |
| NGSE Application DB & Serving | SQL Server (NGSE application DB), Power BI reports, REST APIs            |

### Diagram-Based End-to-End Flow

The “NGSE Architecture Diagram” image in this repository can be read left-to-right as the concrete implementation of the above layers:

- Source systems on the left: external SQL servers, CRM, SAP Cloud, and OSS act as primary structured and semi-structured data providers.  
- Ingestion via ADF: Azure Data Factory pulls data from these systems (including cross-cloud transfers) and lands them into the lakehouse.  
- DDP layer on Databricks: inside the Databricks box, data moves through `RAW → Transform → Governed` folders, forming the DDP layer that standardizes, cleanses, and governs data.  
- DNA feature zone: the `DNA` folder beneath the DDP layer represents AI-oriented feature tables generated from the Governed layer for recommendation and LLM use cases.  
- Data Market: curated and governed data is published into a `Data Market` SQL database, which serves as the primary serving store for analytics and downstream applications.  
- BI and Web analytics: Power BI (BI) and web-based analytics (WEB) consume data from the Data Market to provide dashboards and self-service analysis.  
- External APIs and NGSE Web: external APIs connect through API Management and NGSE Web to support online application scenarios, surfacing metrics and recommendations to end users.  
- NGSE functions and external SQL: NGSE-specific functions and additional external SQL servers integrate with the platform through API Management and SQL endpoints, closing the loop between operational systems and the DDP/AI layers.

---

## 3. Data Flow Design

### Step 1: Data Acquisition

- Use ADF to pull data from SQL Server and Web APIs  
- Support full and incremental loads  
- Control pipelines via parameters

### Step 2: Raw Storage

- Write data to the Raw layer in Azure Data Lake  
- Retain complete raw data for audit and replay

### Step 3: Data Processing

In Databricks:

- Cleansing  
- Joining  
- De-duplication  
- Modeling  
- Aggregation

### Step 4: Data Serving

- Power BI reports  
- Web APIs providing sales metrics

---

## 4. Data Model Design

### 4.1 DDP Layered Data Model

For the China DDP, we use an “Inbox → Raw → Transform → Governed” layered model rather than the traditional ODS/DWD/DM naming, as it better matches real-world delivery:

- Inbox: multi-source landing buffer  
  - Receives raw files or interface outputs from Aliyun OSS, CRM, SAP, SQL Server, Excel, etc.  
  - Preserves original structure for audit and replay; not directly exposed downstream
- Raw (standardization / naming)  
  - Standardizes field names, data types, and codes (e.g., customer, product, region, channel dimensions)  
  - Maintains one-to-one mapping with source systems to simplify issue localization and comparisons
- Transform (cleansing / joining / aggregation)  
  - Uses Databricks to cleanse, de-duplicate, align master data, and aggregate according to business definitions  
  - Produces business semantic models such as sales flow wide table, product flow wide table, inventory snapshot wide table  
  - Supports Power BI reports and downstream AI feature extraction
- Governed (governance / lineage / permissions / publishing)  
  - Exposes “governed datasets” with lineage, data quality checks, and access tags  
  - Publishes different data views and access policies for different roles (exec/ops/market)

Typical core objects:

- Sales flow wide table: sales facts aggregated by customer/product/region/time; serves as the baseline for both exec dashboards and Sales Copilot  
- Inventory snapshot wide table: inventory status by warehouse/product/time; supports replenishment analysis and recommendation filters  
- Dimension tables: customer, product, region, channel, time, etc., providing unified metric definitions

---

### 4.2 DNA Feature Model (Feature Layer)

The DNA layer is a feature layer designed for AI. It organizes configurable feature tables by entity (customer/product/territory) to support recommendation algorithms and LLM capabilities:

- Feature organization  
  - Split by entity: Customer DNA, Product DNA, Territory DNA, etc.  
  - Each entity has a configurable set of feature columns, such as historical sales, growth rate, inventory turnover, visit frequency, and fulfillment rate
- Feature sources  
  - Primarily aggregated from Transform/Governed wide tables to ensure consistency with DDP definitions  
  - Also brings in application-side signals (e.g., recommendation feedback, clicks/adoption)
- Usage  
  - Serves as input data for AI training and inference, supporting Sales Copilot’s ranking and filtering logic  
  - Through a method registry and notebook templates, supports quickly adding or deprecating features, enabling pluggable dimensions and fact tables

With the DNA layer, models can quickly evolve feature combinations for different AI experiments and markets without disturbing the core DDP model.

---

### 4.3 NGSE Application Database Model

In the NGSE application database, we design a lightweight, application-oriented model around “sales opportunity management + AI recommendation results”:

- Opportunity and account model  
  - Opportunity table: stores status, stage, expected revenue, and other attributes for each sales opportunity  
  - Account/customer table: connected to the DDP customer dimension and enriched with business fields (e.g., owner, coverage territory)
- Recommendation and task model  
  - Recommendation result table: records Sales Copilot recommendations (recommended object, score, rationale, feature snapshot used)  
  - Task/to-do table: converts some recommendations into actionable sales tasks for follow-up and closure
- Audit and monitoring model  
  - Log table: records each AI call, input/output summary, model version, and latency  
  - Audit views: transparent views for compliance/risk teams to review recommendation distribution and adoption

Data in the application database is mainly sourced from the Governed layer and the DNA feature layer, written back periodically via Databricks jobs or stored procedures. This ensures consistency with the warehouse while meeting online applications’ requirements for query performance and simple schema.

---

## 5. Pipeline & Scheduling Architecture

NGSE’s orchestration relies on ADF + Databricks Workflows + Azure Functions to connect the full chain of “cross-cloud transfer → DDP layered jobs → DNA feature refresh → application write-back”.

- Unified orchestration in ADF  
  - ADF manages linked services and integration runtimes and handles file transfer from Aliyun OSS to ADLS Gen2  
  - Triggers Databricks notebooks/jobs to run the Inbox→Raw→Transform→Governed pipelines on daily/hourly schedules  
  - Configures retry policies and failure alerts for critical pipelines to ensure batch stability
- Modularization with Databricks Workflows  
  - Breaks ingestion/cleansing/join/aggregation into atomic jobs and connects them through dependencies and global_temp/temp/intermediate tables  
  - Uses Delta versioning and wide-table snapshots to accelerate debugging and replay
- Event-driven Azure Functions  
  - Receives data quality results (schema drift, field completeness, null/duplicate ratios) and triggers email/Teams alerts  
  - Calls Databricks REST APIs to trigger backfills, reruns, or downstream jobs based on business events or validation outcomes
- Application and AI refresh  
  - Periodically refreshes DNA feature tables to provide up-to-date feature snapshots for Sales Copilot  
  - Syncs aggregates and recommendation results to the NGSE application database and Power BI semantic layer via batch write-back or APIs

Together this forms a hybrid “schedule + event” orchestration model: regular batch processing via ADF/Workflows, with Azure Functions handling exceptions and business-driven triggers.

---

## 6. Performance Optimization

Performance optimization focuses on the lakehouse architecture and Delta Lake features, aiming to meet SLAs for both AI training and BI queries.

- Delta Lake versioning and transactions  
  - Leverage Delta for batch replay and full/incremental switching  
  - Combine T-1 full data with incremental difference checks to keep large tables such as sales/product flow accurate at ~99.5% even under high throughput
- Partitioning and Z-Order  
  - Partition wide tables for sales and inventory by date/region/product  
  - Use Z-Order on high-frequency filter fields (such as market, product_id) to improve scan efficiency
- Wide tables and dual-channel consumption  
  - Build unified wide tables in the Transform/Governed layers so that a single dataset can serve both AI training and Power BI queries  
  - Reduce duplicate aggregations across multiple models and lower IO and maintenance cost
- Compute path optimization  
  - Encapsulate common ETL modules (encryption/masking/path parsing/dynamic parameters) to avoid duplicate implementations and redundant operators  
  - Centralize feature generation in the DNA layer to avoid repeated calculations in the application layer

In practice, key inventory/sales reports run about 2–3x faster, meeting exec dashboard timeliness requirements and leaving sufficient window for AI training.

---

## 7. Governance & Security

Governance and security combine “lakehouse + PromptOps + data export/import compliance” as three parallel tracks that cover both data and AI.

- Data governance  
  - DDP layering (Inbox/Raw/Transform/Governed) plus metadata catalog and method registry track data lineage and method dependencies  
  - Automated data quality checks: schema drift, field completeness, null/duplicate ratios, implemented via Databricks jobs and Azure Functions for alerts and closure  
  - T-1 difference checks on key tables such as sales and product flows as a daily quality red line
- Access control and compliance  
  - Role/group management via Azure AD with different access levels for Exec/Director/Ops/Vendor roles  
  - Governed-layer masked views and authorization policies to control cross-region and cross-team access  
  - Under Chinese data export/import regulations, clearly separate data that can be used for AI training from data that must remain local only
- PromptOps and AI governance  
  - Establish prompt templates, versions, and owner management for Sales Copilot and bring them into change management processes  
  - Define LLM usage boundaries and blocked scenarios for sensitive use cases, and manage risk via prompt QA, manual sampling, and keyword alerts  
  - Log all AI calls with input/output summaries and model versions to support auditing and replay

---

## 8. Challenges & Solutions

| Challenge                                                                 | Solution                                                                                                      |
|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| How to land global NGSE data and AI capabilities under Chinese data laws | Build a local DDP and AI engine in China, synchronize only compliant fields, and clearly separate local/global data and model boundaries |
| Differences between global standard models and local distributor/sales models in fields, granularity, and metrics | Use DDP layered modeling and field mapping matrices to align definitions and publish unified semantic wide tables in the Governed layer |
| High data quality and timeliness requirements for AI training and recommendations | Introduce Delta, T-1 difference checks, and automated quality rules to ensure 99.5% accuracy and optimize pipelines to meet training/query windows |
| Explainability and risk control for recommendation algorithms and prompts in a regulated scenario | Build a combined Sales Copilot recommendation algorithm + PromptOps framework with prompt QA, audit logs, and high-risk keyword alerts |
| Need for reuse of warehouse standards and pipelines across multiple markets and teams | Modularize notebooks/ETL/method registry and adopt the DNA architecture to create a reusable blueprint for replication to four additional markets |

---

## 9. Achievements

- Performance and quality  
  - Key inventory/sales reports run 2–3x faster, meeting SLAs for both AI training and BI queries  
  - T-1 difference checks cover core wide tables, keeping data accuracy at around 99.5%
- AI effectiveness  
  - Sales Copilot achieves ~70% recommendation hit rate and saves each salesperson about 6 hours per week in lead preparation and triage  
  - Established training/test/validation dataset bundles that support model regression testing and regulatory sampling
- Organization and reuse  
  - Defined company-level lakehouse and prompt governance standards, reused across four markets with zero high-severity risk incidents  
  - NGSE China has been incorporated into the global reference blueprint for sales digitization

---

## 10. Personal Contributions

My responsibilities:

- Roadmap and architecture  
  - Led the architecture design for the NGSE China DDP and AI engine, defining the overall Inbox→Raw→Transform→Governed + DNA feature layer blueprint  
  - Participated in global and local roadmap discussions and translated data compliance and business requirements into technical solutions
- Pipelines and modeling  
  - Built cross-cloud pipelines (Aliyun OSS → ADLS Gen2) and decomposed ingestion/cleansing/join/aggregation into manageable steps  
  - Designed and implemented wide tables for sales/inventory and DNA feature tables to support both BI and AI dual-channel consumption
- Quality and governance  
  - Designed and implemented Delta + T-1 difference checks and automated quality rules (schema drift, field completeness, null/duplicates)  
  - Unified metadata and method registry standards, connecting DDP layers and application layer for lineage and access control
- AI and PromptOps  
  - Defined Sales Copilot recommendation algorithms and PromptOps workflows, and organized prompt QA, risk reviews, and postmortems  
  - Coordinated among exec, risk, and business teams to align on compliance boundaries and explainability requirements
- Replication and enablement  
  - Curated reusable notebook templates, ETL modules, and DNA architecture patterns to support rapid rollout in additional markets  
  - Enabled local data engineering and analytics teams and helped establish routines for daily operations and optimization

---

## 11. Summary

The NGSE project delivers a data platform in China that balances “lakehouse architecture, AI capabilities, and compliance governance”. It provides a local DDP mirror and high-quality training data for the global sales engine, delivers recommendation capabilities to frontline sales through Sales Copilot, and supports multi-market expansion with a replicable architecture and governance framework.
