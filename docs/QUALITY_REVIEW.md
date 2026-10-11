# Code quality review — MVP baseline

## Scope reviewed
The initial `main` version of the six-vertical AgentOps scaffold, including FastAPI routes, workflow handlers, action approval/execution, in-memory store, tests and CI.

## Findings fixed in this change
- **CI lint failure (resolved):** Ruff flagged UTC aliases and import ordering. The fixes are merged into `main`; the current main CI run passed lint and tests.
- **Idempotency collision:** a tenant could reuse an already-used idempotency key against a different proposal and receive the previous proposal's result. Execution now rejects that collision.
- **Approval expiry:** an expired proposal could previously be approved and only fail later at execution. Approval now rejects it and transitions it to `expired`.
- **Audit event ID concurrency:** the previous sequence derived from list length before taking the lock. Sequence allocation and append now happen under the same lock.
- **Shared in-memory reads:** shipment records are copied while holding the repository lock before evaluation.
- **Test isolation and coverage:** tests reset mutable process-local state and now cover expired approval and idempotency-key collision.

## Latest verification (2026-10-11)
- Merged commit: `6cac33444044efab9f2c9769f6f20084313f137b`.
- GitHub Actions on `main`: success for dependency installation, Ruff linting and pytest. [Run details](https://github.com/dataaispark-spec/Clerivon-AgentOps/actions/runs/38144796557).
- Production-readiness work is tracked in [issue #3](https://github.com/dataaispark-spec/Clerivon-AgentOps/issues/3).

## Important residual limitations
- The app is a **synthetic/demo scaffold**, not an autonomous multi-agent production product.
- `tenant_id` and `approver_id` are client-supplied fields in the demo. They are not authenticated identities. Production must use OIDC claims and RBAC/ABAC.
- In-memory state is lost on restart and is not safe across multiple workers. Production needs a transactional database, tenant RLS and unique idempotency constraints.
- Audit records are neither durable nor tamper-evident.
- A role catalog is defined, but specialist agents are workflow metadata and deterministic scaffolding, not separate LLM agents yet.
- No real carrier, banking, clinical, inventory, advertising or CRM adapter is enabled.
- No production secrets handling, document malware scanning, PII/PHI redaction, prompt-injection test suite, dependency scan, SBOM or container scan is present yet.
- Approval comments and IDs are only demo metadata; they do not prove that a real authorized person performed the approval.

## Recommended release gate
Do not connect real systems until OIDC, server-enforced role checks, PostgreSQL/RLS, durable idempotency and audit, adapter allow-lists, policy/evaluation datasets, domain reviews, penetration tests and incident/recovery procedures are implemented and independently tested.
