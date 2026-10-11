# Clerivon AgentOps

**A governed, synthetic-first AgentOps reference platform for six enterprise workflows.**

Clerivon AgentOps demonstrates how an enterprise workflow can combine deterministic domain checks, policy gates, human approval, idempotent mock execution, and audit events. It is intended for learning, architecture validation, demonstrations, and early product prototyping.

> **Important:** This repository is an MVP/demo scaffold, not a production-certified agent platform. The six vertical workflows currently use deterministic rules and synthetic data. They do not call an LLM, connect to customer systems, or perform real-world actions.

[![CI](https://github.com/dataaispark-spec/Clerivon-AgentOps/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dataaispark-spec/Clerivon-AgentOps/actions/workflows/ci.yml)

## Contents

- [What the project demonstrates](#what-the-project-demonstrates)
- [Six solution packs](#six-solution-packs)
- [Architecture at a glance](#architecture-at-a-glance)
- [Requirements](#requirements)
- [Run locally](#run-locally)
- [Run in GitHub Codespaces](#run-in-github-codespaces)
- [Use the API](#use-the-api)
- [Run tests and quality checks](#run-tests-and-quality-checks)
- [Run with Docker](#run-with-docker)
- [Repository layout](#repository-layout)
- [Safety and governance controls](#safety-and-governance-controls)
- [Current capability boundaries](#current-capability-boundaries)
- [Deploying beyond Codespaces](#deploying-beyond-codespaces)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Documentation](#documentation)

## What the project demonstrates

- Six domain-oriented workflow handlers behind a consistent API.
- Deterministic synthetic-data processing that is reproducible in demos and tests.
- Proposal → human approval/rejection → mock execution lifecycle.
- Approval-expiry and idempotency protections in the mock action service.
- Tenant-scoped behavior in demo workflows and action operations.
- Audit events in an in-memory store.
- Automated quality checks through GitHub Actions (Ruff and pytest).

## Six solution packs

| Vertical | Demo behavior | Explicit boundary |
|---|---|---|
| **BFSI** | Synthetic record mismatch, watchlist-signal triage, missing-evidence checklist | No document OCR, production entity resolution, or autonomous AML decision |
| **Retail** | Rule-based replenishment gap using demand, safety stock, stock on hand, and open purchase orders | No statistical demand forecasting or inventory-system write-back |
| **Logistics** | Detects stale tracking observations; stale data leaves ETA unconfirmed and routes the case for review | No live carrier adapters or production SLA engine |
| **Healthcare** | Checks synthetic prior-authorization packet completeness and produces a draft-only result | No patient-data connection, clinical decision, live guideline retrieval, or submission |
| **Marketing** | Checks synthetic creative claims against required/forbidden strings and creates an experiment brief | Not legal/compliance approval; no ad-platform integration or live optimization |
| **MSME** | Applies a simple lead-score threshold, checks invoice fields, drafts follow-up, and blocks dispatch for opted-out contacts | No CRM/accounting connector and no messages are sent |

The logistics demo includes seed shipment `SHP-10482`, whose source observation is 43 hours old. With the default six-hour freshness threshold, the last-known ETA must not be treated as confirmed.

## Architecture at a glance

```text
Client / API consumer
        |
        v
FastAPI routes  -----> Pydantic models and policy checks
        |                          |
        v                          v
Deterministic vertical workflows  Action proposal / approval / execution
        |                          |
        +------------+-------------+
                     v
          In-memory demo store
          (records and audit events)
```

This is a compact reference architecture, not a fully deployed distributed agent system. The current implementation does not include a LangGraph runtime, model gateway, durable database, real identity provider, or production connectors.

## Requirements

- **Python 3.12 or newer**
- Git
- Optional: Docker with Docker Compose
- Optional: a GitHub account with Codespaces access

The API dependencies are declared in `pyproject.toml`. Development dependencies include pytest, HTTPX, and Ruff.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/dataaispark-spec/Clerivon-AgentOps.git
cd Clerivon-AgentOps
```

### 2. Create and activate a virtual environment

**macOS / Linux**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python directly instead of changing machine-wide execution policy.

### 3. Install the application and development dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 4. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running. Open these URLs in your browser:

- API health: http://127.0.0.1:8000/health
- Interactive Swagger API: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

### 5. Try a demo endpoint

In another terminal:

```bash
curl http://127.0.0.1:8000/api/v1/verticals
curl http://127.0.0.1:8000/api/v1/dashboard/summary
curl http://127.0.0.1:8000/api/v1/logistics/shipments/SHP-10482/exception
```

On Windows, if `curl` behaves as a PowerShell alias, use `curl.exe` or open the endpoint in a browser. Use Swagger at `/docs` to inspect request schemas and submit workflow requests.

## Run in GitHub Codespaces

Codespaces provides a cloud development environment for this repository. It is useful for trying the API without installing Python locally. **A running Codespace is a development session, not a production hosting deployment.**

### Option A — Open the repository in Codespaces

1. Sign in to GitHub and open [Clerivon-AgentOps](https://github.com/dataaispark-spec/Clerivon-AgentOps).
2. Select **Code** → **Codespaces**.
3. Select **Create codespace on main** (or create a Codespace from the branch you want to test).
4. Wait for the VS Code browser editor and terminal to finish starting.
5. In the terminal, check the Python version:

   ```bash
   python --version
   ```

   Use Python 3.12 or newer. If the selected environment has an older version, switch to a Python 3.12 environment before installing dependencies.

### Option B — Start from the terminal

If the Codespace opens without the repository already checked out, run:

```bash
git clone https://github.com/dataaispark-spec/Clerivon-AgentOps.git
cd Clerivon-AgentOps
```

If the repository is already open in the Codespace, **do not clone it again**; run the remaining commands from the repository root.

### Install and run

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Leave the Uvicorn terminal running.

### Open the forwarded port

1. In the Codespaces editor, open the **Ports** panel.
2. Wait for port **8000** to appear. If it does not appear automatically, use **Add Port** and enter `8000`.
3. Open the forwarded address for port 8000 in a browser.
4. Add `/docs` to that forwarded base URL to open Swagger; use `/health` to check service health.
5. Keep port visibility set to **Private** unless you have a clear reason to share the demo. Do not expose real secrets or sensitive data through a public port.

If you stop the Uvicorn process, the forwarded endpoint will stop responding. Start it again from the terminal when you resume work.

### Use the Codespace to make and push changes

```bash
git status
git switch -c docs/my-change
# edit files in the browser editor
pytest -q
ruff check app tests
git add README.md
git commit -m "docs: improve project setup guide"
git push -u origin docs/my-change
```

Then open a pull request on GitHub and review the CI result. Replace `README.md` in `git add` with the paths you actually changed. Do not commit `.env`, credentials, access tokens, customer data, or generated secrets.

### Environment variables

The optional example configuration is in [`.env.example`](.env.example). The current Docker Compose file sets the documented demo defaults directly. For local development, application defaults are used unless the configuration code is explicitly set up to load an environment file. Do not assume that creating `.env` alone changes runtime configuration; verify the settings supported by `app/core/config.py`.

## Use the API

### Useful read-only demo endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness/health response |
| `GET` | `/api/v1/verticals` | Lists the supported verticals |
| `GET` | `/api/v1/dashboard/summary` | Demo summary |
| `GET` | `/api/v1/logistics/shipments/{shipment_id}/exception` | Shipment exception/freshness result |
| `GET` | `/api/v1/audit` | Reads demo audit events |

### Run a vertical workflow

Endpoint:

```http
POST /api/v1/workflows/{vertical}/run
Content-Type: application/json
```

Use one of the vertical identifiers returned by `GET /api/v1/verticals`. Open `/docs` to inspect the exact request model for the chosen vertical and try a synthetic example. Each workflow returns a deterministic demo result; outputs are not evidence of a production-grade domain decision.

### Action lifecycle

The demo action flow separates proposing an action from approving it and executing it:

1. `POST /api/v1/actions/proposals` — create a proposal.
2. `POST /api/v1/actions/approvals` — approve or reject the proposal.
3. `POST /api/v1/actions/execute` — request mock execution with an idempotency key.

Use the request schemas in Swagger (`/docs`) rather than guessing fields. Approval is not the same as execution. The service enforces approval expiry and idempotency protections, but identity and storage are still demo-grade. **Execution does not call an external system.**

## Run tests and quality checks

From the repository root:

```bash
pytest -q
ruff check app tests
```

The GitHub Actions CI workflow installs the project and checks linting and tests on changes. Check the [Actions page](https://github.com/dataaispark-spec/Clerivon-AgentOps/actions) for the latest run. A green CI run confirms these automated checks pass; it does not certify production security, regulatory compliance, or domain correctness.

## Run with Docker

From the repository root, with Docker Compose installed:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Then open http://127.0.0.1:8000/docs. Stop the container with:

```bash
docker compose -f infra/docker-compose.yml down
```

The image runs the API as a non-root user and includes a health check. This Docker setup is a local/demo deployment configuration, not a complete production deployment stack.

## Repository layout

```text
app/
  api/routes.py              FastAPI route definitions
  core/config.py             Application configuration
  core/policies.py           Policy and validation logic
  domain/models.py           Request/response domain models
  domain/verticals.py        Vertical definitions
  services/actions.py        Proposal, approval and mock execution lifecycle
  services/store.py          In-memory demo state and audit events
  services/workflows.py      Six deterministic synthetic workflows
docs/
  ARCHITECTURE.md            Architecture notes
  DEMO_RUNBOOK.md            Step-by-step demo guide
  IMPLEMENTATION_MATRIX.md   Implemented vs. planned capabilities
  QUALITY_REVIEW.md          Quality findings and status
  ROADMAP.md                 Planned evolution
  THREAT_MODEL.md            Threat model and trust boundaries
  VERTICAL_SOLUTION_PACKS.md Vertical use-case descriptions
infra/
  Dockerfile                 Container image
  docker-compose.yml          Local Docker Compose setup
tests/
  test_api.py
  test_policies.py
  test_vertical_workflows.py
.github/workflows/ci.yml      Automated quality checks
```

## Safety and governance controls

The current demo includes these guardrails:

1. **Synthetic-only processing:** no external side effects or live customer records.
2. **Human approval:** consequential mock actions require a separate approval step.
3. **Expiry check:** expired proposals cannot be approved/executed as if still valid.
4. **Idempotency:** replays are constrained so a tenant-scoped key cannot silently execute a different proposal.
5. **Freshness awareness:** the source observation time is distinguished from the time the API reads it; tracking older than six hours is stale by default.
6. **Audit trail:** actions emit audit events in the in-memory demo store.
7. **Input validation:** request models reject unexpected fields where configured.

These controls are useful demonstration patterns, not a substitute for a threat-modelled, independently tested production implementation.

## Current capability boundaries

| Capability | Current status |
|---|---|
| Six vertical workflows | Deterministic synthetic demo logic |
| LLM-powered agent planning | Not implemented |
| LangGraph orchestration/checkpointing | Not implemented |
| Real carrier, banking, retail, healthcare, marketing, CRM or accounting integrations | Not implemented |
| OIDC/SSO authentication and production RBAC/ABAC | Not implemented |
| Database persistence and PostgreSQL row-level security | Not implemented; state is in memory |
| Durable/tamper-evident audit | Not implemented |
| Production dashboard and end-to-end observability | Not implemented |
| Production security, performance and domain certification | Not established |

See the [implementation matrix](docs/IMPLEMENTATION_MATRIX.md), [quality review](docs/QUALITY_REVIEW.md), and [production-readiness backlog](https://github.com/dataaispark-spec/Clerivon-AgentOps/issues/3) for more detail.

## Deploying beyond Codespaces

For a persistent, internet-accessible environment, deploy through an appropriate cloud/container platform rather than relying on a running Codespace. Before exposing this application to real users or data, address at least:

- OIDC/SSO and server-verified user/tenant identity.
- RBAC/ABAC and authorization checks on every tenant-scoped resource.
- PostgreSQL transactions, tenant row-level security, backups, and migration strategy.
- Durable, access-controlled and tamper-evident audit storage.
- Secrets management, TLS, network restrictions, rate limiting, and secure headers.
- PII/PHI controls, retention rules, prompt-injection defenses, and data-loss prevention.
- Allow-listed least-privilege integration adapters and explicit human approval for consequential actions.
- Model gateway, evaluation datasets, failure handling, observability, and domain-expert review.
- Security testing, dependency/container scanning, load testing, recovery exercises, and operational runbooks.

Do not use the current in-memory demo for regulated workloads, real patient records, production financial decisions, or autonomous external actions.

## Troubleshooting

- **`python` not found:** install/select Python 3.12+, or use `python3.12` where available.
- **Dependency installation fails:** confirm Python version, then run `python -m pip install --upgrade pip` and retry.
- **Port 8000 is already in use:** stop the other process or run Uvicorn on another port, for example `--port 8001`.
- **Codespaces URL is unavailable:** confirm Uvicorn is still running and port 8000 is listed in the Ports panel.
- **Endpoint returns 404:** check the path and HTTP method; browse `/docs` for the routes exposed by the current branch.
- **Workflow input returns 422:** use the exact request schema shown in Swagger.
- **Tests fail after edits:** run `pytest -q` and `ruff check app tests`; fix the reported errors before committing.

## Contributing

1. Create a feature branch.
2. Make a focused change and add or update tests.
3. Run `ruff check app tests` and `pytest -q`.
4. Open a pull request with a concise explanation, test evidence, and any new safety assumptions.
5. Never commit secrets, real customer data, or credentials.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md)
- [Implementation matrix](docs/IMPLEMENTATION_MATRIX.md)
- [Quality review](docs/QUALITY_REVIEW.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Vertical solution packs](docs/VERTICAL_SOLUTION_PACKS.md)
- [Roadmap](docs/ROADMAP.md)
- [Production-readiness issue](https://github.com/dataaispark-spec/Clerivon-AgentOps/issues/3)

---

**License:** MIT. See [LICENSE](LICENSE).
