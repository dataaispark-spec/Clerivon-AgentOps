
# Demo runbook

## Start
```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## BFSI
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/bfsi/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"KYC-1001","input":{"document_count":3,"mismatch_count":1,"watchlist_matches":1,"missing_items":["address_proof"]}}'
```

## Retail
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/retail/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"SKU-1001","input":{"store_id":"store-01","sku":"SKU-1001","stock_on_hand":10,"forecast_demand":25,"open_purchase_order_qty":5,"safety_stock":3}}'
```
For this rule-based demo, expected recommendation quantity is 13; it is not a statistical forecast.

## Logistics
```bash
curl http://127.0.0.1:8000/api/v1/logistics/shipments/SHP-10482/exception
curl -X POST http://127.0.0.1:8000/api/v1/workflows/logistics/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"SHP-10482","input":{}}'
```
Expected: stale tracking, ETA unconfirmed.

## Healthcare
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/healthcare/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"PA-2001","input":{"document_count":2,"missing_items":["recent_clinical_note"],"approved_guideline_refs":["SYNTH-GUIDE-01"]}}'
```
Expected: draft-only packet with missing-item checklist.

## Marketing
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/marketing/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"MKT-1001","input":{"creative_claims":["guaranteed outcome"],"required_claims":["terms apply"],"forbidden_claims":["guaranteed outcome"],"campaign_objective":"qualified leads"}}'
```
Expected: required/forbidden string flags for human review.

## MSME
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/msme/run -H "Content-Type: application/json" -d '{"tenant_id":"demo","case_id":"LEAD-1001","input":{"lead_score":85,"invoice_fields":{"invoice_number":"INV-1"},"contact_opted_out":true,"follow_up_draft":"Please review our proposal."}}'
```
Expected: high-priority lead label, missing invoice fields, and dispatch blocked for opted-out contact.

## Action approval walk-through
Use `POST /api/v1/actions/proposals`, `POST /api/v1/actions/approvals`, then `POST /api/v1/actions/execute`. All adapters are mock-only.

## Demo boundary
Do not submit live PII/PHI, financial records or external API credentials. Outputs are deterministic scaffolding, not LLM-agent decisions.
