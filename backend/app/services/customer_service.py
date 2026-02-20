from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.models.billing import Invoice
from app.models.collections import CollectionCase, Payment
from app.models.contract import Contract
from app.models.customer import Client, Subscriber
from app.schemas.customer import ClientCreate, ClientUpdate, SubscriberCreate, SubscriberUpdate


def _get_client_by_cin(db: Session, cin: str) -> Client | None:
    return db.scalar(select(Client).where(Client.cin == cin))


def get_client_by_cin(db: Session, cin: str) -> Client | None:
    return _get_client_by_cin(db, cin)


def create_client(db: Session, payload: ClientCreate) -> Client:
    if payload.cin:
        existing = _get_client_by_cin(db, payload.cin)
        if existing is not None:
            raise ApiException(
                status_code=409,
                code="client_cin_conflict",
                message="Client CIN already exists",
                details={"client_id": existing.id},
            )
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session, page: int, size: int) -> tuple[list[Client], int]:
    total = db.scalar(select(func.count()).select_from(Client)) or 0
    records = db.scalars(
        select(Client)
        .order_by(Client.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return list(records), int(total)


def get_client(db: Session, client_id: str) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise ApiException(
            status_code=404,
            code="client_not_found",
            message="Client was not found",
        )
    return client


def update_client(db: Session, client_id: str, payload: ClientUpdate) -> Client:
    client = get_client(db, client_id)
    if payload.cin:
        existing = _get_client_by_cin(db, payload.cin)
        if existing is not None and existing.id != client_id:
            raise ApiException(
                status_code=409,
                code="client_cin_conflict",
                message="Client CIN already exists",
                details={"client_id": existing.id},
            )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: str) -> None:
    client = get_client(db, client_id)
    has_contracts = (
        db.scalar(select(Contract.id).where(Contract.client_id == client_id).limit(1)) is not None
    )
    has_invoices = (
        db.scalar(select(Invoice.id).where(Invoice.client_id == client_id).limit(1)) is not None
    )
    has_payments = (
        db.scalar(select(Payment.id).where(Payment.client_id == client_id).limit(1)) is not None
    )
    has_collection_cases = (
        db.scalar(select(CollectionCase.id).where(CollectionCase.client_id == client_id).limit(1))
        is not None
    )
    if has_contracts or has_invoices or has_payments or has_collection_cases:
        raise ApiException(
            status_code=409,
            code="client_delete_blocked",
            message=(
                "Client cannot be deleted because contract, invoice, payment, or collection "
                "history exists"
            ),
        )

    db.delete(client)
    db.commit()


def create_subscriber(db: Session, client_id: str, payload: SubscriberCreate) -> Subscriber:
    get_client(db, client_id)

    existing = db.scalar(
        select(Subscriber).where(Subscriber.service_identifier == payload.service_identifier),
    )
    if existing:
        raise ApiException(
            status_code=409,
            code="subscriber_identifier_conflict",
            message="Subscriber service identifier already exists",
        )

    subscriber = Subscriber(client_id=client_id, **payload.model_dump())
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


def list_subscribers_by_client(
    db: Session,
    client_id: str,
    page: int,
    size: int,
) -> tuple[list[Subscriber], int]:
    get_client(db, client_id)
    total = db.scalar(
        select(func.count()).select_from(Subscriber).where(Subscriber.client_id == client_id),
    ) or 0
    records = db.scalars(
        select(Subscriber)
        .where(Subscriber.client_id == client_id)
        .order_by(Subscriber.created_at.desc())
        .offset((page - 1) * size)
        .limit(size),
    ).all()
    return list(records), int(total)


def get_subscriber(db: Session, subscriber_id: str) -> Subscriber:
    subscriber = db.get(Subscriber, subscriber_id)
    if subscriber is None:
        raise ApiException(
            status_code=404,
            code="subscriber_not_found",
            message="Subscriber was not found",
        )
    return subscriber


def update_subscriber(db: Session, subscriber_id: str, payload: SubscriberUpdate) -> Subscriber:
    subscriber = get_subscriber(db, subscriber_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subscriber, field, value)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber
