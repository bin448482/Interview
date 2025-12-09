# 大模型应用开发 + RAG 面试 Q&A（中英双语 · 基于 TarotAI 项目）

> 使用建议：  
> - 每个问题：先记住下面的 **英文一句话**，再用中文往外展开。  
> - 项目主线：**塔罗牌智能应用 TarotAI**（Expo RN + FastAPI + Next.js + SQLite + 多家 LLM）。

---

## 1. 岗位理解 & 项目总览  
Role Understanding & Project Overview

**Q1：你怎么理解「大模型应用开发」？和「算法/模型研发」有什么区别？你在当前项目里更偏哪一块？**

- 中文要点：  
  我理解的大模型应用开发，更偏向把已有 LLM 产品化、工程化：包括业务场景设计、系统架构、RAG 方案、Prompt 与评估，而不是从零训练基础模型。  
  在 TarotAI 里，我几乎不做预训练，只在需要时做少量 Prompt 调优和小规模微调；主要精力在：设计四步塔罗流程和双阶段 AI API、用 SQLite 做轻量 RAG 检索、多模型路由和成本/实验体系。

- English key line:  
  - “I see LLM application development as turning foundation models into reliable products — focusing on use cases, system design, RAG, prompts and evaluation — rather than training base models from scratch.”

---

**Q2：用当前项目简单介绍一下：业务背景、整体架构、你的角色。**

- 中文要点：  
  TarotAI 是一款跨平台塔罗应用，目标是让用户在移动端完成抽牌→看牌→付费解读的闭环。  
  架构上：  
  - 前端：Expo React Native 客户端 + Next.js 管理后台  
  - 后端：FastAPI 单体服务，内含 LLM 网关、RAG 检索、支付、提示治理  
  - 数据/RAG：本地 SQLite 保存 Tarot 配置和历史记录，后端检索结构化信息拼 Prompt  
  - AI 工具链：独立 Python CLI 批量生成文案、多语言内容运营  
  我是独立开发者，负责产品定义、架构设计、开发、上线和运营的全链路。

- English key lines:  
  - “In my current project, TarotAI, I’m basically the full‑stack owner: I design the user journey, the LLM/RAG flow, and I also implement the mobile app, backend and admin console end‑to‑end.”  
  - “TarotAI is a cross‑platform tarot reading app built with Expo React Native, FastAPI and Next.js, where users complete a four‑step tarot flow and get paid AI interpretations.”

---

## 2. 大模型基础与调用实践  
LLM Basics & Calling Practice

**Q3：你用过哪些大模型？在当前项目是怎么选型的？**

- 中文要点：  
  TarotAI 里我封了一层 LLM 工厂，目前支持 GLM‑4、OpenAI 系列和本地 Ollama。  
  - 线上主路由选性价比高、中文表现好的模型承担大部分解读；  
  - 批量内容生成、多语言内容用更强或本地模型；  
  - 上层业务只认「模型别名+能力标签」，不直接依赖具体厂商，方便后续切换。

- English key lines:  
  - “In TarotAI I use a small ‘LLM factory’ layer to route between providers like GLM‑4, OpenAI and local Ollama, so the business logic never depends on a single vendor.”  
  - “For day‑to‑day production traffic I prefer cost‑effective models with good Chinese support, and I switch to more capable or local models for batch content generation and experimentation.”

---

**Q4：结合当前项目，说说上下文长度和 KV Cache 对体验和性能的影响。**

- 中文要点：  
  TarotAI 的每次解读要塞进：牌阵配置、每张牌的核心含义、用户问题、部分历史记录。  
  - 上下文长度限制会约束我能放多少配置，所以我通过更细粒度的结构化字段控制 chunk；  
  - 在批量文案生成或多轮生成时，利用 KV Cache 复用前缀，减少重复计算，降低延迟和成本。  

- English key line:  
  - “Context length mainly affects how much tarot configuration and history I can safely pack into a single request; KV cache helps a lot when I batch similar generations or reuse the same prefix.”

---

## 3. RAG 概念 & 在当前项目中的设计  
RAG Concept & Design in This Project

**Q5：用当前项目解释什么是 RAG，这个项目里为什么要用 RAG？**

- 中文要点：  
  我会用白话解释：RAG 就是先从自己的知识库里把相关内容查出来，再让模型在这些真实内容基础上生成，减少瞎编。  
  在 TarotAI 里，我用的是轻量 RAG：  
  - 知识库：本地 SQLite 里的牌阵、牌义、话术模板等；  
  - 检索：按牌 ID、位置、主题等查出对应片段；  
  - 生成：把这些片段以结构化方式塞进 Prompt，再让 LLM 做个性化润色。  
  这样既保证解读不偏离 Tarot 体系，又方便做多语言和 A/B 实验。

- English key lines:  
  - “I usually explain RAG as: first retrieve the most relevant knowledge from your own corpus, then let the LLM generate on top of that, instead of letting it hallucinate from scratch.”  
  - “In TarotAI I use a lightweight RAG setup: a local SQLite database stores tarot spreads, card meanings and copywriting templates, and the backend retrieves the relevant pieces before calling the LLM.”  
  - “This design keeps the interpretations consistent with the tarot system, and it also makes A/B testing and multi‑language copy much easier to manage.”

---

**Q6：在这个项目里，一个完整的 RAG 流程是怎样的？**

- 中文要点（流程）：  
  1. 客户端把抽到的牌阵 ID、牌 ID/正逆位、用户问题发给后端；  
  2. 后端从 SQLite 检索该牌阵、每张牌的牌义关键词、故事、主题话术片段等；  
  3. 组装结构化 Prompt：系统角色 + 用户问题 + 检索片段 + 业务约束；  
  4. 调用 LLM 工厂生成解读；  
  5. 把使用的卡片/配置版本和输出写日志，用于评估和回放。

- English（可口语化概述）：  
  - “A typical flow is: the app sends the spread and cards, the backend retrieves the relevant meanings and templates from SQLite, builds a structured prompt around that context, calls the LLM, and then logs everything with card IDs and config versions for later analysis.”

---

## 4. 知识库 & 检索策略  
Knowledge Base & Retrieval Strategy

**Q7：这个项目的知识库和检索方式是怎样的？为什么暂时不用向量库？**

- 中文要点：  
  Tarot 领域知识量有限且结构化很好，所以我刻意用 SQLite + 规则检索，而不是一上来上向量库。  
  - 多张表按「牌 / 牌阵 / 主题 / 语言 / 风格」拆分；  
  - 检索时用牌 ID、位置、主题、语言等做精确/半精确匹配。  
  优点是：一致性强、可版本化、可 A/B，维护成本低。后续如引入长文本或 UGC，再考虑向量检索。

- English key lines:  
  - “Because the tarot domain is structured and relatively small, I deliberately use structured SQLite + rule‑based retrieval instead of jumping straight to a vector database.”  
  - “I split the knowledge into multiple tables by card, spread, theme and language, and then I select only the snippets that match the user’s cards and question type.”  
  - “The goal is to provide enough concrete context for the LLM, without flooding the prompt with long, noisy descriptions.”

---

**Q8：你是怎么控制「信息够用但不过多」的？**

- 中文要点：  
  - 每张牌只保留 2～3 个核心关键词 + 一段精简故事；  
  - 按牌在牌阵中的位置（过去/现在/未来/建议）选择不同解释角度；  
  - 同一张牌按不同主题（感情/事业）分组，只选与用户问题匹配的一组。  
  相当于用更细粒度的 chunk + 标签控制 Prompt 体积和相关性。

- English（一句话可用）：  
  - “I intentionally keep each card’s context compact and theme‑specific, so the model gets just enough signal without being overloaded.”

---

## 5. 检索评估与优化  
Evaluation & Retrieval Optimization

**Q9：你如何评估当前项目里 RAG 检索是否有效？**

- 中文要点：  
  - 离线：构造标准解读样本，看检索结果是否覆盖关键牌义和关键信号；  
  - 在线：看免费→付费转化率、满意度、退款等业务指标；  
  - 出现「不准/一般」反馈的主题，会抽样回放 Prompt + 输出，对照检索片段修配置。

- English key lines:  
  - “I evaluate retrieval quality in two ways: offline I check whether the selected snippets cover the essential meanings, and online I look at user‑facing metrics like conversion and satisfaction.”  
  - “When a theme repeatedly gets poor feedback, I replay those conversations, inspect which snippets were retrieved, and then adjust the configuration or add better templates.”

---

**Q10：你做过哪些检索相关的优化？**

- 中文要点：  
  一个明显的优化是多语言 Tarot 配置：  
  - 初始版本只按牌 ID+主题匹配，多语言下翻译质量不稳定；  
  - 后来加了「语言+版本」维度，并记录每段话术的转化表现，优先使用表现好的版本；  
  带来的效果是不同语言下的满意度和付费率都有提升。

- English key line:  
  - “One practical win was adding language and version metadata so I could prioritize higher‑performing texts; that improved both user satisfaction and paid conversion.”

---

## 6. Prompt 设计与输出控制  
Prompt Design & Output Control

**Q11：在这个 RAG 场景里，你是怎么设计 Prompt 结构的？**

- 中文要点：  
  TarotAI 的 Prompt 基本结构：  
  1. 角色：设定为有同理心的专业塔罗师；  
  2. 任务：解释当前牌阵/牌面，重点回答用户问题，并给出行动建议；  
  3. 上下文：注入检索到的牌义关键词、故事片段和高转化话术片段（结构化 JSON/Markdown）；  
  4. 输出格式：要求按「整体氛围→逐张牌解释→综合建议→适度引导下一步」的结构输出。  

- English key lines:  
  - “My prompts for TarotAI follow a fixed structure: define the role, describe the task, inject retrieved tarot context, and then require a clear output format.”  
  - “I explicitly tell the model to act as an empathetic tarot reader, to base its reasoning on the provided card meanings, and to end with actionable but non‑medical, non‑legal advice.”

---

**Q12：如何区分「有检索结果」和「无检索结果」，避免模型瞎编？**

- 中文要点：  
  - 检索为空/不完整时，Prompt 里明确说明「当前缺少可靠牌义，只做非常泛化的支持性回答，不给具体预测」，并且业务上不开放付费解读；  
  - 代码层面，如果配置缺失，直接报错提示更新配置，而不是让 LLM 自由发挥。  

- English key line:  
  - “When there is little or no reliable context, I downgrade the experience: the prompt asks for very generic, non‑specific support, and the API refuses to sell a paid interpretation.”

---

## 7. 架构 & 性能优化（RAG 服务）  
Architecture & Performance in the RAG Service

**Q13：结合当前项目，简单讲一下整体架构和性能优化。**

- 中文要点：  
  - 架构：Expo RN 客户端 → FastAPI 单体（嵌入 SQLite + LLM 网关）→ 多家模型提供方；Next.js 管理台共享同一后端，Nginx+Docker Compose 部署。  
  - 性能：  
    - Tarot 配置启动时加载进内存、缩短检索；  
    - FastAPI + Uvicorn 配合异步接口支撑并发；  
    - 针对塔罗解读限制 `max_tokens` 和温度，稳定延迟和输出风格；  
    - 所有调用记录模型、token、延迟，汇总成成本看板调整路由。  

- English key lines:  
  - “Architecturally, TarotAI is a simple but complete stack: Expo RN client, a FastAPI monolith with embedded SQLite and an LLM gateway, plus a Next.js admin panel behind Nginx and Docker Compose.”  
  - “I keep tarot configuration in memory, use FastAPI with asynchronous endpoints, and cap `max_tokens` and temperature per use case to stabilize latency and cost.”  
  - “Every LLM call is logged with model, tokens and latency, so I can build a basic cost dashboard and tune the routing; with these optimizations TP99 latency for paid interpretations stays around one second on a single server.”

---

## 8. 数据、质量评估与安全  
Data, Quality & Safety

**Q14：你在当前项目里如何评估整体 AI 质量？**

- 中文要点：  
  - 业务指标：关注免费→付费转化、留存、退款等；  
  - 采样评审：定期回放 Prompt + 输出，人工打标签（准确/一般/不准/高风险）；  
  - 结果回流到 Prompt 模板和配置表中，驱动下一轮实验。  

- English key lines:  
  - “Quality is monitored through business metrics like free‑to‑paid conversion and retention, combined with sampled human review of prompts and outputs.”

---

**Q15：项目里如何处理隐私和敏感内容？**

- 中文要点：  
  - 身份：客户端使用匿名 `installation_id` 作为主键，邮箱绑定是可选的；  
  - 数据：SQLite 中只存抽牌记录和问题文本，不存支付 PII；  
  - 日志：对请求日志做脱敏，只保留必要分析字段；  
  - 安全：系统 Prompt 中禁止医学/法律建议，后台维护风险话术黑名单，命中就优先下线。  

- English key lines:  
  - “From a data perspective I use an anonymous installation ID as the main identifier, and treat email as optional; tarot questions and interpretations are stored without payment‑system PII.”  
  - “For safety I encode content policies directly in the system prompt — for example, no medical or legal advice — and I maintain a small blacklist of risky phrases in the admin console.”

---

## 9. 行为面 & 影响案例  
Behavioral & Impact Stories

**Q16：说一个这个项目里「效果从不好到明显提升」的优化案例。**

- 中文要点：  
  - 上线初期免费→付费转化一般，我从日志里发现解读太「鸡汤」、缺少具体建议；  
  - 优化：在 RAG 层补充更偏建议型的话术、调整 Prompt 强调具体可执行建议，然后在不同牌阵/主题上做 A/B 测试；  
  - 结果：转化率提升到大约 18% 左右，用户反馈稳定性更好。  

- English key lines:  
  - “At launch the free‑to‑paid conversion was mediocre; after analyzing logs I found the interpretations were too generic, so I enriched the retrieved snippets and rewrote prompts to push for more concrete, actionable advice.”  
  - “I then A/B tested different wording and structures through the admin panel; this moved the paid conversion up to roughly the high‑teens and made user feedback much more stable.”

---

**Q17：如果让你从 0 到 1 再做一个新的大模型 + RAG 业务，你会怎么推进？**

- 中文要点：  
  我通常按这几个步骤来：  
  1. 和产品对齐北极星指标（问题解决率、转化等）；  
  2. 先梳理知识来源，优先用结构化/规则检索能覆盖的部分，必要时再引入向量 RAG；  
  3. 设计最小可用架构：API 网关 + RAG 层 + LLM 网关，先跑通一个核心场景；  
  4. 从第一天就接入埋点和实验能力，搭建基础 Prompt 治理和评估闭环；  
  5. 效果和成本可控后，再逐步引入多模型路由、向量库、重排模型等复杂能力。  

- English key lines:  
  - “More broadly, I tend to drive LLM projects the same way: define the north‑star metric, ship a minimal RAG‑based flow, instrument it from day one, and then iterate with small, measurable experiments on both retrieval and prompts.”

---

