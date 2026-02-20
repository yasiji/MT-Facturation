from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.common.api import PaginationParams, build_paginated_response, pagination_params
from app.common.auth import get_auth_context
from app.db.session import get_db
from app.schemas.contract import (
    ContractAuditEventRead,
    ContractCreate,
    ContractOfferUpdate,
    ContractProvisionRequest,
    ContractProvisionResult,
    ContractRead,
    ContractStatusUpdate,
)
from app.services.contract_service import (
    create_contract,
    get_contract,
    list_contract_audit_events,
    list_contracts,
    provision_contract,
    update_contract_offer,
    update_contract_status,
)

router = APIRouter(tags=["contract"])


@router.post("/contracts/provision", response_model=ContractProvisionResult)
def provision_contract_endpoint(
    payload: ContractProvisionRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> ContractProvisionResult:
    auth_context = get_auth_context(request)
    contract, created_client, created_subscriber, provisioning_mode = provision_contract(
        db,
        payload,
        actor_id=auth_context.actor_id,
    )
    return ContractProvisionResult(
        contract=ContractRead.model_validate(contract),
        created_client=created_client,
        created_subscriber=created_subscriber,
        provisioning_mode=provisioning_mode,
    )


@router.post("/contracts", response_model=ContractRead)
def create_contract_endpoint(
    payload: ContractCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> ContractRead:
    auth_context = get_auth_context(request)
    return ContractRead.model_validate(create_contract(db, payload, actor_id=auth_context.actor_id))


@router.get("/contracts")
def list_contracts_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    records, total = list_contracts(db, page=params.page, size=params.size)
    data = [ContractRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/contracts/{contract_id}", response_model=ContractRead)
def get_contract_endpoint(
    contract_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> ContractRead:
    return ContractRead.model_validate(get_contract(db, contract_id))


@router.put("/contracts/{contract_id}/status", response_model=ContractRead)
def update_contract_status_endpoint(
    contract_id: str,
    payload: ContractStatusUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> ContractRead:
    auth_context = get_auth_context(request)
    return ContractRead.model_validate(
        update_contract_status(db, contract_id, payload, actor_id=auth_context.actor_id),
    )


@router.put("/contracts/{contract_id}/offer", response_model=ContractRead)
def update_contract_offer_endpoint(
    contract_id: str,
    payload: ContractOfferUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> ContractRead:
    auth_context = get_auth_context(request)
    return ContractRead.model_validate(
        update_contract_offer(db, contract_id, payload, actor_id=auth_context.actor_id),
    )


@router.get("/contracts/{contract_id}/audit", response_model=list[ContractAuditEventRead])
def list_contract_audit_events_endpoint(
    contract_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> list[ContractAuditEventRead]:
    records = list_contract_audit_events(db, contract_id)
    return [ContractAuditEventRead.model_validate(record) for record in records]
