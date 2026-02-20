from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.common.api import PaginationParams, build_paginated_response, pagination_params
from app.common.auth import get_auth_context
from app.db.session import get_db
from app.schemas.collections import (
    CollectionCaseActionCreate,
    CollectionCaseActionRead,
    CollectionCaseRead,
    CollectionCaseStatusUpdate,
    CollectionOverviewRead,
    InvoicePaymentApprovalRequest,
    PaymentAllocationResult,
    PaymentCreate,
    PaymentRead,
)
from app.services.collections_service import (
    approve_invoice_paid,
    build_collections_overview,
    create_collection_case_action,
    list_collection_case_actions,
    list_collection_cases,
    list_payments,
    record_payment,
    update_collection_case_status,
)

router = APIRouter(tags=["collections"])


@router.post("/collections/payments", response_model=PaymentAllocationResult)
def record_payment_endpoint(
    payload: PaymentCreate,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentAllocationResult:
    auth_context = get_auth_context(request)
    return record_payment(
        db,
        payload=payload,
        idempotency_key=idempotency_key,
        actor_id=auth_context.actor_id,
    )


@router.post(
    "/collections/invoices/{invoice_id}/approve-paid",
    response_model=PaymentAllocationResult,
)
def approve_invoice_paid_endpoint(
    invoice_id: str,
    payload: InvoicePaymentApprovalRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentAllocationResult:
    auth_context = get_auth_context(request)
    return approve_invoice_paid(
        db,
        invoice_id=invoice_id,
        payload=payload,
        idempotency_key=idempotency_key,
        actor_id=auth_context.actor_id,
    )


@router.get("/collections/payments")
def list_payments_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
    invoice_id: Annotated[str | None, Query()] = None,
    client_id: Annotated[str | None, Query()] = None,
) -> dict[str, object]:
    records, total = list_payments(
        db,
        page=params.page,
        size=params.size,
        invoice_id=invoice_id,
        client_id=client_id,
    )
    data = [PaymentRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/collections/cases")
def list_collection_cases_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
    status: Annotated[str | None, Query()] = None,
    aging_bucket: Annotated[str | None, Query()] = None,
    client_id: Annotated[str | None, Query()] = None,
) -> dict[str, object]:
    records, total = list_collection_cases(
        db,
        page=params.page,
        size=params.size,
        status=status,
        aging_bucket=aging_bucket,
        client_id=client_id,
    )
    data = [CollectionCaseRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/collections/cases/{case_id}/actions", response_model=list[CollectionCaseActionRead])
def list_collection_case_actions_endpoint(
    case_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> list[CollectionCaseActionRead]:
    records = list_collection_case_actions(db, case_id=case_id)
    return [CollectionCaseActionRead.model_validate(record) for record in records]


@router.put("/collections/cases/{case_id}/status", response_model=CollectionCaseRead)
def update_collection_case_status_endpoint(
    case_id: str,
    payload: CollectionCaseStatusUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> CollectionCaseRead:
    auth_context = get_auth_context(request)
    record = update_collection_case_status(
        db,
        case_id=case_id,
        payload=payload,
        actor_id=auth_context.actor_id,
    )
    return CollectionCaseRead.model_validate(record)


@router.post("/collections/cases/{case_id}/actions", response_model=CollectionCaseActionRead)
def create_collection_case_action_endpoint(
    case_id: str,
    payload: CollectionCaseActionCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> CollectionCaseActionRead:
    auth_context = get_auth_context(request)
    record = create_collection_case_action(
        db,
        case_id=case_id,
        payload=payload,
        actor_id=auth_context.actor_id,
    )
    return CollectionCaseActionRead.model_validate(record)


@router.get("/collections/overview", response_model=CollectionOverviewRead)
def collections_overview_endpoint(
    db: Annotated[Session, Depends(get_db)],
) -> CollectionOverviewRead:
    return build_collections_overview(db)
