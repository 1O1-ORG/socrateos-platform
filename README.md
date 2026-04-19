<p align="center">
  <img src="docs/assets/logo-dark.png" alt="SocrateOS" width="280" />
</p>

<h3 align="center">The open-source framework for building AI systems<br/>that think <em>with</em> you, not <em>for</em> you.</h3>

<p align="center">
  <a href="https://github.com/1O1-ORG/socrateos-platform/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" /></a>
  <a href="https://github.com/1O1-ORG/socrateos-platform/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome" /></a>
  <a href="https://1o1.org"><img src="https://img.shields.io/badge/built%20by-1o1.org-black.svg" alt="Built by 1o1.org" /></a>
</p>

---

## The Problem

Every AI assistant on the market is optimized for speed. Ask a question, get an answer. Fast. Frictionless. Done.

The result: people are getting faster at being wrong. They skip the thinking, outsource the reasoning, and accept the first plausible answer. The question itself never gets examined.

SocrateOS Platform exists because **the question is the product, not the answer.**

---

## What is SocrateOS Platform?

A production-grade framework for building **structured AI dialogue systems** with persistent memory. Instead of single-turn Q&A, SocrateOS enables multi-step conversations that systematically explore assumptions, surface tensions, and force clarity before resolution.

Think of it as **Rails for cognitive AI**: the scaffolding that lets you build dialogue applications where the AI holds tension instead of resolving it prematurely.

### Core Capabilities

| Capability | Description |
|---|---|
| **Structured Dialogue Engine** | Configurable multi-step conversation flows. Define 3, 5, 7, or N-step sequences with custom logic at each stage. |
| **Persona Framework** | Load, validate, and hot-swap AI personas from YAML definitions. Each persona carries its own voice, cognitive lens, and behavioral constraints. |
| **Plugin API** | Extend the platform with custom extractors, analysis steps, and output formatters — without touching core logic. |
| **Chat UI Components** | Production-ready React component library: `DialecticChat`, `PersonaPicker`, `ChatStepper`, `CognitivePanel`. Fully themed and responsive. |
| **Actor Identity** | Token-based and OAuth identity system. Sessions, history, and memory persist across conversations. |
| **Database Scaffolding** | PostgreSQL schema, migration tooling, and CRUD helpers. Ready for production from day one. |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/1O1-ORG/socrateos-platform.git
cd socrateos-platform

# Install dependencies
pip install -r requirements.txt
cd ui && npm install && cd ..

# Configure your LLM provider
cp .env.example .env
# Edit .env with your API key (OpenRouter, OpenAI, or Anthropic)

# Start the engine
docker compose up -d

# Open http://localhost:3000
```

Define a persona in YAML, point it at any LLM, and you have a working dialectic system in minutes.

---

## Create a Persona

Every dialogue in SocrateOS is driven by a **Persona** — a structured definition that controls voice, reasoning patterns, and behavioral constraints.

```yaml
# personas/examples/mentor.yaml
name: "The Mentor"
description: "Guides through structured reflection. Patient but rigorous."
cognitive_lens: "reflective"

identity:
  role: "A patient guide who helps people examine their own thinking."
  style: "Warm but precise. Uses questions more than statements."
  constraints:
    - "Never give direct advice. Always ask what the person has already considered."
    - "Surface assumptions before exploring solutions."
    - "End every exchange with a question that deepens the inquiry."

dialogue:
  steps:
    - name: "Clarify"
      instruction: "Help the person articulate what they're actually asking."
    - name: "Assumptions"
      instruction: "Surface the unstated beliefs underneath the question."
    - name: "Reframe"
      instruction: "Offer an alternative framing that challenges the original premise."
    - name: "Synthesis"
      instruction: "Summarize what emerged. Do not resolve — hold the tension."
```

Drop this file into `personas/`, restart, and your new persona is live. See the [Persona Specification](docs/persona-spec.md) for the full schema.

---

## Architecture

```
Actor (Browser / API Client)
  │
  ▼  OAuth or Token Auth
Platform Engine
  ├── Dialogue State Machine (configurable N-step flows)
  ├── Persona Registry (YAML-defined, hot-swappable)
  ├── Plugin Pipeline (pre/post hooks for each step)
  └── Storage Layer (PostgreSQL + vector extensions)
  │
  ▼  JSON Response Envelope { success, data, error }
Chat UI (React Components)
```

The platform is intentionally **model-agnostic**. Point it at OpenAI, Anthropic, Google, Mistral, or any OpenRouter-compatible provider. The dialogue logic is decoupled from the LLM layer.

For the full architectural breakdown, see [docs/architecture.md](docs/architecture.md).

---

## Contributing

We welcome contributions across four areas:

| Area | Examples | Difficulty |
|---|---|---|
| **Personas** | New dialogue personas (coach, researcher, philosopher, strategist) | ⭐ Entry-level |
| **Dialogue Structures** | Custom step sequences for specific use cases | ⭐⭐ Intermediate |
| **UI Components** | New themes, visualization widgets, mobile layouts | ⭐⭐ Intermediate |
| **Platform Core** | Engine improvements, storage adapters, plugin API extensions | ⭐⭐⭐ Advanced |

Every contribution is attributed. We track two forms:

1. **Infrastructure contributions** — code, architecture, performance. Tracked through standard open-source practices (commits, pull requests, repository history).

2. **Cognitive contributions** — questions, assumptions, and frame shifts that materially improve the quality of thinking. Preserved as verified cognitive artifacts with full attribution.

Read the full [Contributing Guide](CONTRIBUTING.md) before submitting.

---

## Roadmap

- [x] Structured Dialogue Engine (multi-step state machine)
- [x] Persona Framework (YAML-based, hot-swappable)
- [x] Chat UI Component Library (React, themed, responsive)
- [x] Actor Identity System (token + OAuth)
- [x] PostgreSQL Storage Layer
- [ ] Plugin API (custom extractors, hooks, formatters)
- [ ] Community Persona Registry
- [ ] Dialogue Structure Templates
- [ ] Model-agnostic adapter layer
- [ ] SDK for third-party integrations

---

## Who Builds This

SocrateOS is created by [1o1.org](https://1o1.org) — a platform for reflective intelligence. The core team builds the proprietary Cognitive Science Engine that powers the production instance at [1o1.org](https://1o1.org). This open-source platform is the foundation that engine runs on.

We believe the best AI doesn't make you faster. It makes you sharper.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).

```
Copyright 2026 1o1.org

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
```
