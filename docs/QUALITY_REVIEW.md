# Code quality review — MVP baseline

## Scope reviewed
The initial `main` version of the six-vertical AgentOps scaffold, including FastAPI routes, workflow handlers, action approval/execution, in-memory store, tests and CI.

## Findings fixed in this change
- **CI lint failure:** Ruff's current rules flag UTC aliases, unused imports and style items. CI now uses the GitHub annotation formatter, and touched files have been cleaned; re-check the actual run status before treating CI as green.
- **Idempotency collision:** a tenant could reuse an already-used idempotency key against a different proposal and receive the previous proposal's result. Execution now rejects that collision.
- **Approval expiry:** an expired proposal could previously be approved and only fail later at execution. Approval now rejects it and transitions it to `expired`.
- **Audit event ID concurrency:** the previous sequence derived from list length before taking the lock. Sequence allocation and append now happen under the same lock.
- **Shared in-memory reads:** shipment records are copied while holding the repository lock before evaluation.
- **Test isolation and coverage:** tests reset mutable process-local state and now cover expired approval and idempotency-key collision.

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
