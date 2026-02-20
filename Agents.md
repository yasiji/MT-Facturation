# MT-Facturation - Project Charter and Operating Rules

Last Updated: 2026-02-20 10:44 UTC

## 1) Mission
Build a production-grade telecom management system that covers:
- Client and Subscriber management
- Offer catalog management
- Contract lifecycle management
- Monthly invoice generation and download
- Late payment tracking and collections actions
- External system interoperability through stable APIs
- Automated provisioning flow: selecting an offer in checkout/onboarding must create or update contract/subscription records without manual backoffice data entry, with backend auto-detection of upgrade vs new-line when possible.

This project must stay simple in user experience, but strong in architecture and reliability.

## 2) Non-Negotiable Technology Rules
- Backend must be Python.
- Frontend must be React.
- Database must be PostgreSQL.
- Architecture must favor microservices.
- System must be API-ready for integration with external systems.
- Project must provide a one-shot Windows launcher (`launch_all.bat`) for local startup.
- Project should keep Linux launcher parity through `launch_all.sh` for cross-desktop portability.
- No feature is accepted without proper testing.
- No "manual-only validation" for production changes.

## 2.1) Current Access Mode (Testing Stage)
- Keep one operator profile able to execute all flows while development/testing is in progress.
- Defer multi-role and fine-grained RBAC UX complexity until later hardening phases.
- Do not remove backend auth foundations; keep current shared auth conventions intact.

## 3) Product Scope (Current)
Core entities:
- Client
- Subscriber
- Offer
- Contract
- Invoice

Supporting entities required for production behavior:
- Payment
- CollectionCase

## 3.1) Target Operational UX Model
- Keep operator workspace tabs as:
  - Contracts
  - Clients
  - Offers
  - Invoices
  - Collections
- Contract tab is the main routing entrypoint:
  - new client onboarding (capture personal data + choose offer/plan)
  - existing client contract changes (choose offer/plan directly)
- Client tab is focused on management of existing clients (status and controlled deletion policies).
- Subscriber lifecycle must remain automatically managed by provisioning logic and stay compatible with subscriber-service APIs.
- Dedicated client-facing landing flow is allowed as an external intake channel if it remains API-first and feeds the same backend provisioning/orchestration rules as internal contract workflows.
- Landing flow may also expose client self-service billing (invoice lookup and secure PDF download) when it stays API-first and token-protected.
- Current product rule update: landing self-service lookup is CIN-only for plan-change and billing paths (temporary product-stage rule).
- Current orchestration rule update: plan-change effective date from landing must be applied to the upgraded contract start date.
- Active frontend routing baseline now includes:
  - `/` internal operator workspace
  - `/landing` client-facing onboarding and plan-change entrypoint.

## 3.2) Offer Construction Model (Current)
- Staff-facing offer creation must be constrained to exactly three services:
  - `mobile`
  - `internet`
  - `landline`
- Offer components are service-specific and validated by backend rules:
  - Mobile: `data` and/or `calls`
  - Internet: exactly one of `fiber` or `adsl` is mandatory, `landline` is mandatory, `tv` is optional
  - Landline: `national` optional unlimited flag, `international_hours` and `phone_hours` as integer quotas
- Hours must be integer values only.

## 4) Architecture Principles
- Domain-driven service boundaries.
- Each microservice owns its data and schema.
- Strong API contracts and versioning.
- Idempotent billing and payment flows.
- Auditability for all critical business changes.
- Security by default (auth, RBAC, data protection, least privilege).

## 5) External Integration and API Rules
- API-first design is mandatory for all business capabilities.
- OpenAPI specification must be maintained for each service.
- Public and partner-facing endpoints must be versioned.
- Contract compatibility rules must be defined before breaking changes.
- External integration patterns include REST APIs and event/webhook flows where relevant.
- API responses must follow standard pagination, filtering, sorting, and error envelope conventions.

## 6) Proposed Service Boundaries
- `customer-service`: Client and Subscriber.
- `catalog-service`: Offer and OfferVersion.
- `contract-service`: Contract lifecycle.
- `billing-service`: Invoice generation, invoice lines, PDF generation.
- `collections-service`: Payment tracking, overdue status, dunning logic.
- `api-gateway`: Unified external API entrypoint.
- `auth-service` (or external IdP integration): identity and RBAC.

## 7) Data and Ownership Rules
- PostgreSQL is the source of truth for transactional data.
- Service database ownership is strict. No cross-service direct table access.
- Cross-service data exchange is through APIs/events only.
- Monetary values use precise decimal types, never float.
- Invoice records are immutable after issue, except via formal adjustment flows.

## 8) Local Development Database Credentials
- Host: `localhost`
- Port: `5432`
- Database user: `postgres`
- Database password: `Yassine1@;`
- These credentials are for local development only and must not be reused in production.

## 9) Quality Gates (Mandatory)
A task is complete only if all are true:
- Unit tests implemented and passing.
- Integration tests implemented and passing where applicable.
- API contract tests updated and passing.
- Regression impact assessed and covered.
- Observability added for new critical paths (logs/metrics/traces).
- Local launcher smoke checks pass (backend health, authenticated API read, frontend root).
- Documentation synchronized across `Agents.md`, `tasks.md`, `stack.md`, `journal.md`, and `mustread.md`.

## 10) Testing Policy
- Test pyramid target:
  - fast unit tests for domain logic
  - integration tests for DB and service boundaries
  - end-to-end tests for critical business flows
- Critical flows requiring end-to-end coverage:
  - create client -> create subscriber -> activate contract
  - monthly billing run -> invoice issue -> PDF download
  - payment posting -> invoice settlement -> overdue status transitions

## 11) Security and Compliance Baseline
- RBAC required on all write operations.
- Sensitive fields encrypted at rest where required.
- All external and internal service traffic authenticated.
- Audit logs must include actor, timestamp, action, and before/after state reference.
- Never commit secrets. Use environment-based secret management.

## 12) Delivery Workflow
- Work in chronological phase order from `tasks.md`.
- Every completed task must be recorded in `journal.md`.
- Do not skip testing or documentation updates.
- Keep changes small, reviewable, and reversible.
- At each interaction/iteration, all project Markdown files must be reviewed and updated if needed.
- Keep launchers (`launch_all.bat`, `launch_all.sh`) aligned with current backend/frontend startup commands and dependency setup.
- Maintain unbiased and brutally honest technical review behavior: challenge assumptions, state risks clearly, and avoid rubber-stamping proposals.

## 13) Session Start Checklist for Agents
- Read `mustread.md`.
- Read `Agents.md`, `tasks.md`, `stack.md`, and `journal.md`.
- Confirm active phase and next task.
- Log session start in `journal.md`.
- Execute task with tests and update journal with outcomes.

## 14) Definition of Done (Project Level)
The system is release-ready when:
- Core services are implemented and integrated.
- Billing, payment, and collections flows are stable and tested.
- Frontend supports operational workflows for target roles.
- CI pipelines enforce test and quality gates.
- Operational runbooks and rollback strategies are documented.
- One-shot local launchers are working end-to-end (venv setup, dependency install/check, stale-process cleanup, service start, smoke checks).

## 15) Current Baseline Artifacts
- Foundation docs:
  - `docs/business-glossary.md`
  - `docs/release-criteria.md`
  - `docs/documentation-workflow.md`
  - `docs/decision-log.md`
  - `docs/branching-policy.md`
  - `docs/api-reference.md`
  - `docs/api-process-map.md`
- Platform scaffolding:
  - `backend/` (FastAPI template + tests + Dockerfile)
  - `backend/services/` (microservice boundary folders)
  - `backend/app/common/` (shared auth, errors, API conventions, observability)
  - `backend/alembic/` (migration baseline)
- `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/` (domain CRUD layers, including contract lifecycle + audit trail + provisioning + catalog service/component metadata + billing/invoice generation + collections/payment handling + client deletion guardrails)
  - `frontend/` (React + TypeScript + Vite template + tests + domain management UI, including contract-first intake routing for new/existing clients, invoice center, and collections dashboard operations)
  - `infra/docker-compose.yml` (local PostgreSQL dev/test)
  - `.github/workflows/ci.yml` (CI skeleton)
