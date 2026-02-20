from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.api import PaginationParams, build_paginated_response, pagination_params
from app.db.session import get_db
from app.schemas.customer import (
    ClientCreate,
    ClientRead,
    ClientUpdate,
    SubscriberCreate,
    SubscriberRead,
    SubscriberUpdate,
)
from app.services.customer_service import (
    create_client,
    create_subscriber,
    delete_client,
    get_client,
    get_subscriber,
    list_clients,
    list_subscribers_by_client,
    update_client,
    update_subscriber,
)

router = APIRouter(tags=["customer"])


@router.post("/customers", response_model=ClientRead)
def create_client_endpoint(
    payload: ClientCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ClientRead:
    return ClientRead.model_validate(create_client(db, payload))


@router.get("/customers")
def list_clients_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    records, total = list_clients(db, page=params.page, size=params.size)
    data = [ClientRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/customers/{client_id}", response_model=ClientRead)
def get_client_endpoint(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> ClientRead:
    return ClientRead.model_validate(get_client(db, client_id))


@router.put("/customers/{client_id}", response_model=ClientRead)
def update_client_endpoint(
    client_id: str,
    payload: ClientUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> ClientRead:
    return ClientRead.model_validate(update_client(db, client_id, payload))


@router.delete("/customers/{client_id}", status_code=204)
def delete_client_endpoint(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    delete_client(db, client_id)


@router.post("/customers/{client_id}/subscribers", response_model=SubscriberRead)
def create_subscriber_endpoint(
    client_id: str,
    payload: SubscriberCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SubscriberRead:
    return SubscriberRead.model_validate(create_subscriber(db, client_id, payload))


@router.get("/customers/{client_id}/subscribers")
def list_subscribers_endpoint(
    client_id: str,
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    records, total = list_subscribers_by_client(
        db,
        client_id=client_id,
        page=params.page,
        size=params.size,
    )
    data = [SubscriberRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/subscribers/{subscriber_id}", response_model=SubscriberRead)
def get_subscriber_endpoint(
    subscriber_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> SubscriberRead:
    return SubscriberRead.model_validate(get_subscriber(db, subscriber_id))


@router.put("/subscribers/{subscriber_id}", response_model=SubscriberRead)
def update_subscriber_endpoint(
    subscriber_id: str,
    payload: SubscriberUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> SubscriberRead:
    return SubscriberRead.model_validate(update_subscriber(db, subscriber_id, payload))
