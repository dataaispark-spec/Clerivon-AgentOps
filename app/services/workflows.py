from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.policies import is_fresh
from app.domain.models import Evidence, WorkflowResult
from app.domain.verticals import VERTICALS
from app.services import store


def _evidence(source: str, description: str, attributes: dict[str, Any], freshness: str = "fresh") -> Evidence:
    return Evidence(
        source=source,
        description=description,
        observed_at=datetime.now(UTC),
        freshness=freshness,
        attributes=attributes,
    )


def _number(inputs: dict[str, Any], key: str, default: float = 0) -> float:
    try:
        value = float(inputs.get(key, default))
        return value if value >= 0 else default
    except (TypeError, ValueError):
        return default


def run(vertical: str, tenant_id: str, case_id: str | None, inputs: dict[str, Any]) -> WorkflowResult:
    """Deterministic, synthetic-first domain workflow demonstrations.

    These workflows structure and validate provided demo fields; they do not call
    LLMs or external systems. Integrations and domain policy adapters remain future work.
    """
    spec = VERTICALS[vertical]
    flags: list[str] = ["synthetic_demo_only", "domain_expert_review_required"]
    evidence: list[Evidence] = []
    recommendation: dict[str, Any] = {
        "agent_team": spec["agents"],
        "next_steps": spec["workflow"],
        "input_mode": "synthetic_demo",
    }
    status = "ready_for_review"

    if vertical == "logistics":
        shipment_id = str(inputs.get("shipment_id") or case_id or "SHP-10482")
        with store.lock:
            shipment = store.shipments.get(shipment_id)
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
                risk_flags=["shipment_not_found_or_not_authorized", "synthetic_demo_only"],
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
            recommendation.update({"eta_status": "fresh_evidence_available", "required_action": "validate_sla"})
            summary = "Fresh tracking evidence is available for SLA validation; confirm SLA before action."
        else:
            status = "needs_human_review"
            flags.append("tracking_evidence_stale")
            recommendation.update({
                "eta_status": "unconfirmed",
                "last_known_eta": shipment["last_known_eta"].isoformat(),
                "required_action": "request_fresh_tracking_and_validate_sla",
                "sla_status": "not_computed_without_validated_commitment",
            })
            summary = "Tracking evidence is stale; the last-known ETA is unconfirmed."
    elif vertical == "bfsi":
        document_count = int(_number(inputs, "document_count"))
        mismatch_count = int(_number(inputs, "mismatch_count"))
        watchlist_matches = int(_number(inputs, "watchlist_matches"))
        missing_items = inputs.get("missing_items", [])
        missing_items = missing_items if isinstance(missing_items, list) else []
        risk_signals = []
        if mismatch_count:
            risk_signals.append({"signal": "record_mismatch", "count": mismatch_count})
        if watchlist_matches:
            risk_signals.append({"signal": "watchlist_match_requires_review", "count": watchlist_matches})
        if missing_items:
            risk_signals.append({"signal": "missing_evidence", "items": missing_items})
        evidence.append(_evidence("synthetic_bfsi_case", "Synthetic KYC/AML intake fields", {
            "document_count": document_count,
            "mismatch_count": mismatch_count,
            "watchlist_matches": watchlist_matches,
            "missing_items": missing_items,
        }))
        recommendation.update({
            "case_id": case_id,
            "document_intake": {"documents_received": document_count},
            "reconciliation": {"mismatch_count": mismatch_count, "status": "review_required" if mismatch_count else "no_demo_mismatch_detected"},
            "risk_signals": risk_signals,
            "analyst_checklist": ["validate source documents", "resolve mismatches", "review match quality", "record disposition"],
            "decision": "analyst_review_required",
        })
        flags.append("no_autonomous_aml_decision")
        summary = "Synthetic KYC/AML case triaged into an evidence-linked analyst checklist; no determination is made."
    elif vertical == "retail":
        stock = _number(inputs, "stock_on_hand")
        demand = _number(inputs, "forecast_demand")
        open_po = _number(inputs, "open_purchase_order_qty")
        safety_stock = _number(inputs, "safety_stock")
        lead_time_days = _number(inputs, "lead_time_days")
        available = stock + open_po
        gap = max(0.0, demand + safety_stock - available)
        evidence.append(_evidence("synthetic_retail_case", "Synthetic stock and demand inputs", {
            "stock_on_hand": stock, "forecast_demand": demand,
            "open_purchase_order_qty": open_po, "safety_stock": safety_stock,
        }))
        recommendation.update({
            "sku": inputs.get("sku"),
            "store_id": inputs.get("store_id"),
            "available_including_open_po": available,
            "demand_gap": gap,
            "replenishment_recommendation_qty": gap,
            "lead_time_days": lead_time_days,
            "confidence": "not_estimated_without_historical_series",
            "next_step": "human_review_then_mock_inventory_update",
        })
        flags.append("no_purchase_order_or_price_change_without_approval")
        summary = "Synthetic demand/stock reconciliation completed; replenishment quantity is a rule-based suggestion, not a forecast."
    elif vertical == "healthcare":
        document_count = int(_number(inputs, "document_count"))
        missing_items = inputs.get("missing_items", [])
        missing_items = missing_items if isinstance(missing_items, list) else []
        guideline_refs = inputs.get("approved_guideline_refs", [])
        guideline_refs = guideline_refs if isinstance(guideline_refs, list) else []
        evidence.append(_evidence("synthetic_prior_authorization_case", "Synthetic document completeness inputs", {
            "document_count": document_count, "missing_items": missing_items,
            "approved_guideline_refs": guideline_refs,
        }))
        recommendation.update({
            "document_intake": {"documents_received": document_count},
            "completeness": {"missing_items": missing_items, "complete": not missing_items},
            "guideline_references": guideline_refs,
            "coding_suggestions": inputs.get("coding_suggestions", []),
            "packet_status": "draft_only",
            "next_step": "authorized_staff_review",
        })
        flags.append("no_autonomous_clinical_decision_or_submission")
        summary = "Synthetic authorization packet checklist prepared for authorized staff review; no clinical decision or submission is made."
    elif vertical == "marketing":
        required_claims = inputs.get("required_claims", [])
        forbidden_claims = inputs.get("forbidden_claims", [])
        creative_claims = inputs.get("creative_claims", [])
        for name, value in (("required_claims", required_claims), ("forbidden_claims", forbidden_claims), ("creative_claims", creative_claims)):
            if not isinstance(value, list):
                raise ValueError(f"{name} must be a list")
        creative_set = {str(x).strip().casefold() for x in creative_claims}
        required_set = {str(x).strip().casefold() for x in required_claims}
        forbidden_set = {str(x).strip().casefold() for x in forbidden_claims}
        missing_required = sorted(required_set - creative_set)
        forbidden_found = sorted(forbidden_set & creative_set)
        evidence.append(_evidence("synthetic_marketing_case", "Synthetic creative and brand rule fields", {
            "creative_claims": creative_claims,
            "required_claims": required_claims,
            "forbidden_claims": forbidden_claims,
        }))
        recommendation.update({
            "creative_review": {"missing_required_claims": missing_required, "forbidden_claims_found": forbidden_found},
            "compliance_status": "human_review_required" if missing_required or forbidden_found else "no_demo_rule_violation_detected",
            "experiment_brief": {
                "objective": inputs.get("campaign_objective", "not_provided"),
                "variants": inputs.get("variant_ideas", []),
                "success_metric": inputs.get("success_metric", "not_provided"),
            },
            "next_step": "brand_owner_approval_before_publication_or_budget_change",
        })
        flags.append("rule_based_demo_check_not_legal_approval")
        summary = "Synthetic creative rule check and experiment brief prepared; this is not legal or platform-policy approval."
    elif vertical == "msme":
        lead_score = _number(inputs, "lead_score")
        invoice_fields = inputs.get("invoice_fields", {})
        invoice_fields = invoice_fields if isinstance(invoice_fields, dict) else {}
        missing_invoice_fields = sorted(
            key for key in ("invoice_number", "supplier", "invoice_date", "total")
            if not invoice_fields.get(key)
        )
        opt_out = bool(inputs.get("contact_opted_out", False))
        follow_up = str(inputs.get("follow_up_draft", "")).strip()
        evidence.append(_evidence("synthetic_msme_case", "Synthetic lead/invoice/operations fields", {
            "lead_score": lead_score, "invoice_field_names": sorted(invoice_fields.keys()),
            "contact_opted_out": opt_out,
        }))
        recommendation.update({
            "lead": {"score": lead_score, "priority": "high" if lead_score >= 70 else "normal"},
            "invoice_assistance": {"extracted_fields": invoice_fields, "missing_required_fields": missing_invoice_fields},
            "sales_follow_up": {
                "draft_available": bool(follow_up),
                "dispatch_permitted": False if opt_out else "requires_human_approval_and_consent_check",
                "draft": follow_up,
            },
            "operations": {"tasks_received": inputs.get("tasks", [])},
            "owner_report": {"items_to_review": len(missing_invoice_fields) + int(opt_out)},
        })
        flags.append("no_autonomous_payment_tax_filing_or_binding_quote")
        summary = "Synthetic MSME lead and invoice assistance prepared; outbound communication remains a draft pending owner review."
    else:
        raise TypeError(f"Unsupported vertical: {vertical}")

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
