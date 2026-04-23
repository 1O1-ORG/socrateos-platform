# IP Boundary: Open-Core vs Proprietary

This document defines what is included in the open-core SocrateOS platform
and what remains proprietary in the production system.

## Design Principle

Infrastructure and extension surface: **public**.
Proprietary craft (Cognitive Science Engine, personas, editorial stance): **private**.

The public repo must be a functioning engine, not a showcase. Anyone should
be able to clone it, run it, and have a real dialectic conversation.

## What Is Public (This Repo)

### Engine
- Full 5-step dialectic state machine (Clarify → Assumptions → Tension → Tradeoff → Synthesis)
- Input classifier with mode detection (factual, philosophical, decision, emotional, harmful)
- 3-level safety layer (intercepts harmful input before any LLM call)
- Epistemological filter (FACT / INFERENCE / SPECULATION classification)
- YAML-driven behavior configuration (edit config, not code)
- Persona format specification and extension API
- Single default Socratic persona (generic baseline)

### Data Layer
- SQLite database (zero external dependencies)
- Per-session state persistence
- Interaction logging

### Interface
- Minimal Next.js chat interface
- Landing page with protocol documentation
- Responsive design

### Infrastructure
- Docker Compose setup (single `docker compose up`)
- OpenRouter integration (any LLM via unified gateway)
- Rate limiting (slowapi)

## What Is Proprietary (Production System)

### Cognitive Engine
- **Cognitive Memory Graph**: cross-session persistence using typed psychological triples
- **Graph extraction**: LLM-powered triple extraction from completed sessions
- **HippoRAG-inspired retrieval**: Personalized PageRank over actor cognitive graphs
- **Memory consolidation**: automatic deduplication and semantic merging
- **Salience decay**: time-based and activation-based node dormancy
- **Embedding search**: HNSW cosine similarity over 384-dim vectors (all-MiniLM-L6-v2)

### Personas
- Proprietary Ashoka persona definitions (system instructions, cognitive lenses)
- Multi-persona board (concurrent dialectic with multiple perspectives)
- Persona-specific editorial calibration

### Artifacts
- Cognitive Artifact minting (post-session knowledge objects)
- Share token generation and public artifact viewing
- Graph delta computation per session

### Identity & Auth
- Google OAuth (Auth.js v5)
- Magic link email authentication
- Actor identity lifecycle and profile management
- Session history and replay

### Platform
- Admin dashboard (KPI metrics, session review, graph explorer)
- Stripe recurring subscription integration
- PostHog analytics
- hCaptcha bot protection
- Production PostgreSQL + pgvector deployment

## Extension Points

The public engine is designed to be extended. Good contribution areas:

1. **New personas** — follow the YAML spec, add to `personas_seed.py`
2. **Language support** — add ISO codes to `_LANGUAGE_MAP` in `config.py`
3. **Alternative LLM providers** — the engine uses OpenAI-compatible API format
4. **UI themes** — the CSS is plain vanilla, easy to customize
5. **Step customization** — edit `socrates.yaml` dialectic steps

The proprietary layer adds persistence, identity, and cognitive modeling
on top of this foundation. The open-core boundary is chosen so that
community contributions strengthen the foundation without requiring
access to the proprietary craft.
