"""
5-step dialectic state machine.

Guides a user through structured thinking: Clarify → Assumptions →
Tension → Tradeoff → Synthesis. Each step is a single LLM call
with carefully constructed system prompts.

This is the open-core version: no cognitive graph extraction,
no cross-session memory, no post-session background tasks.
"""

import json
import logging
import re
import uuid
from typing import Any

from openai import OpenAI

from .clarifier import analyze_input
from .config import STEP_KEYS, build_dialectic_prompt, load_config
from .db import (
    get_active_model,
    get_dialectic_session,
    get_dialectic_turns,
    get_persona,
    get_persona_by_slug,
    insert_dialectic_session,
    insert_dialectic_turn,
    set_session_persona,
    update_dialectic_state,
)

logger = logging.getLogger(__name__)

MAX_STEPS = 5

_COGNITIVE_META_RE = re.compile(
    r"<cognitive_meta>\s*(.*?)\s*</cognitive_meta>",
    re.DOTALL | re.IGNORECASE,
)
_COGNITIVE_META_UNCLOSED_RE = re.compile(
    r"<cognitive_meta>\s*(.*)",
    re.DOTALL | re.IGNORECASE,
)
_BARE_COGNITIVE_JSON_RE = re.compile(
    r'\s*\{"\s*classifications\s*"\s*:.*',
    re.DOTALL | re.IGNORECASE,
)


def _get_client() -> OpenAI:
    from .clarifier import _client
    if _client is None:
        raise RuntimeError("Clarifier not initialized. Call init_clarifier() first.")
    return _client


def _parse_assumptions(raw: Any) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(a) for a in raw if a]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else [raw]
        except (json.JSONDecodeError, TypeError):
            return [raw] if raw.strip() else []
    return []


def _build_state_dict(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "current_claim": session.get("current_claim"),
        "surfaced_assumptions": _parse_assumptions(session.get("surfaced_assumptions")),
        "active_tension": session.get("active_tension"),
        "loop_step": session.get("loop_step", 1),
        "is_complete": bool(session.get("is_complete", 0)),
    }


def _try_parse_meta(candidate: str) -> str | None:
    candidate = candidate.strip()
    candidate = re.sub(r"</cognitive_meta>\s*$", "", candidate, flags=re.IGNORECASE).strip()
    if not candidate:
        return None
    try:
        parsed = json.loads(candidate)
        return json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        return None


def _split_epistemic_trailer(raw: str) -> tuple[str, str | None]:
    if not raw:
        return raw, None

    match = _COGNITIVE_META_RE.search(raw)
    if match:
        visible = _COGNITIVE_META_RE.sub("", raw).strip()
        meta = _try_parse_meta(match.group(1))
        if meta is None:
            logger.warning("Dropping malformed cognitive_meta (closed tag)")
        visible = _BARE_COGNITIVE_JSON_RE.sub("", visible).strip()
        return visible, meta

    match = _COGNITIVE_META_UNCLOSED_RE.search(raw)
    if match:
        visible = raw[:match.start()].strip()
        meta = _try_parse_meta(match.group(1))
        if meta is None:
            logger.warning("Dropping malformed cognitive_meta (unclosed tag)")
        visible = _BARE_COGNITIVE_JSON_RE.sub("", visible).strip()
        return visible, meta

    bare = _BARE_COGNITIVE_JSON_RE.search(raw)
    if bare:
        visible = raw[:bare.start()].strip()
        meta = _try_parse_meta(bare.group(0))
        if meta is None:
            logger.warning("Dropping malformed bare cognitive JSON")
        return visible, meta

    return raw.strip(), None


def _call_llm(system_prompt: str, user_message: str, config: dict[str, Any]) -> dict[str, Any]:
    client = _get_client()
    dialectic_cfg = config["dialectic"]
    model = get_active_model() or dialectic_cfg.get("model", "anthropic/claude-sonnet-4.6")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=dialectic_cfg.get("max_output_tokens", 500),
        temperature=dialectic_cfg.get("temperature", 0.4),
    )

    choice = response.choices[0]
    usage = response.usage
    visible, cognitive_meta = _split_epistemic_trailer((choice.message.content or "").strip())

    return {
        "content": visible,
        "cognitive_metadata": cognitive_meta,
        "model": model,
        "tokens_used": usage.total_tokens if usage else 0,
    }


def _serialize_turns(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "step": t["step"],
            "role": t["role"],
            "content": t["content"],
            "created_at": t.get("created_at"),
        }
        for t in turns
    ]


def _safety_refusal(config: dict[str, Any], level: int) -> str:
    safety = config["safety"]
    if level == 1:
        return safety.get("level_1_edgy", "I can't help with harm.").strip()
    if level == 2:
        return safety.get("level_2_intent", "I can't assist with that.").strip()
    return safety.get("level_3_extreme", "I'm not able to help with that.").strip()


def _resolve_persona(persona_id: str | None) -> dict[str, Any] | None:
    if persona_id:
        p = get_persona(persona_id)
        if p and p.get("is_active"):
            return p
    return get_persona_by_slug("socrates")


def _persona_voice(persona: dict[str, Any] | None) -> str:
    if not persona:
        return ""
    return str(persona.get("system_instruction") or "")


def create_session(
    user_input: str,
    persona_id: str | None = None,
) -> dict[str, Any]:
    config = load_config()
    session_id = str(uuid.uuid4())

    analysis = analyze_input(user_input)
    input_mode = analysis["mode"]

    if input_mode == "harmful":
        refusal = _safety_refusal(config, analysis.get("harm_level", 1))
        return {
            "session_id": session_id,
            "state": {
                "current_claim": None,
                "surfaced_assumptions": [],
                "active_tension": None,
                "loop_step": 0,
                "is_complete": True,
            },
            "response": refusal,
            "turns": [
                {"step": 0, "role": "user", "content": user_input},
                {"step": 0, "role": "system", "content": refusal},
            ],
            "step_label": "Safety",
        }

    insert_dialectic_session(
        session_id=session_id,
        original_input=user_input,
        input_mode=input_mode,
    )
    persona = _resolve_persona(persona_id)
    if persona:
        try:
            set_session_persona(session_id, str(persona["id"]))
        except Exception:
            logger.exception("Failed to bind persona %s to session %s", persona.get("id"), session_id)

    insert_dialectic_turn(session_id, step=1, role="user", content=user_input)

    system_prompt = build_dialectic_prompt(
        config,
        step=1,
        state={"current_claim": None, "surfaced_assumptions": [], "active_tension": None},
        conversation_history=[{"role": "user", "content": user_input}],
        persona_voice=_persona_voice(persona),
    )
    result = _call_llm(system_prompt, user_input, config)

    insert_dialectic_turn(
        session_id,
        step=1,
        role="system",
        content=result["content"],
        model=result["model"],
        tokens_used=result["tokens_used"],
        cognitive_metadata=result.get("cognitive_metadata"),
    )
    update_dialectic_state(session_id, loop_step=1, current_claim=user_input)

    session = get_dialectic_session(session_id)
    turns = get_dialectic_turns(session_id)
    step_label = config["dialectic"]["steps"][STEP_KEYS[0]]["label"]

    return {
        "session_id": session_id,
        "state": _build_state_dict(session),
        "response": result["content"],
        "turns": _serialize_turns(turns),
        "step_label": step_label,
    }


def advance_session(session_id: str, user_response: str) -> dict[str, Any]:
    config = load_config()

    session = get_dialectic_session(session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")
    if session["is_complete"]:
        raise ValueError("Session is already complete")

    current_step = session["loop_step"]
    next_step = current_step + 1
    if next_step > MAX_STEPS:
        raise ValueError("Session has reached maximum steps")

    insert_dialectic_turn(session_id, step=current_step, role="user", content=user_response)

    turns = get_dialectic_turns(session_id)
    conversation = [{"role": t["role"], "content": t["content"]} for t in turns]
    state = _build_state_dict(session)
    persona = _resolve_persona(session.get("persona_id"))

    system_prompt = build_dialectic_prompt(
        config,
        step=next_step,
        state=state,
        conversation_history=conversation,
        persona_voice=_persona_voice(persona),
    )
    result = _call_llm(system_prompt, user_response, config)

    insert_dialectic_turn(
        session_id,
        step=next_step,
        role="system",
        content=result["content"],
        model=result["model"],
        tokens_used=result["tokens_used"],
        cognitive_metadata=result.get("cognitive_metadata"),
    )

    is_complete = next_step >= MAX_STEPS
    state_updates: dict[str, Any] = {"loop_step": next_step, "is_complete": is_complete}

    if next_step == 2:
        state_updates["surfaced_assumptions"] = json.dumps([user_response], ensure_ascii=False)
    elif next_step == 3:
        state_updates["active_tension"] = result["content"]
    elif next_step == 4:
        existing = _parse_assumptions(state.get("surfaced_assumptions"))
        existing.append(user_response)
        state_updates["surfaced_assumptions"] = json.dumps(existing, ensure_ascii=False)

    if is_complete:
        state_updates["current_claim"] = result["content"]

    update_dialectic_state(session_id, **state_updates)

    session = get_dialectic_session(session_id)
    all_turns = get_dialectic_turns(session_id)
    step_label = config["dialectic"]["steps"][STEP_KEYS[next_step - 1]]["label"]

    return {
        "session_id": session_id,
        "state": _build_state_dict(session),
        "response": result["content"],
        "turns": _serialize_turns(all_turns),
        "step_label": step_label,
    }


def get_session(session_id: str) -> dict[str, Any] | None:
    config = load_config()
    session = get_dialectic_session(session_id)
    if session is None:
        return None

    turns = get_dialectic_turns(session_id)
    step_idx = min(session["loop_step"], MAX_STEPS) - 1
    step_label = config["dialectic"]["steps"][STEP_KEYS[step_idx]]["label"]

    return {
        "session_id": session_id,
        "state": _build_state_dict(session),
        "turns": _serialize_turns(turns),
        "step_label": step_label,
        "original_input": session["original_input"],
        "created_at": session["created_at"],
    }
