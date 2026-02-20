from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.common.api import PaginationParams, build_paginated_response, pagination_params
from app.db.session import get_db
from app.schemas.billing import (
    BillingRunRequest,
    BillingRunResult,
    InvoiceDetailRead,
    InvoiceLineRead,
    InvoiceRead,
)
from app.services.billing_service import (
    get_invoice,
    get_invoice_for_download,
    get_invoice_lines,
    list_invoices,
    run_billing_cycle,
)

router = APIRouter(tags=["billing"])


@router.post("/billing/runs", response_model=BillingRunResult)
def run_billing_cycle_endpoint(
    payload: BillingRunRequest,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: Annotated[Session, Depends(get_db)],
) -> BillingRunResult:
    return run_billing_cycle(db, payload=payload, idempotency_key=idempotency_key)


@router.get("/invoices")
def list_invoices_endpoint(
    params: Annotated[PaginationParams, Depends(pagination_params)],
    db: Annotated[Session, Depends(get_db)],
    client_id: Annotated[str | None, Query()] = None,
    service: Annotated[str | None, Query(pattern="^(mobile|internet|landline)$")] = None,
    offer_id: Annotated[str | None, Query()] = None,
) -> dict[str, object]:
    records, total = list_invoices(
        db,
        page=params.page,
        size=params.size,
        client_id=client_id,
        service_category=service,
        offer_id=offer_id,
    )
    data = [InvoiceRead.model_validate(record).model_dump(mode="json") for record in records]
    return build_paginated_response(data=data, params=params, total=total)


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailRead)
def get_invoice_endpoint(
    invoice_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> InvoiceDetailRead:
    invoice = get_invoice(db, invoice_id)
    lines = get_invoice_lines(db, invoice_id)
    invoice_payload = InvoiceRead.model_validate(invoice).model_dump(mode="json")
    line_payloads = [InvoiceLineRead.model_validate(line) for line in lines]
    return InvoiceDetailRead(
        **invoice_payload,
        lines=line_payloads,
    )


@router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf_endpoint(
    invoice_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    invoice = get_invoice_for_download(db, invoice_id)
    if not invoice.pdf_file_path or not invoice.pdf_file_name:
        raise RuntimeError("Invoice PDF metadata missing after generation")
    return FileResponse(
        path=invoice.pdf_file_path,
        media_type="application/pdf",
        filename=invoice.pdf_file_name,
    )
