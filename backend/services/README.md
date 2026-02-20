# Backend Services Layout

This folder defines domain boundaries for the microservice architecture.

## Service Folders
- `api-gateway`: external entrypoint and request routing layer.
- `customer-service`: client and subscriber domain.
- `catalog-service`: offer and offer-version domain.
- `contract-service`: contract lifecycle domain.
- `billing-service`: invoice generation and billing workflows.
- `collections-service`: payment allocation and overdue management.
- `auth-service`: identity and authorization services.

Current implementation bootstrap lives under `backend/app` and will be split into these folders in Phase 2 and Phase 3.
