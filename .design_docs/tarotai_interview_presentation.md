# TarotAI – Omnichannel Tarot + AI Readings (Interview Deck)

---

## Slide 1 – Title

**TarotAI: Omnichannel Tarot with Structured AI Guidance**

- Candidate: [Your Name]
- Role: LLM Engineer
- Date: [Interview Date]
- Tagline: Expo React Native · FastAPI · Next.js · GLM‑4 / OpenAI

---

## Slide 2 – Who I Am (LLM Engineer)

**About Me**

- Background: LLM‑oriented engineer with X years of full‑stack experience
- What I am good at:
  - Designing and shipping LLM features end‑to‑end
  - Turning fuzzy product ideas into concrete APIs, prompts, and data flows
  - Operating systems in production, not just demos
- Ways of working:
  - Start from thin vertical slices, then harden with tests, logs, and alerts
  - Use telemetry and experiments to debug quality, latency, and cost
  - Communicate clearly with PMs, designers, and other engineers

---

## Slide 3 – Problem & TarotAI in One Page

**TarotAI in One Slide**

- Problem:
  - People want low‑friction emotional reflection without the overhead of therapy
  - Tarot readings are subjective, offline, and hard to revisit or quantify
  - Existing apps often feel spammy or shallow, with little long‑term value
- Solution:
  - TarotAI: an anonymous, cross‑platform tarot companion
  - Flow: choose spread → write intent → draw cards → view layered results
  - Static card meanings plus AI‑generated narratives that can be optionally upgraded
- My role:
  - Designed the intent and emotion tagging pipeline and core LLM prompt flows
  - Implemented key backend APIs and orchestration for LLM calls in FastAPI
  - Drove iteration using logs, user feedback, and internal dogfooding

---

## Slide 4 – System Overview (Architecture & Data Flow)

**System Overview**

- Surfaces:
  - Mobile: Expo React Native (iOS / Android, anonymous users + local SQLite)
  - Backend: FastAPI + SQLite (readings, payments, content, logs)
  - Admin: Next.js + Ant Design (content, dashboards, operations)
- Core flow:
  - Client sends intent, spread, and card selection to FastAPI
  - Backend runs intent and emotion tagging, then tarot engine logic
  - LLM pipeline generates structured interpretations when AI reading is enabled
- LLM responsibilities:
  - Normalize user intent into dimensions and "vibes"
  - Generate card‑aware narratives with clear structure and guardrails
  - Return outputs with metadata to support logging, analysis, and upsell

---

## Slide 5 – "Vibe Coding" as AI Pair Programming

**Vibe Coding – Me as Navigator, AI as Accelerator**

- Definition:
  - "Vibe coding" = my workflow for co‑developing with LLMs
  - I own constraints, behavior, and quality; AI helps explore options and write drafts
- How I use AI:
  - Use LLMs for endpoint skeletons, prompt variants, and alternative designs
  - Provide concrete examples, non‑goals, and failure cases as context
  - Keep critical pieces (data contracts, safety rules, monitoring) under tight manual control
- Applied to TarotAI:
  - Bootstrapped core APIs and UI screens with AI assistance
  - Iterated on prompts using side‑by‑side outputs, logs, and qualitative review
  - Converged on a small set of stable prompt patterns and tags

---

## Slide 6 – Dimension-based Readings: Offline + Online

**Dimension-based Readings – Finite Dimensions, Infinite Questions**

- Structure:
  - Break readings into "dimension × card × emotion" combinations
  - Example: career / relationships / self‑growth × strengths / obstacles / advice
  - Attach intent and emotion tags (e.g. anxious / hopeful / curious)
- Offline mode (precomputed):
  - Pre‑compute interpretations for all combinations with AI and store as structured data
  - Ship them in local databases or static assets for fully offline readings
  - Benefits: low latency, predictable cost, stable minimum quality
- Online mode (long‑tail):
  - Free‑form intent → tagging pipeline → online LLM call
  - Handles long‑tail questions and complex personal context
  - Adds extra explanations and tailored reflection prompts
- Strategy:
  - Offline layer guarantees structure and a quality floor
  - Online layer adds personalization where it has the highest impact

---

## Slide 7 – Tech Stack & LLM Engineering Choices

**Technical Highlights**

- Stack:
  - Mobile: Expo React Native 0.81 + Expo Router 6
  - Backend: Python + FastAPI 0.104, SQLAlchemy, Uvicorn
  - Admin: Next.js + Tailwind CSS + Ant Design
  - LLM: GLM‑4 + OpenAI, behind a thin, pluggable client abstraction
  - Storage: SQLite per service, Expo SQLite on device
- LLM engineering:
  - Modular tarot engine so prompts stay model‑agnostic and reusable
  - Dual‑phase API (`/analyze`, `/generate`) for better observability and control
  - Anonymous identity (`installation_id`) for analytics and cohort studies
  - Logging:
    - End‑to‑end chain of `input → tags → prompt → output` for debugging and A/B tests
    - Reading and payment events for funnel and retention analysis
  - Quality and safety:
    - Validate tone against emotion tags (e.g. anxious → calmer, grounded language)
    - Guard against over‑promising, repetition, and harmful "fortune‑telling" patterns

---

## Slide 8 – Soft Skills in the Project

**Soft Skills Demonstrated**

- End‑to‑end ownership:
  - Took TarotAI from idea to working product across mobile, backend, admin, and LLM flows
  - Defined success metrics around quality, latency, and engagement
- Problem solving:
  - Treat issues as signals: symptom → logs → root cause → reusable fix
  - Example: stabilized "noisy" outputs by introducing the dual‑phase `analyze` / `generate` pipeline
- Collaboration:
  - Explain LLM behavior with simple concepts (vibes, tags, dimensions)
  - Use those concepts to collaborate with non‑ML teammates on UX and safety

---

## Slide 9 – Key Learnings & Role Fit

**Key Learnings & Why It Matters for an LLM Engineer Role**

- Key learnings:
  - Encoding vibes, dimensions, and tags makes LLM systems much more controllable
  - Emotion‑sensitive use cases require safety, empathy, and clear non‑goals from day one
  - A small, stable schema plus good logs can drive large quality gains before heavy modeling work
  - Omnichannel products benefit from a shared events and identity model
- Role fit:
  - I design and ship complete LLM features, not one‑off "call the API" endpoints
  - I balance model quality with UX, latency, safety, and cost
  - I can turn messy product ideas into concrete prompts, contracts, and metrics

---

## Slide 10 – Q&A

**Q&A**

- Happy to go deeper into:
  - The "vibe coding" workflow and how it could scale in your stack
  - TarotAI’s prompt architecture, tagging pipeline, and safety constraints
  - How I would adapt these patterns to your current product, data, and infra

