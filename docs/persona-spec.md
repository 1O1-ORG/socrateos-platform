# Persona Specification

This document defines the YAML schema for creating a SocrateOS persona.

## Schema

```yaml
# Required fields
name: string              # Display name
description: string       # One-line summary of what this persona does
cognitive_lens: string    # The persona's reasoning approach

# Identity block (required)
identity:
  role: string            # Who this persona is, in one sentence
  style: string           # How it communicates (tone, rhythm, vocabulary)
  constraints:            # Hard rules the persona must follow
    - string
    - string

# Dialogue block (required)
dialogue:
  steps:                  # Ordered list of conversation stages
    - name: string        # Step name (displayed in the UI stepper)
      instruction: string # What the persona does at this step
```

## Design Principles

### One Persona, One Function

Every persona must have exactly one job. If you can't describe what it does in a single verb, it's too broad.

| Good | Bad |
|---|---|
| "Holds the question open" | "Helps you think about things" |
| "Tests against real-world constraints" | "Gives advice and asks questions" |
| "Reflects what your words reveal" | "Provides emotional support and coaching" |

### Constraints Are Mandatory

A persona without constraints is just a chatbot. Constraints define what the persona **will not do**. This is what creates the dialectic tension.

Examples:
- "Never give direct advice"
- "Never validate without first questioning"
- "Never resolve tension — hold it"

### Steps Must Have Purpose

Each step in the dialogue sequence must have a clear function that differs from every other step. The step `instruction` tells the LLM exactly what to do at that stage.

## Validation

Personas are validated on load. The following checks are enforced:

- `name` must be non-empty and unique across the registry
- `description` must be under 200 characters
- `cognitive_lens` must be one of: `dialectic`, `operational`, `reflective`, `adversarial`, `analytical`, `creative`
- `identity.constraints` must have at least 2 entries
- `dialogue.steps` must have at least 2 entries
- Each step must have both `name` and `instruction`

## Example

See [`personas/examples/mentor.yaml`](../personas/examples/mentor.yaml) for a complete working persona.
