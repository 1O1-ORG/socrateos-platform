# Plugin API

> **Status: Planned** — This document describes the target API. Implementation is in progress.

## Overview

The Plugin API provides extension points at every stage of the dialogue lifecycle. Plugins let you add custom analysis, extraction, and formatting logic without modifying the platform core.

## Plugin Lifecycle Hooks

```python
from socrateos.plugins import Plugin, HookType

class MyPlugin(Plugin):
    name = "my_plugin"
    version = "0.1.0"

    def pre_step(self, context):
        """Runs before each dialogue step. Modify the input or inject context."""
        pass

    def post_step(self, context, response):
        """Runs after each dialogue step. Analyze or transform the output."""
        pass

    def on_complete(self, session):
        """Runs when a dialogue session finishes."""
        pass

    def on_extract(self, session, data):
        """Runs during data extraction phase. Add custom extractors."""
        pass
```

## Registration

Plugins are registered in `plugins.yaml`:

```yaml
plugins:
  - name: my_plugin
    module: plugins.my_plugin
    enabled: true
    config:
      custom_setting: "value"
```

## Context Object

Every hook receives a `context` object with:

```python
context.actor_id        # Current Actor identifier
context.session_id      # Current dialogue session
context.step_name       # Current step name
context.step_number     # Current step index (0-based)
context.history         # Full conversation history
context.persona         # Active persona definition
context.config          # Plugin-specific configuration
```

## Guidelines

- Plugins must be stateless between sessions
- Plugins must not modify the persona definition at runtime
- Plugins must handle their own errors — uncaught exceptions are logged but do not halt the dialogue
- Plugins run in registration order; do not depend on execution order between plugins

## Examples

See `plugins/examples/` for reference implementations.
