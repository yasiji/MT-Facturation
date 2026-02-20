from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort: str | None = None
    filters: str | None = None


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    sort: str | None = None
    filters: str | None = None


def pagination_params(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    sort: str | None = Query(default=None),
    filters: str | None = Query(default=None),
) -> PaginationParams:
    return PaginationParams(page=page, size=size, sort=sort, filters=filters)


def build_paginated_response(
    data: list[dict[str, object]],
    params: PaginationParams,
    total: int,
) -> dict[str, object]:
    return {
        "data": data,
        "meta": PaginationMeta(
            page=params.page,
            size=params.size,
            total=total,
            sort=params.sort,
            filters=params.filters,
        ).model_dump(),
    }
