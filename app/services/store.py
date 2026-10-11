from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any

lock = RLock()
proposals: dict[str, dict[str, Any]] = {}
approvals: dict[str, dict[str, Any]] = {}
executions: dict[tuple[str, str], dict[str, Any]] = {}
audit: list[dict[str, Any]] = []
shipments = {
    "SHP-10482": {
        "shipment_id": "SHP-10482",
        "tenant_id": "demo",
        "status": "in_transit",
        "last_observed_at": datetime.now(timezone.utc) - timedelta(hours=43),
        "last_known_eta": datetime.now(timezone.utc) + timedelta(hours=5),
        "source": "mock_carrier_api",
    }
}


def event(tenant_id: str, event_type: str, actor: str, details: dict[str, Any]) -> dict[str, Any]:
    item = {
        "event_id": f"aud_{len(audit) + 1:06d}",
        "tenant_id": tenant_id,
        "event_type": event_type,
        "actor": actor,
        "details": details,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with lock:
        audit.append(item)
    return item
