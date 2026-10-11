
# Implementation matrix

| Capability | Current status | Next increment |
|---|---|---|
| Common API/harness | FastAPI endpoints and Pydantic contracts | Version API schema and add async checkpoints |
| Multi-agent orchestration | Role catalog plus deterministic handlers | Actual typed agent graph, model gateway, human interrupt/resume |
| Evidence | Synthetic evidence objects | Persist immutable source links/checksums and source event time separately from retrieval time |
| Freshness | Configurable logistics timestamp check | Source-specific policies and timezone normalization |
| Human approval | Proposal states and mock execution gate | Authenticated approver role and proposal hash/version binding |
| Idempotency | In-memory tenant/key collision check | Database unique constraint and transaction semantics across workers |
| Audit | In-memory event list | Durable append-only storage, integrity proof, retention and SIEM export |
| Tenant isolation | Demo equality checks | OIDC-derived identity and PostgreSQL RLS |
| BFSI | Synthetic mismatch/watchlist triage | Document extraction, entity resolution, source evidence packet |
| Retail | Rule-based replenishment quantity | Forecasting, uncertainty and verified mock stock update |
| Logistics | Stale tracking and unconfirmed ETA | SLA calculation, approved escalation adapter and outcome verification |
| Healthcare | Missing-document checks and draft packet | Approved guideline retrieval and payer-specific packet validation |
| Marketing | Required/forbidden string rules | Brand knowledge, multimodal review and statistical experiment evaluation |
| MSME | Lead threshold, invoice completeness, opt-out block | Source-based consent, OCR confidence, CRM/accounting adapters |
| Observability | Health endpoint and event metadata | OpenTelemetry traces/metrics, redaction and alerting |
| Delivery | Docker and CI lint/test | Dependency/secret/container scanning, SBOM and deployment runbooks |
| UI | No implemented dashboard | Review queue, evidence viewer, approvals and audit timeline |

## Status definitions
**Implemented** means executable and covered by tests. **Scaffolded** means documented or represented by structures without production behavior. **Missing** means no executable feature exists.
