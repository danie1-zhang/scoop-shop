from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException


order_attempts: dict[int, deque[datetime]] = {}
order_attempts_lock = Lock()


def check_order_rate_limit(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)

    with order_attempts_lock:
        attempts = order_attempts.setdefault(user_id, deque())
        while attempts and attempts[0] <= window_start:
            attempts.popleft()
        if len(attempts) >= 5:
            raise HTTPException(status_code=429, detail="too many requests")
        attempts.append(now)
