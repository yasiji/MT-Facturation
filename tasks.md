# MT-Facturation - Execution Plan (Chronological)

Last Updated: 2026-02-20 12:14 UTC

## Recurring Rule - Documentation Synchronization (Every Interaction/Iteration)
Objective: preserve project continuity and avoid context loss.

Tasks:
- [x] Review `mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, and `journal.md`.
- [x] Update all five files in each interaction/iteration as needed.
- [x] Record the updates in `journal.md` with outcomes and rationale.
- [x] Keep API reference documentation synchronized in `docs/api-reference.md`.
- [x] Keep process-oriented API map synchronized in `docs/api-process-map.md`.
- [x] Regenerate `docs/api-reference-table.pdf` with per-endpoint curl command syntax.
- [x] Regenerate `docs/api-process-map.pdf` with per-step curl command syntax.

Exit criteria:
- [x] Documentation is synchronized for the current interaction/iteration.

## Phase 0 - Project Foundation and Governance
Objective: lock scope, standards, and execution discipline.

Tasks:
- [x] Validate business scope and entity glossary.
- [x] Confirm non-negotiable architecture rules from `Agents.md`.
- [x] Confirm API-first interoperability requirements for external systems.
- [x] Define release criteria and acceptance metrics.
- [x] Set documentation workflow (`journal.md` update rules).
- [x] Create decision log for architecture and tradeoffs.

Exit criteria:
- [x] Scope and terminology baseline documented (business sign-off pending).
- [x] Documentation and decision process active.

## Phase 1 - Platform and Repository Setup
Objective: establish production-grade engineering base.

Tasks:
- [x] Create repository structure for microservices and frontend.
- [x] Configure Python service template (lint, format, test, Dockerfile).
- [x] Configure React app template (lint, format, test, build).
- [x] Set up PostgreSQL local and test environments.
- [x] Configure local PostgreSQL credentials (`postgres` / `Yassine1@;`) via environment variables.
- [x] Create and maintain `launch_all.bat` to:
  - [x] create backend venv if missing
  - [x] install backend and frontend dependencies
  - [x] run dependency health checks
  - [x] stop stale local runtime windows/processes and free required ports before launch
  - [x] start backend and frontend in one shot
  - [x] run post-launch smoke checks (backend health, authenticated API read, frontend root)
- [x] Create and maintain Linux parity launcher `launch_all.sh` with equivalent bootstrap/start/smoke flow.
- [x] Add Linux stop companion script `stop_all.sh` for deterministic shutdown (PID-file first, process/port fallback).
- [x] Set up CI pipeline skeleton for lint + test + build.
- [x] Define branching and pull request policy.
- [x] Initialize local git repository baseline (`main`) with first snapshot commit for GitHub migration.
- [x] Create/push remote GitHub repository (`MT-Facturation`) and sync `main` branch with GitHub.
- [x] Correct local Codex GitHub MCP configuration to use environment-variable binding (`bearer_token_env_var = \"GITHUB_TOKEN\"`) instead of raw token literal.

Exit criteria:
- [x] All templates build successfully.
- [ ] CI passes for baseline templates (pending first CI run on hosted repository).

## Phase 2 - Shared Technical Foundations
Objective: implement reusable cross-service foundations.

Tasks:
- [x] Shared authentication and authorization middleware.
- [x] Shared error model and API response conventions.
- [x] Shared API versioning, pagination, filtering, and error-envelope conventions.
- [x] Shared observability package (logging, metrics, tracing hooks).
- [x] Shared DB migration strategy and standards.
- [x] Shared test utilities and fixtures.

Exit criteria:
- [x] Foundations reusable by all services.
- [x] Shared packages covered by unit tests.

## Phase 3 - Customer and Catalog Domains
Objective: deliver core master data services first.

Tasks:
- [x] Implement `customer-service`:
  - [x] Client CRUD
  - [x] Subscriber CRUD
  - [x] Client-to-subscriber relationships
  - [x] Status lifecycle and validation
  - [x] External API endpoints for partner/system integrations
- [x] Implement `catalog-service`:
  - [x] Offer CRUD
  - [x] Offer versioning and validity dates
  - [x] Service type classification (mobile, fiber, ADSL, TV)
  - [x] External API endpoints for partner/system integrations
- [x] Write API contract tests for both services.
- [x] Build frontend pages for Client, Subscriber, and Offer management.

Exit criteria:
- [x] Master data is manageable through API and UI.
- [x] Test suites pass with required coverage.

## Phase 4 - Contract Domain
Objective: implement commercial agreement lifecycle.

Tasks:
- [x] Implement `contract-service`:
  - [x] Add automated provisioning flow: offer selection triggers contract creation/update and subscriber create/reuse decision.
  - [x] Contract creation tied to client/subscriber/offer version
  - [x] Contract status transitions (draft, active, suspended, terminated)
  - [x] Date and commitment validations
  - [x] Audit trail for status and offer changes
  - [x] External API endpoints for partner/system integrations
- [x] Add frontend contract screens and workflows.
- [x] Add integration tests with customer and catalog service dependencies.

Exit criteria:
- [x] Contract lifecycle fully operational.
- [x] Cross-service integrity validated by tests.

## Phase 5 - Billing Domain
Objective: generate and issue grouped monthly invoices.

Tasks:
- [x] Implement `billing-service`:
  - [x] Billing period handling
  - [x] Invoice draft generation per client
  - [x] Invoice line assembly from active contracts
  - [x] Tax and discount calculations
  - [x] Invoice issue and immutability rules
  - [x] PDF generation and storage metadata
  - [x] External API endpoints for partner/system integrations
- [x] Add invoice list/detail/download endpoints.
- [x] Add billing run orchestration and idempotency protection.
- [x] Build frontend invoice center (list, detail, download).
- [x] Expose landing self-service invoice lookup and secure PDF download endpoints.
- [x] Build landing billing flow (verify CIN, list invoices, download PDFs).
- [x] temporary product update: keep landing billing lookup CIN-only (same as plan-change path) while hardening phase is pending.

Exit criteria:
- [x] Monthly billing run works reliably.
- [x] Invoice PDF download works from UI and API.

## Phase 6 - Payments and Collections Domain
Objective: manage payments, overdue detection, and dunning.

Tasks:
- [x] Implement `collections-service`:
  - [x] Payment recording and allocation
  - [x] Partial and full settlement behavior
  - [x] Days-past-due and aging bucket computation
  - [x] CollectionCase lifecycle and action history
  - [x] Client delinquency marking rules
  - [x] External API endpoints for partner/system integrations
- [x] Build collections dashboard with filters and aging views.
- [x] Add reminder and warning event hooks.
- [x] Split operator workspace into dedicated `Invoices` and `Collections` tabs.
- [x] Add invoice-center filters by `client`, `service`, and `offer` with API parity.
- [x] Add invoice approval action to mark monthly bill as paid via API-backed payment recording.

Exit criteria:
- [x] Overdue clients are correctly marked.
- [x] Payment allocation and invoice status updates are consistent.

## Phase 7 - Integration and End-to-End Flows
Objective: prove end-to-end business reliability.

Tasks:
- [ ] Implement cross-service integration tests.
- [ ] Implement end-to-end tests for critical journeys.
- [ ] Validate data consistency and reconciliation checks.
- [ ] Run performance tests on billing and payment operations.

Exit criteria:
- [ ] Critical journeys are green in CI.
- [ ] Performance baseline meets agreed targets.

## Phase 8 - Security, Observability, and Operations
Objective: make the platform production-safe and supportable.

Tasks:
- [ ] Harden RBAC enforcement and permission mapping.
- [ ] Add security scanning in CI.
- [ ] Finalize structured logs, metrics dashboards, and traces.
- [ ] Add health checks, readiness probes, and operational alerts.
- [ ] Prepare backup, restore, and disaster recovery procedures.

Exit criteria:
- [ ] Production operations checklist completed.
- [ ] Security and observability reviews passed.

## Phase 9 - Release Preparation and Go-Live
Objective: launch with controlled risk.

Tasks:
- [ ] UAT cycle with business stakeholders.
- [ ] Final bug triage and release candidate stabilization.
- [ ] Data migration plan and rehearsal.
- [ ] Production deployment and smoke tests.
- [ ] Post-deployment monitoring and rollback readiness.

Exit criteria:
- [ ] UAT sign-off received.
- [ ] Production launch completed with no critical blockers.

## Phase 4.1 - UX Automation Refinement
Objective: simplify operator workflow while preserving contract/subscriber automation.

Tasks:
- [x] Introduce tabbed UI navigation so client/offer/contract/subscriber areas are separated (no long-page scrolling workflow).
- [x] Add semantic status colors/badges for lifecycle states (active/suspended/terminated and related statuses).
- [x] Hide direct subscriber management panel from primary UI flow.
- [x] Keep subscriber APIs/endpoints available for technical/admin operations.
- [x] Route all day-to-day subscription actions through contract provisioning.
- [x] Add automation decision rules for provisioning:
  - [x] system auto-detects upgrade when one active contract candidate exists for the same client + service type, or when target contract is explicitly selected
  - [x] system auto-detects new-line when no upgrade candidate exists, or when a new service identifier is provided
  - [x] multiple matching active contracts require explicit user disambiguation via target contract selection (or forcing new-line with new identifier)
  - [x] explicit `upgrade` / `new_line` intents remain API-compatible for external integrators
- [x] Add tests for upgrade vs new-line behavior decisions.

Exit criteria:
- [x] Operator can complete onboarding and offer changes from one guided flow.
- [x] Subscriber records are managed automatically by contract provisioning rules.

## Phase 4.2 - Catalog Tiering and Plan-Change Readiness
Objective: support upgrade/downgrade scenarios by modeling service families and tiers correctly.

Note (2026-02-17):
- Family/tier modeling items below are retained for historical traceability.
- Active catalog direction for staff workflow is now service-component modeling (Phase 4.4).

Tasks:
- [x] Introduce offer family model (example: `fiber`) separated from tier/plan variants (example: 100Mbps, 200Mbps, 1Gbps).
- [x] Represent commercial tier metadata with recurring price, feature summary, and lifecycle status in catalog records.
- [x] Keep versioned pricing/effective dates per plan to preserve historical billing correctness.
- [x] Keep contracts bound to specific offer version records (plan-version equivalent in current model).
- [ ] Implement plan change operation in contract workflow:
  - [ ] upgrade within same family
  - [ ] downgrade within same family
  - [ ] lateral move between plans with defined policy
- [x] Define migration/compatibility rules from current flat offer records into family/tier structure (runtime defaults and backward-safe fallbacks).
- [x] Add API endpoints and validations for family/plan management foundations (`/offers` metadata + `/offer-families` grouped view).
- [x] Add UI changes for grouped offer visibility and selection labels.
- [ ] Add regression and integration tests covering:
  - [x] grouped family/tier catalog API behavior
  - [ ] downgrade behavior
  - [ ] invoice line correctness after mid-cycle plan change.

Exit criteria:
- [ ] Operators can manage one service family with multiple tiers without duplicating unrelated offer definitions.
- [ ] Contract upgrades/downgrades are deterministic and fully auditable.
- [ ] Billing receives the exact contracted plan version and price timeline.

## Phase 4.3 - Contract-First Intake UX and Subscriber Compatibility
Objective: route onboarding and plan changes through contracts while preserving subscriber-service integrity.

Tasks:
- [x] Redesign contract tab workflow with two explicit paths:
  - [x] new client intake (personal information + offer/plan selection)
  - [x] existing client flow (offer/plan selection only)
- [x] Update client tab to management-only mode:
  - [x] status updates
  - [x] controlled deletion action
- [ ] Implement client deletion guardrails:
  - [x] block hard delete when linked contracts exist
  - [x] allow hard delete only for safe/no-history clients
  - [x] extend guard to invoices once billing is implemented
  - [x] extend guard to payments once collections is implemented
- [x] Ensure subscriber handling remains automatic in contract provisioning and fully compatible with subscriber-service APIs.
- [x] Ensure contract provisioning remains API-ready for both inline new-client payload and existing-client references.
- [ ] Add backend + frontend tests for:
  - [ ] new client provisioning flow (UI + API integration)
  - [ ] existing client provisioning flow (UI + API integration)
  - [x] subscriber auto-create/reuse behavior
  - [x] client deletion restrictions.

Exit criteria:
- [ ] Operator can complete both onboarding and existing-client plan changes from contract tab.
- [ ] Client management tab no longer duplicates onboarding intake responsibilities.
- [ ] Subscriber data integrity is preserved under all supported provisioning paths.

## Phase 4.4 - Offer Service-Component Refactor (Staff Workflow)
Objective: make offer creation operationally simple and rule-driven for staff users.

Tasks:
- [x] Constrain offer creation to three services: `mobile`, `internet`, `landline`.
- [x] Enforce component-specific backend validation rules:
  - [x] mobile requires data and/or calls component
  - [x] internet requires exactly one access component (`fiber` or `adsl`)
  - [x] internet enforces `landline` as always-on mandatory component
  - [x] landline supports national/international/phone components with integer-hour quotas
- [x] Keep contract/subscriber compatibility by deriving backend `service_type` from selected service components.
- [x] Refactor Offers tab to guided service-component form with create + update + delete actions.
- [x] Add frontend pre-submit validation to prevent avoidable `422` offer payload errors and show clear operator-facing messages.
- [x] Apply staff UX simplifications in Offers tab:
  - [x] service selector shown before offer name
  - [x] version input removed from operator form/list (backend versioning retained internally)
  - [x] optional validation-date toggle with undefined display when not applied
  - [x] add `other fees` (activation fee) input after monthly fee
  - [x] landline international/phone hour inputs gated by explicit yes/no toggles
- [x] Upgrade Offers tab visual design to stable operations layout:
  - [x] fixed component rows with disabled-state inputs to prevent layout jumps
  - [x] segmented/pill toggles for binary selections
  - [x] live offer preview panel with service/components/fees/validation summary
  - [x] responsive two-column desktop layout and single-column mobile fallback
- [x] Fix backend middleware ordering so CORS headers are emitted consistently on API failures (debuggability for browser clients).
- [x] Harden launcher/runtime stability on Windows:
  - [x] disable backend reload mode by default
  - [x] add backend port fallback (`8000` -> `8010`) when stale listeners persist
  - [x] inject frontend API base URL from launcher-selected backend port
  - [x] fix launcher batch error handling (`errorlevel` checks) to avoid false startup failures inside parenthesized blocks
  - [x] enforce frontend backend resolution probe with CORS + OpenAPI validation to avoid stale/wrong local port selection
  - [x] enforce OpenAPI contract smoke check for `/api/v1/offer-categories`.
- [x] Add guarded hard-delete endpoint for offers (`409 offer_delete_blocked` when contract history exists).
- [x] Update API contract tests for offer validation, grouped categories, and delete guardrails.
- [x] Reset local PostgreSQL `mt_facturation` database for fresh baseline per current test-stage decision.

Exit criteria:
- [x] Staff can only create offers from allowed services and component sets.
- [x] Invalid component combinations are rejected by API validation.
- [x] Offer update/delete actions are available in UI with backend integrity guardrails.

## Phase 4.5 - Client Landing Subscription Flow and Contract Intake Automation (Independent, API-First)
Objective: deliver a public client landing journey (new subscription and upgrade/downgrade) that drives automated contract provisioning while keeping full API parity with the internal contract workflow.

Tasks:
- [x] Define and freeze API-first contracts for all landing actions (no UI-only behavior):
  - [x] publish OpenAPI request/response schemas for landing flow endpoints under `/api/v1`
  - [x] enforce standard error envelope + correlation IDs on all new endpoints
  - [x] add idempotency key handling for final submit endpoints (new subscription and upgrade/downgrade confirmation)
  - [x] document compatibility and versioning policy for partner/external integrators
- [x] Implement client landing entrypoint (frontend + API):
  - [x] add initial decision step: `subscribe_new_service` vs `upgrade_or_downgrade_existing_service`
  - [x] expose API endpoint for bootstrap data (available services, active offers, flow metadata)
  - [x] expose API endpoint to persist/restore in-progress draft state for recovery-safe navigation
- [x] Implement new-subscription path (frontend + API):
  - [x] service selection step constrained to `mobile`, `internet`, `landline`
  - [x] offer selection step filtered by selected service and offer status
  - [x] personal-information form with required fields:
    - [x] `cin`
    - [x] `full_name`
    - [x] `email`
    - [x] `address`
    - [x] contact phone field behavior based on selected service logic
  - [x] preview/validation step with full summary (service, offer, fees, personal info, identifiers)
  - [x] submit step that calls API to trigger contract provisioning automation
- [x] Implement mobile number decisioning rules (frontend + API):
  - [x] add explicit choice: `use_existing_mobile_number` or `request_new_mobile_number`
  - [x] when existing number is chosen, require operator/client-provided mobile local number and validate Moroccan format (`9` digits local part, rendered as `+2126XXXXXXXXX`)
  - [x] when new number is chosen, backend allocates unique random mobile local number (`9` digits) and frontend displays it as read-only/disabled
  - [x] persist allocated/generated mobile number with uniqueness guarantees and collision retry logic
- [x] Implement internet/landline home-number rules (frontend + API):
  - [x] add required `landline` field for internet and landline service intake
  - [x] backend allocates unique random landline local number (`9` digits) rendered as `+2125XXXXXXXXX`
  - [x] frontend displays generated home landline as read-only/disabled
  - [x] persist generated landline number with uniqueness guarantees and collision retry logic
- [x] Implement upgrade/downgrade path (frontend + API):
  - [x] CIN identification step to fetch existing client profile and active contracts
  - [x] product update: allow CIN-only verification for upgrade/downgrade lookup path
  - [x] enforce single CIN verification endpoint (`/landing/clients/verify-cin`) and remove legacy alias endpoint
  - [x] present current subscribed offers grouped by service for user selection
  - [x] after source contract selection, list eligible target offers only within same service (upgrade/downgrade/lateral policy)
  - [x] implement explicit empty-state behavior when no eligible target offers exist
  - [x] preview/validation step with before/after offer details and client data
  - [x] apply selected effective date to upgraded contract start date in orchestration layer
  - [x] submit step that triggers deterministic contract change orchestration
- [x] Implement orchestration and contract/client tab integration (backend + internal UI):
  - [x] CIN-based reconciliation:
    - [x] new CIN => create new client + create new contract
    - [x] existing CIN + existing service identifier (mobile number/landline) => upgrade/downgrade existing service contract
    - [x] existing CIN + new service identifier => create additional new contract for same client
  - [x] keep manual contract creation in contract tab enabled, but route through same backend orchestration/validation rules
  - [x] ensure successful landing submissions are visible in Contracts and Clients tabs without manual re-entry
- [x] Implement contract document generation and delivery (backend + frontend + API):
  - [x] generate contract PDF on successful provisioning/upgrade confirmation
  - [x] provide API endpoint for PDF retrieval/download
  - [x] wire landing UI confirmation page to download/display contract PDF link
  - [x] store document metadata reference for future retrieval/audit
- [x] Security and audit hardening for landing flow:
  - [x] apply authentication/verification strategy for upgrade/downgrade CIN lookup flow
  - [x] add audit log entries for number allocation, contract creation, contract change, and PDF issuance
  - [x] ensure sensitive personal fields follow data protection and masking standards in logs/responses
- [x] Testing and quality gates (mandatory):
  - [x] unit tests for CIN validation, phone/landline format validation, allocation strategy, and decisioning rules
  - [x] integration tests for orchestration paths:
    - [x] new client + new contract
    - [x] existing client + new service contract
    - [x] existing client + upgrade/downgrade
  - [x] API contract tests for all landing endpoints and submit operations
  - [x] frontend component tests for wizard validation/step transitions and disabled generated-number fields
  - [x] end-to-end tests for both landing journeys (new subscription and upgrade/downgrade)
  - [x] regression tests proving manual contract tab path still works with unified backend rules

Exit criteria:
- [x] A client can complete both landing journeys end-to-end from UI.
- [x] The same journeys can be executed end-to-end via API calls only (without UI).
- [x] Contract/client records are created/updated automatically and visible in internal tabs.
- [x] Moroccan mobile/landline numbering rules are enforced and persisted safely.
- [x] Contract PDF is generated and downloadable after successful confirmation.
- [x] All required unit, integration, API-contract, frontend, and E2E tests pass.





