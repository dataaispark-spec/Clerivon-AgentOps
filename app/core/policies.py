from datetime import UTC, datetime


def is_fresh(observed_at: datetime | None, max_age_hours: int, now: datetime | None = None) -> bool:
    """A missing, future-dated, or over-age observation is not fresh."""
    if observed_at is None:
        return False
    now = now or datetime.now(UTC)
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    age_hours = (now - observed_at).total_seconds() / 3600
    return 0 <= age_hours <= max_age_hours


def tenant_matches(expected: str, actual: str) -> bool:
    return bool(expected) and expected == actual
