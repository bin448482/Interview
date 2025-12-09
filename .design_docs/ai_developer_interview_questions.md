# AI Developer Interview – Practice Question Bank

Use this file to practice answering questions one by one in writing or aloud.

## 1. Deep Dive on Your AI Projects

- Walk me through the architecture of your *MySixth Tarot Card Intelligent Application* (mobile, backend, admin, AI generator). What are the main components and how do they interact?
- Explain the dual-stage AI pipeline (`/readings/analyze` vs `/readings/generate`). Why did you design it that way?
- How does your unified LLM factory work? How do you route between OpenAI / GLM / Ollama? What are your fallback rules?
- How did you achieve the 60% cost reduction while keeping TP99 latency under ~1.2s?
- How do you implement prompt governance and versioning in TarotAI? How do you run A/B tests on prompts and measure impact?
- Describe the telemetry and dashboards you built (conversion, retention, cohorts). How do they feed into product and prompt decisions?
- What was the hardest engineering problem in TarotAI, and how did you solve it?

## 2. LLM / RAG / Agent Fundamentals

- Explain RAG. When would you use RAG vs fine-tuning?
- How would you design a RAG system with ChromaDB for a knowledge base? Walk through ingestion, chunking, embeddings, retrieval, and generation.
- How do you choose chunk size and overlap? What problems occur if you choose badly?
- How do you reduce hallucinations in an LLM application?
- Describe a LangChain agent or tool-calling workflow you’ve built. How do you handle failures and timeouts?
- What’s your approach to prompt design for tools/agents (system vs user prompts, few-shot examples, constraints)?
- How would you log and evaluate LLM outputs in production?

## 3. AI System Design & Architecture

- Design an AI assistant for the company’s product or vertical. How would the architecture look from frontend to LLM to data stores?
- Suppose we need a chat + document-QA feature for enterprise users. How would you design it for reliability, latency, and cost?
- How would you design multi-tenant support and rate limiting for an LLM API?
- What’s your approach to secrets management, PII handling, and audit logging in AI systems?
- How would you design a monitoring system for an LLM service (app metrics + model quality metrics)?

## 4. Metrics, Evaluation, and Experimentation

- In your AI products, what north star metrics did you define and why?
- How do you evaluate LLM quality offline and online? What concrete metrics do you track?
- Describe an experiment you ran (A/B test on prompts, paywall, or funnel). How did you design it and interpret the results?
- How do you detect degradation in model behavior after a model or prompt update?
- Give an example of a time metrics contradicted stakeholder intuition. What did you do?

## 5. Coding & Implementation (Python / Web / Data)

- In Python, how would you implement a simple FastAPI endpoint that calls an LLM and handles timeouts and retries?
- How would you structure a small AI microservice (packages, config, clients, tests) so it is maintainable?
- What are good patterns for wrapping an LLM provider (factory, adapter) to support multiple vendors?
- How would you implement idempotent job processing for batch generation (like your tarot content generator)?
- Describe how you’d profile and optimize a slow inference or data-preprocessing pipeline.

## 6. Data / Lakehouse Background

- Tell me about the Databricks lakehouse you built. How did you design the data model and pipelines?
- How did you integrate AI (recommendations, copilots) into your data platform?
- What data-quality and governance controls did you implement before feeding data to models?

## 7. Responsible AI, Risk, and Governance

- What are the main risks you consider when deploying LLMs in production?
- How do you implement guardrails (content filters, prompt patterns, human-in-the-loop)?
- Describe your approach to bias, safety, and compliance in AI systems you’ve shipped.

## 8. Behavioral & Leadership

- Tell me about a time you led an AI project end-to-end. What was your role vs the team’s?
- Describe a situation where engineering and product disagreed about an AI feature or risk. How did you handle it?
- Give an example of a time you had to cut scope or simplify a model to hit a deadline.
- How do you work with non-technical stakeholders to explain AI limitations and trade-offs?

