
from fastapi.testclient import TestClient

from app.main import app
from app.services import store

client = TestClient(app)

def setup_function():
    with store.lock:
        store.proposals.clear()
        store.approvals.clear()
        store.executions.clear()
        store.audit.clear()

def run_vertical(vertical, payload):
    response = client.post(f"/api/v1/workflows/{vertical}/run", json={
        "tenant_id": "demo", "case_id": f"CASE-{vertical.upper()}", "input": payload
    })
    assert response.status_code == 200
    return response.json()

def test_bfsi_flags_mismatches_and_watchlist_matches_for_analyst():
    body = run_vertical("bfsi", {"document_count": 3, "mismatch_count": 1, "watchlist_matches": 1})
    rec = body["recommendation"]
    assert rec["reconciliation"]["mismatch_count"] == 1
    assert len(rec["risk_signals"]) == 2
    assert "no_autonomous_aml_decision" in body["risk_flags"]

def test_retail_replenishment_math_uses_stock_open_po_demand_and_safety_stock():
    body = run_vertical("retail", {"stock_on_hand": 10, "open_purchase_order_qty": 5, "forecast_demand": 25, "safety_stock": 3})
    rec = body["recommendation"]
    assert rec["available_including_open_po"] == 15
    assert rec["replenishment_recommendation_qty"] == 13
    assert "no_purchase_order_or_price_change_without_approval" in body["risk_flags"]

def test_logistics_stale_tracking_eta_is_unconfirmed():
    body = client.get("/api/v1/logistics/shipments/SHP-10482/exception").json()
    assert body["eta_confirmed"] is False
    workflow = run_vertical("logistics", {"shipment_id": "SHP-10482"})
    assert workflow["recommendation"]["eta_status"] == "unconfirmed"
    assert "tracking_evidence_stale" in workflow["risk_flags"]

def test_healthcare_flags_missing_documents_and_stays_draft():
    body = run_vertical("healthcare", {"document_count": 2, "missing_items": ["recent_clinical_note"], "approved_guideline_refs": ["SYNTH-GUIDE-01"]})
    assert body["recommendation"]["completeness"]["complete"] is False
    assert body["recommendation"]["packet_status"] == "draft_only"
    assert "no_autonomous_clinical_decision_or_submission" in body["risk_flags"]

def test_marketing_flags_required_and_forbidden_claims():
    body = run_vertical("marketing", {"creative_claims": ["guaranteed outcome", "limited offer"], "required_claims": ["terms apply"], "forbidden_claims": ["guaranteed outcome"], "campaign_objective": "qualified leads"})
    rec = body["recommendation"]
    assert rec["creative_review"]["missing_required_claims"] == ["terms apply"]
    assert rec["creative_review"]["forbidden_claims_found"] == ["guaranteed outcome"]
    assert rec["compliance_status"] == "human_review_required"

def test_msme_marks_opted_out_contact_as_not_permitted_for_dispatch():
    body = run_vertical("msme", {"lead_score": 85, "invoice_fields": {"invoice_number": "INV-1"}, "contact_opted_out": True, "follow_up_draft": "Please review our proposal."})
    rec = body["recommendation"]
    assert rec["lead"]["priority"] == "high"
    assert rec["sales_follow_up"]["dispatch_permitted"] is False
    assert "supplier" in rec["invoice_assistance"]["missing_required_fields"]
    assert "no_autonomous_payment_tax_filing_or_binding_quote" in body["risk_flags"]
