from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any

lock = RLock()
proposals: dict[str, dict[str, Any]] = {}
approvals: dict[str, dict[str, Any]] = {}
executions: dict[tuple[str, str], dict[str, Any]] = {}
audit: list[dict[str, Any]] = []
_audit_sequence = 0

shipments = {
    "SHP-10482": {
        "shipment_id": "SHP-10482",
        "tenant_id": "demo",
        "status": "in_transit",
        "last_observed_at": datetime.now(UTC) - timedelta(hours=43),
        "last_known_eta": datetime.now(UTC) + timedelta(hours=5),
        "source": "mock_carrier_api",
    }
}


def event(tenant_id: str, event_type: str, actor: str, details: dict[str, Any]) -> dict[str, Any]:
    # Sequence allocation and append use the same lock to avoid duplicate audit IDs
    # under concurrent requests. The in-memory log is not durable or tamper-evident.
    global _audit_sequence
    with lock:
        _audit_sequence += 1
        item = {
            "event_id": f"aud_{_audit_sequence:06d}",
            "tenant_id": tenant_id,
            "event_type": event_type,
            "actor": actor,
            "details": details,
            "created_at": datetime.now(UTC).isoformat(),
        }
        audit.append(item)
        return item
