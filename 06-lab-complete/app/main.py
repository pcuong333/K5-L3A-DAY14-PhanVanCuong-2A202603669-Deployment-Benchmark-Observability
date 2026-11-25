"""
Production AI Agent — Part 6 Final Project.
"""
import asyncio
import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, record_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask


class JsonFormatter(logging.Formatter):
    """Format every app log record as a single valid JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "lvl": record.levelname,
            "event": getattr(record, "event", "log"),
            "msg": record.getMessage(),
        }
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            payload.update(extra_data)
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

_is_shutting_down = False
_in_flight_requests = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_shutting_down
    logger.info(
        "Agent starting up",
        extra={
            "event": "startup",
            "extra_data": {
                "environment": settings.environment,
                "port": settings.port,
            },
        },
    )
    yield
    _is_shutting_down = True
    logger.info("Agent shutting down gracefully", extra={"event": "shutdown"})
    waited = 0.0
    while _in_flight_requests > 0 and waited < 5.0:
        await asyncio.sleep(0.05)
        waited += 0.05
    logger.info("Shutdown complete", extra={"event": "shutdown_complete"})


app = FastAPI(title="Production AI Agent", lifespan=lifespan)


@app.middleware("http")
async def request_logging_and_tracking(request: Request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        _in_flight_requests -= 1
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "HTTP request",
            extra={
                "event": "request",
                "extra_data": {
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "ms": elapsed_ms,
                },
            },
        )


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str | None = None


@app.get("/health")
def health():
    """Liveness probe: luôn trả 200 khi process còn chạy."""
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/ready")
def ready():
    """Readiness probe: 200 khi sẵn sàng, 503 khi shutdown hoặc Redis lỗi."""
    if _is_shutting_down or not redis_healthy():
        raise HTTPException(status_code=503, detail="Agent not ready")
    return {"ready": True}


@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    check_budget()
    answer = llm_ask(body.question)
    input_tokens = max(1, len(body.question) // 4)
    output_tokens = max(1, len(answer) // 4)
    record_cost(input_tokens, output_tokens)
    return {"question": body.question, "answer": answer}
