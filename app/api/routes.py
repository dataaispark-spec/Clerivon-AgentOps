from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.core.policies import is_fresh
from app.domain.models import ApprovalRequest, ExecuteRequest, ProposalRequest, WorkflowRequest
from app.domain.verticals import VERTICALS
from app.services import store
from app.services.actions import approve, execute, propose
from app.services.workflows import run

router = APIRouter()


@router.get("/verticals")
def verticals():
    return {"verticals": VERTICALS}


@router.get("/dashboard/summary")
def dashboard(tenant_id: str = Query(default="demo", min_length=1, max_length=100)):
    # Tenant ID is caller-supplied in this demo. Production must derive it from the
    # verified identity token rather than trusting a query parameter.
    with store.lock:
        proposals = [p for p in store.proposals.values() if p["tenant_id"] == tenant_id]
        events = [e for e in store.audit if e["tenant_id"] == tenant_id]
    return {
        "tenant_id": tenant_id,
        "vertical_count": len(VERTICALS),
        "proposals_pending_approval": sum(p["status"] == "pending_approval" for p in proposals),
        "proposals_approved": sum(p["status"] == "approved" for p in proposals),
        "proposals_executed": sum(p["status"] == "executed" for p in proposals),
        "audit_event_count": len(events),
        "storage_mode": "in-memory-demo",
    }


@router.get("/logistics/shipments/{shipment_id}/exception")
def shipment_exception(shipment_id: str, tenant_id: str = Query(default="demo", min_length=1, max_length=100)):
    with store.lock:
        item = store.shipments.get(shipment_id)
        # Copy primitive fields to avoid reading a mutable store object outside lock.
        if not item or item["tenant_id"] != tenant_id:
            raise HTTPException(404, "Shipment not found")
        shipment = dict(item)
    fresh = is_fresh(shipment["last_observed_at"], settings.logistics_tracking_max_age_hours)
    return {
        "shipment_id": shipment_id,
        "tenant_id": tenant_id,
        "tracking_status": "fresh" if fresh else "stale",
        "last_observed_at": shipment["last_observed_at"].isoformat(),
        "last_known_eta": shipment["last_known_eta"].isoformat(),
        "eta_confirmed": fresh,
        "policy_max_age_hours": settings.logistics_tracking_max_age_hours,
        "recommended_next_step": "validate_sla" if fresh else "request_fresh_tracking_and_escalate",
        "note": None if fresh else "Retrieval time does not make old source evidence fresh.",
    }


@router.post("/workflows/{vertical}/run")
def workflow(vertical: str, request: WorkflowRequest):
    key = vertical.lower()
    if key not in VERTICALS:
        raise HTTPException(404, "Unknown vertical")
    return run(key, request.tenant_id, request.case_id, request.input)


@router.post("/actions/proposals")
def create_proposal(request: ProposalRequest):
    if request.vertical.lower() not in VERTICALS:
        raise HTTPException(422, "Unknown vertical")
    return propose(request)


@router.post("/actions/approvals")
def create_approval(request: ApprovalRequest):
    return approve(request)


@router.post("/actions/execute")
def execute_approved(request: ExecuteRequest):
    return execute(request)


@router.get("/audit")
def audit(
    tenant_id: str = Query(default="demo", min_length=1, max_length=100),
    limit: int = Query(default=100, ge=1, le=500),
):
    # Caller-supplied tenant is only for the demo; production needs auth-derived scope.
    with store.lock:
        events = [dict(e) for e in store.audit if e["tenant_id"] == tenant_id]
    return {"tenant_id": tenant_id, "events": events[-limit:]}
