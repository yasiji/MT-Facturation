from typing import Annotated

from fastapi import APIRouter, Depends

from app.common.api import PaginationParams, build_paginated_response, pagination_params

router = APIRouter(tags=["conventions"])


@router.get("/conventions/sample")
def sample_conventions(
    params: Annotated[PaginationParams, Depends(pagination_params)],
) -> dict[str, object]:
    sample_data: list[dict[str, object]] = [{"id": "sample-1", "name": "Sample Item"}]
    return build_paginated_response(data=sample_data, params=params, total=1)
