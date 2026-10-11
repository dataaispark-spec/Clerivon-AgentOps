# Clerivon AgentOps

Governed multi-agent workflow reference platform across six enterprise verticals. This is an MVP scaffold using synthetic data and mock execution only; it is not production-certified.

## Solution packs
- **BFSI — KYC & AML Investigation Copilot:** synthetic record-mismatch and watchlist-signal triage with an analyst checklist (document extraction and entity resolution remain future work).
- **Retail — Inventory & Demand Orchestration:** rule-based stock/replenishment gap calculation (statistical forecasting and inventory write verification remain future work).
- **Logistics — Shipment Exception Resolution:** stale-tracking detection and ETA-unconfirmed behavior; SLA calculation and carrier adapters remain future work.
- **Healthcare — Prior Authorization Assistant:** synthetic document-completeness checklist and draft-only packet state (no live clinical data or guideline retrieval).
- **Marketing — Creative Intelligence & Optimization:** synthetic required/forbidden claim string checks and experiment brief (not legal approval or live performance optimization).
- **MSME — AI Digital Workforce:** simple lead-score threshold, invoice-field completeness and opted-out contact dispatch block (no CRM/accounting connectors).

## Safety invariants
1. Evidence and observation timestamps are explicit; retrieval time is not source-observation time.
2. Shipment tracking older than six hours is stale by default and cannot confirm an ETA.
3. Consequential actions require a separate human approval.
4. Approval expires; execution rechecks tenant, approval, expiry and idempotency.
5. Tenant scoping is demonstrated in workflow/action operations; production must derive tenant identity from authenticated claims and enforce database RLS.
6. Audit events are recorded in the demo store. Production requires durable, tamper-evident storage.
7. Synthetic fixtures and mock adapters only; no external side effects.

## Quick start
Requires Python 3.12+.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest -q
```
API docs: http://127.0.0.1:8000/docs

## Demo
```bash
curl http://127.0.0.1:8000/api/v1/logistics/shipments/SHP-10482/exception
```
Seed shipment `SHP-10482` has a 43-hour-old observation, exceeding the six-hour freshness policy. It must not report its last-known ETA as confirmed.

## Action lifecycle
1. `POST /api/v1/actions/proposals`
2. `POST /api/v1/actions/approvals` with decision `approve` or `reject`
3. `POST /api/v1/actions/execute` with an idempotency key
Execution is mock-only.

## Endpoints
- `GET /health`
- `GET /api/v1/verticals`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/logistics/shipments/{shipment_id}/exception`
- `POST /api/v1/workflows/{vertical}/run`
- `POST /api/v1/actions/proposals`
- `POST /api/v1/actions/approvals`
- `POST /api/v1/actions/execute`
- `GET /api/v1/audit`

## Production hardening before live use
PostgreSQL tenant RLS and transactions; OIDC/SSO and RBAC/ABAC; verified approver identity; durable/tamper-evident audit; prompt-injection and PII/PHI controls; least-privilege allow-listed integrations; model gateway and evaluation sets; security, recovery, load and domain-specific reviews. The in-memory demo is not production-ready.

The target repository is `https://github.com/dataaispark-spec/Clerivon-AgentOps`. Never commit tokens or local `.env` files.

## Engineering quality and production status

The current `main` CI run is green for dependency installation, Ruff linting and pytest, including regression tests for each vertical's deterministic synthetic workflow. See [the implementation matrix](docs/IMPLEMENTATION_MATRIX.md) for a precise status by capability. These are not live integrations or autonomous LLM agents. See [the quality review](docs/QUALITY_REVIEW.md) and [production-readiness backlog](https://github.com/dataaispark-spec/Clerivon-AgentOps/issues/3). A green demo test suite does **not** mean production approval: authentication/authorization, PostgreSQL tenant isolation, durable audit, real agent graphs and guarded integration adapters remain unfinished.
