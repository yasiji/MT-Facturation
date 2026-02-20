# Decision Log

## Format
- Date (UTC)
- Decision
- Rationale
- Consequences

## 2026-02-16 - Architecture Baseline
- Decision: Use Python backend, React frontend, PostgreSQL, and microservice-oriented architecture.
- Rationale: aligns with project constraints and production-grade goals.
- Consequences: establish strict API contracts and service ownership boundaries early.

## 2026-02-16 - API-First Integration Model
- Decision: all business capabilities must be exposed through versioned APIs.
- Rationale: external systems must integrate reliably.
- Consequences: contract tests become mandatory for each service API.

## 2026-02-16 - One-Shot Local Bootstrap
- Decision: maintain `launch_all.bat` as canonical local startup command.
- Rationale: minimize setup friction and enforce repeatable local startup.
- Consequences: launcher must evolve with structure and dependency changes.

## 2026-02-17 - Offer Service-Component Modeling
- Decision: replace staff-facing offer family/tier capture with strict service-component model (`mobile`, `internet`, `landline`).
- Rationale: simplifies operator workflow and enforces business-valid combinations at API level.
- Consequences:
  - internet offers require exactly one access type (`fiber` or `adsl`)
  - hour-based components are integer-only
  - offer deletion is hard-blocked when contract history exists
  - `/api/v1/offer-categories` is primary grouped read endpoint; `/api/v1/offer-families` retained as deprecated compatibility alias.

## 2026-02-17 - Windows Runtime Stability Hardening
- Decision: harden launcher and dev startup against stale backend processes and port collisions.
- Rationale: repeated local runs on Windows showed stale runtime state causing API mismatch and false CORS symptoms.
- Consequences:
  - backend `--reload` disabled by default in `start-backend.bat`
  - launcher falls back to backend port `8010` when `8000` cannot be cleaned
  - frontend API base URL is injected by launcher to match active backend port
  - launcher smoke checks validate OpenAPI path `/api/v1/offer-categories` to detect stale backend API shape early.

## 2026-02-18 - Landing Lookup Verification and Secure Document Delivery
- Decision: require CIN lookup verification (email/phone match) before listing subscriptions and secure contract-PDF download through signed, short-lived tokens.
- Rationale: public landing routes needed stronger protection against CIN-only enumeration and unrestricted document access.
- Consequences:
  - new endpoint `POST /api/v1/landing/clients/verify`
  - lookup endpoint now requires `lookup_token`
  - contract document downloads use tokenized landing route with expiry.

## 2026-02-18 - Landing Contract Document Persistence
- Decision: persist contract-document metadata (`contract_documents`) and issue PDF artifacts on both new-subscription and plan-change confirmations.
- Rationale: Phase 4.5 requires automated contract generation and retrieval parity across UI and API flows.
- Consequences:
  - submit responses now provide a live `document_download_url`
  - audit trail includes `landing_service_identifier_allocated` and `contract_document_issued` events
  - partner compatibility/versioning policy documented in `docs/landing-api-compatibility-policy.md`.
