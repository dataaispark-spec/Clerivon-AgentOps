# Roadmap

## Phase 0 — Safe demo baseline (current)
Synthetic fixtures, mock integrations, shared workflow contracts, freshness policy, approval gate, audit events and invariant tests.

## Phase 1 — Platform foundation
PostgreSQL migrations and tenant RLS; OIDC/SSO and RBAC/ABAC; verified approver identity; transactional approval/execution; unique tenant-scoped idempotency; durable audit; secret management and OpenTelemetry with PII redaction.

## Phase 2 — Agent graphs
LangGraph typed state, human interrupt/resume, model gateway, structured-output validation, prompt-injection evaluation and per-vertical benchmark sets.

## Phase 3 — Integrations
Read-only adapters first; allow-listed scopes and egress rules; sandbox contract tests; explicit approvals for writes; read-after-write verification.

## Phase 4 — Pilot readiness
Design partners, baseline and target KPIs, domain/privacy review, load and recovery testing, incident runbooks, retention and support model.

## Four-week starter plan
- Week 1: schemas, synthetic fixtures and mock adapters.
- Week 2: workflow harness, evidence freshness and verification tests.
- Week 3: approvals, audit, tenant checks and threat tests.
- Week 4: dashboard, evaluation runs, demo script and pilot backlog.
