# Contributing to SocrateOS Platform

Thank you for your interest in contributing. This document outlines the standards and process for contributing to the SocrateOS Platform.

## Guiding Principle

SocrateOS is not a chatbot. It is a framework for structured thinking. Every contribution must serve that mission: helping people ask better questions, not giving them faster answers.

If your contribution generates generic advice, resolves tension prematurely, or produces output that could come from any AI assistant, it will be rejected.

---

## Contribution Areas

### 1. Personas (Entry-Level)

A Persona defines how the AI engages in dialogue. Each persona has a unique voice, cognitive lens, and set of behavioral constraints.

**Requirements:**
- Defined in YAML following the [Persona Specification](docs/persona-spec.md)
- Must have a clear, singular function (what does this persona DO that no other persona does?)
- Must include behavioral constraints (what this persona will NOT do)
- Must include at least 3 dialogue steps with specific instructions
- Must be tested against the platform before submission

**Submission:**
- Place your persona file in `personas/community/`
- Open a PR with the title: `[Persona] <Name> — <One-line description>`
- Include 3 example conversations in the PR description showing the persona in action

### 2. Dialogue Structures (Intermediate)

A Dialogue Structure defines the step sequence and transition logic for a conversation type.

**Requirements:**
- Clear use case (coaching, research, decision-making, etc.)
- Each step must have a defined purpose and transition condition
- Must include entry and exit criteria
- Must be tested with at least 2 different personas

**Submission:**
- Place your structure in `dialogue/templates/`
- Open a PR with title: `[Dialogue] <Name> — <Use case>`

### 3. UI Components (Intermediate)

New themes, visualization widgets, or interaction patterns for the chat interface.

**Requirements:**
- Built with React and CSS Modules (no Tailwind)
- Fully responsive (mobile-first)
- Accessible (WCAG 2.1 AA minimum)
- No inline styles. Use design tokens from the theme system.
- Must work in both light and dark mode

**Submission:**
- Place components in `ui/components/`
- Include a visual demo (screenshot or recording) in the PR

### 4. Platform Core (Advanced)

Engine improvements, storage adapters, plugin API extensions.

**Requirements:**
- Must not break the existing plugin or persona API contracts
- Must include tests
- Python: type hints on every function, no bare `except`, parameterized SQL
- TypeScript: no `any`, strict mode, CSS Modules
- Comments only for non-obvious decisions (why, not what)

**Submission:**
- Open an issue first to discuss the approach before writing code
- PRs without a linked issue will be closed

---

## Code Standards

### Python
- snake_case for functions and variables
- Type hints on every function signature
- All SQL uses parameter substitution — no string-built queries
- No bare `except` blocks — catch specific exceptions
- One concern per file; keep modules under 500 lines

### TypeScript / React
- camelCase for functions and variables
- No `any` type — use proper interfaces
- CSS Modules for all styling — no inline styles, no utility classes
- Components must be self-contained and reusable

### General
- All API responses follow: `{ success, data, error }`
- Comments explain WHY, never WHAT — code should be self-documenting
- No placeholder content. If it's not ready, don't ship it.

---

## Review Process

1. **Automated checks**: lint, type-check, build verification
2. **Architectural review**: does this fit the platform's design?
3. **Quality review**: does this meet the code standards above?
4. **Mission alignment**: does this help people think better, or just think faster?

PRs that pass all four gates are merged. Typical review time: 3-5 business days.

---

## Attribution

Every merged contribution is attributed in the project's contributor graph. We track both infrastructure contributions (code) and cognitive contributions (ideas, frameworks, and insights that shape the platform's direction).

Select contributions may be highlighted in the project's public contributor showcase.

---

## Code of Conduct

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). Be respectful, be constructive, be direct. No fluff.

---

## Questions?

Open an issue with the `[Question]` tag, or reach out at [contact@1o1.org](mailto:contact@1o1.org).
