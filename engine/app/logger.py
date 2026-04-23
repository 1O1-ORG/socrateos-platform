from datetime import datetime, timezone

from .db import init_db, insert_interaction


def init_logger(db_path: str | None = None) -> None:
    init_db(db_path)


def log_interaction(
    session_id: str,
    user_input: str,
    clarified_output: str,
    model: str,
    tokens_used: int,
    input_mode: str | None = None,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    return insert_interaction(
        timestamp=now,
        session_id=session_id,
        user_input=user_input,
        clarified=clarified_output,
        model=model,
        tokens_used=tokens_used,
        input_mode=input_mode,
    )
