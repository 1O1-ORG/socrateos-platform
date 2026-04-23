# Architecture

## System Overview

SocrateOS is a two-service application:

1. **Engine** (Python/FastAPI) — the dialectic reasoning backend
2. **UI** (Next.js/React) — the chat interface

The engine uses SQLite for persistence and OpenRouter as a unified LLM gateway.
No external databases, no GPU requirements, no heavyweight dependencies.

## Request Flow

```
User types a thought
       │
       ▼
   [Next.js UI]
       │ POST /api/dialectic/start
       ▼
   [FastAPI Engine]
       │
       ├─▶ [Input Classifier]
       │     Cheap LLM call (gpt-4o-mini)
       │     Returns: mode + language + harm_level
       │
       ├─▶ [Safety Layer]
       │     If mode == "harmful": return refusal, skip LLM
       │
       ├─▶ [Prompt Builder]
       │     Loads config from socrates.yaml
       │     Constructs system prompt for current step
       │     Injects: persona voice + state + conversation history
       │
       ├─▶ [LLM Call]
       │     OpenRouter API (any model)
       │     Parses response + strips epistemic trailer
       │
       ├─▶ [State Update]
       │     SQLite: update session state, insert turn
       │
       └─▶ Response: { session_id, state, response, turns, step_label }
```

## Database Schema

```sql
dialectic_sessions
├── id (TEXT PK)
├── original_input
├── input_mode
├── loop_step (1-5)
├── is_complete
├── current_claim
├── surfaced_assumptions (JSON array)
├── active_tension
├── persona_id
├── created_at
└── updated_at

dialectic_turns
├── id (INTEGER PK)
├── session_id (FK → sessions)
├── step
├── role (user | system)
├── content
├── model
├── tokens_used
├── cognitive_metadata (JSON)
└── created_at

personas
├── id (TEXT PK)
├── slug (UNIQUE)
├── name
├── description
├── icon
├── system_instruction
├── cognitive_lens
├── is_premium
├── is_active
└── created_at
```

## Epistemological Filter

Every LLM response includes a machine-readable trailer:

```xml
<cognitive_meta>
{"classifications":[
  {"text":"claim paraphrase","category":"FACT|INFERENCE|SPECULATION"}
]}
</cognitive_meta>
```

The engine strips this before returning the visible response to the user.
The metadata is stored in `dialectic_turns.cognitive_metadata` for analysis.

## Configuration

All behavior is controlled by `engine/config/socrates.yaml`:

- **identity** — who Socrates is
- **behavior** — tone, style, principles, output format, epistemic rules
- **constraints** — model, temperature, token limits
- **routing** — classifier model and prompt
- **modes** — per-classification prompt injections
- **safety** — 3-level refusal messages
- **dialectic** — system preamble, epistemological filter, 5 step instructions

Change the YAML, restart the server. No code modifications needed.

## Persona System

Personas are cognitive lenses that modify Socrates' approach without
changing the underlying 5-step protocol. Each persona provides:

- `system_instruction` — injected into the system prompt as "Persona Voice"
- `cognitive_lens` — a label describing the reasoning approach

The persona voice is layered before step instructions, so the dialectic
structure remains identical regardless of which persona is active.
