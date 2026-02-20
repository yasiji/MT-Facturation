# MT-Facturation - Technical Stack and Engineering Standards

Last Updated: 2026-02-20 11:46 UTC

## 1) Core Stack
- Backend: Python 3.12+
- Backend framework: FastAPI
- Frontend: React + TypeScript
- Frontend build tool: Vite
- Database: PostgreSQL 16+
- Database driver: psycopg (v3)

## 2) Microservices Stack
- API style: REST for synchronous domain operations.
- Async processing: background workers for billing and heavy jobs.
- Message transport (recommended): RabbitMQ (or Redis Streams for simpler setup).
- Service-to-service auth: JWT service tokens or mTLS (environment dependent).
- API gateway: single entrypoint for frontend and external clients.
- Provisioning orchestration: onboarding/checkout API orchestrates automatic contract and subscriber provisioning (create or reuse), not manual operator data stitching.
- Contract provisioning intent handling: API defaults to `auto` intent with backend decisioning; optional `target_contract_id` and explicit intents are supported for deterministic integrations.

## 2.1) API Readiness Standards (Mandatory)
- All core capabilities must be accessible via documented APIs for external systems.
- OpenAPI specs must be generated and version-controlled for every service.
- External endpoints must be versioned (`/api/v1`, `/api/v2`, ...).
- Backward compatibility policy must be defined before breaking changes.
- Idempotency keys required on critical write operations (billing, payment, contract activation).
- Standardized API error envelope and correlation ID propagation required.
- API authentication: JWT/OAuth2 compatible integration model.
- Middleware ordering rule (local/web): CORS middleware must wrap auth/error paths so browser clients receive CORS headers even when requests fail.

## 3) Backend Standards
- Dependency and packaging: `pyproject.toml` with Poetry or uv.
- Validation: Pydantic v2 schemas.
- ORM/data layer: SQLAlchemy 2.0 plus explicit transaction boundaries.
- Migrations: Alembic.
- API docs: OpenAPI auto-generated from FastAPI.
- Runtime: Uvicorn/Gunicorn in containerized deployment.

## 4) Frontend Standards
- State and server cache: TanStack Query.
- Routing: React Router.
- Forms and validation: React Hook Form + Zod.
- UI system: component library with a shared design token layer.
- Accessibility: WCAG baseline checks for critical pages.
- Build quality gates: lint, type-check, unit tests.
- Workflow mode for current development stage: single operator UX path that drives automated contract provisioning.

## 5) Data Modeling Standards
- Use UUID primary keys by default.
- Use `numeric` for monetary amounts and tax values.
- Store timestamps in UTC.
- Track `created_at`, `updated_at`, and actor context where possible.
- Enforce unique constraints for business identifiers.
- Prefer soft-delete for core business entities, hard-delete only for safe technical data.

## 5.1) Catalog and Contract Modeling Baseline
- Staff-facing offer creation is constrained to three categories:
  - `mobile`
  - `internet`
  - `landline`
- Offers are component-driven with strict backend validation:
  - Mobile:
    - at least one of `mobile_data_gb` or `mobile_calls_hours`
  - Internet:
    - `internet_access_type` required and must be exactly one of `fiber` or `adsl`
    - corresponding speed field required (`internet_fiber_speed_mbps` or `internet_adsl_speed_mbps`)
    - `internet_landline_included` is mandatory and always `true`
    - optional boolean: `internet_tv_included`
  - Landline:
    - at least one component among `landline_national_included`, `landline_international_hours`, `landline_phone_hours`
    - hour fields are integer-only
- Offer `service_type` remains persisted as a compatibility field for provisioning:
  - `mobile` for mobile offers
  - `fiber` or `adsl` for internet offers based on access choice
  - `landline` for landline offers
- Grouped catalog read endpoint available: `GET /api/v1/offer-categories` (`/api/v1/offer-families` kept as deprecated compatibility alias).
- Commercial fee fields:
  - `monthly_fee` required and strictly positive
  - `activation_fee` (staff-facing label: `other fees`) required and zero-or-greater
- Offer validity behavior:
  - `valid_to` is optional (undefined when not set)
  - frontend operator UX exposes `valid_to` only when explicit validation-date toggle is enabled.
- Offer tab UX baseline (current):
  - stable row-based component editor with disabled-state controls (no jumpy layout)
  - segmented/pill toggles for binary options (`On`/`Off`)
  - live preview panel reflecting service components, fees, and validity before submit.

## 5.2) Subscriber Compatibility and Client Deletion Policy
- Subscriber records are system-managed through contract provisioning in the main UX path; direct manual subscriber operations are technical/admin-only.
- Keep subscriber-service APIs available and compatible for integrations and controlled operations.
- Contract provisioning must maintain subscriber integrity constraints:
  - service-type compatibility between subscriber and selected plan
  - deterministic create-vs-upgrade decisioning
  - explicit disambiguation when multiple active candidates exist.
- Client deletion policy:
  - hard delete only when the client has no contractual/billing/payment history
  - otherwise enforce non-destructive lifecycle handling (status termination/soft-delete/anonymization strategy).
- Current implementation enforces contract/invoice/payment/collection-history guard on client hard delete (`409 client_delete_blocked`).

## 5.3) Landing API Baseline (Phase 4.5 Backend Slice)
- Public landing endpoints are exposed under `/api/v1/landing/*` for client-facing journeys.
- Current backend landing APIs include:
  - `GET /api/v1/landing/bootstrap`
  - `POST /api/v1/landing/drafts`
  - `GET /api/v1/landing/drafts/{draft_id}`
  - `PUT /api/v1/landing/drafts/{draft_id}`
  - `POST /api/v1/landing/clients/verify-cin`
  - `GET /api/v1/landing/clients/{cin}/subscriptions?lookup_token=...`
  - `GET /api/v1/landing/clients/{cin}/invoices?lookup_token=...`
  - `POST /api/v1/landing/submit/new`
  - `POST /api/v1/landing/submit/plan-change`
  - `POST /api/v1/landing/contracts/{contract_id}/document-link`
  - `GET /api/v1/landing/contracts/{contract_id}/document?token=...`
  - `GET /api/v1/landing/invoices/{invoice_id}/document?token=...`
- Final submit endpoints require `Idempotency-Key` and enforce payload-hash conflict protection.
- Lookup token rules:
  - plan-change subscription lookup is CIN-only (`/landing/clients/verify-cin`).
  - billing lookup is also CIN-only (`/landing/clients/verify-cin`) under the temporary product-stage policy.
  - all lookup flows return signed short-lived lookup tokens used by `/landing/clients/{cin}/subscriptions` and `/landing/clients/{cin}/invoices`.
- Plan-change orchestration rule:
  - for upgrade/downgrade flow, selected `contract_start_date` is applied as the upgraded contract effective start date.
- Contract PDF retrieval is tokenized with signed short-lived access links and persisted metadata (`contract_documents`).
- CIN is now supported as a first-class client identifier (`clients.cin`) for landing reconciliation.
- Moroccan number handling baseline:
  - canonical storage format: `+212` + 9-digit national number
  - mobile national numbers must start with `6` or `7`
  - landline national numbers must start with `5` or `8`
  - accepted intake formats include:
    - `+212 6 55 33 44 22`
    - `06 55 33 44 22`
    - `07 55 33 44 22`
    - equivalent digit-only forms after normalization
- New-subscription payload supports operator/client guided numbering:
  - mobile existing-number path: `existing_mobile_local_number`
  - mobile assign-new path: optional `requested_mobile_local_number`
  - internet/landline path: required `home_landline_local_number`
- Frontend route baseline:
  - `/landing` serves the client-facing subscription and plan-change wizard
  - `/landing` also serves client billing self-service (invoice list + PDF download)
  - `/` keeps the internal operator workspace (Contracts/Clients/Offers tabs).
- Sensitive data handling baseline for landing flows:
  - logs use masked CIN/email/phone values
  - lookup responses expose masked contact fields for email/phone.
- Configuration hardening baseline:
  - `landing_token_secret` default is accepted only in `local`/`test` environments; non-local environments must override it.

## 5.4) Billing API Baseline (Phase 5 Slice)
- Billing run endpoint:
  - `POST /api/v1/billing/runs`
  - requires `Idempotency-Key`
  - supports period boundaries, due-day offset, and tax rate.
- Invoice APIs:
  - `GET /api/v1/invoices`
  - `GET /api/v1/invoices/{invoice_id}`
  - `GET /api/v1/invoices/{invoice_id}/pdf`
  - list endpoint supports filters:
    - `client_id`
    - `service` (`mobile` | `internet` | `landline`)
    - `offer_id`
- Billing behavior baseline:
  - invoice aggregation is per client across billable active contracts
  - recurring and activation lines are generated from active contract + offer fees
  - invoice records are issued with immutable historical totals and PDF metadata
  - PDF documents are generated server-side and stored with SHA-256 metadata
  - billing run idempotency uses payload-hash conflict protection.

## 5.5) Collections API Baseline (Phase 6 Slice)
- Collections APIs:
  - `POST /api/v1/collections/payments` (requires `Idempotency-Key`)
  - `POST /api/v1/collections/invoices/{invoice_id}/approve-paid` (requires `Idempotency-Key`)
  - `GET /api/v1/collections/payments`
  - `GET /api/v1/collections/cases`
  - `GET /api/v1/collections/cases/{case_id}/actions`
  - `PUT /api/v1/collections/cases/{case_id}/status`
  - `POST /api/v1/collections/cases/{case_id}/actions`
  - `GET /api/v1/collections/overview`
- Collections behavior baseline:
  - payments are allocated to invoices with strict no-overpayment validation
  - invoice-approval action records a full outstanding settlement payment (audit-safe, no direct status force)
  - idempotency key replay/conflict handling is enforced on payment writes
  - invoice statuses are synchronized to `issued` / `overdue` / `paid` based on outstanding and due date
  - overdue invoices open collection cases automatically with aging bucket computation
  - full settlement resolves collection cases and clears client delinquency when no overdue invoices remain
  - reminder/warning actions are tracked with event-hook style logs for dunning integration.
- Internal operator UI baseline:
  - dedicated `Invoices` tab (billing run + invoice filters by client/service/offer + detail/PDF)
  - dedicated `Collections` tab (aging filters + case lifecycle + payment/action operations)

## 6) Testing Standards (Mandatory)
Backend:
- Unit tests: `pytest`
- Async tests: `pytest-asyncio`
- Integration tests: database-backed tests (Testcontainers recommended)
- Contract tests: endpoint request/response compatibility

Frontend:
- Unit/component tests: Vitest + React Testing Library
- End-to-end tests: Playwright

Cross-service:
- End-to-end business flow tests in CI for critical journeys.

Policy:
- Any feature without tests is incomplete.
- Bug fixes must include regression tests.

## 7) Quality and Static Analysis
Backend:
- Formatting: Ruff format
- Linting: Ruff
- Type checking: mypy (or pyright with strict mode)

Frontend:
- Formatting: Prettier
- Linting: ESLint
- Type checking: TypeScript strict mode

## 8) CI/CD Baseline
- CI pipeline per pull request:
  - lint
  - type check
  - unit tests
  - integration tests
  - build artifacts
- Main branch protections:
  - no direct pushes
  - all checks required
  - at least one code review

## 9) Observability and Operations
- Logging: structured JSON logs with trace IDs.
- Metrics: Prometheus-compatible metrics.
- Tracing: OpenTelemetry instrumentation.
- Dashboards: service health, latency, error rate, billing job duration.
- Alerts: error spikes, failed billing runs, queue backlogs, DB issues.

## 10) Security Baseline
- JWT-based authentication and role-based authorization.
- Password and secret handling through secure vault/environment secrets.
- Input validation on all APIs.
- Rate limiting on sensitive endpoints.
- Audit logging for critical business events.
- Local MCP integrations must reference secret environment variable names (e.g., `GITHUB_TOKEN`) and never inline raw tokens in config files.

## 11) Deployment Baseline
- Containerization: Docker for all services.
- Local orchestration: Docker Compose.
- Production orchestration: Kubernetes (preferred) or managed container platform.
- Database backups: scheduled and tested restore procedures.
- Release strategy: blue/green or rolling with health-gated rollout.

## 11.1) Local One-Shot Launcher
- Required file: `launch_all.bat` at project root.
- Linux parity file: `launch_all.sh` at project root.
- Companion stop file: `stop_all.sh` at project root (graceful stop via PID files with fallback process/port cleanup).
- Responsibilities:
  - bootstrap backend virtual environment if missing
  - install backend and frontend dependencies
  - run dependency checks (`pip check`, `npm ls --depth=0`)
  - stop stale backend/frontend launcher windows and terminate listeners on required ports
  - start backend and frontend with project defaults
  - execute smoke checks after startup (backend health endpoint, authenticated backend API read, frontend root availability)
- Runtime hardening:
  - backend dev server reload mode is disabled by default for stability on Windows
  - if backend port `8000` remains busy after cleanup, launcher falls back to `8010`
  - launcher injects `VITE_API_BASE_URL` for frontend startup to keep API target aligned with selected backend port
  - launcher uses runtime-safe `errorlevel` checks to avoid false failures from batch parse-time expansion inside grouped blocks
  - frontend runtime backend discovery validates both CORS behavior (with operator headers) and required OpenAPI paths before selecting a base URL
  - launcher verifies OpenAPI contract path presence (`/api/v1/offer-categories`) during smoke checks to detect stale runtime code.
- Launcher must remain compatible with current service startup contracts.

## 12) PostgreSQL Credentials (Current Project Input)
- Host: `localhost`
- Port: `5432`
- Username: `postgres`
- Password: `Yassine1@;`
- Development DSN example:
  - `postgresql+psycopg://postgres:Yassine1@%3B@localhost:5432/mt_facturation`
- These credentials are for local development and must be moved to secret management for non-local environments.

## 13) Documentation Synchronization Rule
- At each interaction/iteration, all project Markdown files must be reviewed and updated:
  - `mustread.md`
  - `Agents.md`
  - `tasks.md`
  - `stack.md`
  - `journal.md`

## 14) Baseline Repository Layout
- `backend/`: FastAPI service template, tests, Dockerfile, and local start script.
- `backend/services/`: microservice boundary folders for domain split implementation.
- `backend/app/common/`: shared middleware and cross-cutting API foundations.
- `backend/alembic/`: migration configuration and revision workflow baseline.
- `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`: domain model and CRUD service implementation layers (customer, catalog, contract, audit, provisioning).
- `frontend/`: React + TypeScript + Vite template, domain management UI, lint/type/test/build scripts.
- `infra/`: local PostgreSQL dev/test docker compose setup.
- `docs/`: glossary, release criteria, workflow, decision log, branching policy, API reference (`docs/api-reference.md`), process API map (`docs/api-process-map.md`), and PDF artifacts (`docs/api-reference-table.pdf`, `docs/api-process-map.pdf`).
- `.github/workflows/ci.yml`: baseline CI for backend/frontend quality gates.


