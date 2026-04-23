from pydantic import BaseModel, Field
from typing import Optional


class ClarifyRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=2000)


class ClarifyData(BaseModel):
    clarified: str
    model: str
    tokens_used: int
    input_mode: str | None = None
    id: int | None = None


class ClarifyResponse(BaseModel):
    success: bool
    data: Optional[ClarifyData] = None
    error: Optional[str] = None


class DialecticStartRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=2000)
    persona_id: Optional[str] = Field(None, max_length=64)


class DialecticContinueRequest(BaseModel):
    session_id: str
    user_response: str = Field(..., min_length=1, max_length=2000)


class DialecticState(BaseModel):
    current_claim: Optional[str] = None
    surfaced_assumptions: Optional[list[str]] = None
    active_tension: Optional[str] = None
    loop_step: int = 1
    is_complete: bool = False


class DialecticTurn(BaseModel):
    step: int
    role: str
    content: str
    created_at: Optional[str] = None


class DialecticResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    state: Optional[DialecticState] = None
    response: Optional[str] = None
    turns: Optional[list[DialecticTurn]] = None
    step_label: Optional[str] = None
    error: Optional[str] = None


class PersonaSummary(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    cognitive_lens: str
    is_premium: bool = False


class PersonasResponse(BaseModel):
    success: bool
    data: Optional[list[PersonaSummary]] = None
    error: Optional[str] = None
