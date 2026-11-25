"""
Rate limiting (tiêu chí 7) — Sliding window lưu trên Redis.
"""
import logging
import time
import uuid

from fastapi import HTTPException

from app.config import settings
from app.redis_client import r

logger = logging.getLogger("agent")


def check_rate_limit(key: str) -> None:
    """Mỗi API key tối đa RATE_LIMIT_PER_MINUTE request / 60 giây."""
    if r is None:
        return

    now = time.time()
    window_seconds = 60
    window_start = now - window_seconds
    redis_key = f"ratelimit:{key}"

    try:
        r.zremrangebyscore(redis_key, 0, window_start)
        current_count = r.zcard(redis_key)

        if current_count >= settings.rate_limit_per_minute:
            oldest = r.zrange(redis_key, 0, 0, withscores=True)
            retry_after = (
                max(1, int(oldest[0][1] + window_seconds - now) + 1)
                if oldest
                else window_seconds
            )
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )

        r.zadd(redis_key, {f"{now}:{uuid.uuid4().hex}": now})
        r.expire(redis_key, window_seconds)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Redis unavailable in rate_limiter: %s", exc)
