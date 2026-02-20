# MT-Facturation - Project Journal

Last Updated: 2026-02-20 10:09 UTC

## Purpose
This file is the project memory across sessions. Every meaningful action must be logged here to preserve continuity.

## Logging Rules
- Add one entry per work session.
- Keep entries chronological (oldest to newest).
- Include real outcomes, not intentions only.
- Record decisions, risks, and next actions.
- Record what tests were run and their results.
- In every interaction/iteration, review and update all project Markdown files.

## Entry Template
```md
## [YYYY-MM-DD HH:MM UTC] Session Entry
Author: <name or role>
Context:
- <why this session happened>

Actions:
- <what was done>

Decisions:
- <technical/product decisions made>

Files Changed:
- <path>

Tests:
- <test name or suite>: <pass/fail/not run>

Risks/Blockers:
- <risk or blocker>

Next Steps:
- <next action>
```

## Entries

## [2026-02-16 00:00 UTC] Session Entry
Author: Codex Agent
Context:
- User requested project governance and planning documents before implementation.

Actions:
- Created project charter and operating rules in `Agents.md`.
- Created chronological execution roadmap in `tasks.md`.
- Created technical stack and engineering standards in `stack.md`.
- Created mandatory startup rules in `mustread.md`.
- Initialized this journal with template and first log entry.
- Verified all created files exist and are readable.

Decisions:
- Adopted Python + React + PostgreSQL as hard constraints.
- Adopted microservice-first architecture with strict testing gates.
- Added explicit phase-based delivery model.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation task: no code tests required.
- File creation verification: pass.

Risks/Blockers:
- None currently.

Next Steps:
- Start Phase 0 tasks and log completion updates in this journal.

## [2026-02-16 00:30 UTC] Session Entry
Author: Codex Agent
Context:
- User added new governance constraints: API readiness, PostgreSQL credentials, and mandatory Markdown synchronization at each interaction.

Actions:
- Updated `Agents.md` to enforce API-first interoperability and interaction-level documentation synchronization.
- Updated `tasks.md` with a recurring documentation synchronization rule and API integration tasks in phase flows.
- Updated `stack.md` with mandatory API standards and the provided PostgreSQL local credentials.
- Updated `mustread.md` startup/completion checklists to enforce synchronization across all project Markdown files.
- Updated `journal.md` logging rules and recorded this session.

Decisions:
- External interoperability is now a hard platform rule.
- Credentials are documented as local development inputs only.
- Every interaction/iteration now requires reviewing and updating all project Markdown governance files.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation task: no code tests required.
- File update verification: pass.

Risks/Blockers:
- Storing plaintext credentials in repository documentation is risky for shared/non-local environments.

Next Steps:
- Start Phase 0 execution with API-first constraints and synchronized documentation updates.

## [2026-02-16 01:00 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a one-shot Windows batch launcher to bootstrap and run the full system, including venv setup and dependency verification.

Actions:
- Added `launch_all.bat` at project root with:
  - backend venv bootstrap (`backend\.venv`) if missing
  - backend dependency installation from `requirements.txt` or `pyproject.toml`
  - backend dependency check using `pip check`
  - frontend dependency installation (`npm ci` or `npm install`)
  - frontend dependency check using `npm ls --depth=0`
  - backend and frontend startup in separate terminal windows
  - PostgreSQL environment variables for backend process (`PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`)
- Updated governance docs to make one-shot launcher a project rule.
- Updated planning and startup protocols to track launcher maintenance.

Decisions:
- Launcher filename standardized to `launch_all.bat`.
- Launcher supports custom per-app startup scripts:
  - `backend\start-backend.bat`
  - `frontend\start-frontend.bat`
- Fallback startup commands are used when custom scripts do not exist.

Files Changed:
- launch_all.bat
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation and script creation task: completed.
- Runtime execution test of launcher: not run (backend/frontend folders not present yet).

Risks/Blockers:
- Current repository does not yet contain `backend` and `frontend` directories, so full launcher runtime validation must wait.

Next Steps:
- Create backend/frontend project skeletons and run `launch_all.bat` for full integration validation.

## [2026-02-16 01:10 UTC] Session Entry
Author: Codex Agent
Context:
- Performed launcher validation and final synchronization updates across all Markdown governance files.

Actions:
- Fixed a batch parser issue in `launch_all.bat` caused by unescaped parentheses in `echo` lines.
- Dry-ran `launch_all.bat` from project root to validate execution path and error handling.
- Added `Last Updated` stamps in all required project Markdown files:
  - `Agents.md`
  - `tasks.md`
  - `stack.md`
  - `mustread.md`
  - `journal.md`

Decisions:
- Keep launcher fail-fast when no `backend` and `frontend` directories exist to avoid false-positive startup.

Files Changed:
- launch_all.bat
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- `cmd /c launch_all.bat`: pass for script execution and guardrails; returns expected failure because backend/frontend folders do not exist yet.

Risks/Blockers:
- Full end-to-end launcher validation remains blocked until backend and frontend skeletons are created.

Next Steps:
- Create `backend` and `frontend` scaffolds, then rerun `launch_all.bat` for full successful startup validation.

## [2026-02-16 12:04 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to start execution from `tasks.md` and begin real implementation work.

Actions:
- Completed Phase 0 foundational artifacts:
  - `docs/business-glossary.md`
  - `docs/release-criteria.md`
  - `docs/documentation-workflow.md`
  - `docs/decision-log.md`
- Completed key Phase 1 scaffolding:
  - `backend/` FastAPI template with settings, versioned API routing, tests, lint/type config, Dockerfile, and `start-backend.bat`
  - `frontend/` React + TypeScript + Vite template with lint/type/test/build scripts and `start-frontend.bat`
  - `infra/docker-compose.yml` with local PostgreSQL dev/test instances
  - `.github/workflows/ci.yml` CI skeleton
  - `.gitignore`
  - `docs/branching-policy.md`
- Improved `launch_all.bat` frontend dependency handling to run install and checks inside `frontend/`.
- Executed one-shot launcher validation and terminated spawned runtime processes after verification.
- Updated all required governance Markdown files and task checkboxes.

Decisions:
- Keep Phase 0 fully complete with baseline documentation, while noting business sign-off remains pending.
- Keep Phase 1 CI exit criterion pending until first hosted CI run confirms pipeline execution.

Files Changed:
- docs/business-glossary.md
- docs/release-criteria.md
- docs/documentation-workflow.md
- docs/decision-log.md
- docs/branching-policy.md
- backend/requirements.txt
- backend/pyproject.toml
- backend/Dockerfile
- backend/start-backend.bat
- backend/.env.example
- backend/app/__init__.py
- backend/app/main.py
- backend/app/core/__init__.py
- backend/app/core/settings.py
- backend/app/api/__init__.py
- backend/app/api/v1/__init__.py
- backend/app/api/v1/router.py
- backend/app/api/v1/endpoints/__init__.py
- backend/app/api/v1/endpoints/health.py
- backend/tests/test_health.py
- frontend/package.json
- frontend/tsconfig.json
- frontend/tsconfig.node.json
- frontend/vite.config.ts
- frontend/vitest.setup.ts
- frontend/.eslintrc.cjs
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/index.css
- frontend/src/App.test.tsx
- frontend/src/vite-env.d.ts
- frontend/start-frontend.bat
- frontend/.env.example
- infra/docker-compose.yml
- infra/README.md
- .github/workflows/ci.yml
- .gitignore
- launch_all.bat
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt`: pass.
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass.
- `backend/.venv/Scripts/python.exe -m mypy backend/app`: pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (2 tests).
- `npm install` (workdir `frontend`): pass.
- `npm run lint` (workdir `frontend`): pass.
- `npm run typecheck` (workdir `frontend`): pass.
- `npm run test:run` (workdir `frontend`): pass (1 test).
- `npm run build` (workdir `frontend`): pass.
- `cmd /c launch_all.bat`: pass (start sequence succeeds with current scaffold).

Risks/Blockers:
- Python environment emits repeated message `Could not find platform independent libraries <prefix>` from local interpreter setup; current execution succeeds but environment health should be reviewed.
- Frontend dependency audit reports moderate vulnerabilities in transitive packages; remediation should be planned in a dedicated hardening task.

Next Steps:
- Begin Phase 2 by implementing shared auth, error envelope, and API conventions across service templates.

## [2026-02-16 12:07 UTC] Session Entry
Author: Codex Agent
Context:
- Finalized this iteration with explicit microservice boundary structure alignment and documentation synchronization.

Actions:
- Added explicit microservice boundary directories under `backend/services/`.
- Added architecture mapping document at `backend/services/README.md`.
- Updated baseline artifact references in governance and technical documents.
- Refreshed `Last Updated` stamps across required Markdown files for this interaction.

Decisions:
- Keep runtime bootstrap in `backend/app` for now, while preserving domain service boundaries in `backend/services/` for upcoming implementation phases.

Files Changed:
- backend/services/README.md
- Agents.md
- stack.md
- tasks.md
- mustread.md
- journal.md

Tests:
- Structure and documentation update: no additional code execution required.

Risks/Blockers:
- None new; existing environment warning on Python interpreter remains tracked.

Next Steps:
- Start Phase 2 implementation from `tasks.md` using established service boundary folders.

## [2026-02-16 12:26 UTC] Session Entry
Author: Codex Agent
Context:
- Continued execution from `tasks.md` and implemented Phase 2 shared technical foundations.

Actions:
- Added shared backend foundations under `backend/app/common/`:
  - `auth.py` for authentication context extraction, authorization checks, and auth middleware
  - `errors.py` for standardized API error envelope and global exception handlers
  - `api.py` for pagination/filtering/sorting conventions and paginated response builder
  - `observability.py` for request context, trace ID propagation, logging, and hooks
- Added Phase 2 API endpoints:
  - `GET /api/v1/me`
  - `GET /api/v1/admin/ping`
  - `GET /api/v1/conventions/sample`
- Integrated middleware and exception handlers in `backend/app/main.py`.
- Extended settings with configurable public paths.
- Added migration strategy baseline:
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/README.md`
  - `backend/alembic/versions/README.md`
  - `backend/docs/db-migration-standards.md`
  - `backend/app/db/base.py`
- Added shared test fixtures and Phase 2 tests:
  - `backend/tests/conftest.py`
  - `backend/tests/test_auth_and_conventions.py`
- Updated router wiring and existing tests to use shared fixtures.
- Updated project tracking docs and marked Phase 2 tasks complete in `tasks.md`.

Decisions:
- Authentication middleware is enabled by default for non-public paths with two local input modes:
  - `Authorization: Bearer actor_id:role1,role2`
  - `X-Actor-Id` + `X-Actor-Roles`
- API error payload is standardized as:
  - `error.code`
  - `error.message`
  - `error.details`
  - `error.trace_id`

Files Changed:
- backend/app/common/__init__.py
- backend/app/common/api.py
- backend/app/common/auth.py
- backend/app/common/errors.py
- backend/app/common/observability.py
- backend/app/db/__init__.py
- backend/app/db/base.py
- backend/app/api/v1/router.py
- backend/app/api/v1/endpoints/authz.py
- backend/app/api/v1/endpoints/conventions.py
- backend/app/main.py
- backend/app/core/settings.py
- backend/tests/conftest.py
- backend/tests/test_health.py
- backend/tests/test_auth_and_conventions.py
- backend/requirements.txt
- backend/.env.example
- backend/alembic.ini
- backend/alembic/env.py
- backend/alembic/README.md
- backend/alembic/versions/README.md
- backend/docs/db-migration-standards.md
- tasks.md
- Agents.md
- stack.md
- mustread.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt`: pass.
- `backend/.venv/Scripts/python.exe -m ruff check --fix backend`: pass.
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass.
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (8 tests).
- `cmd /c launch_all.bat`: pass.

Risks/Blockers:
- Local Python installation still emits `Could not find platform independent libraries <prefix>` warning; execution is successful but environment hygiene remains a risk.

Next Steps:
- Start Phase 3 (`customer-service` and `catalog-service`) with real domain models, CRUD endpoints, and API contract tests.

## [2026-02-16 12:33 UTC] Session Entry
Author: Codex Agent
Context:
- Continued execution from `tasks.md` into Phase 3 backend domain delivery.

Actions:
- Implemented `customer-service` backend domain APIs with SQLAlchemy:
  - client CRUD endpoints (`/api/v1/customers`)
  - subscriber CRUD endpoints and client-subscriber relationship endpoints
- Implemented `catalog-service` backend domain APIs with SQLAlchemy:
  - offer CRUD endpoints (`/api/v1/offers`)
  - versioned offer uniqueness (`name + version`)
- Added domain layers:
  - `backend/app/models/` (ORM models)
  - `backend/app/schemas/` (Pydantic request/response contracts)
  - `backend/app/services/` (business/service logic)
  - `backend/app/db/session.py` (DB session dependency and schema init helper)
- Added Phase 3 contract tests:
  - `backend/tests/test_customer_catalog_contract.py`
- Updated test infrastructure to use isolated SQLite with dependency overrides in `backend/tests/conftest.py`.
- Verified launcher still executes after backend expansion and then stopped spawned runtime processes.
- Updated Phase 3 status in `tasks.md` and synchronized all mandatory Markdown files.

Decisions:
- Keep Phase 3 frontend pages pending while backend domains and contract tests are established.
- Use dependency-overridden SQLite in tests for deterministic domain/API validation without external DB runtime dependency.

Files Changed:
- backend/app/models/__init__.py
- backend/app/models/customer.py
- backend/app/models/catalog.py
- backend/app/schemas/__init__.py
- backend/app/schemas/customer.py
- backend/app/schemas/catalog.py
- backend/app/services/customer_service.py
- backend/app/services/catalog_service.py
- backend/app/db/session.py
- backend/app/api/v1/endpoints/customer.py
- backend/app/api/v1/endpoints/catalog.py
- backend/app/api/v1/router.py
- backend/app/api/v1/endpoints/conventions.py
- backend/app/main.py
- backend/app/core/settings.py
- backend/tests/conftest.py
- backend/tests/test_customer_catalog_contract.py
- backend/.env.example
- tasks.md
- Agents.md
- stack.md
- mustread.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m ruff check --fix backend`: pass.
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass.
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (11 tests).
- `cmd /c launch_all.bat`: pass.

Risks/Blockers:
- FastAPI warns that `@app.on_event("startup")` is deprecated; migrate to lifespan handlers in a hardening pass.
- Local Python still emits `Could not find platform independent libraries <prefix>` warnings; environment remains operational but non-clean.

Next Steps:
- Implement frontend pages for Client, Subscriber, and Offer management to complete Phase 3.

## [2026-02-16 12:46 UTC] Session Entry
Author: Codex Agent
Context:
- Continued execution from `tasks.md` and completed Phase 3 frontend item.

Actions:
- Replaced `frontend/src/App.tsx` with a production-oriented management UI that connects directly to backend endpoints for:
  - client create/list/update status
  - subscriber create/list/update status (scoped by selected client)
  - offer create/list/update status
- Added frontend API request layer in-app with standard auth headers:
  - `X-Actor-Id`
  - `X-Actor-Roles`
- Updated frontend configuration example with actor settings:
  - `VITE_ACTOR_ID`
  - `VITE_ACTOR_ROLES`
- Reworked frontend styles in `frontend/src/App.css` for responsive multi-panel operations UI.
- Updated frontend test to mock fetch and assert the new domain sections.
- Validated backend tests still pass after frontend completion.
- Validated launcher still runs after this iteration and then stopped spawned runtime processes.
- Marked Phase 3 frontend task and exit criteria complete in `tasks.md`.

Decisions:
- Keep all management flows in a single `App.tsx` screen for current phase speed; split into feature modules in later refactor once Phase 4 starts.
- Keep auth header defaults environment-driven for external system/API readiness.

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/App.test.tsx
- frontend/.env.example
- tasks.md
- Agents.md
- stack.md
- mustread.md
- journal.md

Tests:
- `npm run lint` (workdir `frontend`): pass.
- `npm run typecheck` (workdir `frontend`): pass.
- `npm run test:run` (workdir `frontend`): pass.
- `npm run build` (workdir `frontend`): pass.
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass.
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (11 tests).
- `cmd /c launch_all.bat`: pass.

Risks/Blockers:
- Backend still emits FastAPI deprecation warnings for `@app.on_event("startup")`; migrate to lifespan handlers.
- Local Python warning `Could not find platform independent libraries <prefix>` still present but non-blocking.

Next Steps:
- Start Phase 4 (`contract-service`) implementation and corresponding frontend contract workflow screens.

## [2026-02-16 12:47 UTC] Session Entry
Author: Codex Agent
Context:
- Post-change validation follow-up after frontend tests temporarily failed due missing local `vitest` binary resolution.

Actions:
- Reinstalled frontend dependencies (`npm install`) in `frontend/`.
- Re-ran full frontend quality gate:
  - lint
  - typecheck
  - unit tests
  - build
- Confirmed backend quality gate still passes.

Decisions:
- Keep `npm install` as immediate remediation when local `node_modules` state becomes inconsistent.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- `npm install` (workdir `frontend`): pass.
- `npm run lint` (workdir `frontend`): pass.
- `npm run typecheck` (workdir `frontend`): pass.
- `npm run test:run` (workdir `frontend`): pass.
- `npm run build` (workdir `frontend`): pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (11 tests).

Risks/Blockers:
- `npm install` emitted Windows cleanup EPERM warnings for transient binary folders; execution remained successful.

Next Steps:
- Move to Phase 4 contract-service implementation.

## [2026-02-16 12:53 UTC] Session Entry
Author: Codex Agent
Context:
- User reported runtime logs with startup warnings and repeated `OPTIONS` 401 responses.

Actions:
- Diagnosed root causes from log:
  - CORS preflight (`OPTIONS`) requests were blocked by auth middleware.
  - local Python environment warning (`Could not find platform independent libraries <prefix>`) remains non-blocking.
  - intermittent Windows shell message (`The filename, directory name, or volume label syntax is incorrect.`) is startup-script side noise.
- Implemented backend fix for preflight/auth compatibility:
  - skip auth enforcement for `OPTIONS` in `AuthContextMiddleware`
  - added FastAPI `CORSMiddleware` with configurable allowed origins
  - extended settings and `.env.example` with `CORS_ALLOW_ORIGINS`
- Added regression test to ensure CORS preflight is not blocked by auth.
- Re-ran backend quality gates and launcher.

Decisions:
- Keep auth required for business endpoints, but always allow CORS preflight to pass.
- Configure default allowed origins for local frontend hosts (`localhost:5173`, `127.0.0.1:5173`).

Files Changed:
- backend/app/common/auth.py
- backend/app/main.py
- backend/app/core/settings.py
- backend/.env.example
- backend/tests/test_auth_and_conventions.py
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass.
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass.
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (12 tests).
- `cmd /c launch_all.bat`: pass.

Risks/Blockers:
- Python local warning `Could not find platform independent libraries <prefix>` still appears; does not block current execution.
- FastAPI startup deprecation warning (`@app.on_event`) still pending lifespan migration.

Next Steps:
- Continue with Phase 4 implementation and include lifespan migration in a hardening pass.

## [2026-02-16 14:20 UTC] Session Entry
Author: Codex Agent
Context:
- User reported backend crashes after running `launch_all.bat` and requested stronger real testing, including runtime terminal and browser-level checks.

Actions:
- Reproduced runtime behavior and confirmed CORS preflight works while intermittent `500 OperationalError` on `/api/v1/customers` occurred due stale running processes bound to launcher ports.
- Hardened backend starter script:
  - `backend/start-backend.bat` now uses explicit `backend\.venv\Scripts\python.exe` and clears `PYTHONHOME` before startup.
- Hardened one-shot launcher:
  - added stale launcher window cleanup (`MT-Facturation Backend`, `MT-Facturation Frontend`)
  - added listener cleanup on backend/frontend ports before startup
  - added post-launch smoke checks for:
    - backend health endpoint
    - authenticated backend customer list endpoint
    - frontend root endpoint
- Performed full runtime and quality verification using:
  - direct HTTP smoke requests
  - backend/ frontend test/lint/type/build suites
  - Playwright browser smoke (page render + console errors + API network status)
- Synchronized all governance Markdown files for this iteration.

Decisions:
- Launcher must fail fast if runtime smoke checks do not pass.
- Local startup reliability now includes stale-process cleanup to avoid hidden port/process contamination across repeated runs.

Files Changed:
- backend/start-backend.bat
- launch_all.bat
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- `cmd /c launch_all.bat`: pass (returns success with smoke checks).
- API smoke:
  - `OPTIONS /api/v1/customers`: pass (`200`)
  - `GET /api/v1/customers` with auth: pass (`200`)
  - `GET http://127.0.0.1:5173`: pass (`200`)
- Backend quality gate:
  - `backend/.venv/Scripts/python.exe -m pytest -q`: pass (13 tests)
  - `backend/.venv/Scripts/python.exe -m ruff check .`: pass
  - `backend/.venv/Scripts/python.exe -m mypy app`: pass
- Frontend quality gate:
  - `npm run test:run`: pass
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run build`: pass
- Playwright smoke:
  - page load on `http://127.0.0.1:5173`: pass
  - console error check: pass (0 errors)
  - network checks for `/api/v1/customers` and `/api/v1/offers`: pass (`200`)

Risks/Blockers:
- Local Python installation still prints `Could not find platform independent libraries <prefix>`; runtime now stable but workstation Python installation remains non-clean.

Next Steps:
- Continue with Phase 4 (`contract-service`) implementation.

## [2026-02-16 14:43 UTC] Session Entry
Author: Codex Agent
Context:
- User asked for a current-state capability assessment to understand if the app is already usable or still too early.

Actions:
- Reviewed implemented scope against current phase progress and runtime-validated behavior.
- Prepared a capability snapshot for current delivery status.
- Synchronized all required Markdown governance files for this interaction.

Decisions:
- Keep current status clear: app is functional for implemented domains, but full telecom billing/collections scope is not complete yet.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- No new code changes in this interaction; no additional test suite executed.

Risks/Blockers:
- Remaining planned domains (contracts, invoices, payments/collections) are not yet implemented.

Next Steps:
- Continue with Phase 4 contract-service implementation.

## [2026-02-16 14:54 UTC] Session Entry
Author: Codex Agent
Context:
- User reported subscriber creation failing from UI with `422 Unprocessable Content` on `POST /api/v1/customers/{client_id}/subscribers`.

Actions:
- Reproduced and analyzed subscriber request validation path.
- Implemented backend normalization/validation for subscriber identifiers:
  - trims `service_identifier`
  - rejects identifiers with fewer than 3 non-space characters.
- Fixed validation error serialization in global error handler so custom validator errors always return JSON-safe payloads.
- Improved frontend API error extraction to show precise validation hints instead of generic fallback status message.
- Added frontend guardrails for subscriber create:
  - `service_identifier` input has `minLength=3` and `maxLength=100`
  - submit path trims identifier before sending
  - submit blocked with explicit banner when trimmed identifier is too short.
- Added/updated tests for new behavior and validation.
- Validated behavior with runtime API calls after launcher startup.

Decisions:
- Keep backend as source of truth for validation and add matching client-side checks for immediate UX feedback.
- Keep response format stable (`validation_error`) while improving detail readability in frontend.

Files Changed:
- backend/app/schemas/customer.py
- backend/app/common/errors.py
- backend/tests/test_customer_catalog_contract.py
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m pytest -q`: pass (14 tests)
  - `backend/.venv/Scripts/python.exe -m ruff check .`: pass
  - `backend/.venv/Scripts/python.exe -m mypy app`: pass
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Runtime:
  - `cmd /c launch_all.bat`: pass
  - `POST /subscribers` with `"service_identifier": " a "`: pass expected `422`
  - `POST /subscribers` with `"service_identifier": " 21655123459 "`: pass `200` with normalized stored identifier `21655123459`.

Risks/Blockers:
- Local Python warning `Could not find platform independent libraries <prefix>` still appears and remains a workstation environment hygiene issue.

Next Steps:
- Continue Phase 4 implementation while preserving the new validation and UX error behavior.

## [2026-02-16 15:04 UTC] Session Entry
Author: Codex Agent
Context:
- User asked for domain clarification about the role of `subscriber` and whether offer selection should happen there.

Actions:
- Clarified telecom business flow and entity responsibilities:
  - Client as billing/legal party
  - Subscriber as technical service instance (line/account)
  - Offer as catalog template
  - Contract as legal/commercial link between client/subscriber and selected offer
  - Invoice/receipt generated from contract charges and payments
- Confirmed that current app state (subscriber without offer binding) is expected before Phase 4 contract implementation.
- Synchronized all required Markdown governance files for this interaction.

Decisions:
- Keep domain direction: offer should be selected during contract creation (or checkout flow that creates contract), not as a hard requirement of raw subscriber record creation.
- Plan Phase 4 UI to make offer-to-subscriber relationship explicit via contract creation workflow.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- No code changes in this interaction; no additional test run required.

Risks/Blockers:
- User confusion risk remains until contract workflow UI is implemented.

Next Steps:
- Implement contract creation flow with offer selection and activation states in Phase 4.

## [2026-02-16 15:10 UTC] Session Entry
Author: Codex Agent
Context:
- User asked to validate proposed business logic for new and existing client onboarding with offer binding.

Actions:
- Confirmed the proposed flow is largely correct and aligned with telecom domain patterns.
- Clarified one important modeling rule: offer selection should create a contract; subscriber may be auto-created only when required by service type.
- Synchronized all required Markdown governance files for this interaction.

Decisions:
- Keep target flow: offer assignment must be expressed through contract creation.
- Support automatic subscriber creation in checkout flow where technically valid, while still keeping subscriber as first-class entity.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- No code changes in this interaction; no test run required.

Risks/Blockers:
- Potential confusion remains until Phase 4 UI exposes explicit contract creation and “auto-create subscriber” behavior rules.

Next Steps:
- Implement Phase 4 contract workflow and define per-offer-type subscriber auto-provisioning rules.

## [2026-02-16 15:19 UTC] Session Entry
Author: Codex Agent
Context:
- User asked to confirm that contracts and subscriptions should be handled automatically by the app, not manually.

Actions:
- Confirmed automation as the target business rule.
- Updated project governance and planning docs to encode this requirement for implementation.

Decisions:
- Contract/subscriber handling is automated from offer selection flow.
- Manual data-entry for contract/subscriber linkage is not the primary operational path.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation-only update; no code changes or test runs.

Risks/Blockers:
- Until Phase 4 is implemented, UI behavior will still look partially manual.

Next Steps:
- Implement automated provisioning in Phase 4 contract-service and frontend flow.

## [2026-02-16 15:30 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to move to the next phase/task after confirming automation direction.

Actions:
- Implemented Phase 4 contract domain backend with automated provisioning:
  - added contract and contract-audit ORM models.
  - added contract schemas for provisioning, creation, status updates, offer updates, and audit reads.
  - implemented contract service with:
    - automated provisioning flow (offer selection drives contract creation and subscriber create/reuse logic)
    - client create/reuse logic during provisioning
    - subscriber create/reuse logic with compatibility checks
    - contract status transition rules
    - date and commitment validation logic
    - audit event recording for provisioning, creation, status changes, and offer changes.
- Added contract API endpoints:
  - `POST /api/v1/contracts/provision`
  - `POST /api/v1/contracts`
  - `GET /api/v1/contracts`
  - `GET /api/v1/contracts/{contract_id}`
  - `PUT /api/v1/contracts/{contract_id}/status`
  - `PUT /api/v1/contracts/{contract_id}/offer`
  - `GET /api/v1/contracts/{contract_id}/audit`
- Integrated contract router and schema initialization imports.
- Added backend integration tests covering:
  - automated provisioning with auto-created client/subscriber
  - provisioning with existing client/subscriber reuse
  - status transitions, invalid transitions, offer change, and audit trail verification.
- Extended frontend with Contract Provisioning workflow:
  - contract list panel
  - offer/client selection
  - optional subscriber reuse (or auto-create)
  - contract start + commitment + auto-activate controls
  - contract status update control
  - refresh flow and UX messages tied to provisioning result.
- Updated frontend tests for new contract panel visibility.
- Validated runtime contract APIs and UI loading after launcher execution.
- Updated project planning docs and marked Phase 4 items complete.

Decisions:
- Provisioning is now first-class API behavior and the default operational path.
- Subscriber selection is optional in contract provisioning; omission triggers automated compatible subscriber creation.

Files Changed:
- backend/app/models/contract.py
- backend/app/db/session.py
- backend/app/schemas/contract.py
- backend/app/services/contract_service.py
- backend/app/api/v1/endpoints/contract.py
- backend/app/api/v1/router.py
- backend/tests/conftest.py
- backend/tests/test_contract_service.py
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check .`: pass
  - `backend/.venv/Scripts/python.exe -m mypy app`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q`: pass (17 tests)
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Runtime:
  - `cmd /c launch_all.bat`: pass
  - runtime contract API flow: create offer -> provision contract -> list contracts -> fetch audit: pass
  - Playwright smoke: app loads, contract section visible, API calls for customers/offers/contracts return `200`.

Risks/Blockers:
- Local Python warning `Could not find platform independent libraries <prefix>` persists as workstation environment hygiene issue.
- FastAPI startup deprecation warning (`@app.on_event`) still pending lifespan migration.

Next Steps:
- Start Phase 5 billing domain (invoice generation/list/download and billing orchestration).

## [2026-02-16 15:59 UTC] Session Entry
Author: Codex Agent
Context:
- User asked whether creating offer, then client, then contract is too heavy for regular usage.

Actions:
- Clarified UX split between admin/backoffice setup and sales/onboarding flow:
  - offer creation is catalog admin activity and should not happen per customer.
  - customer onboarding should be a single flow that captures client + selected offer and triggers automated contract/subscriber provisioning.
- Confirmed current implementation is functionally correct but can be simplified in UX for non-admin users.
- Synchronized all required Markdown governance files for this interaction.

Decisions:
- Keep domain model as-is.
- Position current multi-panel UI as operational/admin console.
- Plan a simpler onboarding UX path for day-to-day user operations.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- No code changes in this interaction; no additional test run required.

Risks/Blockers:
- If onboarding UX is not simplified, user friction remains high for non-technical operators.

Next Steps:
- Add a dedicated “New Subscription” guided flow (single form) on top of existing APIs.

## [2026-02-16 16:07 UTC] Session Entry
Author: Codex Agent
Context:
- User confirmed current build works and asked for guidance on automation behavior, multi-offer handling, and upgrade flows without destabilizing implemented features.

Actions:
- Confirmed direction to keep backend foundations and avoid disruptive rewrites.
- Captured product rule for current stage: single operator workflow is acceptable while testing.
- Added UX automation refinement phase to plan:
  - hide direct subscriber panel from primary workflow
  - keep subscriber APIs for technical/admin use
  - route daily operations through contract provisioning
  - formalize upgrade vs new-line automation decisions.
- Synchronized all required Markdown governance files for this interaction.

Decisions:
- Offer + client actions should stay contract-first in the primary UX.
- Multiple offers usually imply multiple contracts, but upgrades should reuse existing subscriber and update/transition contract where appropriate.
- Keep one user/role mode for now; postpone RBAC complexity until later hardening.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation/planning update only; no code changes or additional test runs.

Risks/Blockers:
- Without explicit decision rules in UI, users may confuse upgrade flow vs new-line flow.

Next Steps:
- Implement Phase 4.1 UX automation refinement with explicit upgrade/new-line decision behavior.

## [2026-02-16 16:18 UTC] Session Entry
Author: Codex Agent
Context:
- User requested UI usability improvements: separate sections into tabs, add status colors, and track these in Phase 4.1 tasks.

Actions:
- Implemented tabbed navigation in frontend so sections are no longer stacked vertically:
  - Contracts
  - Clients
  - Offers
  - Subscribers
- Set Contract tab as the default active tab to align with automated provisioning workflow.
- Added status color badges for lifecycle states (`active`, `suspended`, `terminated`) and related states (`draft`, `retired`).
- Updated frontend test to validate tabbed workspace behavior and subscriber tab form field validation visibility.
- Updated `tasks.md` Phase 4.1 to include requested items and marked completed:
  - tabbed UI navigation
  - semantic status colors/badges.
- Synchronized all required Markdown governance files.

Decisions:
- Keep subscriber feature available in a separate tab for now; primary path remains contract-first.
- Do not alter backend behavior in this iteration; UX-only refinement.

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/App.test.tsx
- tasks.md
- Agents.md
- stack.md
- mustread.md
- journal.md

Tests:
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Playwright smoke:
  - app loads with tab navigation visible
  - default contract tab visible
  - only console error is `favicon.ico` 404 (non-functional).

Risks/Blockers:
- Subscriber tab is still visible (by design for now); hide-from-primary-flow task remains pending in Phase 4.1.

Next Steps:
- Implement remaining Phase 4.1 behavior: hide subscriber tab from primary flow and add explicit upgrade/new-line decision logic.

## [2026-02-16 16:28 UTC] Session Entry
Author: Codex Agent
Context:
- User requested full completion of Phase 4.1 UX automation refinement.

Actions:
- Completed backend automation decision rules in contract provisioning:
  - added provisioning intent (`upgrade`, `new_line`) to request schema.
  - enforced upgrade path to update existing active contract offer (no new subscriber).
  - enforced new-line path to create a new subscriber + new contract.
  - added disambiguation handling when multiple active upgrade candidates exist.
  - added `provisioning_mode` in provisioning response.
- Completed frontend primary-flow UX:
  - removed Subscriber tab from primary navigation.
  - contract form now includes intent selector and target contract chooser for upgrade.
  - new-line flow supports optional service identifier and automatic subscriber creation.
  - submit disabling and hinting for upgrade disambiguation.
- Kept subscriber APIs/endpoints unchanged for technical/admin operations.
- Added/updated tests for upgrade vs new-line decisions and disambiguation scenarios.
- Updated Phase 4.1 tasks and exit criteria to completed.

Decisions:
- Subscriber management is no longer part of primary operator navigation.
- Day-to-day subscription and offer-change actions are contract-first.
- Backend remains authoritative for disambiguation and intent validation.

Files Changed:
- backend/app/schemas/contract.py
- backend/app/services/contract_service.py
- backend/app/api/v1/endpoints/contract.py
- backend/tests/test_contract_service.py
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- tasks.md
- Agents.md
- stack.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check .`: pass
  - `backend/.venv/Scripts/python.exe -m mypy app`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q`: pass (19 tests)
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Runtime:
  - `cmd /c launch_all.bat`: pass
  - API smoke for Phase 4.1:
    - upgrade with multiple candidates returns `409 contract_upgrade_disambiguation_required`
    - targeted upgrade succeeds with `provisioning_mode=upgrade_existing_contract`
    - new-line provisioning succeeds with `provisioning_mode=new_contract` and `created_subscriber=true`
  - Playwright smoke confirms tabbed UI with Contracts/Clients/Offers only and contract-first provisioning controls.

Risks/Blockers:
- Local Python warning `Could not find platform independent libraries <prefix>` persists as workstation environment hygiene issue.

Next Steps:
- Start Phase 5 billing domain implementation.

## [2026-02-16 16:43 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a final refinement: provisioning intent should be auto-detected by the system rather than manually selected in UI.

Actions:
- Finalized backend auto-detection behavior for contract provisioning:
  - kept request schema `provisioning_intent` default as `auto`
  - maintained compatibility for explicit `upgrade` and `new_line` intents
  - auto mode now resolves to upgrade/new-contract based on candidate contracts, target contract selection, and subscriber hints.
- Finalized frontend contract provisioning UX for auto mode:
  - removed manual intent selection from contract form
  - added read-only detected mode indicator
  - kept optional target contract selection for disambiguation
  - kept optional new service identifier to force new-line provisioning.
- Updated frontend test to assert the new auto-detection controls (`Detected Mode`, `Target Contract (Optional)`).
- Expanded backend contract tests to validate auto mode behaviors:
  - auto upgrade when a unique upgrade candidate exists
  - auto disambiguation requirement when multiple upgrade candidates exist
  - auto targeted upgrade success
  - auto new-line creation when new service identifier is provided.
- Performed runtime and UI smoke checks:
  - executed `launch_all.bat`
  - verified ports `8000` and `5173` listening
  - verified backend health and frontend root return HTTP 200
  - ran Playwright navigation smoke and tab/contract-form assertions.
- Synchronized all required Markdown files for this iteration.

Decisions:
- Contract provisioning in operator UI is now fully auto-intent by default.
- Manual intent choice remains available only as API-level compatibility for external systems.

Files Changed:
- backend/app/services/contract_service.py
- backend/tests/test_contract_service.py
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend\\.venv\\Scripts\\python -m ruff check .`: pass
  - `backend\\.venv\\Scripts\\python -m mypy app`: pass
  - `backend\\.venv\\Scripts\\python -m pytest -q`: pass (20 passed)
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Runtime/Smoke:
  - `cmd /c launch_all.bat`: pass
  - `GET http://127.0.0.1:8000/api/v1/health`: 200
  - `GET http://127.0.0.1:5173`: 200
  - Playwright UI smoke: pass (only console error is missing `favicon.ico` 404).

Risks/Blockers:
- Local environment still emits `Could not find platform independent libraries <prefix>` on some backend Python command runs; commands still complete successfully.

Next Steps:
- Begin Phase 5 billing-service implementation (invoice generation, listing, and download APIs/UI).

## [2026-02-16 16:59 UTC] Session Entry
Author: Codex Agent
Context:
- User requested explicit governance enforcement that agent behavior must remain unbiased, brutally honest, and challenging when ideas are weak.
- User also clarified catalog intent: one service family should support multiple commercial tiers for upgrade/downgrade readiness.

Actions:
- Updated `mustread.md` startup/completion checklists to enforce:
  - unbiased and brutally honest technical guidance
  - explicit challenge/critical-review verification for each iteration.
- Updated `Agents.md` delivery workflow to require objective challenge behavior and no rubber-stamping.
- Added a new planning section in `tasks.md`:
  - `Phase 4.2 - Catalog Tiering and Plan-Change Readiness`
  - includes data model, API, UI, migration, and test tasks.
- Updated `stack.md` with recommended catalog hierarchy:
  - `offer_family` -> `offer_plan` -> `offer_plan_version`
  - contracts to reference versioned plan for billing immutability.
- Synchronized all required project Markdown files.

Decisions:
- Offer-family + tier modeling is accepted as a required hardening step before full contract upgrade/downgrade maturity.
- Agent behavior policy now explicitly requires critical challenge and objective tradeoff analysis.

Files Changed:
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Documentation/planning updates only; no code changes and no test reruns in this iteration.

Risks/Blockers:
- Catalog model migration from current flat offers to family/tier/version structure will require careful data migration design.

Next Steps:
- Implement Phase 4.2 schema and API foundations for offer family/tier/version.

## [2026-02-17 10:15 UTC] Session Entry
Author: Codex Agent
Context:
- User proposed a simplified operational redesign:
  - keep three tabs (Contracts, Clients, Offers)
  - move onboarding intake to Contract tab (new client vs existing client paths)
  - keep Client tab management-focused
  - preserve automatic subscriber handling and compatibility.

Actions:
- Reviewed proposal with critical constraints and accepted the direction with guardrails.
- Updated planning with `Phase 4.3 - Contract-First Intake UX and Subscriber Compatibility`.
- Added explicit subscriber compatibility and client deletion integrity rules in technical standards.
- Updated governance/startup protocol to validate:
  - contract-first routing
  - subscriber-service compatibility
  - safe client deletion policy.
- Synchronized all required project markdown files.

Decisions:
- Contract tab becomes the operational routing hub for onboarding and plan changes.
- Client tab should not duplicate onboarding intake responsibilities.
- Hard delete of client records is restricted and must be blocked when contracts/invoices/payments exist.

Files Changed:
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Documentation/planning update only; no code execution in this iteration.

Risks/Blockers:
- Client hard-delete requirement can conflict with billing/audit integrity if applied without dependency checks.

Next Steps:
- Implement Phase 4.2 first (family/tier/version model), then Phase 4.3 UX and deletion guardrails with tests.

## [2026-02-17 10:41 UTC] Session Entry
Author: Codex Agent
Context:
- User approved implementation start and requested compatibility with subscriber-service behavior while adopting the new contract-first operational design.

Actions:
- Implemented catalog tiering foundations (Phase 4.2 start):
  - extended offer domain with family/tier metadata (`family_name`, `tier_name`, `tier_rank`, `feature_summary`).
  - added grouped catalog endpoint `GET /api/v1/offer-families`.
  - kept contract linkage to `offer_id` unchanged to preserve subscriber compatibility.
- Implemented contract-first intake and client-management changes (Phase 4.3 start):
  - frontend contract tab now supports explicit `existing client` vs `new client` flow.
  - new-client intake fields moved into contract provisioning form.
  - client tab switched to management-only workflow (status + delete action).
  - backend added `DELETE /api/v1/customers/{client_id}` with contract-history guardrail.
- Added client address support to schemas/models and runtime bootstrap compatibility helper for PostgreSQL column backfill.
- Added/updated tests:
  - grouped offer family API behavior
  - client deletion guardrails
  - frontend contract-first UI expectations.
- Executed Playwright smoke checks validating:
  - contract flow switcher and new-client intake rendering
  - offers tab family/tier form fields and grouped display.

Decisions:
- Chose a backward-safe implementation that enriches existing `offers` records rather than introducing a breaking multi-table catalog split in one step.
- Preserved automatic subscriber behavior as the source of truth inside contract provisioning.
- Enforced destructive-delete guardrail for clients with contract history.

Files Changed:
- backend/app/models/catalog.py
- backend/app/models/customer.py
- backend/app/schemas/catalog.py
- backend/app/schemas/customer.py
- backend/app/schemas/contract.py
- backend/app/services/catalog_service.py
- backend/app/services/customer_service.py
- backend/app/api/v1/endpoints/catalog.py
- backend/app/api/v1/endpoints/customer.py
- backend/app/db/session.py
- backend/tests/test_customer_catalog_contract.py
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- Agents.md
- tasks.md
- stack.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend\\.venv\\Scripts\\python -m ruff check .`: pass
  - `backend\\.venv\\Scripts\\python -m mypy app`: pass
  - `backend\\.venv\\Scripts\\python -m pytest -q`: pass (22 passed)
- Frontend:
  - `npm run lint`: pass
  - `npm run typecheck`: pass
  - `npm run test:run`: pass
  - `npm run build`: pass
- Runtime/Smoke:
  - `cmd /c launch_all.bat`: pass
  - Playwright UI smoke: pass (contract-first controls + offers family/tier form visible and functional).

Risks/Blockers:
- Live local backend process started by launcher may expose stale API shape in some sessions; automated backend test suite validates the updated API contracts directly.
- Client deletion guardrails currently enforce contract-history checks; invoice/payment-level guards will be finalized when billing/collections domains are implemented.

Next Steps:
- Continue Phase 4.2 by adding explicit same-family upgrade/downgrade policy validation.
- Continue Phase 4.3 with end-to-end tests for full new-client and existing-client contract provisioning journeys.

## [2026-02-17 12:15 UTC] Session Entry
Author: Codex Agent
Context:
- User requested an offers-tab refactor for staff workflow with strict service/component rules:
  - services restricted to Mobile / Internet / Landline
  - internet must include exactly one of fiber/adsl
  - hours must be integer-only
  - database baseline should be reset (fresh start).

Actions:
- Refactored catalog backend schema/model to service-component structure:
  - added `service_category` with component fields for mobile/internet/landline.
  - kept `service_type` as a derived compatibility field for contract/subscriber provisioning.
- Implemented strict backend validation rules in `OfferCreate`:
  - mobile requires data and/or calls component
  - internet requires `internet_access_type` and corresponding speed with fiber/adsl exclusivity
  - landline requires at least one component with integer hour fields.
- Refactored catalog service logic:
  - normalized create/update via shared validation path
  - grouped endpoint `GET /api/v1/offer-categories`
  - deprecated compatibility alias retained on `GET /api/v1/offer-families`
  - added guarded hard-delete (`DELETE /api/v1/offers/{offer_id}`) blocked by contract history.
- Updated runtime PostgreSQL bootstrap compatibility column checks for the new offer fields.
- Refactored frontend Offers tab:
  - replaced family/tier inputs with guided service/component builder
  - added create/update using same form (edit mode)
  - added delete action from offer list
  - kept contract tab integration by updating offer labels and service-type compatibility usage.
- Updated backend tests for new offer contract/validation/delete behavior.
- Reset local PostgreSQL `mt_facturation` database (drop + recreate) and reinitialized schema.
- Synchronized project governance docs (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Adopt service-component offer modeling for current operator workflow; family/tier tasks remain historical.
- Keep destructive delete guardrails even in fresh-start mode to avoid future data-integrity regressions.
- Keep deprecated `/offer-families` route temporarily for API compatibility while shifting to `/offer-categories`.

Files Changed:
- backend/app/models/catalog.py
- backend/app/schemas/catalog.py
- backend/app/schemas/customer.py
- backend/app/services/catalog_service.py
- backend/app/api/v1/endpoints/catalog.py
- backend/app/db/session.py
- backend/tests/test_customer_catalog_contract.py
- backend/tests/test_contract_service.py
- frontend/src/App.tsx
- frontend/src/App.css
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (23 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass
  - `npm run build` (workdir `frontend`): pass
- Database reset/bootstrap:
  - drop + recreate `mt_facturation`: pass
  - `backend/.venv/Scripts/python.exe -m app.db.bootstrap` (workdir `backend`): pass

Risks/Blockers:
- Existing family/tier assumptions are now superseded; any external integrations using those semantics must migrate to service-component payloads.
- FastAPI startup deprecation warning (`@app.on_event`) still pending lifespan migration.

Next Steps:
- Add targeted frontend E2E tests for the new Offers tab component rules.
- Add contract-flow tests for landline offers and mixed internet bundles (fiber/adsl + options).

## [2026-02-17 12:17 UTC] Session Entry
Author: Codex Agent
Context:
- User reported runtime backend log showing `POST /api/v1/offers` returning `422 Unprocessable Content`.

Actions:
- Diagnosed the behavior as expected backend validation rejection for invalid offer component payloads (for example mobile offer submitted without data/calls).
- Added frontend pre-submit validation in `frontend/src/App.tsx` to block invalid submissions before API call and show explicit, operator-friendly messages:
  - mobile requires at least one of data/calls
  - internet requires integer speed for selected access type
  - landline requires at least one component and integer-hour quotas
  - monthly fee must be positive.
- Kept backend strict validation unchanged (source of truth remains API).
- Updated planning/governance markdown synchronization files and refreshed timestamps.

Decisions:
- Preserve backend hard validation and complement it with frontend early validation rather than loosening API rules.
- Treat `422` as a useful guardrail; convert it into clearer in-form guidance to reduce operator friction.

Files Changed:
- frontend/src/App.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `npm run lint` (workdir `frontend`): pass
- `npm run typecheck` (workdir `frontend`): pass
- `npm run test:run` (workdir `frontend`): pass

Risks/Blockers:
- Direct API consumers (outside frontend) can still submit invalid payloads and receive `422`; this is intentional and correct.

Next Steps:
- Add inline helper text under each service component section in Offers tab to make required inputs explicit before submit.

## [2026-02-17 12:30 UTC] Session Entry
Author: Codex Agent
Context:
- User reported browser errors:
  - CORS blocked message on `GET /api/v1/offers`
  - HTTP `500` on `GET /api/v1/offers`
  - HTTP `422` on `POST /api/v1/offers`.

Actions:
- Reproduced runtime issue and confirmed backend returns `500` with `ProgrammingError` on `GET /api/v1/offers`.
- Verified this is not a frontend-only issue: direct API call also returns `500`.
- Verified local code quality/tests are green; issue is runtime process/data-state mismatch.
- Implemented backend robustness improvement by reordering middleware so CORS wraps auth/error paths:
  - moved CORS middleware to outermost position in `backend/app/main.py`.
- Re-ran backend quality gates after middleware change.
- Synchronized required Markdown governance files.

Decisions:
- Treat browser CORS message as secondary symptom when backend fails with `500`.
- Keep strict backend offer validation (`422`) and improve operator guidance from frontend side.
- Enforce CORS middleware ordering as a project baseline for easier browser debugging.

Files Changed:
- backend/app/main.py
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (23 passed)

Risks/Blockers:
- Active backend process in user environment may still be stale/out-of-sync with current code; restart is required to apply latest API contract (`/offer-categories`, delete offer route, new offer schema).

Next Steps:
- Restart backend/frontend from a clean state and verify OpenAPI exposes new catalog paths.
- If `500` persists after restart, capture backend traceback for the exact SQL error and patch immediately.

## [2026-02-17 13:10 UTC] Session Entry
Author: Codex Agent
Context:
- User reported persistent fetch failures after restart:
  - browser CORS errors
  - `GET /api/v1/offers` returning `500`
  - `POST /api/v1/offers` returning `422`.

Actions:
- Reproduced issue and confirmed primary failure was backend runtime mismatch (`500 ProgrammingError` on offers list), with CORS shown as secondary browser symptom.
- Isolated runtime inconsistency:
  - direct clean backend launch from codebase exposed new routes and returned `200` for offers
  - launcher/start script path was still landing on stale API shape (`/offer-categories` missing), causing schema/query mismatch.
- Applied runtime hardening fixes:
  - `backend/start-backend.bat`:
    - disabled reload mode by default (optional via `BACKEND_ENABLE_RELOAD=true`)
    - made backend port configurable with `BACKEND_PORT` env.
  - `launch_all.bat`:
    - added stale-port fallback: if `8000` remains busy, switch backend to `8010`
    - pass `BACKEND_PORT` to backend starter
    - pass `VITE_API_BASE_URL=http://localhost:%BACKEND_PORT%` to frontend startup
    - replaced fragile catalog smoke call with OpenAPI contract check for `/api/v1/offer-categories`
    - kept backend health/authenticated smoke checks.
  - `frontend/src/App.tsx`:
    - trimmed `VITE_API_BASE_URL` at runtime to avoid URL parse failures from accidental whitespace.
- Validated launcher end-to-end via captured run log:
  - fallback to `8010` triggered
  - backend health and customers checks passed
  - OpenAPI catalog path check passed
  - frontend root check passed
  - launch sequence completed.

Decisions:
- Treat stale local backend listeners/port conflicts as a platform reliability issue and solve in launcher logic, not only via manual process cleanup.
- Keep API contract smoke checks as mandatory startup guardrail to catch stale runtime shape early.

Files Changed:
- backend/start-backend.bat
- launch_all.bat
- frontend/src/App.tsx
- docs/decision-log.md
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (23 passed)
- Launcher/runtime:
  - `launch_all.bat` captured run: pass
  - smoke checks passed, with backend fallback port `8010` and OpenAPI path verification.

Risks/Blockers:
- Persistent hidden listeners on `8000` in local environment can still exist outside project control; launcher now mitigates by switching to `8010`.
- FastAPI startup deprecation warning (`@app.on_event`) remains pending lifespan migration.

Next Steps:
- Optional: add UI banner indicating active backend URL was launcher-injected (e.g., `8010`) to reduce operator confusion.
- Optional: add a one-click “Stop Local Runtime” utility script to force-stop backend/frontend processes before launch.

## [2026-02-17 13:40 UTC] Session Entry
Author: Codex Agent
Context:
- User reported persistent browser failed-to-fetch and CORS preflight failures after restart, with frontend origin switching to 5174 and requests still hitting 8000.

Actions:
- Reproduced the preflight failure:
  - OPTIONS http://127.0.0.1:8000/api/v1/customers with origin http://localhost:5174 returned 400 Disallowed CORS origin.
  - OPTIONS http://127.0.0.1:8010/api/v1/customers with origin http://localhost:5174 returned 200 with access-control-allow-origin.
- Fixed launcher reliability in `launch_all.bat` by replacing parse-time fragile `%errorlevel%` checks with runtime-safe `if errorlevel` checks inside grouped blocks.
- Hardened frontend backend selection in `frontend/src/App.tsx`:
  - probe now uses real operator headers (CORS preflight aware) on `/api/v1/health`
  - candidate validation now requires expected OpenAPI paths (`/api/v1/customers`, `/api/v1/offers`, `/api/v1/contracts`).
- Added `set "PYTHONHOME="` in `launch_all.bat` startup path for environment hygiene.
- Re-ran launcher smoke flow and validated backend/frontend checks succeed with aligned selected ports.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Keep runtime hardening centered on deterministic backend discovery and startup checks instead of relying on manual process cleanup.
- Keep OpenAPI path verification and CORS-aware probing as startup guardrails for local reliability.

Files Changed:
- launch_all.bat
- frontend/src/App.tsx
- frontend/.env.example
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
- Runtime/Smoke:
  - `cmd /c "launch_all.bat > launch_verify.log 2>&1"`: pass
  - preflight check on `8010` from origin `5174`: pass
  - preflight check on `8000` from origin `5174`: reproduces disallowed-origin trap (expected environment conflict).
  - Playwright browser verification (`http://127.0.0.1:5174`): pass, app resolved API base to `http://localhost:8010` and loaded customers/offers/contracts with HTTP 200.

Risks/Blockers:
- Port 8000 is occupied by a non-target local runtime in this environment and can still confuse manual flows that bypass launcher/env injection.
- Local Python warning `Could not find platform independent libraries <prefix>` still appears during some launcher Python invocations; currently non-blocking.

Next Steps:
- Add a dedicated `stop_local_runtime.bat` utility to force-stop known backend/frontend listeners before launch.
- Optionally surface selected API base URL more prominently in frontend status for operator diagnostics.

## [2026-02-17 14:05 UTC] Session Entry
Author: Codex Agent
Context:
- User requested minor offer-tab simplifications for staff operation:
  - remove visible version handling
  - make validation date optional/hidden unless enabled
  - reorder service before offer name
  - add `other fees` (activation fee)
  - gate landline international/phone hours behind explicit toggles.

Actions:
- Updated backend catalog model/schema/runtime bootstrap to support persisted `activation_fee`:
  - added `activation_fee` to `Offer` model
  - added `activation_fee` to `OfferCreate`, `OfferUpdate`, and `OfferRead`
  - included `activation_fee` in offer merge/update path
  - added PostgreSQL runtime compatibility DDL/DML for `activation_fee` (`ADD COLUMN`, backfill `0`, default, not-null).
- Updated frontend offers flow in `frontend/src/App.tsx`:
  - reordered fields to show `Service` before `Offer Name`
  - removed `Version` input and table column from operator UI (backend still uses internal version value)
  - added `Other Fees (Activation Fee)` input after monthly fee
  - added `Apply Validation Date` toggle and conditional `Validation Date` input
  - show `Undefined` in offers table when no validation date is set
  - changed landline international/phone quotas to explicit yes/no toggles with conditional input visibility
  - kept integer-hour validation and updated payload composition accordingly.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Keep backend versioning unchanged for compatibility/integrity while hiding version controls from staff UX.
- Treat activation fee as first-class persisted catalog data (not frontend-only transient field).

Files Changed:
- backend/app/models/catalog.py
- backend/app/schemas/catalog.py
- backend/app/services/catalog_service.py
- backend/app/db/session.py
- frontend/src/App.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (23 passed)

Risks/Blockers:
- Local Python warning `Could not find platform independent libraries <prefix>` still appears in this environment but is non-blocking for checks.

Next Steps:
- Optional: add a compact inline fee helper text in the UI clarifying `Other Fees` is one-time activation.
- Optional: include activation fee in contract/checkout pricing preview when that flow is expanded.

## [2026-02-17 14:25 UTC] Session Entry
Author: Codex Agent
Context:
- User requested implementation of a more futuristic and stable Offers-tab design after logic was validated.

Actions:
- Refactored `frontend/src/App.tsx` Offers UI into a two-column operations workspace:
  - left: structured offer editor
  - right: sticky live preview panel.
- Introduced reusable pill toggle control (`On`/`Off`) via `BinaryToggle` component for binary choices.
- Reworked service component editing to eliminate visual jump/popup behavior:
  - rows remain structurally stable
  - quota inputs are disabled/enabled instead of appearing/disappearing.
- Upgraded Internet section:
  - segmented access selector (`Fiber`/`ADSL`)
  - both speed rows visible; inactive type is disabled.
- Upgraded Landline section:
  - National toggle row
  - International toggle + disabled/enabled hours input in same row
  - Phone toggle + disabled/enabled hours input in same row.
- Upgraded validity UX:
  - validation-date input remains in layout and is disabled when toggle is off.
- Added real-time preview summary for:
  - service
  - components
  - monthly fee
  - activation fee
  - validation date/status.
- Added dedicated Offers styling in `frontend/src/App.css`:
  - futuristic card/gradient styling
  - segmented toggle visuals
  - stable component rows
  - responsive behavior (2-column desktop, single-column mobile).
- Synchronized required markdown files for this iteration.

Decisions:
- Keep existing backend/API payload behavior unchanged while upgrading UI interaction model and visual language.
- Prioritize layout stability over conditional field insertion/removal to improve perceived quality.

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.css
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass

Risks/Blockers:
- No functional blockers identified in this iteration.

Next Steps:
- Optional: add subtle staggered reveal animation for component rows on service switch.
- Optional: mirror live-preview style tokens in Contracts tab for visual consistency.

## [2026-02-17 16:05 UTC] Session Entry
Author: Codex Agent
Context:
- User requested one business-rule adjustment: Internet service must always include landline (always ON).

Actions:
- Enforced backend normalization in `OfferCreate`:
  - internet offers now always set `internet_landline_included = True` during validation.
- Added runtime PostgreSQL compatibility enforcement:
  - during schema bootstrap, existing internet offers are updated to set `internet_landline_included = TRUE`.
- Updated Offers UI behavior:
  - internet landline control is no longer user-togglable and now displays as mandatory (`Always On`).
  - payload builder for internet offers always sends `internet_landline_included: true`.
  - edit/service-switch flows now keep internet landline state locked to true.
  - offer summary/preview now reflects internet landline as mandatory on.
- Added regression coverage in backend tests:
  - create and update internet offer attempts with `internet_landline_included=false` are normalized to `true`.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Apply hard business-rule enforcement server-side (source of truth) and mirror it in UI as read-only mandatory state.
- Backfill existing local data at startup so legacy internet offers cannot remain in invalid state.

Files Changed:
- backend/app/schemas/catalog.py
- backend/app/db/session.py
- backend/tests/test_customer_catalog_contract.py
- frontend/src/App.tsx
- frontend/src/App.css
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (24 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass

Risks/Blockers:
- Local Python warning `Could not find platform independent libraries <prefix>` still appears in this environment but remains non-blocking.

Next Steps:
- Optional: surface a helper text in internet offer preview explicitly saying "Landline included by policy".

## [2026-02-17 16:32 UTC] Session Entry
Author: Codex Agent
Context:
- User requested turning the landing-flow recommendation into a standalone detailed plan phase in `tasks.md`, with strict API-call parity for all capabilities.

Actions:
- Added a new independent planning phase in `tasks.md`:
  - `Phase 4.5 - Client Landing Subscription Flow and Contract Intake Automation (Independent, API-First)`.
- Split the phase into detailed, execution-ready tasks across:
  - API contract design/versioning/idempotency
  - landing wizard entry + draft state
  - new-subscription flow
  - mobile/landline numbering rules (Moroccan format and random allocation)
  - upgrade/downgrade flow with eligible-offer filtering
  - orchestration integration with Contracts/Clients tabs
  - contract PDF generation and retrieval
  - security/audit requirements
  - mandatory testing matrix (unit/integration/API/E2E/regression).
- Added explicit exit criteria requiring both:
  - full UI journey completion
  - equivalent API-only execution for the same journeys.
- Reviewed governance Markdown files for synchronization; no additional policy text changes were required outside planning/log updates for this iteration.

Decisions:
- Treat landing flow as an independent phase under contract-domain evolution (`4.5`) to keep scope isolated and trackable.
- Enforce API-first parity as a non-negotiable acceptance gate for every landing workflow capability.

Files Changed:
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Documentation/planning update: no code tests required.

Risks/Blockers:
- Scope is broad; implementation should still be executed in slices (API contracts first, then orchestration, then UI/E2E) to reduce regression risk.

Next Steps:
- Begin implementation from Phase 4.5 task order, starting with API contracts and endpoint scaffolding.

## [2026-02-17 16:48 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to start implementation immediately for the new independent Phase 4.5 landing flow.

Actions:
- Implemented Phase 4.5 backend API slice for client landing orchestration:
  - added CIN support to client domain (`clients.cin`) with normalization and uniqueness guardrails
  - added landing persistence models:
    - `landing_drafts` (draft save/restore)
    - `idempotency_records` (submit replay/conflict protection)
  - added landing schemas and OpenAPI-backed endpoint contracts
  - added landing service layer with:
    - bootstrap listing
    - draft create/read/update
    - CIN lookup + active subscription/eligible-offer discovery
    - new subscription submit orchestration
    - plan-change submit orchestration
    - idempotency key hashing/replay/conflict handling
  - wired public landing endpoints under `/api/v1/landing/*`
  - updated runtime defaults and env example so landing endpoints are treated as public paths.
- Implemented Moroccan number handling in backend provisioning intake:
  - mobile identifiers: `+2126` + 9-digit local part
  - landline identifiers: `+2125` + 9-digit local part
  - random unique generation with collision retries against existing subscriber identifiers.
- Added backend test coverage in `backend/tests/test_landing_flow.py` for:
  - public bootstrap contract
  - new mobile subscription creating client/contract/subscriber from CIN flow
  - existing CIN + existing mobile identifier triggering upgrade path
  - CIN subscription lookup with eligible target offers
  - idempotency replay and payload conflict detection.
- Updated planning progress in `tasks.md` for completed Phase 4.5 backend/API items.
- Synchronized required project Markdown files for this iteration.

Decisions:
- Delivered Phase 4.5 as backend-first slice to keep contract/tab behavior stable while enabling API-first external landing integration.
- Kept manual contract flow intact while sharing orchestration logic through existing `provision_contract` decisioning.
- Deferred frontend wizard and PDF delivery to next slices to avoid bundling UI and domain refactors in one risk-heavy change set.

Files Changed:
- backend/app/models/customer.py
- backend/app/models/landing.py
- backend/app/schemas/customer.py
- backend/app/schemas/contract.py
- backend/app/schemas/landing.py
- backend/app/services/customer_service.py
- backend/app/services/landing_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/app/api/v1/router.py
- backend/app/db/session.py
- backend/app/core/settings.py
- backend/tests/conftest.py
- backend/tests/test_landing_flow.py
- backend/.env.example
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
- `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
- `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (29 passed)

Risks/Blockers:
- CIN column rollout currently uses runtime compatibility DDL while project remains on bootstrap strategy; formal Alembic migration still recommended for production hardening.
- Upgrade/downgrade client verification remains basic (CIN lookup only) and still needs stronger security controls (OTP/verified channel) before exposure beyond controlled environments.
- Contract PDF generation/download is not implemented in this slice yet.

Next Steps:
- Implement frontend landing wizard screens and wire them to new `/api/v1/landing/*` endpoints.
- Add backend API for contract PDF retrieval and hook landing confirmation download UX.
- Add missing orchestration tests for existing client + new service contract path.

## [2026-02-17 17:02 UTC] Session Entry
Author: Codex Agent
Context:
- Continued Phase 4.5 execution to implement the client-facing landing UI and finish the frontend/API integration slice.

Actions:
- Added dedicated client-facing landing page implementation at `frontend/src/LandingPage.tsx` with a guided process for:
  - new subscription flow (service selection, offer selection, personal information, validation preview, submit)
  - upgrade/downgrade flow (CIN lookup, current subscription selection, eligible target offer selection, validation preview, submit).
- Added dedicated landing styling in `frontend/src/LandingPage.css` with a responsive, non-default visual direction and mobile fallback.
- Updated app entry routing in `frontend/src/main.tsx`:
  - `/landing` renders client landing wizard
  - `/` keeps operator control center.
- Added frontend coverage for landing bootstrap + flow start behavior in `frontend/src/LandingPage.test.tsx`.
- Extended backend landing payload contract and orchestration to support deterministic displayed/generated numbers:
  - added `requested_mobile_local_number` for mobile assign-new path
  - added `home_landline_local_number` for internet/landline path
  - enforced identifier uniqueness for client-provided generated values before provisioning.
- Marked completed Phase 4.5 tasks in `tasks.md` for the implemented frontend + orchestration slice.
- Synchronized required project markdown files.

Decisions:
- Kept operator workspace and client landing flow separated by route (`/` vs `/landing`) to avoid operational UX regressions while enabling external-facing onboarding.
- Chose deterministic generated-number submission support so read-only numbers shown to the client can match final persisted service identifiers.
- Deferred contract PDF generation to a later Phase 4.5 slice; UI currently exposes placeholder text when `document_download_url` is absent.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- frontend/src/main.tsx
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.css
- frontend/src/LandingPage.test.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (29 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (2 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- Upgrade/downgrade verification still relies on CIN lookup without second-factor confirmation; must be hardened before public exposure.
- Contract PDF delivery endpoint is still pending and currently represented as a placeholder in landing success screens.

Next Steps:
- Implement contract PDF generation + download endpoint and connect landing success screens to real document URLs.
- Add targeted tests for existing client + new service contract creation path in landing orchestration.
- Add E2E tests for complete `/landing` journeys (new subscription and plan change).

## [2026-02-18 10:48 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a landing-flow correction:
  - mobile flow must ask phone criteria before personal form
  - manual phone entry must accept common Moroccan formats and normalize reliably (`+212...`, `06...`, `07...`, etc.).

Actions:
- Refactored frontend landing new-subscription journey in `frontend/src/LandingPage.tsx`:
  - introduced explicit mobile phone-criteria step before personal information form
  - flow order for mobile is now:
    - service/offer selection
    - phone criteria choice (existing vs new)
    - personal information form
    - validation preview
    - submit
  - if `new` number is chosen, phone field in form is read-only and auto-generated
  - if `existing` is chosen, phone field is manually editable.
- Implemented frontend normalization helper for Moroccan number parsing in the landing UX:
  - accepts user-friendly variants with spaces and local prefix `0`
  - validates service-type prefixes (mobile: `6`/`7`, landline: `5`/`8`).
- Updated backend landing contract normalization in `backend/app/services/landing_service.py`:
  - introduced canonical normalization to `+212` + 9-digit national number
  - mobile validation enforces first national digit `6` or `7`
  - landline validation enforces first national digit `5` or `8`
  - accepted incoming formats now include `+212...`, `0...`, and digit-only normalized variants
  - auto-generated identifiers now follow valid Moroccan prefixes for each service type.
- Relaxed landing schema field length constraints for manual phone inputs to support real-world formatted strings:
  - `existing_mobile_local_number`
  - `requested_mobile_local_number`
  - `home_landline_local_number`.
- Added backend regression test for invalid mobile prefix rejection (`05...` in mobile existing-number path).
- Updated landing frontend test to follow new step sequence (`offer -> phone criteria -> form`).
- Synchronized required markdown files.

Decisions:
- Treated phone-format normalization as backend source-of-truth to avoid UI-only validation drift and preserve API-first behavior for external callers.
- Kept API field names stable for compatibility while broadening accepted value formats through normalization.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.css
- frontend/src/LandingPage.test.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (30 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (2 passed)

Risks/Blockers:
- Phone normalization is now robust for common formats, but public exposure still needs stronger client verification controls for CIN-based operations.
- Contract PDF endpoint remains pending and still returns no download URL in success payload.

Next Steps:
- Implement contract PDF generation/download endpoint and surface real file links in landing success screens.
- Add additional tests for existing-client + new-service-number path and full landing E2E journeys.

## [2026-02-18 10:54 UTC] Session Entry
Author: Codex Agent
Context:
- User reported a blocking UX regression: in mobile existing-number mode, landing flow validated phone input at Phone Criteria step before the form where the number is entered.

Actions:
- Fixed frontend flow in `frontend/src/LandingPage.tsx`:
  - removed premature validation at Phone Criteria step
  - Phone Criteria now only captures mode decision and proceeds to Personal Info form
  - added explicit helper text that existing number is entered in the next step.
- Kept definitive mobile-number validation in the Personal Info submission path.
- Updated landing UI copy to reflect accepted Moroccan formats and expected behavior.
- Verified frontend quality gates after fix.
- Synchronized required markdown files for this interaction.

Decisions:
- Preserve the requested UX contract strictly:
  - choose existing/new first
  - enter existing number later in form (not in criteria step).

Files Changed:
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.css
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (2 passed)

Risks/Blockers:
- None new from this fix; existing tracked risks remain (PDF endpoint pending, CIN verification hardening pending).

Next Steps:
- Continue with contract PDF endpoint implementation and landing success download integration.

## [2026-02-18 11:01 UTC] Session Entry
Author: Codex Agent
Context:
- User reported that existing-mobile-number flow still fails at submit with validation error:
  `existing_mobile_local_number: String should have at most 9 characters`.

Actions:
- Fixed frontend submission payload in `frontend/src/LandingPage.tsx`:
  - when `mobile_number_mode = use_existing`, submit the normalized Moroccan 9-digit national part (`nsn`) instead of raw formatted input.
  - fallback to raw trimmed input only if normalization unexpectedly fails (guarded by existing UI validation).
- Re-ran frontend quality gates after patch.
- Synchronized required markdown files for this interaction.

Decisions:
- Applied compatibility-first fix on frontend payload shape to work against strict backend validators still enforcing 9-char limit.
- Kept user-friendly input formats in UI while sending canonical API-compatible value.

Files Changed:
- frontend/src/LandingPage.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (2 passed)

Risks/Blockers:
- If a stale backend process is still running old code, other legacy constraints may still surface until runtime is fully refreshed.

Next Steps:
- Refresh local runtime via `launch_all.bat` if stale process behavior persists.

## [2026-02-18 11:19 UTC] Session Entry
Author: Codex Agent
Context:
- User requested removal of separate `Contact Phone` from landing personal info and to rely on a single phone number for both new and existing number paths.

Actions:
- Updated `frontend/src/LandingPage.tsx`:
  - removed `Contact Phone` state and form input from Personal Information step
  - derived `contact_phone` payload directly from the service identifier phone logic:
    - mobile/new: generated `+212` mobile number
    - mobile/existing: normalized existing mobile canonical number
    - internet/landline: generated `+212` landline number
  - renamed non-mobile form label from `Landline` to `Phone Number` for consistency.
- Re-ran frontend quality gates after patch.
- Synchronized required markdown files for this interaction.

Decisions:
- Keep API field `contact_phone` for backward compatibility, but source it from the same single phone-number flow to eliminate duplicate/manual phone capture.

Files Changed:
- frontend/src/LandingPage.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (2 passed)

Risks/Blockers:
- None introduced by this patch.

Next Steps:
- Continue contract-tab refactor tasks and keep landing + internal contract flow API behavior aligned.

## [2026-02-18 11:54 UTC] Session Entry
Author: Codex Agent
Context:
- User requested execution of the full remaining Phase 4.5 scope (landing flow completion end-to-end, API parity, security hardening, documents, and tests).

Actions:
- Backend landing security and API hardening:
  - added `POST /api/v1/landing/clients/verify` to validate CIN ownership using registered email/phone and return a signed short-lived lookup token.
  - enforced lookup token on `GET /api/v1/landing/clients/{cin}/subscriptions`.
  - added signed short-lived tokenized contract document endpoint: `GET /api/v1/landing/contracts/{contract_id}/document?token=...`.
- Backend contract document implementation:
  - added `ContractDocument` ORM model with metadata persistence (`contract_documents` table) in `backend/app/models/contract.py`.
  - implemented PDF generation (server-side) and metadata persistence in landing service.
  - wired both landing submit paths (`submit/new` and `submit/plan-change`) to issue PDF and return live `document_download_url`.
- Backend audit and data protection:
  - added landing audit events:
    - `landing_service_identifier_allocated`
    - `contract_document_issued`
  - added masked logging for CIN/email/phone in landing verification/submit flows.
  - masked email/phone in lookup response payload to reduce sensitive exposure.
- Frontend landing updates:
  - upgrade/downgrade flow now requires verification value (email or phone) with CIN before listing subscriptions.
  - landing now consumes lookup token automatically for lookup API.
  - confirmation screens (new subscription + plan change) now use live download links against backend API base URL.
  - preserved previously fixed phone flow behavior and single phone field model.
- Tests extended to close remaining Phase 4.5 gaps:
  - backend tests added for:
    - existing client + new service contract path
    - verification-required lookup behavior
    - verification failure behavior
    - full API journey (verify -> lookup -> plan-change -> PDF download)
    - allocation collision retry strategy for generated mobile numbers
    - manual contract provisioning regression path
    - PDF generation/download and audit events coverage
  - frontend tests added for:
    - wizard step transitions baseline
    - generated-number field disabled/enabled behavior (new vs existing mobile)
    - upgrade verification step calling verify API before listing offers
- Documentation and policy:
  - added `docs/landing-api-compatibility-policy.md`.
  - updated `docs/decision-log.md` with landing security/document decisions.
  - marked Phase 4.5 checklist and exit criteria completed in `tasks.md`.
  - synchronized required markdown files.

Decisions:
- Kept landing routes public but introduced token-based verification and document access to avoid CIN-only enumeration/document exposure.
- Maintained API-first compatibility by extending endpoints/contracts instead of introducing UI-only logic.
- Kept `contact_phone` API field stable while deriving it from the single canonical identifier flow in frontend/backend behavior.

Files Changed:
- backend/app/models/contract.py
- backend/app/core/settings.py
- backend/.env.example
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.test.tsx
- docs/landing-api-compatibility-policy.md
- docs/decision-log.md
- tasks.md
- stack.md
- mustread.md
- Agents.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (36 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (4 passed)

Risks/Blockers:
- Token signing currently uses local env secret defaults if not overridden; production deployment must provide managed secrets.
- Current PDF generator is a lightweight internal renderer; future branding/legal formatting requirements may require dedicated PDF templating library.

Next Steps:
- Start Phase 5 (Billing Domain) implementation from `tasks.md` in chronological order.

## [2026-02-18 12:32 UTC] Session Entry
Author: Codex Agent
Context:
- User reported no PDF download button in landing success screen and requested a professionally designed contract PDF (not plain-text output).

Actions:
- Implemented robust download-link recovery for landing flows:
  - Added backend endpoint `POST /api/v1/landing/contracts/{contract_id}/document-link`.
  - Endpoint validates CIN + contact verification value and returns a fresh secure tokenized `document_download_url`.
  - Used this as fallback when submit responses contain `document_download_url = null`.
- Upgraded PDF generation to designed contract output:
  - Replaced plain PDF text writer with ReportLab-based document builder in `backend/app/services/landing_service.py`.
  - New contract PDF includes branded header, structured sections, tables (parties + service/fees), key terms, and signature blocks.
- Updated frontend landing done screens:
  - If URL exists: show `Download Contract PDF` link.
  - If URL missing: show `Generate PDF Link` button that calls the new backend recovery endpoint.
  - Applied to both new-subscription and plan-change confirmation screens.
- Added required schema/API support:
  - `LandingContractDocumentLinkRequest`
  - `LandingContractDocumentLinkResponse`
- Updated stack documentation endpoint list and synchronized mandatory markdown timestamps.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/requirements.txt
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- stack.md
- mustread.md
- Agents.md
- tasks.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt`: pass (installed `reportlab`)
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (36 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (4 passed)

Risks/Blockers:
- If backend runtime is stale (old process), landing may still return legacy `document_download_url: null` behavior until restart.

Next Steps:
- Restart local runtime to load new backend/frontend code paths and verify landing success screen now shows either direct download link or `Generate PDF Link` fallback.

## [2026-02-18 13:07 UTC] Session Entry
Author: Codex Agent
Context:
- User requested moving to the next chronological phase. Active target: Phase 5 Billing Domain completion.

Actions:
- Completed frontend invoice-center wiring in `frontend/src/App.tsx` under Contracts tab:
  - billing run form (`period_start`, `period_end`, `due_days`, `tax_rate`)
  - invoice list with selection and status display
  - invoice detail panel with line-level breakdown
  - authenticated PDF download action (`/api/v1/invoices/{invoice_id}/pdf`)
- Added responsive invoice-center styling in `frontend/src/App.css`.
- Expanded frontend test coverage in `frontend/src/App.test.tsx` to include:
  - backend discovery mock (`/api/v1/health`, `/openapi.json`)
  - invoice endpoint mocking
  - invoice-center presence assertions.
- Stabilized backend quality for billing additions:
  - formatted and lint-fixed `backend/app/models/billing.py`
  - fixed billing string assembly and Decimal aggregation typing in `backend/app/services/billing_service.py`
  - wrapped client-delete invoice guard line in `backend/app/services/customer_service.py`.
- Updated planning/docs state:
  - marked Phase 5 tasks + exit criteria complete in `tasks.md`
  - split client-delete guardrail progress into:
    - invoices complete
    - payments pending collections phase
  - added Phase 5 billing API baseline in `stack.md`.

Decisions:
- Kept invoice operations inside the Contracts tab to preserve the agreed three-tab UX while exposing full billing capabilities via APIs.
- Kept billing idempotency + PDF generation backend-first and made frontend a direct consumer of those APIs (no UI-only billing logic).

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/App.test.tsx
- backend/app/models/billing.py
- backend/app/services/billing_service.py
- backend/app/services/customer_service.py
- tasks.md
- stack.md
- mustread.md
- Agents.md
- journal.md

Tests:
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (4 passed)
  - `npm run build` (workdir `frontend`): pass
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (39 passed)

Risks/Blockers:
- Frontend test run still emits a React `act(...)` warning in `src/App.test.tsx` due async state updates after mount; tests pass but warning cleanup is still recommended.
- Launcher smoke check (`launch_all.bat`) was not rerun in this iteration.

Next Steps:
- Start Phase 6 (Payments and Collections Domain) implementation from `tasks.md` in chronological order.

## [2026-02-18 13:24 UTC] Session Entry
Author: Codex Agent
Context:
- User requested adding billing self-service into landing so clients can check billing and download invoices; business rule emphasized monthly telecom charging at beginning of month.

Actions:
- Extended landing backend API surface for billing self-service:
  - added `GET /api/v1/landing/clients/{cin}/invoices?lookup_token=...`
  - added `GET /api/v1/landing/invoices/{invoice_id}/document?token=...`
- Reused existing CIN verification + short-lived lookup token flow for secure invoice access.
- Added tokenized invoice-document access control in landing service:
  - invoice-specific signed token purpose (`landing_invoice_document`)
  - ownership checks (`invoice_id` + `cin`)
  - fallback PDF generation via billing service when metadata/file is missing.
- Extended landing schema contracts:
  - `check_billing_and_download_invoices` flow type
  - invoice lookup response models (`LandingInvoiceSummary`, `LandingInvoiceLookupResponse`).
- Implemented landing frontend billing journey in `frontend/src/LandingPage.tsx`:
  - new flow card: `Check Billing & Invoices`
  - verify step (`CIN` + `email/phone`)
  - invoice table with issued/due/amount/status and secure `Download Invoice PDF` links
  - explicit operator-facing note: invoices are issued at beginning of month.
- Added styling support for landing billing table and notes in `frontend/src/LandingPage.css`.
- Added/updated tests:
  - backend: CIN lookup invoices + PDF download token flow
  - frontend: billing flow verification and invoice-link rendering.
- Synchronized required markdown governance files.

Decisions:
- Kept billing self-service fully API-first and token-protected; no invoice data exposed from CIN alone.
- Used existing verification mechanism for consistency and reduced security surface.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.css
- frontend/src/LandingPage.test.tsx
- tasks.md
- stack.md
- Agents.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (40 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- Invoice timing policy (“beginning of month”) is currently communicated in UX; automated scheduler/cron orchestration for day-1 runs is still not part of this slice.

Next Steps:
- If required, implement automated monthly billing trigger (day-1 run orchestration) with audit + retry behavior.

## [2026-02-18 13:37 UTC] Session Entry
Author: Codex Agent
Context:
- User requested direct local data injection for demo/testing: one old contract with 3 historical monthly invoices so landing billing can be validated immediately.

Actions:
- Ran a one-off backend seed command (local DB) that:
  - creates/reuses a demo client by CIN
  - creates/reuses an internet fiber offer
  - creates/reuses a subscriber and active contract backdated to 2025-10-01
  - creates/reuses 3 invoices for periods:
    - 2025-11-01..2025-11-30
    - 2025-12-01..2025-12-31
    - 2026-01-01..2026-01-31
  - ensures invoice PDFs are generated and linked.
- Verified seed output and captured identifiers for immediate use in landing verification flow.
- Synchronized required markdown files for this interaction.

Decisions:
- Performed targeted invoice insertion for the single demo client instead of running global billing cycles, to avoid generating invoices for unrelated active contracts.

Files Changed:
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Data injection command output validation: pass (`SEED_OK`, `INVOICES_TOTAL=3`, `PDFS_ENSURED=3`).
- Full backend/frontend suites: not rerun in this interaction (no application code change).

Risks/Blockers:
- Seed data is local-environment specific and persists in current database until manually removed.

Next Steps:
- Use `/landing` -> `Check Billing & Invoices` with seeded CIN to validate invoice listing and PDF downloads end-to-end.

## [2026-02-18 14:06 UTC] Session Entry
Author: Codex Agent
Context:
- User requested moving to Phase 6 implementation.

Actions:
- Completed Phase 6 backend/frontend integration slice and quality hardening:
  - finalized collections backend domain wiring already in progress (`payments`, `collection_cases`, `collection_case_actions`) and cleaned lint/type issues.
  - confirmed router exposure for collections endpoints under `/api/v1/collections/*`.
  - kept deletion guardrails aligned by checking payments and collection cases in client delete flow.
- Implemented internal operator Collections Center in `frontend/src/App.tsx` under Contracts tab:
  - collections overview cards (open, in-progress, overdue, outstanding total)
  - aging bucket totals (`current`, `1_30`, `31_60`, `61_90`, `90_plus`)
  - filterable case table (status/aging/client), case selection, and status updates
  - payment posting form (invoice selection, amount/date/method/reference/note) with idempotency key
  - case action logging form (`reminder_sent`, `warning_sent`, `note`) and action history panel.
- Added collections dashboard styling in `frontend/src/App.css`.
- Updated frontend test coverage in `frontend/src/App.test.tsx` to mock collections endpoints and assert Collections Center rendering.
- Updated project planning/governance docs to reflect Phase 6 completion and collections baseline:
  - marked Phase 6 tasks + exit criteria complete in `tasks.md`
  - marked Phase 4.3 payment-delete guard extension complete in `tasks.md`
  - added Collections API baseline section in `stack.md`
  - updated baseline artifact wording in `Agents.md`
  - refreshed required markdown timestamps.

Decisions:
- Kept collections operations inside the Contracts tab to preserve the agreed 3-tab operator UX while exposing full API parity.
- Preserved idempotency-key semantics for payment recording and used API-first calls from frontend (no local-only payment logic).

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/App.test.tsx
- backend/app/models/customer.py
- backend/app/services/collections_service.py
- backend/app/services/customer_service.py
- backend/tests/test_collections_flow.py
- tasks.md
- stack.md
- Agents.md
- mustread.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (43 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- Frontend test suite still emits React `act(...)` warning for async mount updates in `src/App.test.tsx` (non-blocking, tests pass).
- Local Python runtime still emits `Could not find platform independent libraries <prefix>` warning while commands succeed.
- Launcher smoke check (`launch_all.bat`) was not rerun in this iteration.

Next Steps:
- Start Phase 7 (cross-service integration and E2E hardening) from `tasks.md`.

## [2026-02-18 14:30 UTC] Session Entry
Author: Codex Agent
Context:
- User requested UI separation of billing/collections from Contracts tab and requested invoice filtering by client, service, and offer.

Actions:
- Refactored operator workspace navigation in `frontend/src/App.tsx`:
  - added dedicated tabs: `Invoices` and `Collections`
  - kept `Contracts` focused on provisioning only.
- Moved invoice operations into a dedicated Invoice Center tab:
  - billing run form kept intact
  - added invoice filter form with:
    - client selector
    - service selector (`mobile` / `internet` / `landline`)
    - offer selector
  - wired filter apply/reset to invoice list loading.
- Moved collections operations into a dedicated Collections tab:
  - retained overview cards, aging buckets, filters, case table, payment posting, and action history.
- Implemented API-side invoice filters for parity with UI:
  - updated `GET /api/v1/invoices` to accept `service` and `offer_id` query params (in addition to `client_id`).
  - updated billing service query logic to filter invoices by offer/service through invoice-line -> contract -> offer joins.
- Added regression coverage:
  - backend test for invoice filtering by client/service/offer in `backend/tests/test_billing_flow.py`.
  - frontend tab/render test updates in `frontend/src/App.test.tsx`.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Enforced API-first requirement by implementing invoice filter behavior in backend endpoint logic, not only in frontend state filtering.
- Updated project UX baseline docs to reflect dedicated `Invoices` and `Collections` tabs.

Files Changed:
- frontend/src/App.tsx
- frontend/src/App.test.tsx
- backend/app/api/v1/endpoints/billing.py
- backend/app/services/billing_service.py
- backend/tests/test_billing_flow.py
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (44 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- Frontend tests still show a non-blocking React `act(...)` warning in `src/App.test.tsx`.
- Existing backend warnings remain:
  - FastAPI `on_event` deprecation
  - ReportLab Python 3.14 deprecation warning (`ast.NameConstant`).

Next Steps:
- Continue with Phase 7 integration and end-to-end flow hardening.

## [2026-02-19 16:33 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a way to approve a monthly bill as paid directly in the system.

Actions:
- Implemented API-first invoice payment approval flow:
  - added request schema `InvoicePaymentApprovalRequest` in `backend/app/schemas/collections.py`.
  - added service method `approve_invoice_paid` in `backend/app/services/collections_service.py`:
    - validates idempotency key
    - computes outstanding amount
    - records a full settlement payment (no direct invoice status override)
    - reuses existing payment allocation + invoice/case/delinquency sync logic
    - supports idempotency replay behavior.
  - added endpoint:
    - `POST /api/v1/collections/invoices/{invoice_id}/approve-paid`
    - requires `Idempotency-Key`.
- Added backend regression test in `backend/tests/test_collections_flow.py`:
  - validates approve-paid sets invoice to `paid`
  - validates outstanding amount becomes `0.00`
  - validates idempotency replay with same key.
- Updated frontend Invoice Center in `frontend/src/App.tsx`:
  - added `Approve Paid` row action for non-paid/non-void invoices
  - action calls new API endpoint
  - refreshes invoices + collections overview/cases and selected invoice detail.
- Synchronized required markdown files and updated stack/tasks references for this capability.

Decisions:
- Chose payment-led settlement (recorded payment) instead of direct invoice status mutation to preserve auditability and financial integrity.

Files Changed:
- backend/app/schemas/collections.py
- backend/app/services/collections_service.py
- backend/app/api/v1/endpoints/collections.py
- backend/tests/test_collections_flow.py
- frontend/src/App.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (45 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- Frontend test suite still has a non-blocking React `act(...)` warning in `src/App.test.tsx`.
- Backend still emits existing deprecation warnings (FastAPI `on_event`, ReportLab `ast.NameConstant`).

Next Steps:
- If needed, add a mandatory operator note/reference policy when approving payments for compliance traceability.

## [2026-02-19 17:28 UTC] Session Entry
Author: Codex Agent
Context:
- User requested reverting landing upgrade/downgrade verification to CIN-only.

Actions:
- Implemented CIN-only verification path for landing plan-change lookup:
  - added schema `LandingCinLookupRequest`.
  - added backend service function `verify_lookup_identity_by_cin`.
  - added endpoint `POST /api/v1/landing/clients/verify-cin`.
- Updated landing frontend upgrade/downgrade flow (`frontend/src/LandingPage.tsx`):
  - removed email/phone input from plan-change verify step.
  - verify action now posts CIN to `/api/v1/landing/clients/verify-cin`.
  - updated UI copy/button labels to CIN-only wording.
- Kept billing lookup flow unchanged (still CIN + contact verification via `/landing/clients/verify`).
- Updated contract document-link recovery to support CIN-only request body:
  - `verification_value` is now optional in `LandingContractDocumentLinkRequest`.
  - backend document-link issuance accepts CIN-only when `verification_value` is omitted.
- Added/updated tests:
  - backend test for CIN-only verify token issuance.
  - updated plan-change API journey test to use CIN-only verify endpoint.
  - updated landing frontend test for CIN-only upgrade verification flow.
- Synchronized required markdown docs and updated baseline notes.

Decisions:
- Applied CIN-only lookup strictly to plan-change path to match product request.
- Preserved stronger contact verification for billing self-service to limit unnecessary security regression on financial data access.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.test.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (46 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- CIN-only plan-change lookup lowers identity assurance versus contact-based verification.
- Existing non-blocking warnings remain:
  - React `act(...)` warning in `src/App.test.tsx`
  - FastAPI `on_event` deprecation
  - ReportLab Python deprecation (`ast.NameConstant`).

Next Steps:
- If requested, add a configurable policy flag to toggle CIN-only vs contact-verified lookup by environment.

## [2026-02-19 17:41 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to make everything CIN-only for now (landing verification across plan-change and billing flows).

Actions:
- Finalized CIN-only behavior across landing frontend and backend:
  - removed remaining `verification_value` usage from landing frontend document-link fallback flow.
  - kept plan-change and billing verification both on `POST /api/v1/landing/clients/verify-cin`.
  - removed contact-verification helper logic from `landing_service.py` (no longer used).
- Tightened API request contracts to CIN-only:
  - `LandingLookupVerificationRequest` now CIN-only.
  - `LandingContractDocumentLinkRequest` now CIN-only.
- Updated backend landing tests:
  - switched lookup helper to CIN-only endpoint.
  - updated document-link recovery test payload to CIN-only.
  - replaced old wrong-contact rejection test with legacy `/verify` CIN-only compatibility test.
- Updated frontend landing tests:
  - removed `/landing/clients/verify` mock path.
  - added assertions that upgrade and billing flows do not call `/landing/clients/verify`.
- Synchronized required markdown docs to reflect CIN-only temporary policy.

Decisions:
- Applied CIN-only verification consistently across all landing self-service flows to match current product direction.
- Kept `/api/v1/landing/clients/verify` as a backward-compatible alias but with CIN-only behavior.

Files Changed:
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/tests/test_landing_flow.py
- frontend/src/LandingPage.tsx
- frontend/src/LandingPage.test.tsx
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (46 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- CIN-only verification lowers identity assurance for client self-service until a stronger verification policy is reintroduced.
- Existing non-blocking warnings remain:
  - React `act(...)` warning in `src/App.test.tsx`
  - FastAPI `on_event` deprecation
  - ReportLab Python deprecation (`ast.NameConstant`).

Next Steps:
- If requested, introduce an environment-level verification policy toggle (`cin_only` vs `cin_plus_contact`) without changing frontend UX again.

## [2026-02-19 18:15 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to fix the important remaining process-flow issues while keeping CIN-only behavior and prepare to move to remaining phases.

Actions:
- Fixed plan-change effective-date handling in provisioning:
  - upgrade path now applies selected `contract_start_date` to the upgraded contract `start_date`.
  - added defensive date validation for upgrade using effective `start_date` + resulting `end_date` + resulting `commitment_months` to prevent invalid contract timelines.
  - enriched upgrade audit payload with `from_start_date` and `to_start_date`.
- Removed legacy landing verification endpoint and kept a single CIN verification API:
  - removed `POST /api/v1/landing/clients/verify`.
  - kept canonical `POST /api/v1/landing/clients/verify-cin`.
  - removed unused schema/service compatibility code for legacy verify payload handling.
- Added configuration hardening for token security:
  - `landing_token_secret` default is now allowed only in `local`/`test`; non-local envs must override it.
- Updated tests:
  - plan-change journey test now verifies upgraded contract `start_date` matches selected effective date.
  - legacy verify endpoint test now asserts endpoint removal (`404`).
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Enforced a single CIN verification endpoint to reduce ambiguity and keep API behavior explicit.
- Prioritized effective-date correctness in upgrade flow as a blocking business integrity fix before entering remaining phases.

Files Changed:
- backend/app/services/contract_service.py
- backend/app/api/v1/endpoints/landing.py
- backend/app/schemas/landing.py
- backend/app/services/landing_service.py
- backend/app/core/settings.py
- backend/tests/test_landing_flow.py
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Backend:
  - `backend/.venv/Scripts/python.exe -m ruff check backend`: pass
  - `backend/.venv/Scripts/python.exe -m mypy backend/app backend/tests`: pass
  - `backend/.venv/Scripts/python.exe -m pytest -q backend/tests`: pass (46 passed)
- Frontend:
  - `npm run lint` (workdir `frontend`): pass
  - `npm run typecheck` (workdir `frontend`): pass
  - `npm run test:run` (workdir `frontend`): pass (5 passed)
  - `npm run build` (workdir `frontend`): pass

Risks/Blockers:
- CIN-only verification remains lower-assurance identity verification for self-service flows; acceptable only under current controlled product stage.
- Existing non-blocking warnings remain:
  - React `act(...)` warning in `src/App.test.tsx`
  - FastAPI `on_event` deprecation
  - ReportLab Python deprecation (`ast.NameConstant`).

Next Steps:
- Proceed with Phase 7 integration/E2E scope with current CIN-only baseline and upgraded effective-date correctness in place.

## [2026-02-19 21:36 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a dedicated Markdown file documenting all available API calls with detailed explanations.

Actions:
- Created `docs/api-reference.md` containing a complete API catalog for `/api/v1`.
- Documented every current endpoint by method and path, grouped by domain:
  - health/auth/conventions
  - customer/subscriber
  - catalog
  - contract
  - landing (public self-service flow)
  - billing
  - collections
- For each endpoint, documented:
  - purpose/what it does
  - auth requirement
  - required inputs (headers/path/query/body)
  - response type/shape
  - key business rules and side effects (idempotency, guardrails, tokenized document access, audit implications).
- Added documentation-governance references to include the new API reference artifact:
  - `Agents.md` baseline docs list now includes `docs/api-reference.md`.
  - `stack.md` repository layout now references API reference documentation.
  - `tasks.md` recurring documentation checklist now includes API reference synchronization.
- Updated required markdown file timestamps for this iteration.

Decisions:
- API reference is maintained as a human-readable operational guide separate from OpenAPI output to help product/ops/backend/frontend alignment.
- Kept endpoint explanations aligned to actual backend behavior (including current CIN-only landing policy).

Files Changed:
- docs/api-reference.md
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Not run (documentation-only update; no executable code changes).

Risks/Blockers:
- API documentation must be kept in sync with future endpoint/schema changes to avoid drift from implementation.

Next Steps:
- If needed, add request/response JSON examples per endpoint in `docs/api-reference.md` for faster external integration onboarding.

## [2026-02-19 21:44 UTC] Session Entry
Author: Codex Agent
Context:
- User requested converting the API reference markdown into table format in PDF.

Actions:
- Added a reusable PDF generator script:
  - `docs/generate_api_reference_pdf.py`
  - parses endpoint sections from `docs/api-reference.md`
  - builds a multi-page table PDF with columns:
    - Method
    - Endpoint
    - Auth
    - Purpose
    - Inputs
    - Response / Rules
- Generated final PDF artifact:
  - `docs/api-reference-table.pdf`
  - contains 51 API endpoint rows.
- Updated stack baseline doc layout to include the new API PDF artifact.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Kept the generator script in-repo to allow regeneration whenever API docs change.
- Used ReportLab table rendering for stable pagination and printable output.

Files Changed:
- docs/generate_api_reference_pdf.py
- docs/api-reference-table.pdf
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Generation command:
  - `backend/.venv/Scripts/python.exe docs/generate_api_reference_pdf.py`: pass
  - output confirmed at `docs/api-reference-table.pdf`.

Risks/Blockers:
- PDF content quality depends on keeping `docs/api-reference.md` headings and bullet structure stable.

Next Steps:
- If requested, add automatic regeneration (e.g., pre-commit or CI check) when `docs/api-reference.md` changes.

## [2026-02-20 09:57 UTC] Session Entry
Author: Codex Agent
Context:
- User requested process-oriented API guidance (clear call sequences by business flow), without unnecessary standalone subscriber API usage.

Actions:
- Added new process map markdown:
  - `docs/api-process-map.md`
  - includes step-by-step API sequences for:
    - creating contract to downloading contract PDF
    - updating contract to downloading contract PDF
    - creating offer
    - updating offer
    - upgrading client offer to downloading contract PDF
    - downgrading client contract to downloading contract PDF
- Avoided dedicated subscriber endpoint calls in the process guidance; used provisioning and landing flow APIs instead.
- Added PDF generator for process guide:
  - `docs/generate_api_process_map_pdf.py`
- Generated shareable process PDF artifact:
  - `docs/api-process-map.pdf`
- Synchronized required markdown governance files and docs inventory references.

Decisions:
- Kept process map separate from endpoint catalog to support teammate onboarding by workflow rather than raw route list.
- Kept the guidance CIN-first and aligned with current landing policy.

Files Changed:
- docs/api-process-map.md
- docs/generate_api_process_map_pdf.py
- docs/api-process-map.pdf
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe docs/generate_api_process_map_pdf.py`: pass
- output file created and verified: `docs/api-process-map.pdf`.

Risks/Blockers:
- Process guide must be updated if endpoint contracts change to avoid drift.

Next Steps:
- If requested, add per-step request/response examples with real IDs and a ready Postman collection grouped by these six processes.

## [2026-02-20 10:09 UTC] Session Entry
Author: Codex Agent
Context:
- User requested a complete chronological process map (not only six example processes) to share with teammate.

Actions:
- Expanded `docs/api-process-map.md` from a limited example set into a full platform chronology:
  - P0 Environment and access checks
  - P1 Catalog foundation
  - P2 Offer maintenance
  - P3 Client master data lifecycle
  - P4 Internal contract provisioning
  - P5 Manual contract creation path
  - P6 Contract lifecycle management
  - P7 Landing bootstrap and draft management
  - P8 Landing new subscription flow to contract PDF
  - P9 Landing upgrade/downgrade flow to contract PDF
  - P10 Internal contract document retrieval
  - P11 Monthly billing run
  - P12 Internal invoice operations
  - P13 Client self-service billing and invoice download
  - P14 Payment and settlement process
  - P15 Collections lifecycle and dunning operations
- Kept the guidance aligned with current product rules:
  - CIN-only landing verification
  - no standalone subscriber API usage in normal workflows.
- Regenerated shareable PDF from the expanded process map:
  - `docs/api-process-map.pdf` using `docs/generate_api_process_map_pdf.py`.
- Synchronized required markdown files (`mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`).

Decisions:
- Process map now prioritizes real operational sequence and handover clarity over endpoint taxonomy.
- Kept `contracts/provision` and landing plan-change as the primary operational paths.

Files Changed:
- docs/api-process-map.md
- docs/api-process-map.pdf
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `backend/.venv/Scripts/python.exe docs/generate_api_process_map_pdf.py`: pass

Risks/Blockers:
- Process map and PDF must be regenerated whenever major endpoint behavior changes to avoid teammate integration drift.

Next Steps:
- If requested, add per-process cURL and Postman-ready request examples for immediate integration execution.
## [2026-02-20 10:36 UTC] Session Entry
Author: Codex Agent
Context:
- User reported oversized action buttons in the operator `Invoices` and `Collections` views.

Actions:
- Updated button sizing behavior in `frontend/src/App.css` for `.billing-run-form` controls:
  - set grid alignment to bottom (`align-items: end`) to avoid stretched button height,
  - made form action buttons compact (`justify-self: start`, `width: auto`, `min-width: 160px`, reduced padding),
  - kept mobile usability by restoring full-width buttons under `@media (max-width: 760px)`.

Decisions:
- Kept changes CSS-only and scoped to `.billing-run-form` so other tabs/components are unaffected.

Files Changed:
- frontend/src/App.css
- journal.md

Tests:
- `npm run lint` (frontend): pass
- `npm run typecheck` (frontend): pass
- `npm run test:run` (frontend): pass
- `npm run build` (frontend): pass

Risks/Blockers:
- Existing React test warning about `act(...)` remains in `src/App.test.tsx`; no functional regression introduced by this UI sizing change.

Next Steps:
- If desired, I can fine-tune compactness further (e.g., 150px min-width or pill-style secondary actions) after visual review.
## [2026-02-20 10:44 UTC] Session Entry
Author: Codex Agent
Context:
- User requested Linux migration support by creating a root launcher script (`launch_all.sh`).

Actions:
- Added `launch_all.sh` at repository root with Linux-compatible one-shot orchestration:
  - tooling checks (`python3`/`python`, `node`, `npm`, `curl`),
  - stale-process cleanup (PID files, uvicorn runtime matches, port listeners),
  - backend bootstrap (`.venv` creation, pip upgrade, dependency install, `pip check`, DB bootstrap via `python -m app.db.bootstrap`),
  - frontend bootstrap (`npm ci`/`npm install`, `npm ls --depth=0`),
  - backend/frontend startup in background with persisted PID files and logs,
  - smoke checks for backend health, authenticated API read, OpenAPI path presence, and frontend root.
- Added runtime behavior parity with Windows launcher:
  - backend port fallback (`8000` -> `8010`) if still busy,
  - frontend port fallback (`5173` -> `5174`) if still busy,
  - frontend API base injection (`VITE_API_BASE_URL=http://localhost:<backend-port>`).
- Synchronized project markdown governance files:
  - updated `mustread.md`, `Agents.md`, `tasks.md`, and `stack.md` to include Linux launcher parity references.

Decisions:
- Implemented Linux launcher as direct shell orchestration in one file (no extra wrapper scripts) to keep migration friction low.
- Kept smoke-check contract equivalent to existing Windows launcher expectations.

Files Changed:
- launch_all.sh
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `bash -n launch_all.sh`: pass (syntax validation)

Risks/Blockers:
- Runtime execution validation was not performed in this Windows environment; full end-to-end launcher verification must be run on the target Linux desktop.

Next Steps:
- On Linux desktop: run `chmod +x launch_all.sh && ./launch_all.sh` and validate emitted URLs/log paths.
## [2026-02-20 10:53 UTC] Session Entry
Author: Codex Agent
Context:
- User requested moving the full project to GitHub.

Actions:
- Checked tooling and auth state:
  - `git` is available
  - `gh` (GitHub CLI) is not installed in this environment
  - no existing `.git` repository was present in project root.
- Initialized repository locally at project root:
  - `git init -b main`
  - configured local author name for commit metadata
  - staged full workspace and created initial snapshot commit.
- Verified repo status:
  - latest commit: `6ad5f82` (`Initial project snapshot`)
  - working tree clean
  - no remote configured yet.
- Synchronized governance markdown timestamps and phase tracking notes for this iteration.

Decisions:
- Completed all non-credentialed migration steps locally first.
- Deferred GitHub remote creation/push because account-level authentication and destination repo URL are not available in current shell.

Files Changed:
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- `git status --short`: pass (clean after commit)
- `git log --oneline -n 1`: pass (`6ad5f82 Initial project snapshot`)

Risks/Blockers:
- Cannot push to GitHub until destination repository URL exists and authentication is provided (PAT/credential manager/SSH).

Next Steps:
- Set remote URL and push `main` once user provides target GitHub repo path or creates an empty repo.
## [2026-02-20 11:01 UTC] Session Entry
Author: Codex Agent
Context:
- User reported GitHub MCP was added and requested continuation of GitHub migration.

Actions:
- Validated MCP state:
  - `list_mcp_resources` and `list_mcp_resource_templates` returned empty (GitHub MCP not active in current session tool surface).
- Inspected local Codex config and validated GitHub token usability for API read:
  - authenticated user confirmed as `yasiji`
  - repository read/list operations succeeded.
- Attempted automated GitHub repo creation for `MT-Facturation` via REST API:
  - `POST /user/repos` returned `403 Resource not accessible by personal access token`.
- Verified local git repository remains ready for push:
  - branch: `main`
  - commits present (`6ad5f82`, `07178b7`)
  - working tree clean before this documentation sync.
- Updated project docs to track blocker and required next action.

Decisions:
- Keep local repository fully prepared; defer push until token scope allows repository creation or an empty remote repository is created manually.

Files Changed:
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- GitHub API auth check (`GET /user`): pass
- GitHub repo existence check (`GET /repos/yasiji/MT-Facturation`): pass (404 not found)
- GitHub repo creation (`POST /user/repos`): blocked (`403` token scope)

Risks/Blockers:
- Current token cannot create repositories.
- Current Codex config uses `bearer_token_env_var` with what appears to be a raw token value; recommended to rotate token and store it in a real environment variable name.

Next Steps:
- Either (1) grant token permission to create repos, or (2) create empty `yasiji/MT-Facturation` repository manually, then run remote add + push.
## [2026-02-20 11:06 UTC] Session Entry
Author: Codex Agent
Context:
- User requested to fix GitHub MCP configuration and make it work.

Actions:
- Repaired Codex config at `C:\Users\yassi\.codex\config.toml`:
  - replaced invalid raw-token literal in `bearer_token_env_var` with proper variable binding:
    - `bearer_token_env_var = "GITHUB_TOKEN"`
- Migrated existing token value into user environment variable storage:
  - set user env var `GITHUB_TOKEN` (non-empty, length validated).
- Verified post-fix state:
  - config reflects environment variable binding
  - user env var present.
- Checked live MCP availability in current session:
  - `list_mcp_resources` / templates still do not expose `github`
  - explicit query returns `unknown MCP server 'github'`.

Decisions:
- Config + secret binding is now correct on disk and user profile.
- Remaining step is process reload: Codex session must restart to load updated MCP server registrations.

Files Changed:
- C:\Users\yassi\.codex\config.toml
- mustread.md
- Agents.md
- tasks.md
- stack.md
- journal.md

Tests:
- Config verification: pass (`bearer_token_env_var = "GITHUB_TOKEN"`)
- User env verification: pass (`GITHUB_TOKEN` present)
- MCP discovery in live session: blocked until restart (`unknown MCP server 'github'`).

Risks/Blockers:
- Current Codex runtime does not hot-reload MCP server config.

Next Steps:
- Restart Codex/IDE session, then re-run MCP discovery and GitHub push workflow.
