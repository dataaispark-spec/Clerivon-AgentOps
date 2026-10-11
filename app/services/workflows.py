from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.policies import is_fresh
from app.domain.models import Evidence, WorkflowResult
from app.domain.verticals import VERTICALS
from app.services import store


def run(vertical: str, tenant_id: str, case_id: str | None, inputs: dict[str, Any]) -> WorkflowResult:
    spec = VERTICALS[vertical]
    flags: list[str] = []
    evidence: list[Evidence] = []
    recommendation: dict[str, Any] = {
        "agent_team": spec["agents"],
        "next_steps": spec["workflow"],
    }

    if vertical == "logistics":
        shipment_id = str(inputs.get("shipment_id") or case_id or "SHP-10482")
        with store.lock:
            shipment = store.shipments.get(shipment_id)
            # Copy while locked: the shared in-memory repository is mutable.
            if not shipment or shipment["tenant_id"] != tenant_id:
                shipment = None
            else:
                shipment = dict(shipment)
        if shipment is None:
            return WorkflowResult(
                tenant_id=tenant_id,
                vertical=vertical,
                status="needs_input",
                summary="Shipment not found in this tenant.",
                recommendation={"next_step": "verify_identifier"},
                risk_flags=["shipment_not_found_or_not_authorized"],
            )
        fresh = is_fresh(shipment["last_observed_at"], settings.logistics_tracking_max_age_hours)
        evidence.append(Evidence(
            source=shipment["source"],
            description="Last carrier tracking observation",
            observed_at=shipment["last_observed_at"],
            freshness="fresh" if fresh else "stale",
            attributes={"shipment_id": shipment_id, "status": shipment["status"]},
        ))
        if fresh:
            status = "ready_for_review"
            summary = "Fresh tracking evidence is available for SLA validation."
            recommendation.update({"eta_status": "fresh_evidence_available", "required_action": "validate_sla"})
        else:
            status = "needs_human_review"
            summary = "Tracking evidence is stale; the last known ETA must not be presented as confirmed."
            flags.append("tracking_evidence_stale")
            recommendation.update({
                "eta_status": "unconfirmed",
                "last_known_eta": shipment["last_known_eta"].isoformat(),
                "required_action": "request_fresh_tracking_and_validate_sla",
            })
    else:
        evidence.append(Evidence(
            source="synthetic_demo_input",
            description=f"Synthetic input for {spec['name']}",
            observed_at=datetime.now(UTC),
            freshness="fresh",
            attributes={"input_fields": sorted(inputs)},
        ))
        flags.append("domain_expert_review_required")
        recommendation.update({
            "review_required": True,
            "guardrails": spec["guardrails"],
            "pilot_kpis": spec["pilot_kpis"],
            "input_received": inputs,
        })
        status = "ready_for_review"
        summary = f"{spec['name']}: structured recommendation prepared for human review."

    result = WorkflowResult(
        tenant_id=tenant_id,
        vertical=vertical,
        status=status,
        summary=summary,
        recommendation=recommendation,
        evidence=evidence,
        risk_flags=flags,
        requires_human_approval=True,
    )
    store.event(tenant_id, "workflow.completed", "orchestrator", {
        "workflow_id": result.workflow_id,
        "vertical": vertical,
        "status": status,
        "risk_flags": flags,
    })
    return result
