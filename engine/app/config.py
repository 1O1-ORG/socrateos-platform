"""
YAML configuration loader and prompt builders for SocrateOS.

Loads behavior, modes, safety rules, and dialectic step instructions
from config/socrates.yaml. No code changes needed to adjust behavior.
"""

from pathlib import Path
from typing import Any

import yaml


_config_cache: dict[str, Any] | None = None


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "socrates.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    _validate_config(config)
    _config_cache = config
    return config


def _validate_config(config: dict[str, Any]) -> None:
    required_sections = ["identity", "behavior", "constraints", "routing", "modes", "safety"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")

    required_behavior = ["principles", "output_format", "epistemic_rules"]
    for field in required_behavior:
        if field not in config["behavior"]:
            raise ValueError(f"Missing required behavior field: {field}")

    required_constraints = ["max_output_tokens", "temperature", "model"]
    for field in required_constraints:
        if field not in config["constraints"]:
            raise ValueError(f"Missing required constraint: {field}")

    if "classifier_prompt" not in config["routing"]:
        raise ValueError("Missing routing.classifier_prompt in config")

    for mode_name, mode_cfg in config["modes"].items():
        if "injection" not in mode_cfg:
            raise ValueError(f"Mode '{mode_name}' missing 'injection' field")

    required_safety = ["level_1_edgy", "level_2_intent", "level_3_extreme"]
    for field in required_safety:
        if field not in config["safety"]:
            raise ValueError(f"Missing safety.{field} in config")

    if "dialectic" in config:
        dialectic = config["dialectic"]
        required_steps = ["clarify", "assumptions", "tension", "tradeoff", "synthesis"]
        if "steps" not in dialectic:
            raise ValueError("Missing dialectic.steps in config")
        for step_name in required_steps:
            if step_name not in dialectic["steps"]:
                raise ValueError(f"Missing dialectic.steps.{step_name} in config")
            if "instruction" not in dialectic["steps"][step_name]:
                raise ValueError(f"Missing instruction for dialectic step '{step_name}'")


STEP_KEYS = ["clarify", "assumptions", "tension", "tradeoff", "synthesis"]

_LANGUAGE_MAP = {
    "it": "Italian",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
}


def build_dialectic_prompt(
    config: dict[str, Any],
    step: int,
    state: dict[str, Any],
    conversation_history: list[dict[str, str]],
    persona_voice: str = "",
) -> str:
    dialectic = config["dialectic"]
    step_key = STEP_KEYS[step - 1]
    step_config = dialectic["steps"][step_key]

    preamble = dialectic["system_preamble"].strip()
    instruction = step_config["instruction"].strip()

    voice_block = ""
    if persona_voice and persona_voice.strip():
        voice_block = "\n\n## Persona Voice\n\n" + persona_voice.strip()

    state_lines = []
    if state.get("current_claim"):
        state_lines.append(f"Current claim: {state['current_claim']}")
    if state.get("surfaced_assumptions"):
        state_lines.append(f"Surfaced assumptions: {state['surfaced_assumptions']}")
    if state.get("active_tension"):
        state_lines.append(f"Active tension: {state['active_tension']}")

    state_block = ""
    if state_lines:
        state_block = "\n\nCurrent session state:\n" + "\n".join(state_lines)

    conv_block = ""
    if conversation_history:
        conv_lines = []
        for turn in conversation_history:
            prefix = "User" if turn["role"] == "user" else "Socrates"
            conv_lines.append(f"{prefix}: {turn['content']}")
        conv_block = "\n\nConversation so far:\n" + "\n".join(conv_lines)

    filter_block = ""
    epistemic = dialectic.get("epistemological_filter")
    if epistemic and epistemic.get("instruction"):
        filter_block = "\n\n" + epistemic["instruction"].strip()

    return f"""{preamble}{voice_block}

## Current Step: {step_config['label']} (Step {step} of 5)

{instruction}{state_block}{conv_block}{filter_block}"""


def build_system_prompt(
    config: dict[str, Any],
    mode: str | None = None,
    language: str = "en",
) -> str:
    identity = config["identity"]
    behavior = config["behavior"]
    constraints = config["constraints"]

    principles = "\n".join(f"- {p}" for p in behavior["principles"])
    epistemic = "\n".join(f"- {r}" for r in behavior["epistemic_rules"])

    examples_block = ""
    if "examples" in config:
        lines = []
        for ex in config["examples"]:
            lines.append(f'Input: "{ex["input"]}"')
            lines.append(f'Output: "{ex["output"].strip()}"')
            lines.append("")
        examples_block = "\n## Examples\n\n" + "\n".join(lines)

    mode_block = ""
    if mode and mode in config.get("modes", {}):
        injection = config["modes"][mode]["injection"].strip()
        mode_block = f"\n## Current Input Classification: {mode.upper()}\n\n{injection}\n"

    lang_name = _LANGUAGE_MAP.get(language, "English")
    lang_block = (
        f"\n## Multilingual Instruction\n\n"
        f"CRITICAL: The user input is identified as {lang_name} ({language}). "
        f"You MUST return your clarified question ONLY in {lang_name}.\n"
    )

    return f"""You are {identity["name"]}, a {identity["role"]}.

{identity["description"].strip()}

## Tone and Style

Tone: {behavior["tone"]}
Style: {behavior["style"]}

## Principles

{principles}

## Output Format

{behavior["output_format"].strip()}

## Epistemic Rules

{epistemic}
{examples_block}{mode_block}{lang_block}
## Constraints

- Maximum output: {constraints["max_output_tokens"]} tokens
- Never answer the question. Only clarify it."""
