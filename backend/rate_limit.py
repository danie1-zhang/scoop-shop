from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException


order_attempts: dict[int, deque[datetime]] = {}
order_attempts_lock = Lock()


RATE_LIMIT_WINDOW = timedelta(minutes=1)
CLEANUP_INTERVAL = timedelta(minutes=1)
last_cleanup_at = datetime.min.replace(tzinfo=timezone.utc)


def check_order_rate_limit(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - RATE_LIMIT_WINDOW

    with order_attempts_lock:
        cleanup_expired_attempts(now)

        attempts = order_attempts.setdefault(user_id, deque())

        while attempts and attempts[0] <= window_start:
            attempts.popleft()

        if len(attempts) >= 5:
            raise HTTPException(status_code=429, detail="too many requests")

        attempts.append(now)


def cleanup_expired_attempts(now: datetime) -> None:
    global last_cleanup_at

    if now - last_cleanup_at < CLEANUP_INTERVAL:
        return

    window_start = now - RATE_LIMIT_WINDOW

    for user_id, attempts in list(order_attempts.items()):
        while attempts and attempts[0] <= window_start:
            attempts.popleft()

        if not attempts:
            del order_attempts[user_id]

    last_cleanup_at = now
