# DB Migration Standards

## Naming Convention
Use the SQLAlchemy naming convention from `app/db/base.py` for deterministic constraint names.

## Rules
- Every schema change must be represented by an Alembic revision.
- Revisions must be ordered and reviewed.
- Apply migrations through Alembic only, never manual ad-hoc SQL in production pipelines.
- `upgrade` and `downgrade` functions must be explicit and testable.

## Workflow
1. Update SQLAlchemy models/metadata.
2. Generate revision draft with `--autogenerate`.
3. Review and adjust generated script.
4. Run migration on local dev database.
5. Run integration tests against migrated schema.

