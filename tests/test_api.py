from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_six_verticals():
    keys = set(client.get("/api/v1/verticals").json()["verticals"])
    assert keys == {"bfsi", "retail", "logistics", "healthcare", "marketing", "msme"}


def test_seed_shipment_eta_not_confirmed():
    body = client.get("/api/v1/logistics/shipments/SHP-10482/exception").json()
    assert body["tracking_status"] == "stale"
    assert body["eta_confirmed"] is False


def test_approval_required_and_idempotent():
    proposal = client.post("/api/v1/actions/proposals", json={
        "tenant_id": "test",
        "vertical": "logistics",
        "action_type": "carrier_escalation",
        "target_id": "SHP-X",
        "summary": "Request fresh tracking",
        "payload": {"external_side_effect": True},
    }).json()
    proposal_id = proposal["proposal_id"]
    blocked = client.post("/api/v1/actions/execute", json={
        "tenant_id": "test", "proposal_id": proposal_id, "idempotency_key": "blocked-key-001",
    })
    assert blocked.status_code == 409
    approval = client.post("/api/v1/actions/approvals", json={
        "tenant_id": "test", "proposal_id": proposal_id, "approver_id": "reviewer",
        "decision": "approve", "comment": "Approved",
    })
    assert approval.status_code == 200
    payload = {"tenant_id": "test", "proposal_id": proposal_id, "idempotency_key": "idem-key-001"}
    first = client.post("/api/v1/actions/execute", json=payload)
    second = client.post("/api/v1/actions/execute", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_cross_tenant_cannot_approve():
    proposal = client.post("/api/v1/actions/proposals", json={
        "tenant_id": "tenant-a", "vertical": "msme", "action_type": "send_followup",
        "target_id": "lead-1", "summary": "Draft follow-up", "payload": {},
    }).json()
    response = client.post("/api/v1/actions/approvals", json={
        "tenant_id": "tenant-b", "proposal_id": proposal["proposal_id"],
        "approver_id": "intruder", "decision": "approve", "comment": "",
    })
    assert response.status_code == 404
