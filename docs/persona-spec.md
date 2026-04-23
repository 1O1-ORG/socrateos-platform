# Persona Specification

Personas are cognitive lenses that modify how Socrates approaches a
dialectic conversation. The 5-step protocol stays the same; the
persona changes the voice, framing, and emphasis.

## Schema

Each persona has these fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `persona_id` | string (UUID) | Yes | Unique identifier |
| `slug` | string | Yes | URL-safe identifier (lowercase, hyphens ok) |
| `name` | string | Yes | Display name |
| `description` | string | No | Short description (1-2 sentences) |
| `icon` | string | No | Emoji or icon reference |
| `system_instruction` | string | Yes | Injected into the system prompt |
| `cognitive_lens` | string | Yes | Label for the reasoning approach |
| `is_premium` | bool | No | Whether this persona is premium (default: false) |

## How It Works

The `system_instruction` is injected into the dialectic system prompt
as a "Persona Voice" section, placed after the preamble but before
the step instruction. This means:

1. The persona sets the tone and framing
2. The step instruction provides the specific task
3. The epistemological filter remains mandatory

The persona never overrides the 5-step structure or the safety layer.

## Example: Adding a Persona

In `engine/app/personas_seed.py`:

```python
upsert_persona(
    persona_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "socrateos.stoic")),
    slug="stoic",
    name="Marcus Aurelius",
    description=(
        "Stoic emperor. Separates what you control from what you don't. "
        "Focuses on virtue, duty, and rational acceptance."
    ),
    icon="🏛️",
    system_instruction=(
        "You reason through the lens of Stoic philosophy. "
        "Separate what the person can control from what they cannot. "
        "Emphasize virtue over outcome, duty over desire, and rational "
        "acceptance over emotional reaction. Reference Stoic principles "
        "when introducing tension. Plain prose only, no lists."
    ),
    cognitive_lens="stoic reasoning",
)
```

## Guidelines for Good Personas

1. **One verb per persona.** Each persona should have a clear primary action:
   "challenge", "reframe", "ground", "provoke", etc.

2. **Don't override the protocol.** The system_instruction adjusts
   voice and emphasis. It should not try to skip steps or change the
   dialectic structure.

3. **Be specific.** "Think critically" is useless. "Identify the
   unstated power dynamics in every assumption" is useful.

4. **Keep it short.** The system_instruction competes for context
   window space with conversation history. 3-5 sentences max.

5. **Plain prose.** Instruct the persona to avoid markdown, lists,
   and formatting. The engine enforces this, but explicit instruction
   helps.

## Testing a Persona

1. Add the persona to `personas_seed.py`
2. Restart the engine (the seed runs on startup)
3. Start a session with `persona_id`:

```bash
curl -X POST http://localhost:8000/api/dialectic/start \
  -H "Content-Type: application/json" \
  -d '{"input": "I feel stuck in my career", "persona_id": "YOUR_PERSONA_ID"}'
```

4. Verify the response reflects the persona's cognitive lens
5. Run a full 5-step session to confirm coherence across steps
