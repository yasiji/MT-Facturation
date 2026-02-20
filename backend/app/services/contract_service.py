import json
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.models.catalog import Offer
from app.models.contract import Contract, ContractAuditEvent
from app.models.customer import Client, Subscriber
from app.schemas.contract import (
    ContractCreate,
    ContractOfferUpdate,
    ContractProvisionRequest,
    ContractStatusUpdate,
    ProvisionClientInput,
    ProvisioningMode,
    ProvisionSubscriberInput,
)

OPEN_CONTRACT_STATUSES = {"draft", "active", "suspended"}
UPGRADE_CONTRACT_STATUSES = {"active"}
STATUS_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"active", "terminated"},
    "active": {"suspended", "terminated"},
    "suspended": {"active", "terminated"},
    "terminated": set(),
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _add_months(start_date: date, months: int) -> date:
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    # Clamp end-of-month safely for month length changes.
    is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    month_starts = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = min(start_date.day, month_starts[month - 1])
    return date(year, month, day)


def _validate_contract_dates(
    start_date: date,
    end_date: date | None,
    commitment_months: int | None,
) -> None:
    if end_date and end_date < start_date:
        raise ApiException(
            status_code=422,
            code="contract_date_invalid",
            message="end_date cannot be earlier than start_date",
        )
    if commitment_months and end_date:
        min_end_date = _add_months(start_date, commitment_months)
        if end_date < min_end_date:
            raise ApiException(
                status_code=422,
                code="contract_commitment_invalid",
                message="end_date does not satisfy commitment period",
                details={"minimum_end_date": min_end_date.isoformat()},
            )


def _get_client(db: Session, client_id: str) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise ApiException(status_code=404, code="client_not_found", message="Client was not found")
    return client


def _get_subscriber(db: Session, subscriber_id: str) -> Subscriber:
    subscriber = db.get(Subscriber, subscriber_id)
    if subscriber is None:
        raise ApiException(
            status_code=404,
            code="subscriber_not_found",
            message="Subscriber was not found",
        )
    return subscriber


def _get_offer(db: Session, offer_id: str) -> Offer:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise ApiException(status_code=404, code="offer_not_found", message="Offer was not found")
    return offer


def _ensure_offer_valid_for_contract(offer: Offer, contract_start_date: date) -> None:
    if offer.status != "active":
        raise ApiException(
            status_code=409,
            code="offer_not_active",
            message="Offer is not active and cannot be provisioned",
        )
    if offer.valid_from > contract_start_date:
        raise ApiException(
            status_code=422,
            code="offer_validity_invalid",
            message="Offer is not valid on contract_start_date",
        )
    if offer.valid_to and offer.valid_to < contract_start_date:
        raise ApiException(
            status_code=422,
            code="offer_validity_invalid",
            message="Offer is not valid on contract_start_date",
        )


def _record_audit_event(
    db: Session,
    contract_id: str,
    event_type: str,
    actor_id: str | None,
    details: dict[str, object] | None = None,
) -> None:
    event = ContractAuditEvent(
        contract_id=contract_id,
        event_type=event_type,
        actor_id=actor_id,
        details=json.dumps(details or {}, sort_keys=True),
    )
    db.add(event)


def _assert_subscriber_offer_compatibility(subscriber: Subscriber, offer: Offer) -> None:
    if subscriber.service_type != offer.service_type:
        raise ApiException(
            status_code=422,
            code="subscriber_offer_mismatch",
            message="Subscriber service_type is incompatible with selected offer",
            details={
                "subscriber_service_type": subscriber.service_type,
                "offer_service_type": offer.service_type,
            },
        )


def _assert_subscriber_available(db: Session, subscriber_id: str) -> None:
    existing_open_contract = db.scalar(
        select(Contract).where(
            Contract.subscriber_id == subscriber_id,
            Contract.status.in_(OPEN_CONTRACT_STATUSES),
        ),
    )
    if existing_open_contract:
        raise ApiException(
            status_code=409,
            code="subscriber_contract_conflict",
            message="Subscriber already has an active/suspended/draft contract",
            details={"contract_id": existing_open_contract.id},
        )


def _build_auto_identifier(service_type: str) -> str:
    return f"AUTO-{service_type.upper()}-{uuid.uuid4().hex[:10]}"


def _create_client_from_payload(db: Session, payload: ProvisionClientInput) -> Client:
    client = Client(**payload.model_dump())
    db.add(client)
    db.flush()
    return client


def _resolve_subscriber_for_provisioning(
    db: Session,
    client: Client,
    offer: Offer,
    payload: ContractProvisionRequest,
    *,
    allow_reuse: bool,
) -> tuple[Subscriber, bool]:
    if payload.subscriber_id:
        if not allow_reuse:
            raise ApiException(
                status_code=422,
                code="provisioning_intent_conflict",
                message="Subscriber reuse is not allowed for new-contract provisioning",
            )
        subscriber = _get_subscriber(db, payload.subscriber_id)
        if subscriber.client_id != client.id:
            raise ApiException(
                status_code=422,
                code="subscriber_client_mismatch",
                message="Subscriber does not belong to the selected client",
            )
        _assert_subscriber_offer_compatibility(subscriber, offer)
        return subscriber, False

    subscriber_payload: ProvisionSubscriberInput | None = payload.subscriber
    preferred_identifier = subscriber_payload.service_identifier if subscriber_payload else None

    if preferred_identifier:
        existing = db.scalar(
            select(Subscriber).where(Subscriber.service_identifier == preferred_identifier),
        )
        if existing:
            if not allow_reuse:
                raise ApiException(
                    status_code=409,
                    code="subscriber_identifier_conflict",
                    message="Subscriber service identifier already exists",
                )
            if existing.client_id != client.id:
                raise ApiException(
                    status_code=409,
                    code="subscriber_identifier_conflict",
                    message="Subscriber service identifier already exists for another client",
                )
            _assert_subscriber_offer_compatibility(existing, offer)
            return existing, False

    service_type = offer.service_type
    if (
        subscriber_payload
        and subscriber_payload.service_type
        and subscriber_payload.service_type != offer.service_type
    ):
        raise ApiException(
            status_code=422,
            code="subscriber_offer_mismatch",
            message="Subscriber service_type is incompatible with selected offer",
            details={
                "subscriber_service_type": subscriber_payload.service_type,
                "offer_service_type": offer.service_type,
            },
        )

    subscriber = Subscriber(
        client_id=client.id,
        service_type=service_type,
        service_identifier=preferred_identifier or _build_auto_identifier(service_type),
        status="active" if payload.auto_activate else "suspended",
    )
    db.add(subscriber)
    db.flush()
    return subscriber, True


def _list_upgrade_candidate_contracts(
    db: Session,
    client_id: str,
    service_type: str,
) -> list[Contract]:
    return list(
        db.scalars(
            select(Contract)
            .join(Subscriber, Contract.subscriber_id == Subscriber.id)
            .where(
                Contract.client_id == client_id,
                Contract.status.in_(UPGRADE_CONTRACT_STATUSES),
                Subscriber.service_type == service_type,
            )
            .order_by(Contract.created_at.asc()),
        ).all(),
    )


def _resolve_upgrade_target_contract(
    db: Session,
    client_id: str,
    service_type: str,
    target_contract_id: str | None,
) -> Contract:
    candidates = _list_upgrade_candidate_contracts(db, client_id, service_type)
    if not candidates:
        raise ApiException(
            status_code=409,
            code="contract_upgrade_target_missing",
            message="No active contract available for upgrade on this service",
        )

    if target_contract_id:
        for candidate in candidates:
            if candidate.id == target_contract_id:
                return candidate
        raise ApiException(
            status_code=422,
            code="contract_upgrade_target_invalid",
            message="target_contract_id is not a valid upgrade candidate",
            details={"candidate_contract_ids": [candidate.id for candidate in candidates]},
        )

    if len(candidates) > 1:
        raise ApiException(
            status_code=409,
            code="contract_upgrade_disambiguation_required",
            message="Multiple active contracts match upgrade criteria; select target_contract_id",
            details={"candidate_contract_ids": [candidate.id for candidate in candidates]},
        )

    return candidates[0]


def _resolve_provisioning_mode(
    db: Session,
    payload: ContractProvisionRequest,
    client: Client,
    offer: Offer,
) -> tuple[ProvisioningMode, Contract | None]:
    if payload.provisioning_intent == "new_line":
        return "new_contract", None

    if payload.provisioning_intent == "upgrade":
        target_contract = _resolve_upgrade_target_contract(
            db,
            client.id,
            offer.service_type,
            payload.target_contract_id,
        )
        return "upgrade_existing_contract", target_contract

    candidates = _list_upgrade_candidate_contracts(db, client.id, offer.service_type)
    if not candidates:
        return "new_contract", None

    if payload.target_contract_id:
        target_contract = _resolve_upgrade_target_contract(
            db,
            client.id,
            offer.service_type,
            payload.target_contract_id,
        )
        return "upgrade_existing_contract", target_contract

    if payload.subscriber_id:
        for candidate in candidates:
            if candidate.subscriber_id == payload.subscriber_id:
                return "upgrade_existing_contract", candidate
        return "new_contract", None

    if payload.subscriber and payload.subscriber.service_identifier:
        existing_subscriber = db.scalar(
            select(Subscriber).where(
                Subscriber.service_identifier == payload.subscriber.service_identifier,
                Subscriber.client_id == client.id,
            ),
        )
        if existing_subscriber:
            _assert_subscriber_offer_compatibility(existing_subscriber, offer)
            for candidate in candidates:
                if candidate.subscriber_id == existing_subscriber.id:
                    return "upgrade_existing_contract", candidate
            return "new_contract", None
        return "new_contract", None

    if len(candidates) == 1:
        return "upgrade_existing_contract", candidates[0]

    raise ApiException(
        status_code=409,
        code="contract_upgrade_disambiguation_required",
        message="Multiple active contracts match upgrade criteria; select target_contract_id",
        details={"candidate_contract_ids": [candidate.id for candidate in candidates]},
    )


def list_contracts(db: Session, page: int, size: int) -> tuple[list[Contract], int]:
    total = db.scalar(select(func.count()).select_from(Contract)) or 0
    records = db.scalars(
        select(Contract)
        .order_by(Contract.created_at.desc())
        .offset((page - 1) * size)
        .limit(size),
    ).all()
    return list(records), int(total)


def get_contract(db: Session, contract_id: str) -> Contract:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise ApiException(
            status_code=404,
            code="contract_not_found",
            message="Contract was not found",
        )
    return contract


def list_contract_audit_events(db: Session, contract_id: str) -> list[ContractAuditEvent]:
    get_contract(db, contract_id)
    return list(
        db.scalars(
            select(ContractAuditEvent)
            .where(ContractAuditEvent.contract_id == contract_id)
            .order_by(ContractAuditEvent.created_at.asc()),
        ).all(),
    )


def create_contract(db: Session, payload: ContractCreate, actor_id: str | None = None) -> Contract:
    client = _get_client(db, payload.client_id)
    subscriber = _get_subscriber(db, payload.subscriber_id)
    offer = _get_offer(db, payload.offer_id)

    if subscriber.client_id != client.id:
        raise ApiException(
            status_code=422,
            code="subscriber_client_mismatch",
            message="Subscriber does not belong to the selected client",
        )
    _assert_subscriber_offer_compatibility(subscriber, offer)
    _assert_subscriber_available(db, subscriber.id)
    _validate_contract_dates(
        payload.contract_start_date,
        payload.end_date,
        payload.commitment_months,
    )

    contract = Contract(
        client_id=client.id,
        subscriber_id=subscriber.id,
        offer_id=offer.id,
        status=payload.status,
        start_date=payload.contract_start_date,
        end_date=payload.end_date,
        commitment_months=payload.commitment_months,
        activated_at=_utc_now() if payload.status == "active" else None,
        terminated_at=_utc_now() if payload.status == "terminated" else None,
    )
    db.add(contract)
    db.flush()
    _record_audit_event(
        db,
        contract.id,
        "contract_created",
        actor_id,
        {"status": contract.status, "offer_id": offer.id},
    )
    db.commit()
    db.refresh(contract)
    return contract


def provision_contract(
    db: Session,
    payload: ContractProvisionRequest,
    actor_id: str | None = None,
) -> tuple[Contract, bool, bool, ProvisioningMode]:
    _validate_contract_dates(
        payload.contract_start_date,
        payload.end_date,
        payload.commitment_months,
    )

    offer = _get_offer(db, payload.offer_id)
    _ensure_offer_valid_for_contract(offer, payload.contract_start_date)

    created_client = False
    if payload.client_id:
        client = _get_client(db, payload.client_id)
    else:
        if payload.client is None:
            raise ApiException(
                status_code=422,
                code="client_input_missing",
                message="Client payload is required",
            )
        client = _create_client_from_payload(db, payload.client)
        created_client = True

    provisioning_mode, target_contract = _resolve_provisioning_mode(db, payload, client, offer)

    if provisioning_mode == "upgrade_existing_contract":
        if target_contract is None:
            raise ApiException(
                status_code=500,
                code="contract_upgrade_target_missing_internal",
                message="Upgrade mode requires a target contract",
            )
        subscriber = _get_subscriber(db, target_contract.subscriber_id)
        _assert_subscriber_offer_compatibility(subscriber, offer)

        previous_offer_id = target_contract.offer_id
        previous_start_date = target_contract.start_date
        effective_end_date = (
            payload.end_date
            if payload.end_date is not None
            else target_contract.end_date
        )
        effective_commitment_months = (
            payload.commitment_months
            if payload.commitment_months is not None
            else target_contract.commitment_months
        )
        _validate_contract_dates(
            payload.contract_start_date,
            effective_end_date,
            effective_commitment_months,
        )

        target_contract.offer_id = offer.id
        target_contract.start_date = payload.contract_start_date
        if payload.commitment_months is not None:
            target_contract.commitment_months = payload.commitment_months
        if payload.end_date is not None:
            target_contract.end_date = payload.end_date
        db.add(target_contract)
        _record_audit_event(
            db,
            target_contract.id,
            "contract_offer_changed",
            actor_id,
            {
                "from_offer_id": previous_offer_id,
                "to_offer_id": offer.id,
                "from_start_date": previous_start_date.isoformat(),
                "to_start_date": target_contract.start_date.isoformat(),
                "source": "provision_upgrade",
            },
        )
        db.commit()
        db.refresh(target_contract)
        return target_contract, False, False, "upgrade_existing_contract"

    subscriber, created_subscriber = _resolve_subscriber_for_provisioning(
        db,
        client,
        offer,
        payload,
        allow_reuse=False,
    )
    _assert_subscriber_available(db, subscriber.id)

    contract = Contract(
        client_id=client.id,
        subscriber_id=subscriber.id,
        offer_id=offer.id,
        status="active" if payload.auto_activate else "draft",
        start_date=payload.contract_start_date,
        end_date=payload.end_date,
        commitment_months=payload.commitment_months,
        activated_at=_utc_now() if payload.auto_activate else None,
    )
    db.add(contract)
    db.flush()
    _record_audit_event(
        db,
        contract.id,
        "contract_provisioned",
        actor_id,
        {
            "offer_id": offer.id,
            "auto_activate": payload.auto_activate,
            "created_client": created_client,
            "created_subscriber": created_subscriber,
            "provisioning_intent": payload.provisioning_intent,
        },
    )
    db.commit()
    db.refresh(contract)
    return contract, created_client, created_subscriber, "new_contract"


def update_contract_status(
    db: Session,
    contract_id: str,
    payload: ContractStatusUpdate,
    actor_id: str | None = None,
) -> Contract:
    contract = get_contract(db, contract_id)
    from_status = contract.status
    to_status = payload.status
    if from_status == to_status:
        return contract

    allowed = STATUS_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise ApiException(
            status_code=409,
            code="contract_status_transition_invalid",
            message="Invalid contract status transition",
            details={"from": from_status, "to": to_status},
        )

    contract.status = to_status
    now = _utc_now()
    if to_status == "active":
        contract.activated_at = contract.activated_at or now
    if to_status == "terminated":
        contract.terminated_at = now
        contract.end_date = contract.end_date or now.date()

    db.add(contract)
    _record_audit_event(
        db,
        contract.id,
        "contract_status_changed",
        actor_id,
        {"from": from_status, "to": to_status},
    )
    db.commit()
    db.refresh(contract)
    return contract


def update_contract_offer(
    db: Session,
    contract_id: str,
    payload: ContractOfferUpdate,
    actor_id: str | None = None,
) -> Contract:
    contract = get_contract(db, contract_id)
    offer = _get_offer(db, payload.offer_id)
    subscriber = _get_subscriber(db, contract.subscriber_id)
    _assert_subscriber_offer_compatibility(subscriber, offer)

    previous_offer_id = contract.offer_id
    contract.offer_id = offer.id
    db.add(contract)
    _record_audit_event(
        db,
        contract.id,
        "contract_offer_changed",
        actor_id,
        {"from_offer_id": previous_offer_id, "to_offer_id": offer.id},
    )
    db.commit()
    db.refresh(contract)
    return contract
