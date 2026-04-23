<p align="center">
  <img src="docs/assets/banner.png" alt="SocrateOS Platform" width="100%" />
</p>

<p align="center">
  <strong>The open-source framework for building AI systems that think <em>with</em> you, not <em>for</em> you.</strong>
</p>

<p align="center">
  <a href="https://github.com/1O1-ORG/socrateos-platform/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square" alt="License" /></a>&nbsp;
  <a href="https://github.com/1O1-ORG/socrateos-platform/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square" alt="PRs Welcome" /></a>&nbsp;
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />&nbsp;
  <img src="https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js" />&nbsp;
  <a href="https://1o1.org"><img src="https://img.shields.io/badge/Built_by-1o1.org-c4a35a?style=flat-square" alt="Built by 1o1.org" /></a>
</p>

<br/>

> *"The unexamined life is not worth living."* — Socrates
>
> Most AI is optimized for speed. Ask a question, get an answer. Fast. Frictionless. Done.
> The result: people are getting faster at being wrong.
>
> **SocrateOS exists because the question is the product, not the answer.**

<br/>

## See the Difference

Before you install anything, see what the system actually does.

**Input:**
> *"Is it better to prioritize extreme transparency with users if it might cause temporary panic?"*

**What SocrateOS returns:**

| Step | What happens |
|:---|:---|
| **Clarify** | *Under what specific circumstances, and for which types of information, is prioritizing extreme transparency — even when it risks causing temporary panic — a more beneficial strategy than phased disclosure, considering the long-term impact on user trust and organizational reputation?* |
| **Assumptions** | The thesis assumes audiences are rational agents who benefit from full information. But that assumption itself is a belief, not a given. Under what conditions does "complete transparency" become a liability? |
| **Tension** | Immediate, unvarnished disclosure respects users as capable agents. But the counterpoint is real: in certain high-stakes situations, unvarnished disclosure could trigger unmanageable chaos. Phased disclosure is not deception; it is responsible crisis management. |
| **Tradeoff** | Choose: do you optimize for long-term trust at the cost of short-term stability, or do you phase disclosure to manage risk at the cost of appearing manipulative? The stakes are personal. |
| **Synthesis** | The goal should be to provide information as promptly as possible, while simultaneously implementing mitigation strategies. Any phasing must be transparent in its purpose, and full truth revealed as soon as safely feasible. |

The system didn't answer the question. It transformed it. The person entered with a binary ("should I be transparent?") and left with a structured map of the real tensions underneath.

That's the product.

<br/>

## The Mars Test: Fastest Demo — 90 Seconds

You need one thing: an [OpenRouter API key](https://openrouter.ai/keys).

```bash
git clone https://github.com/1O1-ORG/socrateos-platform.git
cd socrateos-platform
cp .env.example .env       # Add your API key here
docker compose up -d
```

Open **http://localhost:3000**

Paste this prompt:

> *"I want to launch a new service, but I'm afraid it will fail."*

Watch the system think. Step by step. That's the dialectic.

### Without Docker

```bash
# Backend
cd engine
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API key
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd ui
npm install
npm run dev
```

<br/>

## What is SocrateOS Platform?

A production-grade framework for building **structured AI dialogue systems**. Instead of single-turn Q&A, SocrateOS enables multi-step conversations that systematically explore assumptions, surface tensions, and force clarity before resolution.

**Think of it as Rails for cognitive AI.** Define a persona in YAML. Configure a dialogue flow. Deploy a system where the AI holds tension instead of resolving it prematurely.

### Who This Is For

| You are a... | You can... | Start here |
|:---|:---|:---:|
| **Developer** | Deploy a working dialectic system, build custom personas, extend via plugins | [Fastest Demo](#the-mars-test-fastest-demo--90-seconds) |
| **Contributor** | Design personas, propose dialogue structures, improve the engine | [Contributing](#contributing) |
| **Researcher** | Study the cognitive principles, analyze the dialogue architecture | [Cognitive Principles](#cognitive-principles) |

<br/>

<table>
<tr>
<td width="50%">

### 🏛️ &nbsp; Structured Dialogue Engine

Configurable multi-step conversation flows. The default runs a 5-step Socratic protocol (Clarify → Assumptions → Tension → Tradeoff → Synthesis) with custom transition logic at each stage. Not a chatbot — a structured thinking protocol.

</td>
<td width="50%">

### 🎭 &nbsp; Persona Framework

Load, validate, and hot-swap AI personas from YAML definitions. Each persona carries its own voice, cognitive lens, and behavioral constraints. Build a mentor, a challenger, a strategist.

</td>
</tr>
<tr>
<td width="50%">

### 🔌 &nbsp; Plugin API

Extend the platform with custom extractors, analysis steps, and output formatters. Hook into every stage of the dialogue lifecycle without touching core logic.

</td>
<td width="50%">

### 💬 &nbsp; Chat UI Components

Production-ready Next.js interface with a clean chat experience. Landing page with protocol overview, dialectic session with step indicators, session completion with before/after synthesis.

</td>
</tr>
<tr>
<td width="50%">

### 🔐 &nbsp; Safety Layer

3-level input classifier that intercepts harmful content before any LLM call. Every input is classified by mode (factual, philosophical, decision, emotional, harmful) and routed accordingly.

</td>
<td width="50%">

### 🗄️ &nbsp; Zero-Config Storage

SQLite database with idempotent schema migrations. No external databases to configure. Session state, interaction logs, and persona definitions all persist automatically.

</td>
</tr>
</table>

<br/>

## Create a Persona in 60 Seconds

Every dialogue in SocrateOS is driven by a **Persona** — a structured definition that controls voice, reasoning, and behavioral constraints.

```yaml
# personas/examples/mentor.yaml

name: "The Mentor"
description: "Guides through structured reflection. Patient but rigorous."
cognitive_lens: "reflective"

identity:
  role: "A patient guide who helps people examine their own thinking."
  style: "Warm but precise. Uses questions more than statements."
  constraints:
    - "Never give direct advice."
    - "Surface assumptions before exploring solutions."
    - "End every exchange with a question that deepens the inquiry."

dialogue:
  steps:
    - name: "Clarify"
      instruction: "Help the person articulate what they're actually asking."
    - name: "Assumptions"
      instruction: "Surface the unstated beliefs underneath the question."
    - name: "Reframe"
      instruction: "Offer an alternative framing that challenges the premise."
    - name: "Synthesis"
      instruction: "Summarize what emerged. Do not resolve — hold the tension."
```

Drop this into `personas/`, restart, and your new persona is live.

→ [Full Persona Specification](docs/persona-spec.md)

<br/>

## Extend with Plugins

Plugins hook into the dialogue lifecycle at four points. Here's a concrete example — a plugin that logs cognitive bias patterns detected during synthesis:

```python
from socrateos.plugins import Plugin

class BiasDetector(Plugin):
    name = "bias_detector"
    version = "0.1.0"

    def post_step(self, context, response):
        """Runs after each dialogue step. Analyze the output."""
        if context.step_name != "Synthesis":
            return response

        # Check for common cognitive bias indicators
        bias_signals = {
            "sunk_cost": ["already invested", "come this far", "can't stop now"],
            "confirmation": ["proves that", "as I expected", "confirms my"],
            "anchoring": ["the first option", "originally thought", "started with"],
        }

        detected = []
        text = response.content.lower()
        for bias, indicators in bias_signals.items():
            if any(phrase in text for phrase in indicators):
                detected.append(bias)

        if detected:
            response.metadata["detected_biases"] = detected

        return response

    def on_complete(self, session):
        """Runs when the dialogue session finishes."""
        biases = []
        for step in session.steps:
            biases.extend(step.metadata.get("detected_biases", []))

        if biases:
            session.artifacts.append({
                "type": "bias_report",
                "data": {"biases": biases, "count": len(biases)},
            })
```

Register it in `plugins.yaml`:

```yaml
plugins:
  - name: bias_detector
    module: plugins.bias_detector
    enabled: true
```

The plugin runs automatically. No core code modified. The bias report appears in the session artifacts.

→ [Full Plugin API Documentation](docs/plugin-api.md)

<br/>

## Architecture

```
┌──────────────┐     HTTP      ┌───────────────────────────────┐
│              │ ──────────▶   │  FastAPI Engine (port 8000)    │
│  Next.js UI  │               │                               │
│  (port 3000) │ ◀──────────   │  ┌─────────┐  ┌───────────┐  │
│              │     JSON      │  │Classifier│→ │ Dialectic  │  │
└──────────────┘               │  │(mode +   │  │ 5-Step     │  │
                               │  │ safety)  │  │ State      │  │
                               │  └─────────┘  │ Machine    │  │
                               │               └─────┬─────┘  │
                               │                     │        │
                               │              ┌──────▼──────┐ │
                               │              │  OpenRouter  │ │
                               │              │  (any LLM)   │ │
                               │              └─────────────┘ │
                               │                              │
                               │  ┌──────────┐  ┌──────────┐ │
                               │  │  SQLite   │  │ socrates │ │
                               │  │  (data)   │  │  .yaml   │ │
                               │  └──────────┘  └──────────┘ │
                               └───────────────────────────────┘
```

The platform is **model-agnostic**. Point it at OpenAI, Anthropic, Google, Mistral, or any OpenRouter-compatible provider. The dialogue logic is fully decoupled from the LLM layer.

### Key Files

| File | What it does |
|---|---|
| `engine/app/main.py` | FastAPI endpoints (health, clarify, start, continue, session, personas) |
| `engine/app/dialectic.py` | 5-step dialectic state machine |
| `engine/app/clarifier.py` | Input classifier + 3-level safety layer |
| `engine/app/config.py` | YAML config loader + prompt builders |
| `engine/app/db.py` | SQLite database layer |
| `engine/config/socrates.yaml` | All behavior config (edit this, not code) |
| `ui/src/app/chat/page.tsx` | Chat interface |
| `ui/src/app/page.tsx` | Landing page |

### API Reference

All responses follow `{ success, data|error }` envelope format.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/dialectic/start` | Start a new dialectic session |
| `POST` | `/api/dialectic/continue` | Advance to the next step |
| `GET` | `/api/dialectic/session/{id}` | Retrieve session state |
| `POST` | `/api/clarify` | Single-shot question clarification |
| `GET` | `/api/personas` | List available personas |

→ [Full Architecture Documentation](docs/architecture.md)

<br/>

## Cognitive Principles

SocrateOS is built on six publicly documented principles. These are not aspirational values — they are **constraints the system enforces**.

| # | Principle | What it prevents | What it forces |
|:---:|:---|:---|:---|
| 1 | **The Question Is the Product** | Answer-optimization | System returns sharpened problems, not solutions |
| 2 | **Structured Dialectic** | Free-form conversational drift | Actor moves through layers of reasoning in sequence |
| 3 | **Cognition as Trajectory** | Treating each session as isolated | System tracks patterns, contradictions, and evolution over time |
| 4 | **The Epistemological Stance** | Certainty theater | Every claim classified as FACT, INFERENCE, or SPECULATION |
| 5 | **Personas as Cognitive Lenses** | Generic, overlapping advice | Each persona has exactly one function, one verb |
| 6 | **Actor Agency** | System deciding for the Actor | System holds tension; the Actor decides |

If a principle can't answer "what does this prevent?" and "what does this force?" — it doesn't belong here.

The principles are open. The implementation is proprietary. The platform connects them.

→ [Full Cognitive Principles](docs/cognitive-principles.md)

<br/>

## Open-Core Boundary

This repo contains the open-core foundation. The following capabilities exist in the production system but are **not** included here:

| Proprietary Layer | What It Does |
|---|---|
| **Cognitive Memory Graph** | Cross-session persistence, triple extraction, Personalized PageRank |
| **Multi-Persona Board** | Concurrent dialectic with multiple cognitive lenses |
| **Cognitive Artifacts** | Post-session knowledge objects with share tokens |
| **Ashoka Personas** | Proprietary persona definitions calibrated from 40 years of IP |
| **Predictive Modeling** | Cognitive blind spot anticipation and trajectory analysis |

Infrastructure and extension surface: **public**. Proprietary craft: **private**.

→ [Full IP Boundary Definition](docs/IP_BOUNDARY.md)

<br/>

## Contributing

We welcome contributions across four areas:

| Area | Examples | Entry Point |
|:---|:---|:---:|
| **Personas** | Coaching, research, philosophy, strategy personas | ⭐ |
| **Dialogue Structures** | Custom step sequences for specific use cases | ⭐⭐ |
| **UI Components** | New themes, visualizations, mobile layouts | ⭐⭐ |
| **Platform Core** | Engine improvements, storage adapters, plugin extensions | ⭐⭐⭐ |

Every contribution is attributed. We maintain two forms of credit:

- **Infrastructure contributions** — code, architecture, performance. Tracked through commits and pull requests.
- **Cognitive contributions** — questions, assumptions, and frame shifts that materially improve the platform's design. Preserved as verified cognitive artifacts with full attribution.

→ [Full Contributing Guide](CONTRIBUTING.md)

<br/>

## Roadmap

| Status | Milestone |
|:---:|:---|
| ✅ | Structured Dialogue Engine (5-step Socratic state machine) |
| ✅ | Persona Framework (YAML-based, hot-swappable) |
| ✅ | Chat UI (Next.js, responsive, step indicators) |
| ✅ | Input Classification + Safety Layer |
| ✅ | Epistemological Filter (FACT / INFERENCE / SPECULATION) |
| ✅ | Docker Compose Quickstart (clone → configure → run) |
| 🔄 | Plugin API (custom extractors, hooks, formatters) |
| 🔜 | Community Persona Registry |
| 🔜 | Dialogue Structure Templates |
| 🔜 | Model-agnostic adapter layer |
| 🔜 | SDK for third-party integrations |

<br/>

## Support the Project

The core dialectic engine remains open and free. If you believe in building AI that maps the human mind through structured reflection, consider supporting our infrastructure:

- 💸 **[Fund the Project via Stripe](https://1o1.org/donate)**
- 📊 **[View the Pitch Deck](https://1o1.org/socrates)**

<br/>

## The Team

<table>
<tr>
<td align="center" width="50%">

**[1o1.org](https://1o1.org)**

SocrateOS is built by 1o1.org — a platform for reflective intelligence. The core team builds the proprietary **Cognitive Science Engine** that powers the production instance. This open-source platform is the foundation that engine runs on.

</td>
<td align="center" width="50%">

**The Thesis**

We believe the best AI doesn't make you faster.
It makes you **sharper**.

Every conversation is an opportunity to see what you couldn't see before. SocrateOS is the infrastructure for that kind of thinking.

</td>
</tr>
</table>

<br/>

## License

```
Apache License 2.0
Copyright 2026 1o1.org
```

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.

<br/>

---

<p align="center">
  <sub>Built with conviction by <a href="https://1o1.org">1o1.org</a> · The question is the product.</sub>
</p>
