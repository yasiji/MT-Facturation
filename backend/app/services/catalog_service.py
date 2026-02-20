from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.models.catalog import Offer
from app.models.contract import Contract
from app.schemas.catalog import (
    OfferCategoryRead,
    OfferCreate,
    OfferRead,
    OfferServiceCategory,
    OfferUpdate,
)


def _base_offer_payload(offer: Offer) -> dict[str, Any]:
    return {
        "name": offer.name,
        "service_category": offer.service_category,
        "version": offer.version,
        "monthly_fee": offer.monthly_fee,
        "activation_fee": offer.activation_fee,
        "status": offer.status,
        "valid_from": offer.valid_from,
        "valid_to": offer.valid_to,
        "mobile_data_gb": offer.mobile_data_gb,
        "mobile_calls_hours": offer.mobile_calls_hours,
        "internet_access_type": offer.internet_access_type,
        "internet_fiber_speed_mbps": offer.internet_fiber_speed_mbps,
        "internet_adsl_speed_mbps": offer.internet_adsl_speed_mbps,
        "internet_landline_included": offer.internet_landline_included,
        "internet_tv_included": offer.internet_tv_included,
        "landline_national_included": offer.landline_national_included,
        "landline_international_hours": offer.landline_international_hours,
        "landline_phone_hours": offer.landline_phone_hours,
    }


def _ensure_unique_offer_identity(
    db: Session,
    *,
    name: str,
    service_category: str,
    version: int,
    excluding_offer_id: str | None = None,
) -> None:
    query = select(Offer).where(
        Offer.name == name,
        Offer.service_category == service_category,
        Offer.version == version,
    )
    if excluding_offer_id:
        query = query.where(Offer.id != excluding_offer_id)
    existing = db.scalar(query)
    if existing:
        raise ApiException(
            status_code=409,
            code="offer_version_conflict",
            message=(
                "Offer name, service category, and version combination already exists"
            ),
        )


def create_offer(db: Session, payload: OfferCreate) -> Offer:
    payload_data = payload.model_dump()
    _ensure_unique_offer_identity(
        db,
        name=str(payload_data["name"]),
        service_category=str(payload_data["service_category"]),
        version=int(payload_data["version"]),
    )

    offer = Offer(**payload_data)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


def list_offers(db: Session, page: int, size: int) -> tuple[list[Offer], int]:
    total = db.scalar(select(func.count()).select_from(Offer)) or 0
    records = db.scalars(
        select(Offer)
        .order_by(Offer.created_at.desc())
        .offset((page - 1) * size)
        .limit(size),
    ).all()
    return list(records), int(total)


def list_offer_categories(db: Session) -> list[OfferCategoryRead]:
    offers = list(
        db.scalars(
            select(Offer).order_by(
                Offer.service_category.asc(),
                Offer.name.asc(),
                Offer.version.desc(),
            ),
        ).all(),
    )

    grouped: dict[str, list[OfferRead]] = {"mobile": [], "internet": [], "landline": []}
    for offer in offers:
        grouped.setdefault(offer.service_category, []).append(OfferRead.model_validate(offer))

    response: list[OfferCategoryRead] = []
    for category, category_offers in grouped.items():
        if not category_offers:
            continue
        response.append(
            OfferCategoryRead(
                service_category=cast(OfferServiceCategory, category),
                offers=category_offers,
            ),
        )
    return response


def get_offer(db: Session, offer_id: str) -> Offer:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise ApiException(
            status_code=404,
            code="offer_not_found",
            message="Offer was not found",
        )
    return offer


def update_offer(db: Session, offer_id: str, payload: OfferUpdate) -> Offer:
    offer = get_offer(db, offer_id)
    incoming = payload.model_dump(exclude_unset=True)
    merged: dict[str, Any] = _base_offer_payload(offer)
    merged.update(incoming)
    normalized = OfferCreate.model_validate(merged)
    normalized_data = normalized.model_dump()
    _ensure_unique_offer_identity(
        db,
        name=normalized.name,
        service_category=normalized.service_category,
        version=normalized.version,
        excluding_offer_id=offer_id,
    )

    for field, value in normalized_data.items():
        setattr(offer, field, value)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


def delete_offer(db: Session, offer_id: str) -> None:
    offer = get_offer(db, offer_id)
    has_contracts = db.scalar(select(Contract.id).where(Contract.offer_id == offer_id).limit(1))
    if has_contracts:
        raise ApiException(
            status_code=409,
            code="offer_delete_blocked",
            message="Offer cannot be deleted because contract history exists",
        )
    db.delete(offer)
    db.commit()
