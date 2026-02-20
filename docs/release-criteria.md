# Release Criteria And Acceptance Metrics

## Release Gate
A release candidate is accepted only if all criteria below pass:
- Critical flows pass end-to-end tests.
- No blocker or critical open defects.
- API contracts published and versioned.
- Observability dashboards and alerts active.
- Rollback strategy documented and validated.

## Measurable Acceptance Metrics
- Unit test pass rate: `100%` on required suites.
- Integration/API contract pass rate: `100%` on required suites.
- End-to-end critical journey pass rate: `100%`.
- Build success rate on main branch: `>= 95%` rolling 14-day window.
- P95 API latency target for core read endpoints: `< 300 ms` (non-load-test baseline).
- Failed billing run tolerance: `0` for release sign-off.

## Critical Journeys (Mandatory)
- Client + Subscriber + Contract activation.
- Billing run + invoice issue + invoice download.
- Payment posting + invoice settlement + overdue transition.

## Non-Functional Checks
- Security scan in CI with no high/critical unresolved findings.
- Structured logs include trace/correlation identifiers.
- DB backup and restore rehearsal documented.
