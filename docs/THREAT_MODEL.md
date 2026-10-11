# Threat model

| Threat | Example | Required control |
|---|---|---|
| Prompt injection | A source document tells an agent to ignore rules | Treat documents as data; isolate system instructions; adversarial tests |
| Stale evidence | Old carrier update shown as current | Compare source observation timestamp to policy; block confirmed ETA |
| Cross-tenant access | Tenant A reads Tenant B's case | OIDC claims, tenant-scoped reads, database RLS and negative tests |
| Approval bypass | Agent directly invokes a write tool | Central execution gateway requires unexpired approval |
| Duplicate side effect | Retry sends duplicate message | Transactional, tenant-scoped idempotency key |
| Tool overreach | Agent attempts arbitrary network or shell action | Typed allow-list tools and egress restrictions |
| PII/PHI leakage | Sensitive data appears in model trace | Minimize, redact, retention controls and private telemetry |
| Fabricated evidence | Model invents a citation | Evidence IDs must resolve to persisted source records |
| Approval spoofing | Unqualified user self-approves | Verified identity and approver-role authorization |
| Audit tampering | Events are changed after an action | Append-only integrity-protected store and restricted access |

This is a starter threat model, not a security certification. The current demo has no production authentication, database RLS or durable audit storage.
