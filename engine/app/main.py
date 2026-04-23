"""
SocrateOS — Open-Core Dialectic Engine API

A self-contained FastAPI application for structured dialectic reasoning.
Run with: uvicorn app.main:app --reload --port 8000
"""

import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .clarifier import clarify_question, init_clarifier
from .db import list_active_personas
from .dialectic import advance_session, create_session, get_session
from .logger import init_logger, log_interaction
from .models import (
    ClarifyRequest, ClarifyResponse, ClarifyData,
    DialecticStartRequest, DialecticContinueRequest, DialecticResponse,
    DialecticState, DialecticTurn,
    PersonaSummary, PersonasResponse,
)

load_dotenv()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    init_clarifier()
    try:
        from . import personas_seed
        personas_seed.seed()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Persona seed failed at startup")
    yield


app = FastAPI(
    title="SocrateOS",
    description=(
        "Open-core dialectic engine. Guides structured thinking through "
        "a 5-step Socratic method: Clarify → Assumptions → Tension → "
        "Tradeoff → Synthesis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
origins = [o.strip() for o in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/clarify", response_model=ClarifyResponse)
@limiter.limit(os.getenv("RATE_LIMIT", "10/minute"))
async def clarify(request: Request, body: ClarifyRequest) -> ClarifyResponse:
    session_id = str(uuid.uuid4())

    try:
        result = clarify_question(body.input)
    except Exception as e:
        return ClarifyResponse(success=False, error=str(e))

    row_id = log_interaction(
        session_id=session_id,
        user_input=body.input,
        clarified_output=result["clarified"],
        model=result["model"],
        tokens_used=result["tokens_used"],
        input_mode=result.get("input_mode"),
    )

    return ClarifyResponse(
        success=True,
        data=ClarifyData(
            clarified=result["clarified"],
            model=result["model"],
            tokens_used=result["tokens_used"],
            input_mode=result.get("input_mode"),
            id=row_id,
        ),
    )


@app.post("/api/dialectic/start", response_model=DialecticResponse)
@limiter.limit(os.getenv("RATE_LIMIT", "10/minute"))
async def dialectic_start(request: Request, body: DialecticStartRequest) -> DialecticResponse:
    try:
        result = create_session(
            body.input,
            persona_id=body.persona_id,
        )
    except Exception as e:
        return DialecticResponse(success=False, error=str(e))

    return DialecticResponse(
        success=True,
        session_id=result["session_id"],
        state=DialecticState(**result["state"]),
        response=result["response"],
        turns=[DialecticTurn(**t) for t in result["turns"]],
        step_label=result["step_label"],
    )


@app.post("/api/dialectic/continue", response_model=DialecticResponse)
@limiter.limit(os.getenv("RATE_LIMIT", "10/minute"))
async def dialectic_continue(
    request: Request, body: DialecticContinueRequest,
) -> DialecticResponse:
    try:
        result = advance_session(body.session_id, body.user_response)
    except ValueError as e:
        return DialecticResponse(success=False, error=str(e))
    except Exception as e:
        return DialecticResponse(success=False, error=str(e))

    return DialecticResponse(
        success=True,
        session_id=result["session_id"],
        state=DialecticState(**result["state"]),
        response=result["response"],
        turns=[DialecticTurn(**t) for t in result["turns"]],
        step_label=result["step_label"],
    )


@app.get("/api/dialectic/session/{session_id}", response_model=DialecticResponse)
async def dialectic_get_session(request: Request, session_id: str) -> DialecticResponse:
    result = get_session(session_id)
    if result is None:
        return DialecticResponse(success=False, error="Session not found")

    return DialecticResponse(
        success=True,
        session_id=result["session_id"],
        state=DialecticState(**result["state"]),
        turns=[DialecticTurn(**t) for t in result["turns"]],
        step_label=result["step_label"],
    )


@app.get("/api/personas", response_model=PersonasResponse)
@limiter.limit("60/minute")
async def list_personas_endpoint(request: Request) -> PersonasResponse:
    try:
        rows = list_active_personas()
    except Exception as exc:
        return PersonasResponse(success=False, error=str(exc))
    return PersonasResponse(
        success=True,
        data=[
            PersonaSummary(
                id=str(r["id"]),
                slug=str(r["slug"]),
                name=str(r["name"]),
                description=r.get("description"),
                icon=r.get("icon"),
                cognitive_lens=str(r["cognitive_lens"]),
                is_premium=bool(r.get("is_premium", False)),
            )
            for r in rows
        ],
    )
