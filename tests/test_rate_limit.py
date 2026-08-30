from collections import deque
from datetime import datetime, timedelta, timezone

from backend import rate_limit


def test_cleanup_removes_only_expired_user_entries(monkeypatch):
    now = datetime.now(timezone.utc)
    expired_attempt = (
        now - rate_limit.RATE_LIMIT_WINDOW - timedelta(seconds=1)
    )
    active_attempt = now - timedelta(seconds=30)

    rate_limit.order_attempts[100] = deque([expired_attempt])
    rate_limit.order_attempts[200] = deque([active_attempt])
    monkeypatch.setattr(
        rate_limit,
        "last_cleanup_at",
        datetime.min.replace(tzinfo=timezone.utc),
    )

    rate_limit.check_order_rate_limit(user_id=300)

    assert 100 not in rate_limit.order_attempts
    assert 200 in rate_limit.order_attempts
    assert 300 in rate_limit.order_attempts
