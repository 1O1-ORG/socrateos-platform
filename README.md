<div align="center">

# SocrateOS

**Open-core dialectic reasoning engine.**

Take messy human thinking and run it through structured Socratic inquiry.
Five steps from raw thought to actionable clarity.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000.svg)](https://nextjs.org)

</div>

---

## What Is This

SocrateOS is a dialectic engine that doesn't answer questions — it makes you confront what you're actually asking.

Every session follows a five-step protocol:

1. **Clarify the Claim** — narrow ambiguity, surface what feels unresolved
2. **Surface Assumptions** — identify hidden beliefs taken for granted
3. **Introduce Tension** — present a genuine counterpoint that creates cognitive dissonance
4. **Force a Tradeoff** — choose between competing values with clear stakes
5. **Synthesize a Position** — show how thinking evolved, end with a concrete next step

The engine routes input through a classifier (factual, philosophical, decision, emotional, harmful), applies safety layers, and manages the multi-turn dialectic state machine.

## Quickstart

You need one thing: an [OpenRouter API key](https://openrouter.ai/keys).

```bash
# 1. Clone
git clone https://github.com/1O1-ORG/socrateos-platform.git
cd socrateos-platform

# 2. Configure
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 3. Run
docker compose up -d

# 4. Open
open http://localhost:3000
```

That's it. The engine uses SQLite (zero external databases) and starts in seconds.

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

### Key Files

| File | What it does |
|---|---|
| `engine/app/main.py` | FastAPI endpoints |
| `engine/app/dialectic.py` | 5-step state machine |
| `engine/app/clarifier.py` | Input classifier + safety layer |
| `engine/app/config.py` | YAML config loader + prompt builders |
| `engine/app/db.py` | SQLite database layer |
| `engine/config/socrates.yaml` | All behavior config (edit this, not code) |
| `ui/src/app/chat/page.tsx` | Chat interface |

## API Reference

All responses follow `{ success, data|error }` envelope format.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/dialectic/start` | Start a new dialectic session |
| `POST` | `/api/dialectic/continue` | Advance to the next step |
| `GET` | `/api/dialectic/session/{id}` | Retrieve session state |
| `POST` | `/api/clarify` | Single-shot question clarification |
| `GET` | `/api/personas` | List available personas |

### Start a Session

```bash
curl -X POST http://localhost:8000/api/dialectic/start \
  -H "Content-Type: application/json" \
  -d '{"input": "I think I should quit my job but I am not sure"}'
```

### Continue a Session

```bash
curl -X POST http://localhost:8000/api/dialectic/continue \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "user_response": "I value stability but feel stuck"}'
```

## Building Your Own Persona

Personas are YAML-defined cognitive lenses that change how Socrates approaches a conversation. The engine ships with a single default Socratic persona. You can add more.

See [docs/persona-spec.md](docs/persona-spec.md) for the full specification.

Quick example:

```python
# In engine/app/personas_seed.py, add:
upsert_persona(
    persona_id="your-uuid",
    slug="stoic",
    name="Marcus Aurelius",
    description="Stoic emperor. Focus on what you control.",
    icon="🏛️",
    system_instruction=(
        "You reason through the lens of Stoic philosophy. "
        "Separate what the person controls from what they don't. "
        "Focus on virtue, duty, and rational acceptance."
    ),
    cognitive_lens="stoic reasoning",
)
```

## The Behavior Config

Everything the engine does is controlled by `engine/config/socrates.yaml`. No code changes needed to adjust:

- **Identity** — name, role, description
- **Behavior** — tone, style, principles, output format
- **Modes** — how each input classification modifies the prompt
- **Safety** — refusal messages for harmful input (3 severity levels)
- **Dialectic** — system preamble, epistemological filter, all 5 step instructions
- **Routing** — classifier model, temperature, prompt

Edit the YAML, restart the server.

## Open-Core Boundary

This repo contains the open-core foundation. The following capabilities exist in the production system but are **not** included here:

- Cognitive Memory Graph (cross-session persistence, triple extraction, PPR)
- Multi-persona board (concurrent dialectic with multiple personas)
- Cognitive Artifact minting (post-session knowledge objects)
- OAuth / email authentication
- Admin dashboard and analytics
- Stripe billing integration

See [docs/IP_BOUNDARY.md](docs/IP_BOUNDARY.md) for the full boundary definition.

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-persona`)
3. Follow the patterns in existing code
4. Test locally with `docker compose up`
5. Open a PR with a clear description

Good first contributions:
- New personas (follow the spec in `docs/persona-spec.md`)
- Translations (add language codes to `config.py._LANGUAGE_MAP`)
- UI improvements
- Documentation

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
