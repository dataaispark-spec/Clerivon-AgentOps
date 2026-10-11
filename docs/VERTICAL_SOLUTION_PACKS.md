
# Six vertical solution packs — implementation mapping

All workflows currently operate on synthetic request fields and return structured recommendation/evidence objects. They do not call an LLM or any external system. The role names are orchestration targets, not implemented independent agents.

## 1. BFSI — KYC & AML Investigation Copilot
**Current demo logic:** accepts document count, mismatch count, watchlist match count and missing evidence list; returns reconciliation summary, risk-signal checklist and analyst steps.
**Control:** flags no-autonomous-AML decision. A watchlist hit is not a determination.
**Still needed:** safe document extraction, entity resolution, source-linked evidence storage, versioned policy rules and analyst case packet.

## 2. Retail — Inventory & Demand Orchestration
**Current demo logic:** computes a rule-based replenishment gap: `max(0, demand + safety_stock - stock_on_hand - open_purchase_order_qty)`.
**Control:** this is a recommendation, not a forecast; no purchase-order or pricing side effect is enabled.
**Still needed:** time-series history, seasonality/promotions, uncertainty intervals, supplier lead-time models, stock consistency and approval-gated update verification.

## 3. Logistics — Shipment Exception Resolution
**Current demo logic:** checks source observation time against the configured six-hour freshness limit. Seed shipment `SHP-10482` is 43 hours stale, so its ETA is unconfirmed.
**Control:** stale evidence cannot be represented as a confirmed ETA.
**Still needed:** carrier event normalization, SLA calculation from validated contractual data, approval-bound escalation payload and outcome verification.

## 4. Healthcare — Prior Authorization Assistant
**Current demo logic:** checks a supplied missing-items list, passes through supplied guideline references and marks the packet draft-only.
**Control:** no autonomous diagnosis, treatment decision or submission.
**Still needed:** approved-source retrieval, provenance, code validation, PHI controls and payer-specific schemas.

## 5. Marketing — Creative Intelligence & Optimization
**Current demo logic:** compares synthetic creative claim strings with required/forbidden lists and returns an experiment brief.
**Control:** a string rule check is not legal, brand or platform-policy approval.
**Still needed:** versioned policy sources, multimodal review, experiment design/statistical evaluation and aggregate performance connectors.

## 6. MSME — AI Digital Workforce
**Current demo logic:** applies a simple lead-score threshold, checks required invoice fields, drafts a follow-up and blocks dispatch when opt-out is true.
**Control:** no autonomous payment, tax filing, binding quotation or outbound message dispatch.
**Still needed:** calibrated lead scoring, OCR confidence, verified consent data, owner approvals and CRM/accounting connectors.

## Shared production requirements
All verticals still require OIDC/RBAC, server-derived tenant scope, PostgreSQL/RLS, durable approval/action transactions, durable tamper-evident audit, observability and independent evaluation/security review.
