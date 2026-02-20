from fastapi import APIRouter

from app.api.v1.endpoints.authz import router as authz_router
from app.api.v1.endpoints.billing import router as billing_router
from app.api.v1.endpoints.catalog import router as catalog_router
from app.api.v1.endpoints.collections import router as collections_router
from app.api.v1.endpoints.contract import router as contract_router
from app.api.v1.endpoints.conventions import router as conventions_router
from app.api.v1.endpoints.customer import router as customer_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.landing import router as landing_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(authz_router)
router.include_router(conventions_router)
router.include_router(customer_router)
router.include_router(catalog_router)
router.include_router(contract_router)
router.include_router(landing_router)
router.include_router(billing_router)
router.include_router(collections_router)
