# Architecture

## System Overview

SocrateOS Platform is a modular framework with four primary subsystems:

```
┌─────────────────────────────────────────────────┐
│                   Chat UI Layer                  │
│         React Components · CSS Modules           │
├─────────────────────────────────────────────────┤
│                  Platform Engine                 │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐ │
│  │  Dialogue    │  │ Persona  │  │  Plugin    │ │
│  │  Engine      │  │ Registry │  │  Pipeline  │ │
│  └──────┬───────┘  └────┬─────┘  └─────┬──────┘ │
│         │               │              │         │
│  ┌──────▼───────────────▼──────────────▼──────┐ │
│  │           Actor Identity Layer              │ │
│  └──────────────────┬─────────────────────────┘ │
├─────────────────────┼───────────────────────────┤
│                     ▼                            │
│              Storage Layer                       │
│        PostgreSQL · pgvector · Migrations        │
└─────────────────────────────────────────────────┘
```

## Subsystems

### Dialogue Engine

The core state machine that drives structured conversations. Each dialogue follows a configurable sequence of steps, where each step has:

- **Name**: displayed in the UI stepper
- **Instruction**: injected into the LLM system prompt
- **Transition logic**: conditions for advancing to the next step

The engine is step-count agnostic. Define 3 steps or 12. The state machine handles progression, history tracking, and session persistence.

### Persona Registry

Loads persona definitions from YAML files, validates them against the schema, and makes them available to the dialogue engine at runtime.

Personas are hot-swappable: change the YAML file, restart the service, and the new persona is live. No code changes required.

See [Persona Specification](persona-spec.md) for the full schema.

### Plugin Pipeline

Extension points at every stage of the dialogue lifecycle:

- `pre_step`: runs before each dialogue step (input preprocessing)
- `post_step`: runs after each dialogue step (output analysis)
- `on_complete`: runs when a dialogue session finishes
- `on_extract`: runs during any data extraction phase

Plugins are Python classes that inherit from the base `Plugin` class and register for specific hooks.

### Actor Identity

Token-based and OAuth identity system. Each Actor (the person using the system) has:

- A unique persistent token
- Session history
- Optional OAuth identity (Google, GitHub)
- Memory context from prior sessions

### Storage Layer

PostgreSQL with pgvector extension for vector similarity operations. The schema is managed through idempotent migrations that run on startup.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Frontend | Next.js, React, TypeScript, CSS Modules |
| Database | PostgreSQL 18 + pgvector |
| LLM Gateway | OpenRouter (model-agnostic) |
| Deployment | Docker Compose, Traefik |

## API Convention

All API responses follow the envelope format:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Error responses:

```json
{
  "success": false,
  "data": null,
  "error": "Human-readable error description"
}
```
