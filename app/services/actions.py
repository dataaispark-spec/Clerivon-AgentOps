from datetime import datetime, timedelta

from fastapi import HTTPException

from app.core.config import settings
from app.core.policies import tenant_matches
from app.domain.models import make_id, now_utc
from app.services import store


def propose(data):
    created = now_utc()
    item = {
        **data.model_dump(),
        "proposal_id": make_id("prop"),
        "status": "pending_approval",
        "created_at": created.isoformat(),
        "expires_at": (created + timedelta(minutes=settings.approval_ttl_minutes)).isoformat(),
    }
    with store.lock:
        store.proposals[item["proposal_id"]] = item
    store.event(data.tenant_id, "action.proposed", "system", {
        "proposal_id": item["proposal_id"],
        "action_type": data.action_type,
        "target_id": data.target_id,
    })
    return item


def approve(data):
    with store.lock:
        item = store.proposals.get(data.proposal_id)
        if not item or not tenant_matches(data.tenant_id, item["tenant_id"]):
            raise HTTPException(404, "Proposal not found")
        if item["status"] != "pending_approval":
            raise HTTPException(409, f"Proposal is {item['status']}")
        if data.decision not in {"approve", "reject"}:
            raise HTTPException(422, "decision must be approve or reject")
        approval = {
            **data.model_dump(),
            "approval_id": make_id("appr"),
            "created_at": now_utc().isoformat(),
        }
        store.approvals[approval["approval_id"]] = approval
        item["status"] = "approved" if data.decision == "approve" else "rejected"
    store.event(data.tenant_id, "action.approval_recorded", data.approver_id, {
        "proposal_id": data.proposal_id,
        "decision": data.decision,
    })
    return approval


def execute(data):
    with store.lock:
        item = store.proposals.get(data.proposal_id)
        if not item or not tenant_matches(data.tenant_id, item["tenant_id"]):
            raise HTTPException(404, "Proposal not found")
        if item["status"] != "approved":
            raise HTTPException(409, "Action requires an approved proposal")
        if datetime.fromisoformat(item["expires_at"]) <= now_utc():
            item["status"] = "expired"
            raise HTTPException(409, "Approval window expired; create a new proposal")
        if not any(
            a["proposal_id"] == data.proposal_id
            and a["tenant_id"] == data.tenant_id
            and a["decision"] == "approve"
            for a in store.approvals.values()
        ):
            raise HTTPException(403, "Valid approval record not found")
        key = (data.tenant_id, data.idempotency_key)
        if key in store.executions:
            return store.executions[key]
        result = {
            "execution_id": f"exec_{data.idempotency_key}",
            "tenant_id": data.tenant_id,
            "proposal_id": data.proposal_id,
            "status": "mock_executed",
            "side_effect": "none; demo adapter only",
            "executed_at": now_utc().isoformat(),
        }
        store.executions[key] = result
        item["status"] = "executed"
    store.event(data.tenant_id, "action.mock_executed", "system", {
        "proposal_id": data.proposal_id,
        "idempotency_key": data.idempotency_key,
    })
    return result
