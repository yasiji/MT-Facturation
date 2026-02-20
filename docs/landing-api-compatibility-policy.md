# Landing API Compatibility and Versioning Policy

## Scope
This policy covers public landing endpoints under `/api/v1/landing` used by web clients and external partners.

## Versioning Rules
- All landing endpoints are versioned through the `/api/v1` prefix.
- Additive changes (new optional fields, new endpoints) are allowed in `v1`.
- Breaking changes (required field changes, field removals, semantic response changes) require a new API version.

## Backward Compatibility Rules
- Existing request fields must remain accepted for the full `v1` lifecycle.
- Existing response fields must remain present unless a new version is introduced.
- Idempotency behavior for submit endpoints must remain stable:
  - same key + same payload => replay previous response
  - same key + different payload => conflict error

## Deprecation Process
- Deprecations are announced in release notes and `docs/decision-log.md`.
- Deprecated fields/endpoints remain functional for at least one release cycle before removal in a new version.
- Deprecated behavior should emit warning metadata when feasible.

## Security and Token Compatibility
- Lookup verification and document-download tokens are signed and short-lived.
- Token format is opaque to clients and may change without notice as long as endpoint contracts remain stable.

## Error Envelope Stability
- All landing APIs must return the standard error envelope:
  - `error.code`
  - `error.message`
  - `error.details`
  - `error.trace_id`

## Partner Guidance
- Integrators must treat unknown response fields as forward-compatible.
- Integrators must avoid strict ordering assumptions for list payloads unless explicitly documented.
