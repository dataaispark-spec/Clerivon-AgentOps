from datetime import UTC, datetime, timedelta

from app.core.policies import is_fresh, tenant_matches


def test_missing_timestamp_is_stale():
    assert is_fresh(None, 6) is False


def test_43_hour_tracking_is_stale():
    assert is_fresh(datetime.now(UTC) - timedelta(hours=43), 6) is False


def test_recent_tracking_is_fresh():
    assert is_fresh(datetime.now(UTC) - timedelta(minutes=5), 6) is True


def test_future_timestamp_is_not_fresh():
    assert is_fresh(datetime.now(UTC) + timedelta(minutes=2), 6) is False


def test_tenant_isolation_predicate():
    assert tenant_matches("tenant-a", "tenant-a")
    assert not tenant_matches("tenant-a", "tenant-b")
