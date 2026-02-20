import base64
import hashlib
import hmac
import json
import logging
import os
import random
import re
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any, cast

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import mm  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.core.settings import get_settings
from app.models.billing import Invoice
from app.models.catalog import Offer
from app.models.contract import Contract, ContractAuditEvent, ContractDocument
from app.models.customer import Client, Subscriber
from app.models.landing import IdempotencyRecord, LandingDraft
from app.schemas.catalog import OfferServiceCategory, OfferServiceType
from app.schemas.contract import ContractProvisionRequest, ContractRead, ProvisionSubscriberInput
from app.schemas.landing import (
    LandingBootstrapResponse,
    LandingCinLookupRequest,
    LandingClientLookupResponse,
    LandingClientSummary,
    LandingContractDocumentLinkRequest,
    LandingContractDocumentLinkResponse,
    LandingCurrentSubscriptionRead,
    LandingDraftCreate,
    LandingDraftRead,
    LandingDraftStatus,
    LandingDraftUpdate,
    LandingFlowType,
    LandingInvoiceLookupResponse,
    LandingInvoiceSummary,
    LandingLookupVerificationResponse,
    LandingNewSubscriptionSubmitRequest,
    LandingOfferCategory,
    LandingOfferSummary,
    LandingPlanChangeSubmitRequest,
    LandingSubmitResult,
)
from app.services.billing_service import get_invoice_for_download
from app.services.contract_service import provision_contract

logger = logging.getLogger("mt_facturation.landing")
FLOW_OPTIONS: list[LandingFlowType] = [
    "subscribe_new_service",
    "upgrade_or_downgrade_existing_service",
    "check_billing_and_download_invoices",
]
SERVICES: list[OfferServiceCategory] = ["mobile", "internet", "landline"]
NINE_DIGITS_REGEX = re.compile(r"^\d{9}$")
RANDOM_RETRY_LIMIT = 100
TOKEN_VERSION = 1


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _mask_cin(cin: str) -> str:
    normalized = cin.strip().upper()
    if len(normalized) <= 4:
        return f"{normalized[:1]}***"
    return f"{normalized[:2]}***{normalized[-2:]}"


def _mask_email(email: str) -> str:
    cleaned = email.strip()
    if "@" not in cleaned:
        return "***"
    local, domain = cleaned.split("@", 1)
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def _mask_phone(phone: str) -> str:
    digits = "".join(char for char in phone if char.isdigit())
    if len(digits) < 4:
        return "***"
    return f"+******{digits[-4:]}"


def _urlsafe_b64encode(raw_value: bytes) -> str:
    return base64.urlsafe_b64encode(raw_value).decode("ascii").rstrip("=")


def _urlsafe_b64decode(encoded_value: str) -> bytes:
    padding = "=" * ((4 - len(encoded_value) % 4) % 4)
    return base64.urlsafe_b64decode(f"{encoded_value}{padding}")


def _sign_landing_token(payload: dict[str, Any]) -> str:
    settings = get_settings()
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_segment = _urlsafe_b64encode(payload_bytes)
    signature = hmac.new(
        settings.landing_token_secret.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_segment = _urlsafe_b64encode(signature)
    return f"{payload_segment}.{signature_segment}"


def _verify_landing_token(token: str, *, purpose: str) -> dict[str, Any]:
    if "." not in token:
        raise ApiException(
            status_code=401,
            code="landing_token_invalid",
            message="Token format is invalid",
        )
    payload_segment, signature_segment = token.split(".", 1)
    settings = get_settings()
    expected_signature = hmac.new(
        settings.landing_token_secret.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    actual_signature = _urlsafe_b64decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise ApiException(
            status_code=401,
            code="landing_token_invalid",
            message="Token signature is invalid",
        )

    try:
        payload = json.loads(_urlsafe_b64decode(payload_segment).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ApiException(
            status_code=401,
            code="landing_token_invalid",
            message="Token payload is invalid",
            details={"reason": str(exc)},
        ) from exc

    if not isinstance(payload, dict):
        raise ApiException(
            status_code=401,
            code="landing_token_invalid",
            message="Token payload is invalid",
        )

    if payload.get("v") != TOKEN_VERSION or payload.get("purpose") != purpose:
        raise ApiException(
            status_code=401,
            code="landing_token_invalid",
            message="Token purpose is invalid",
        )

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int) or expires_at <= int(_utc_now().timestamp()):
        raise ApiException(
            status_code=401,
            code="landing_token_expired",
            message="Token expired",
        )
    return payload


def _new_lookup_token(cin: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = _utc_now().timestamp() + settings.landing_lookup_token_ttl_seconds
    payload = {
        "v": TOKEN_VERSION,
        "purpose": "landing_lookup",
        "cin": cin,
        "exp": int(expires_at),
    }
    return _sign_landing_token(payload), datetime.fromtimestamp(int(expires_at), tz=UTC)


def _new_document_token(*, contract_id: str, cin: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = _utc_now().timestamp() + settings.landing_document_token_ttl_seconds
    payload = {
        "v": TOKEN_VERSION,
        "purpose": "landing_contract_document",
        "contract_id": contract_id,
        "cin": cin,
        "exp": int(expires_at),
    }
    return _sign_landing_token(payload), datetime.fromtimestamp(int(expires_at), tz=UTC)


def _new_invoice_document_token(*, invoice_id: str, cin: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = _utc_now().timestamp() + settings.landing_document_token_ttl_seconds
    payload = {
        "v": TOKEN_VERSION,
        "purpose": "landing_invoice_document",
        "invoice_id": invoice_id,
        "cin": cin,
        "exp": int(expires_at),
    }
    return _sign_landing_token(payload), datetime.fromtimestamp(int(expires_at), tz=UTC)


def _record_contract_audit_event(
    db: Session,
    *,
    contract_id: str,
    event_type: str,
    actor_id: str | None,
    details: dict[str, Any],
) -> None:
    db.add(
        ContractAuditEvent(
            contract_id=contract_id,
            event_type=event_type,
            actor_id=actor_id,
            details=json.dumps(details, sort_keys=True),
        ),
    )


def _build_contract_pdf(
    *,
    contract: Contract,
    client: Client,
    offer: Offer,
    service_identifier: str,
) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=f"Contract {contract.id}",
    )

    stylesheet = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ContractTitle",
        parent=stylesheet["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#102F4A"),
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=stylesheet["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#0D5C63"),
        spaceAfter=6,
        spaceBefore=10,
    )
    body_style = ParagraphStyle(
        "ContractBody",
        parent=stylesheet["BodyText"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E2B3A"),
    )
    muted_style = ParagraphStyle(
        "ContractMuted",
        parent=body_style,
        fontSize=9,
        textColor=colors.HexColor("#4D5D6C"),
    )

    client_cin = _require_client_cin(client)
    issue_time = _utc_now().strftime("%Y-%m-%d %H:%M UTC")
    monthly_fee = f"{offer.monthly_fee} MAD"
    activation_fee = f"{offer.activation_fee} MAD"

    story: list[Any] = []
    story.append(Paragraph("MT FACTURATION", muted_style))
    story.append(Paragraph("Telecom Service Contract", title_style))
    story.append(
        Paragraph(
            (
                f"<b>Contract ID:</b> {contract.id}<br/>"
                f"<b>Issued At:</b> {issue_time}<br/>"
                f"<b>Status:</b> {contract.status}"
            ),
            body_style,
        ),
    )

    story.append(Spacer(1, 8))
    story.append(Paragraph("Contracting Parties", section_style))
    party_table = Table(
        [
            ["Provider", "Client"],
            ["MT Facturation", client.full_name],
            ["Business Ref", client_cin],
            ["Contact", client.email or client.phone or "-"],
            ["Address", client.address or "-"],
        ],
        colWidths=[58 * mm, 108 * mm],
    )
    party_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D7EDF1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#10334A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7CBD6")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FBFC")]),
            ],
        ),
    )
    story.append(party_table)

    story.append(Paragraph("Subscribed Service", section_style))
    service_table = Table(
        [
            ["Service Category", offer.service_category.title()],
            ["Service Type", offer.service_type],
            ["Offer Name", offer.name],
            ["Service Identifier", service_identifier],
            ["Contract Start Date", contract.start_date.isoformat()],
            ["Commitment (months)", str(contract.commitment_months or "-")],
            ["Monthly Fee", monthly_fee],
            ["Activation Fee", activation_fee],
        ],
        colWidths=[58 * mm, 108 * mm],
    )
    service_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E9F4F6")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#203347")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BFD0D9")),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
        ),
    )
    story.append(service_table)

    story.append(Paragraph("Key Terms", section_style))
    story.append(
        Paragraph(
            (
                "1. The subscribed offer remains governed by MT Facturation service conditions and "
                "applicable legal requirements.<br/>"
                "2. The client confirms that provided identity and contact data are accurate "
                "and complete.<br/>"
                "3. Service changes, upgrades, and downgrades are processed under the active "
                "offer catalog "
                "rules at the time of the request.<br/>"
                "4. This document is digitally issued and archived as the official contract "
                "reference."
            ),
            body_style,
        ),
    )

    signature_table = Table(
        [["Client Signature", "MT Facturation Signature"], ["", ""]],
        colWidths=[83 * mm, 83 * mm],
        rowHeights=[9 * mm, 18 * mm],
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#23405A")),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B6C8D2")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6F8")),
            ],
        ),
    )
    story.append(Spacer(1, 10))
    story.append(signature_table)
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Digitally generated by MT Facturation contract platform.",
            muted_style,
        ),
    )

    def draw_frame(canvas_obj: Any, _doc: Any) -> None:
        width, height = A4
        canvas_obj.saveState()
        canvas_obj.setStrokeColor(colors.HexColor("#9FC7D8"))
        canvas_obj.setLineWidth(1.1)
        canvas_obj.roundRect(
            12 * mm,
            12 * mm,
            width - 24 * mm,
            height - 24 * mm,
            7 * mm,
            stroke=1,
            fill=0,
        )
        canvas_obj.setFillColor(colors.HexColor("#0D5C63"))
        canvas_obj.rect(12 * mm, height - 24 * mm, width - 24 * mm, 8 * mm, stroke=0, fill=1)
        canvas_obj.restoreState()

    document.build(story, onFirstPage=draw_frame, onLaterPages=draw_frame)
    return buffer.getvalue()


def _contract_documents_root() -> Path:
    configured = get_settings().contract_documents_dir.strip()
    base_path = Path(configured)
    if base_path.is_absolute():
        return base_path
    return Path(os.getcwd()) / base_path


def _issue_contract_document(
    db: Session,
    *,
    contract: Contract,
    client: Client,
    offer: Offer,
    service_identifier: str,
    actor_id: str,
) -> str:
    client_cin = _require_client_cin(client)
    pdf_bytes = _build_contract_pdf(
        contract=contract,
        client=client,
        offer=offer,
        service_identifier=service_identifier,
    )

    root = _contract_documents_root()
    root.mkdir(parents=True, exist_ok=True)
    file_name = f"contract-{contract.id}.pdf"
    file_path = root / file_name
    file_path.write_bytes(pdf_bytes)
    digest = hashlib.sha256(pdf_bytes).hexdigest()

    document = db.scalar(
        select(ContractDocument).where(
            ContractDocument.contract_id == contract.id,
            ContractDocument.document_type == "contract_pdf",
        ),
    )
    if document is None:
        document = ContractDocument(
            contract_id=contract.id,
            document_type="contract_pdf",
            file_name=file_name,
            file_path=str(file_path),
            mime_type="application/pdf",
            sha256=digest,
            issued_by_actor=actor_id,
        )
    else:
        document.file_name = file_name
        document.file_path = str(file_path)
        document.mime_type = "application/pdf"
        document.sha256 = digest
        document.issued_by_actor = actor_id
    db.add(document)
    db.flush()

    _record_contract_audit_event(
        db,
        contract_id=contract.id,
        event_type="contract_document_issued",
        actor_id=actor_id,
        details={
            "document_id": document.id,
            "document_type": "contract_pdf",
            "sha256": digest,
        },
    )

    token, _ = _new_document_token(contract_id=contract.id, cin=client_cin)
    return f"/api/v1/landing/contracts/{contract.id}/document?token={token}"


def _offer_summary(offer: Offer) -> LandingOfferSummary:
    return LandingOfferSummary(
        id=offer.id,
        name=offer.name,
        service_category=cast(OfferServiceCategory, offer.service_category),
        service_type=cast(OfferServiceType, offer.service_type),
        monthly_fee=Decimal(str(offer.monthly_fee)),
        activation_fee=Decimal(str(offer.activation_fee)),
        status=offer.status,
        valid_from=offer.valid_from,
        valid_to=offer.valid_to,
    )


def list_landing_bootstrap_data(db: Session) -> LandingBootstrapResponse:
    offers = list(
        db.scalars(
            select(Offer)
            .where(Offer.status == "active")
            .order_by(Offer.service_category, Offer.name),
        ).all(),
    )
    grouped: dict[str, list[LandingOfferSummary]] = {"mobile": [], "internet": [], "landline": []}
    for offer in offers:
        grouped.setdefault(offer.service_category, []).append(_offer_summary(offer))

    categories: list[LandingOfferCategory] = []
    for service_category in SERVICES:
        categories.append(
            LandingOfferCategory(
                service_category=service_category,
                offers=grouped[service_category],
            ),
        )
    return LandingBootstrapResponse(
        flow_options=FLOW_OPTIONS,
        services=SERVICES,
        offer_categories=categories,
    )


def _draft_to_read(record: LandingDraft) -> LandingDraftRead:
    payload_data: dict[str, Any]
    try:
        payload_data = json.loads(record.payload)
    except json.JSONDecodeError:
        payload_data = {}
    return LandingDraftRead(
        id=record.id,
        flow_type=cast(LandingFlowType, record.flow_type),
        step=record.step,
        cin=record.cin,
        payload=payload_data,
        status=cast(LandingDraftStatus, record.status),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def create_landing_draft(db: Session, payload: LandingDraftCreate) -> LandingDraftRead:
    record = LandingDraft(
        flow_type=payload.flow_type,
        step=payload.step,
        cin=payload.cin,
        payload=json.dumps(payload.payload, sort_keys=True),
        status=payload.status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _draft_to_read(record)


def get_landing_draft(db: Session, draft_id: str) -> LandingDraftRead:
    record = db.get(LandingDraft, draft_id)
    if record is None:
        raise ApiException(
            status_code=404,
            code="landing_draft_not_found",
            message="Landing draft was not found",
        )
    return _draft_to_read(record)


def update_landing_draft(
    db: Session,
    draft_id: str,
    payload: LandingDraftUpdate,
) -> LandingDraftRead:
    record = db.get(LandingDraft, draft_id)
    if record is None:
        raise ApiException(
            status_code=404,
            code="landing_draft_not_found",
            message="Landing draft was not found",
        )

    patch = payload.model_dump(exclude_unset=True)
    if "step" in patch:
        record.step = payload.step or record.step
    if "cin" in patch:
        record.cin = payload.cin
    if "payload" in patch:
        record.payload = json.dumps(payload.payload or {}, sort_keys=True)
    if "status" in patch:
        record.status = payload.status or record.status

    db.add(record)
    db.commit()
    db.refresh(record)
    return _draft_to_read(record)


def _request_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_idempotent_response(
    db: Session,
    *,
    operation: str,
    idempotency_key: str,
    request_payload: dict[str, Any],
) -> tuple[LandingSubmitResult | None, str]:
    if len(idempotency_key.strip()) < 8:
        raise ApiException(
            status_code=400,
            code="idempotency_key_invalid",
            message="Idempotency-Key header must contain at least 8 characters",
        )

    payload_hash = _request_hash(request_payload)
    record = db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.operation == operation,
            IdempotencyRecord.idempotency_key == idempotency_key,
        ),
    )
    if record is None:
        return None, payload_hash
    if record.request_hash != payload_hash:
        raise ApiException(
            status_code=409,
            code="idempotency_key_payload_conflict",
            message="Idempotency-Key was already used with a different payload",
        )

    try:
        payload = json.loads(record.response_payload)
    except json.JSONDecodeError as exc:
        raise ApiException(
            status_code=500,
            code="idempotency_record_invalid",
            message="Stored idempotency response payload is invalid",
            details={"reason": str(exc)},
        ) from exc
    return LandingSubmitResult.model_validate(payload), payload_hash


def save_idempotent_response(
    db: Session,
    *,
    operation: str,
    idempotency_key: str,
    request_hash: str,
    response: LandingSubmitResult,
) -> None:
    record = IdempotencyRecord(
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response_payload=json.dumps(response.model_dump(mode="json"), sort_keys=True),
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.operation == operation,
                IdempotencyRecord.idempotency_key == idempotency_key,
            ),
        )
        if existing is None or existing.request_hash != request_hash:
            raise ApiException(
                status_code=409,
                code="idempotency_key_payload_conflict",
                message="Idempotency-Key was already used with a different payload",
            )


def _get_client_by_cin(db: Session, cin: str) -> Client | None:
    return db.scalar(select(Client).where(Client.cin == cin))


def _require_client_cin(client: Client) -> str:
    if not client.cin:
        raise ApiException(
            status_code=409,
            code="client_cin_missing",
            message="Client record has no CIN assigned",
        )
    return client.cin


def verify_lookup_identity_by_cin(
    db: Session,
    payload: LandingCinLookupRequest,
) -> LandingLookupVerificationResponse:
    client = _get_client_by_cin(db, payload.cin)
    if client is None:
        raise ApiException(
            status_code=404,
            code="landing_client_not_found",
            message="No client found for the provided CIN",
        )
    client_cin = _require_client_cin(client)
    lookup_token, expires_at = _new_lookup_token(client_cin)
    logger.info("landing.lookup_verified_by_cin cin=%s", _mask_cin(client_cin))
    return LandingLookupVerificationResponse(
        cin=client_cin,
        masked_contact=_mask_cin(client_cin),
        lookup_token=lookup_token,
        expires_at=expires_at,
    )


def _get_contract_bundle(
    db: Session,
    *,
    contract_id: str,
) -> tuple[Contract, Client, Offer, str]:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise ApiException(
            status_code=404,
            code="contract_not_found",
            message="Contract was not found",
        )

    client = db.get(Client, contract.client_id)
    offer = db.get(Offer, contract.offer_id)
    subscriber = db.get(Subscriber, contract.subscriber_id)
    if client is None or offer is None:
        raise ApiException(
            status_code=409,
            code="contract_related_data_missing",
            message="Contract related data is missing",
        )
    service_identifier = subscriber.service_identifier if subscriber else "-"
    return contract, client, offer, service_identifier


def issue_contract_document_link(
    db: Session,
    *,
    contract_id: str,
    payload: LandingContractDocumentLinkRequest,
) -> LandingContractDocumentLinkResponse:
    contract, client, offer, service_identifier = _get_contract_bundle(
        db,
        contract_id=contract_id,
    )
    client_cin = _require_client_cin(client)
    if client_cin != payload.cin:
        raise ApiException(
            status_code=403,
            code="landing_contract_client_mismatch",
            message="Contract does not belong to provided CIN",
        )

    verified_reference = _mask_cin(client_cin)
    document = db.scalar(
        select(ContractDocument).where(
            ContractDocument.contract_id == contract.id,
            ContractDocument.document_type == "contract_pdf",
        ),
    )
    if document is None or not Path(document.file_path).exists():
        url = _issue_contract_document(
            db,
            contract=contract,
            client=client,
            offer=offer,
            service_identifier=service_identifier,
            actor_id="landing-flow",
        )
        db.commit()
    else:
        token, _ = _new_document_token(contract_id=contract.id, cin=client_cin)
        url = f"/api/v1/landing/contracts/{contract.id}/document?token={token}"

    logger.info(
        "landing.contract_document_link cin=%s contract_id=%s verified=%s",
        _mask_cin(client_cin),
        contract.id,
        verified_reference,
    )
    return LandingContractDocumentLinkResponse(contract_id=contract.id, document_download_url=url)


def _assert_lookup_access(cin: str, lookup_token: str) -> None:
    payload = _verify_landing_token(lookup_token, purpose="landing_lookup")
    token_cin = payload.get("cin")
    if not isinstance(token_cin, str) or token_cin != cin:
        raise ApiException(
            status_code=403,
            code="landing_lookup_token_mismatch",
            message="Lookup token does not match CIN",
        )


def resolve_contract_document_for_download(
    db: Session,
    *,
    contract_id: str,
    access_token: str,
) -> ContractDocument:
    token_payload = _verify_landing_token(access_token, purpose="landing_contract_document")
    token_contract_id = token_payload.get("contract_id")
    token_cin = token_payload.get("cin")
    if not isinstance(token_contract_id, str) or token_contract_id != contract_id:
        raise ApiException(
            status_code=403,
            code="landing_document_token_mismatch",
            message="Document token does not match the requested contract",
        )

    contract = db.get(Contract, contract_id)
    if contract is None:
        raise ApiException(
            status_code=404,
            code="contract_not_found",
            message="Contract was not found",
        )

    client = db.get(Client, contract.client_id)
    if client is None or not isinstance(token_cin, str) or client.cin != token_cin:
        raise ApiException(
            status_code=403,
            code="landing_document_token_mismatch",
            message="Document token does not match contract ownership",
        )

    document = db.scalar(
        select(ContractDocument).where(
            ContractDocument.contract_id == contract.id,
            ContractDocument.document_type == "contract_pdf",
        ),
    )
    if document is None:
        raise ApiException(
            status_code=404,
            code="contract_document_not_found",
            message="Contract PDF is not available",
        )
    if not Path(document.file_path).exists():
        raise ApiException(
            status_code=404,
            code="contract_document_not_found",
            message="Contract PDF file is missing",
        )
    return document


def resolve_invoice_document_for_download(
    db: Session,
    *,
    invoice_id: str,
    access_token: str,
) -> Invoice:
    token_payload = _verify_landing_token(access_token, purpose="landing_invoice_document")
    token_invoice_id = token_payload.get("invoice_id")
    token_cin = token_payload.get("cin")
    if not isinstance(token_invoice_id, str) or token_invoice_id != invoice_id:
        raise ApiException(
            status_code=403,
            code="landing_invoice_token_mismatch",
            message="Invoice token does not match requested invoice",
        )

    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise ApiException(
            status_code=404,
            code="invoice_not_found",
            message="Invoice was not found",
        )

    client = db.get(Client, invoice.client_id)
    if client is None or not isinstance(token_cin, str) or client.cin != token_cin:
        raise ApiException(
            status_code=403,
            code="landing_invoice_token_mismatch",
            message="Invoice token does not match invoice ownership",
        )

    return get_invoice_for_download(db, invoice_id)


def _normalize_to_moroccan_nsn(raw_value: str, *, kind: str) -> str:
    digits = "".join(char for char in raw_value if char.isdigit())

    if digits.startswith("212"):
        nsn = digits[3:]
    elif digits.startswith("0"):
        nsn = digits[1:]
    else:
        nsn = digits

    if not NINE_DIGITS_REGEX.fullmatch(nsn):
        raise ApiException(
            status_code=422,
            code=f"{kind}_number_invalid",
            message="Number must contain a valid Moroccan national format",
            details={
                "accepted_examples": [
                    "+212 6 55 33 44 22",
                    "06 55 33 44 22",
                    "07 55 33 44 22",
                ]
                if kind == "mobile"
                else [
                    "+212 5 24 33 44 55",
                    "05 24 33 44 55",
                    "08 24 33 44 55",
                ],
            },
        )

    first_digit = nsn[0]
    if kind == "mobile" and first_digit not in {"6", "7"}:
        raise ApiException(
            status_code=422,
            code="mobile_number_invalid",
            message="Mobile number must start with 6 or 7 after +212 (or 0 locally)",
        )
    if kind == "landline" and first_digit not in {"5", "8"}:
        raise ApiException(
            status_code=422,
            code="landline_number_invalid",
            message="Landline number must start with 5 or 8 after +212 (or 0 locally)",
        )
    return nsn


def _build_mobile_identifier(raw_number: str) -> str:
    nsn = _normalize_to_moroccan_nsn(raw_number, kind="mobile")
    return f"+212{nsn}"


def _build_landline_identifier(raw_number: str) -> str:
    nsn = _normalize_to_moroccan_nsn(raw_number, kind="landline")
    return f"+212{nsn}"


def _generate_moroccan_nsn(*, kind: str) -> str:
    rng = random.SystemRandom()
    first_digit = rng.choice(["6", "7"]) if kind == "mobile" else rng.choice(["5", "8"])
    suffix = "".join(str(rng.randrange(10)) for _ in range(8))
    return f"{first_digit}{suffix}"


def _generate_unique_identifier(db: Session, *, kind: str) -> str:
    for _ in range(RANDOM_RETRY_LIMIT):
        nsn = _generate_moroccan_nsn(kind=kind)
        candidate = f"+212{nsn}"
        existing = db.scalar(
            select(Subscriber.id).where(Subscriber.service_identifier == candidate).limit(1),
        )
        if existing is None:
            return candidate
    raise ApiException(
        status_code=500,
        code="identifier_generation_exhausted",
        message="Could not allocate a unique service identifier",
    )


def _ensure_identifier_available(db: Session, identifier: str) -> None:
    existing = db.scalar(
        select(Subscriber.id).where(Subscriber.service_identifier == identifier).limit(1),
    )
    if existing is not None:
        raise ApiException(
            status_code=409,
            code="subscriber_identifier_conflict",
            message="Subscriber service identifier already exists",
        )


def _resolve_service_identifier(
    db: Session,
    payload: LandingNewSubscriptionSubmitRequest,
) -> str:
    if payload.service_category == "mobile":
        if payload.mobile_number_mode == "use_existing":
            if payload.existing_mobile_local_number is None:
                raise ApiException(
                    status_code=422,
                    code="mobile_number_missing",
                    message="existing_mobile_local_number is required",
                )
            return _build_mobile_identifier(payload.existing_mobile_local_number)
        if payload.requested_mobile_local_number:
            identifier = _build_mobile_identifier(payload.requested_mobile_local_number)
            _ensure_identifier_available(db, identifier)
            return identifier
        return _generate_unique_identifier(db, kind="mobile")

    if payload.home_landline_local_number:
        identifier = _build_landline_identifier(payload.home_landline_local_number)
        _ensure_identifier_available(db, identifier)
        return identifier
    return _generate_unique_identifier(db, kind="landline")


def _get_offer_for_subscription(db: Session, offer_id: str, service_category: str) -> Offer:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise ApiException(status_code=404, code="offer_not_found", message="Offer was not found")
    if offer.service_category != service_category:
        raise ApiException(
            status_code=422,
            code="landing_offer_service_mismatch",
            message="Selected offer does not belong to the selected service",
            details={"offer_service_category": offer.service_category},
        )
    if offer.status != "active":
        raise ApiException(
            status_code=409,
            code="offer_not_active",
            message="Offer is not active and cannot be selected",
        )
    return offer


def _upsert_client_from_landing(
    db: Session,
    payload: LandingNewSubscriptionSubmitRequest,
) -> tuple[Client, bool]:
    client = _get_client_by_cin(db, payload.cin)
    if client is None:
        client = Client(
            cin=payload.cin,
            client_type="individual",
            full_name=payload.full_name,
            email=payload.email,
            address=payload.address,
            phone=payload.contact_phone,
            status="active",
        )
        db.add(client)
        db.flush()
        return client, True

    client.full_name = payload.full_name
    client.email = payload.email
    client.address = payload.address
    client.phone = payload.contact_phone
    db.add(client)
    db.flush()
    return client, False


def submit_new_subscription(
    db: Session,
    payload: LandingNewSubscriptionSubmitRequest,
) -> LandingSubmitResult:
    offer = _get_offer_for_subscription(db, payload.offer_id, payload.service_category)
    service_identifier = _resolve_service_identifier(db, payload)
    client, created_client = _upsert_client_from_landing(db, payload)

    contract, _, created_subscriber, provisioning_mode = provision_contract(
        db,
        ContractProvisionRequest(
            offer_id=offer.id,
            contract_start_date=payload.contract_start_date,
            commitment_months=payload.commitment_months,
            client_id=client.id,
            subscriber=ProvisionSubscriberInput(service_identifier=service_identifier),
            provisioning_intent="auto",
        ),
        actor_id="landing-flow",
    )

    allocation_mode = "generated"
    if payload.service_category == "mobile":
        if payload.mobile_number_mode == "use_existing":
            allocation_mode = "existing_input"
        elif payload.requested_mobile_local_number:
            allocation_mode = "requested_input"
    elif payload.home_landline_local_number:
        allocation_mode = "provided_home_landline"

    _record_contract_audit_event(
        db,
        contract_id=contract.id,
        event_type="landing_service_identifier_allocated",
        actor_id="landing-flow",
        details={
            "service_category": payload.service_category,
            "allocation_mode": allocation_mode,
            "service_identifier_masked": _mask_phone(service_identifier),
        },
    )
    download_url = _issue_contract_document(
        db,
        contract=contract,
        client=client,
        offer=offer,
        service_identifier=service_identifier,
        actor_id="landing-flow",
    )
    db.commit()
    logger.info(
        "landing.submit_new cin=%s contract_id=%s mode=%s",
        _mask_cin(_require_client_cin(client)),
        contract.id,
        provisioning_mode,
    )

    return LandingSubmitResult(
        contract=ContractRead.model_validate(contract),
        client_id=client.id,
        client_cin=payload.cin,
        service_identifier=service_identifier,
        created_client=created_client,
        created_subscriber=created_subscriber,
        provisioning_mode=provisioning_mode,
        document_download_url=download_url,
    )


def _service_category_eligible_offers(
    db: Session,
    *,
    service_category: str,
    exclude_offer_id: str,
) -> list[LandingOfferSummary]:
    today = _utc_now().date()
    offers = list(
        db.scalars(
            select(Offer)
            .where(
                Offer.service_category == service_category,
                Offer.status == "active",
                Offer.id != exclude_offer_id,
                Offer.valid_from <= today,
                (Offer.valid_to.is_(None) | (Offer.valid_to >= today)),
            )
            .order_by(Offer.monthly_fee.asc(), Offer.name.asc()),
        ).all(),
    )
    return [_offer_summary(offer) for offer in offers]


def lookup_client_subscriptions(
    db: Session,
    *,
    cin: str,
    lookup_token: str,
) -> LandingClientLookupResponse:
    _assert_lookup_access(cin, lookup_token)
    client = _get_client_by_cin(db, cin)
    if client is None:
        raise ApiException(
            status_code=404,
            code="landing_client_not_found",
            message="No client found for the provided CIN",
        )

    contracts = list(
        db.scalars(
            select(Contract)
            .where(Contract.client_id == client.id, Contract.status == "active")
            .order_by(Contract.created_at.desc()),
        ).all(),
    )

    subscriptions: list[LandingCurrentSubscriptionRead] = []
    for contract in contracts:
        offer = db.get(Offer, contract.offer_id)
        subscriber = db.get(Subscriber, contract.subscriber_id)
        if offer is None or subscriber is None:
            continue
        subscriptions.append(
            LandingCurrentSubscriptionRead(
                contract_id=contract.id,
                subscriber_id=subscriber.id,
                service_identifier=subscriber.service_identifier,
                service_category=cast(OfferServiceCategory, offer.service_category),
                service_type=cast(OfferServiceType, offer.service_type),
                current_offer=_offer_summary(offer),
                eligible_offers=_service_category_eligible_offers(
                    db,
                    service_category=offer.service_category,
                    exclude_offer_id=offer.id,
                ),
            ),
        )

    return LandingClientLookupResponse(
        client=LandingClientSummary(
            id=client.id,
            cin=cin,
            full_name=client.full_name,
            email=_mask_email(client.email) if client.email else None,
            address=client.address,
            phone=_mask_phone(client.phone) if client.phone else None,
        ),
        subscriptions=subscriptions,
    )


def lookup_client_invoices(
    db: Session,
    *,
    cin: str,
    lookup_token: str,
) -> LandingInvoiceLookupResponse:
    _assert_lookup_access(cin, lookup_token)
    client = _get_client_by_cin(db, cin)
    if client is None:
        raise ApiException(
            status_code=404,
            code="landing_client_not_found",
            message="No client found for the provided CIN",
        )

    invoices = list(
        db.scalars(
            select(Invoice)
            .where(Invoice.client_id == client.id)
            .order_by(Invoice.issued_at.desc()),
        ).all(),
    )

    invoice_payloads: list[LandingInvoiceSummary] = []
    client_cin = _require_client_cin(client)
    for invoice in invoices:
        token, _ = _new_invoice_document_token(invoice_id=invoice.id, cin=client_cin)
        invoice_payloads.append(
            LandingInvoiceSummary(
                invoice_id=invoice.id,
                period_start=invoice.period_start,
                period_end=invoice.period_end,
                due_date=invoice.due_date,
                issued_at=invoice.issued_at,
                status=invoice.status,
                currency=invoice.currency,
                subtotal_amount=Decimal(str(invoice.subtotal_amount)),
                tax_amount=Decimal(str(invoice.tax_amount)),
                total_amount=Decimal(str(invoice.total_amount)),
                document_download_url=(
                    f"/api/v1/landing/invoices/{invoice.id}/document?token={token}"
                ),
            ),
        )

    return LandingInvoiceLookupResponse(
        client=LandingClientSummary(
            id=client.id,
            cin=cin,
            full_name=client.full_name,
            email=_mask_email(client.email) if client.email else None,
            address=client.address,
            phone=_mask_phone(client.phone) if client.phone else None,
        ),
        invoices=invoice_payloads,
    )


def submit_plan_change(
    db: Session,
    payload: LandingPlanChangeSubmitRequest,
) -> LandingSubmitResult:
    client = _get_client_by_cin(db, payload.cin)
    if client is None:
        raise ApiException(
            status_code=404,
            code="landing_client_not_found",
            message="No client found for the provided CIN",
        )

    source_contract = db.get(Contract, payload.source_contract_id)
    if source_contract is None:
        raise ApiException(
            status_code=404,
            code="contract_not_found",
            message="Source contract was not found",
        )
    if source_contract.client_id != client.id:
        raise ApiException(
            status_code=422,
            code="landing_contract_client_mismatch",
            message="Source contract does not belong to the CIN client",
        )

    source_offer = db.get(Offer, source_contract.offer_id)
    target_offer = db.get(Offer, payload.target_offer_id)
    if source_offer is None or target_offer is None:
        raise ApiException(status_code=404, code="offer_not_found", message="Offer was not found")
    if source_offer.service_category != target_offer.service_category:
        raise ApiException(
            status_code=422,
            code="landing_offer_service_mismatch",
            message="Target offer must belong to the same service as source contract",
        )

    contract, _, _, provisioning_mode = provision_contract(
        db,
        ContractProvisionRequest(
            offer_id=target_offer.id,
            contract_start_date=payload.contract_start_date,
            commitment_months=payload.commitment_months,
            client_id=client.id,
            provisioning_intent="upgrade",
            target_contract_id=source_contract.id,
        ),
        actor_id="landing-flow",
    )

    subscriber = db.get(Subscriber, source_contract.subscriber_id)
    service_identifier = subscriber.service_identifier if subscriber else ""
    download_url = _issue_contract_document(
        db,
        contract=contract,
        client=client,
        offer=target_offer,
        service_identifier=service_identifier,
        actor_id="landing-flow",
    )
    db.commit()
    logger.info(
        "landing.submit_plan_change cin=%s contract_id=%s",
        _mask_cin(_require_client_cin(client)),
        contract.id,
    )

    return LandingSubmitResult(
        contract=ContractRead.model_validate(contract),
        client_id=client.id,
        client_cin=payload.cin,
        service_identifier=service_identifier,
        created_client=False,
        created_subscriber=False,
        provisioning_mode=provisioning_mode,
        document_download_url=download_url,
    )
