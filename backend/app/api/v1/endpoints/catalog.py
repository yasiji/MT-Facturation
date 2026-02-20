from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.common.api import PaginationParams, build_paginated_response, pagination_params
from app.db.session import get_db
from app.schemas.catalog import OfferCategoryRead, OfferCreate, OfferRead, OfferUpdate
from app.services.catalog_service import (
    create_offer,
    delete_offer,
    get_offer,
    list_offer_categories,
    list_offers,
    update_offer,
)

router = APIRouter(tags=["catalog"])


@router.post("/offers", response_model=OfferRead)
def create_offer_endpoint(
    payload: OfferCreate,
    db: Annotated[Session, Depends(get_db)],
) -> OfferRead:
    return OfferRead.model_validate(create_offer(db, payload))


@router.get("/offers")
def list_offers_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    records, total = list_offers(db, page=params.page, size=params.size)
    data = [OfferRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/offer-categories", response_model=list[OfferCategoryRead])
def list_offer_categories_endpoint(
    db: Annotated[Session, Depends(get_db)],
) -> list[OfferCategoryRead]:
    return list_offer_categories(db)


@router.get("/offer-families", response_model=list[OfferCategoryRead], deprecated=True)
def list_offer_families_compat_endpoint(
    db: Annotated[Session, Depends(get_db)],
) -> list[OfferCategoryRead]:
    return list_offer_categories(db)


@router.get("/offers/{offer_id}", response_model=OfferRead)
def get_offer_endpoint(
    offer_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> OfferRead:
    return OfferRead.model_validate(get_offer(db, offer_id))


@router.put("/offers/{offer_id}", response_model=OfferRead)
def update_offer_endpoint(
    offer_id: str,
    payload: OfferUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> OfferRead:
    return OfferRead.model_validate(update_offer(db, offer_id, payload))


@router.delete("/offers/{offer_id}", status_code=204)
def delete_offer_endpoint(
    offer_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    delete_offer(db, offer_id)
    return Response(status_code=204)
