# Contributing

1. Keep fixtures synthetic.
2. Add tests for policy and security invariants.
3. Model output must never bypass deterministic policy checks.
4. Every write-capable action needs a typed proposal, approval, expiry, idempotency and audit.
5. Test cross-tenant access explicitly.
6. Update the threat model when adding an integration.
