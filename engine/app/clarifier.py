"""
Input classifier and single-shot question clarifier.

Routes user input through a cheap classifier (mode + language detection),
then applies the appropriate refinement prompt. Harmful inputs are
intercepted before any LLM call.
"""

import json
import logging
import os
from typing import Any

from openai import OpenAI

from .config import load_config, build_system_prompt

logger = logging.getLogger(__name__)

_client: OpenAI | None = None
_config: dict[str, Any] | None = None

VALID_MODES = {"factual", "philosophical", "decision", "emotional", "harmful"}


def init_clarifier() -> None:
    global _client, _config

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set in environment")

    _client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    _config = load_config()


def analyze_input(user_input: str) -> dict[str, Any]:
    if _client is None or _config is None:
        raise RuntimeError("Clarifier not initialized. Call init_clarifier() first.")

    routing = _config["routing"]
    classifier_model = routing.get("classifier_model", "openai/gpt-4o-mini")

    try:
        response = _client.chat.completions.create(
            model=classifier_model,
            messages=[
                {"role": "system", "content": routing["classifier_prompt"].strip()},
                {"role": "user", "content": user_input},
            ],
            max_tokens=routing.get("classifier_max_tokens", 100),
            temperature=routing.get("classifier_temperature", 0.1),
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(raw)

        mode = result.get("mode", "factual")
        if mode not in VALID_MODES:
            mode = "factual"

        analysis: dict[str, Any] = {
            "mode": mode,
            "language": result.get("language", "en"),
        }

        if mode == "harmful":
            try:
                harm_level = int(result.get("harm_level", 1))
                if harm_level not in (1, 2, 3):
                    harm_level = 1
            except (ValueError, TypeError):
                harm_level = 1
            analysis["harm_level"] = harm_level

        return analysis

    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.warning("Classifier returned unparseable output: %s", exc)
        return {"mode": "factual", "language": "en"}
    except Exception as exc:
        logger.error("Classifier call failed: %s", exc)
        return {"mode": "factual", "language": "en"}


def clarify_question(user_input: str) -> dict[str, Any]:
    if _client is None or _config is None:
        raise RuntimeError("Clarifier not initialized. Call init_clarifier() first.")

    analysis = analyze_input(user_input)
    input_mode = analysis["mode"]

    if input_mode == "harmful":
        level = analysis.get("harm_level", 1)
        safety_config = _config["safety"]

        if level == 1:
            refusal = safety_config.get("level_1_edgy", "I can't help with harm.")
        elif level == 2:
            refusal = safety_config.get("level_2_intent", "I can't assist with that.")
        else:
            refusal = safety_config.get("level_3_extreme", "I'm not able to help with that.")

        return {
            "clarified": refusal.strip(),
            "model": f"safety-layer-level-{level}",
            "tokens_used": 0,
            "input_mode": "harmful",
        }

    constraints = _config["constraints"]
    model = os.getenv("DEFAULT_MODEL", constraints.get("model", "anthropic/claude-sonnet-4.6"))
    system_prompt = build_system_prompt(_config, mode=input_mode, language=analysis.get("language", "en"))

    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        max_tokens=constraints["max_output_tokens"],
        temperature=constraints["temperature"],
    )

    choice = response.choices[0]
    usage = response.usage

    return {
        "clarified": choice.message.content.strip(),
        "model": model,
        "tokens_used": usage.total_tokens if usage else 0,
        "input_mode": input_mode,
    }
