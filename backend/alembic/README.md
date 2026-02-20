# Alembic Baseline

## Purpose
Centralized migration strategy for backend services with naming conventions and explicit revision history.

## Commands
- Create revision:
  - `alembic -c alembic.ini revision -m "describe change"`
- Create autogeneration draft:
  - `alembic -c alembic.ini revision --autogenerate -m "describe change"`
- Apply migrations:
  - `alembic -c alembic.ini upgrade head`
- Rollback one step:
  - `alembic -c alembic.ini downgrade -1`

## Standards
- One logical schema change per revision.
- Review autogeneration output before applying.
- Include downgrade path for reversible changes.
- Do not edit applied revisions in place.

