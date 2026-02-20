from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.landing import (
    LandingBootstrapResponse,
    LandingCinLookupRequest,
    LandingClientLookupResponse,
    LandingContractDocumentLinkRequest,
    LandingContractDocumentLinkResponse,
    LandingDraftCreate,
    LandingDraftRead,
    LandingDraftUpdate,
    LandingInvoiceLookupResponse,
    LandingLookupVerificationResponse,
    LandingNewSubscriptionSubmitRequest,
    LandingPlanChangeSubmitRequest,
    LandingSubmitResult,
)
from app.services.landing_service import (
    create_landing_draft,
    get_idempotent_response,
    get_landing_draft,
    issue_contract_document_link,
    list_landing_bootstrap_data,
    lookup_client_invoices,
    lookup_client_subscriptions,
    resolve_contract_document_for_download,
    resolve_invoice_document_for_download,
    save_idempotent_response,
    submit_new_subscription,
    submit_plan_change,
    update_landing_draft,
    verify_lookup_identity_by_cin,
)

router = APIRouter(tags=["landing"])


@router.get("/landing/bootstrap", response_model=LandingBootstrapResponse)
def landing_bootstrap_endpoint(
    db: Annotated[Session, Depends(get_db)],
) -> LandingBootstrapResponse:
    return list_landing_bootstrap_data(db)


@router.post("/landing/drafts", response_model=LandingDraftRead)
def create_landing_draft_endpoint(
    payload: LandingDraftCreate,
    db: Annotated[Session, Depends(get_db)],
) -> LandingDraftRead:
    return create_landing_draft(db, payload)


@router.get("/landing/drafts/{draft_id}", response_model=LandingDraftRead)
def get_landing_draft_endpoint(
    draft_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> LandingDraftRead:
    return get_landing_draft(db, draft_id)


@router.put("/landing/drafts/{draft_id}", response_model=LandingDraftRead)
def update_landing_draft_endpoint(
    draft_id: str,
    payload: LandingDraftUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> LandingDraftRead:
    return update_landing_draft(db, draft_id, payload)


@router.get("/landing/clients/{cin}/subscriptions", response_model=LandingClientLookupResponse)
def lookup_landing_client_subscriptions_endpoint(
    cin: str,
    lookup_token: Annotated[str, Query(alias="lookup_token")],
    db: Annotated[Session, Depends(get_db)],
) -> LandingClientLookupResponse:
    return lookup_client_subscriptions(
        db,
        cin=cin.strip().upper(),
        lookup_token=lookup_token.strip(),
    )


@router.get("/landing/clients/{cin}/invoices", response_model=LandingInvoiceLookupResponse)
def lookup_landing_client_invoices_endpoint(
    cin: str,
    lookup_token: Annotated[str, Query(alias="lookup_token")],
    db: Annotated[Session, Depends(get_db)],
) -> LandingInvoiceLookupResponse:
    return lookup_client_invoices(
        db,
        cin=cin.strip().upper(),
        lookup_token=lookup_token.strip(),
    )


@router.post("/landing/clients/verify-cin", response_model=LandingLookupVerificationResponse)
def verify_landing_client_lookup_by_cin_endpoint(
    payload: LandingCinLookupRequest,
    db: Annotated[Session, Depends(get_db)],
) -> LandingLookupVerificationResponse:
    return verify_lookup_identity_by_cin(db, payload)


@router.post("/landing/submit/new", response_model=LandingSubmitResult)
def submit_landing_new_subscription_endpoint(
    payload: LandingNewSubscriptionSubmitRequest,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: Annotated[Session, Depends(get_db)],
) -> LandingSubmitResult:
    operation = "landing_submit_new"
    replayed, request_hash = get_idempotent_response(
        db,
        operation=operation,
        idempotency_key=idempotency_key,
        request_payload=payload.model_dump(mode="json"),
    )
    if replayed:
        return replayed.model_copy(update={"idempotency_replayed": True})

    result = submit_new_subscription(db, payload)
    save_idempotent_response(
        db,
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response=result,
    )
    return result


@router.post("/landing/submit/plan-change", response_model=LandingSubmitResult)
def submit_landing_plan_change_endpoint(
    payload: LandingPlanChangeSubmitRequest,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: Annotated[Session, Depends(get_db)],
) -> LandingSubmitResult:
    operation = "landing_submit_plan_change"
    replayed, request_hash = get_idempotent_response(
        db,
        operation=operation,
        idempotency_key=idempotency_key,
        request_payload=payload.model_dump(mode="json"),
    )
    if replayed:
        return replayed.model_copy(update={"idempotency_replayed": True})

    result = submit_plan_change(db, payload)
    save_idempotent_response(
        db,
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response=result,
    )
    return result


@router.post(
    "/landing/contracts/{contract_id}/document-link",
    response_model=LandingContractDocumentLinkResponse,
)
def issue_landing_contract_document_link_endpoint(
    contract_id: str,
    payload: LandingContractDocumentLinkRequest,
    db: Annotated[Session, Depends(get_db)],
) -> LandingContractDocumentLinkResponse:
    return issue_contract_document_link(db, contract_id=contract_id, payload=payload)


@router.get("/landing/contracts/{contract_id}/document")
def download_landing_contract_document_endpoint(
    contract_id: str,
    token: Annotated[str, Query(alias="token")],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    document = resolve_contract_document_for_download(
        db,
        contract_id=contract_id,
        access_token=token.strip(),
    )
    return FileResponse(
        path=document.file_path,
        media_type=document.mime_type,
        filename=document.file_name,
    )


@router.get("/landing/invoices/{invoice_id}/document")
def download_landing_invoice_document_endpoint(
    invoice_id: str,
    token: Annotated[str, Query(alias="token")],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    invoice = resolve_invoice_document_for_download(
        db,
        invoice_id=invoice_id,
        access_token=token.strip(),
    )
    if not invoice.pdf_file_path or not invoice.pdf_file_name:
        raise RuntimeError("Invoice PDF metadata missing after generation")
    return FileResponse(
        path=invoice.pdf_file_path,
        media_type="application/pdf",
        filename=invoice.pdf_file_name,
    )
