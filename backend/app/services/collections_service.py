import hashlib
import json
import logging
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.models.billing import Invoice
from app.models.collections import CollectionCase, CollectionCaseAction, Payment
from app.models.customer import Client
from app.schemas.collections import (
    AgingBucket,
    AllocationState,
    CollectionCaseActionCreate,
    CollectionCaseStatus,
    CollectionCaseStatusUpdate,
    CollectionOverviewRead,
    InvoicePaymentApprovalRequest,
    InvoiceStatus,
    PaymentAllocationResult,
    PaymentCreate,
    PaymentRead,
)

logger = logging.getLogger("mt_facturation.collections")
MONEY_QUANT = Decimal("0.01")


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _request_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _sum_posted_payments(db: Session, invoice_id: str) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.invoice_id == invoice_id, Payment.status == "posted"),
    )
    return _money(Decimal(str(total)))


def _aging_bucket(days_past_due: int) -> str:
    if days_past_due <= 0:
        return "current"
    if days_past_due <= 30:
        return "1_30"
    if days_past_due <= 60:
        return "31_60"
    if days_past_due <= 90:
        return "61_90"
    return "90_plus"


def _get_invoice(db: Session, invoice_id: str) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise ApiException(
            status_code=404,
            code="invoice_not_found",
            message="Invoice was not found",
        )
    return invoice


def _append_case_action(
    db: Session,
    *,
    collection_case: CollectionCase,
    action_type: str,
    actor_id: str | None,
    note: str | None,
    payload: dict[str, Any] | None = None,
) -> CollectionCaseAction:
    action = CollectionCaseAction(
        case_id=collection_case.id,
        action_type=action_type,
        actor_id=actor_id,
        note=note,
        payload=json.dumps(payload or {}, sort_keys=True),
    )
    collection_case.last_action_at = _now_utc()
    db.add(collection_case)
    db.add(action)
    db.flush()
    return action


def _set_client_delinquency(db: Session, *, client_id: str, is_delinquent: bool) -> None:
    client = db.get(Client, client_id)
    if client is None:
        return
    if is_delinquent:
        if not client.is_delinquent:
            client.is_delinquent = True
            client.delinquent_since = _now_utc()
    else:
        client.is_delinquent = False
        client.delinquent_since = None
    db.add(client)
    db.flush()


def _sync_invoice_collection_state(
    db: Session,
    *,
    invoice: Invoice,
    actor_id: str,
    add_payment_action: bool = False,
    payment_amount: Decimal | None = None,
) -> tuple[Decimal, CollectionCase | None]:
    if invoice.status == "void":
        return Decimal("0.00"), None

    paid_total = _sum_posted_payments(db, invoice.id)
    outstanding = _money(Decimal(str(invoice.total_amount)) - paid_total)
    if outstanding < Decimal("0.00"):
        outstanding = Decimal("0.00")

    today = date.today()
    days_past_due = 0
    next_status = "issued"
    if outstanding == Decimal("0.00"):
        next_status = "paid"
    elif invoice.due_date < today:
        next_status = "overdue"
        days_past_due = (today - invoice.due_date).days

    if invoice.status != next_status:
        invoice.status = next_status
        db.add(invoice)
        db.flush()

    case = db.scalar(select(CollectionCase).where(CollectionCase.invoice_id == invoice.id))
    bucket = _aging_bucket(days_past_due)
    if next_status == "overdue" and outstanding > Decimal("0.00"):
        if case is None:
            case = CollectionCase(
                invoice_id=invoice.id,
                client_id=invoice.client_id,
                status="open",
                reason="invoice_overdue",
                days_past_due=days_past_due,
                aging_bucket=bucket,
                outstanding_amount=outstanding,
            )
            db.add(case)
            db.flush()
            _append_case_action(
                db,
                collection_case=case,
                action_type="case_opened",
                actor_id=actor_id,
                note="Invoice overdue case opened automatically",
                payload={"invoice_id": invoice.id, "days_past_due": days_past_due},
            )
        else:
            if case.status in {"resolved", "closed"}:
                case.status = "open"
                case.closed_at = None
                db.add(case)
                db.flush()
                _append_case_action(
                    db,
                    collection_case=case,
                    action_type="case_reopened",
                    actor_id=actor_id,
                    note="Collection case reopened due to outstanding overdue balance",
                    payload={"invoice_id": invoice.id},
                )
            case.days_past_due = days_past_due
            case.aging_bucket = bucket
            case.outstanding_amount = outstanding
            db.add(case)
            db.flush()
            if add_payment_action and payment_amount is not None:
                _append_case_action(
                    db,
                    collection_case=case,
                    action_type="payment_recorded",
                    actor_id=actor_id,
                    note="Payment recorded on overdue invoice",
                    payload={
                        "invoice_id": invoice.id,
                        "payment_amount": str(payment_amount),
                        "outstanding_amount": str(outstanding),
                    },
                )
        _set_client_delinquency(db, client_id=invoice.client_id, is_delinquent=True)
        return outstanding, case

    if case is not None:
        case.days_past_due = 0
        case.aging_bucket = "current"
        case.outstanding_amount = outstanding
        if case.status not in {"resolved", "closed"}:
            case.status = "resolved" if next_status == "paid" else "closed"
            case.closed_at = _now_utc()
            db.add(case)
            db.flush()
            _append_case_action(
                db,
                collection_case=case,
                action_type="case_resolved" if next_status == "paid" else "case_closed",
                actor_id=actor_id,
                note=(
                    "Collection case resolved after full settlement"
                    if next_status == "paid"
                    else "Collection case closed because invoice is not overdue"
                ),
                payload={
                    "invoice_id": invoice.id,
                    "invoice_status": next_status,
                    "outstanding_amount": str(outstanding),
                },
            )
        else:
            db.add(case)
            db.flush()

    has_overdue = (
        db.scalar(
            select(Invoice.id).where(
                Invoice.client_id == invoice.client_id,
                Invoice.status == "overdue",
            ).limit(1),
        )
        is not None
    )
    _set_client_delinquency(db, client_id=invoice.client_id, is_delinquent=has_overdue)
    return outstanding, case


def _sync_all_overdue_states(db: Session, *, actor_id: str = "collections-sync") -> None:
    invoices = list(
        db.scalars(
            select(Invoice).where(Invoice.status.in_(["issued", "overdue", "paid"])),
        ).all(),
    )
    for invoice in invoices:
        _sync_invoice_collection_state(db, invoice=invoice, actor_id=actor_id)
    db.commit()


def _build_payment_result(
    payment: Payment,
    *,
    replayed: bool,
    collection_case_status: CollectionCaseStatus | None,
) -> PaymentAllocationResult:
    return PaymentAllocationResult(
        payment=PaymentRead.model_validate(payment),
        invoice_status=cast(InvoiceStatus, payment.invoice_status_after),
        outstanding_amount=payment.outstanding_after,
        allocation_state=cast(AllocationState, payment.allocation_state),
        collection_case_status=collection_case_status,
        idempotency_replayed=replayed,
    )


def record_payment(
    db: Session,
    *,
    payload: PaymentCreate,
    idempotency_key: str,
    actor_id: str,
) -> PaymentAllocationResult:
    normalized_key = idempotency_key.strip()
    if len(normalized_key) < 8:
        raise ApiException(
            status_code=400,
            code="idempotency_key_invalid",
            message="Idempotency-Key header must contain at least 8 characters",
        )

    payload_hash = _request_hash(payload.model_dump(mode="json"))
    existing = db.scalar(select(Payment).where(Payment.idempotency_key == normalized_key))
    if existing is not None:
        if existing.request_hash != payload_hash:
            raise ApiException(
                status_code=409,
                code="idempotency_key_payload_conflict",
                message="Idempotency-Key was already used with a different payload",
            )
        case = db.scalar(
            select(CollectionCase).where(CollectionCase.invoice_id == existing.invoice_id),
        )
        return _build_payment_result(
            existing,
            replayed=True,
            collection_case_status=cast(CollectionCaseStatus | None, case.status if case else None),
        )

    invoice = _get_invoice(db, payload.invoice_id)
    if invoice.status == "void":
        raise ApiException(
            status_code=409,
            code="invoice_void",
            message="Void invoice cannot accept payments",
        )
    if invoice.client_id is None:
        raise ApiException(
            status_code=409,
            code="invoice_client_missing",
            message="Invoice client reference is missing",
        )

    outstanding_before = _money(
        Decimal(str(invoice.total_amount)) - _sum_posted_payments(db, invoice.id),
    )
    if outstanding_before <= Decimal("0.00"):
        raise ApiException(
            status_code=409,
            code="invoice_already_paid",
            message="Invoice is already settled",
        )
    if payload.amount > outstanding_before:
        raise ApiException(
            status_code=422,
            code="payment_exceeds_outstanding",
            message="Payment amount cannot exceed invoice outstanding balance",
            details={
                "outstanding_amount": str(outstanding_before),
                "payment_amount": str(payload.amount),
            },
        )

    payment = Payment(
        invoice_id=invoice.id,
        client_id=invoice.client_id,
        amount=_money(payload.amount),
        currency=invoice.currency,
        payment_date=payload.payment_date,
        method=payload.method,
        reference=payload.reference,
        note=payload.note,
        status="posted",
        idempotency_key=normalized_key,
        request_hash=payload_hash,
    )
    db.add(payment)
    db.flush()

    outstanding_after, case = _sync_invoice_collection_state(
        db,
        invoice=invoice,
        actor_id=actor_id,
        add_payment_action=True,
        payment_amount=payment.amount,
    )

    payment.outstanding_after = _money(outstanding_after)
    payment.invoice_status_after = invoice.status
    payment.allocation_state = "full" if outstanding_after == Decimal("0.00") else "partial"
    db.add(payment)
    db.commit()
    db.refresh(payment)

    logger.info(
        "collections.payment_recorded payment_id=%s invoice_id=%s amount=%s outstanding=%s",
        payment.id,
        payment.invoice_id,
        payment.amount,
        payment.outstanding_after,
    )
    return _build_payment_result(
        payment,
        replayed=False,
        collection_case_status=cast(CollectionCaseStatus | None, case.status if case else None),
    )


def approve_invoice_paid(
    db: Session,
    *,
    invoice_id: str,
    payload: InvoicePaymentApprovalRequest,
    idempotency_key: str,
    actor_id: str,
) -> PaymentAllocationResult:
    normalized_key = idempotency_key.strip()
    if len(normalized_key) < 8:
        raise ApiException(
            status_code=400,
            code="idempotency_key_invalid",
            message="Idempotency-Key header must contain at least 8 characters",
        )

    existing = db.scalar(select(Payment).where(Payment.idempotency_key == normalized_key))
    if existing is not None:
        if existing.invoice_id != invoice_id:
            raise ApiException(
                status_code=409,
                code="idempotency_key_payload_conflict",
                message="Idempotency-Key was already used with a different payload",
            )
        case = db.scalar(select(CollectionCase).where(CollectionCase.invoice_id == invoice_id))
        return _build_payment_result(
            existing,
            replayed=True,
            collection_case_status=cast(CollectionCaseStatus | None, case.status if case else None),
        )

    invoice = _get_invoice(db, invoice_id)
    if invoice.status == "void":
        raise ApiException(
            status_code=409,
            code="invoice_void",
            message="Void invoice cannot be approved as paid",
        )

    outstanding = _money(Decimal(str(invoice.total_amount)) - _sum_posted_payments(db, invoice_id))
    if outstanding <= Decimal("0.00"):
        raise ApiException(
            status_code=409,
            code="invoice_already_paid",
            message="Invoice is already settled",
        )

    approval_note = payload.note.strip() if payload.note else ""
    if not approval_note:
        approval_note = "Invoice marked as paid by operator approval"

    payment_payload = PaymentCreate(
        invoice_id=invoice_id,
        amount=outstanding,
        payment_date=payload.payment_date or date.today(),
        method=payload.method,
        reference=payload.reference,
        note=approval_note,
    )
    return record_payment(
        db,
        payload=payment_payload,
        idempotency_key=normalized_key,
        actor_id=actor_id,
    )


def list_payments(
    db: Session,
    *,
    page: int,
    size: int,
    invoice_id: str | None = None,
    client_id: str | None = None,
) -> tuple[list[Payment], int]:
    base_query = select(Payment)
    count_query = select(func.count()).select_from(Payment)

    if invoice_id:
        base_query = base_query.where(Payment.invoice_id == invoice_id)
        count_query = count_query.where(Payment.invoice_id == invoice_id)
    if client_id:
        base_query = base_query.where(Payment.client_id == client_id)
        count_query = count_query.where(Payment.client_id == client_id)

    total = int(db.scalar(count_query) or 0)
    records = db.scalars(
        base_query.order_by(Payment.created_at.desc()).offset((page - 1) * size).limit(size),
    ).all()
    return list(records), total


def list_collection_cases(
    db: Session,
    *,
    page: int,
    size: int,
    status: str | None = None,
    aging_bucket: str | None = None,
    client_id: str | None = None,
) -> tuple[list[CollectionCase], int]:
    _sync_all_overdue_states(db)

    base_query = select(CollectionCase)
    count_query = select(func.count()).select_from(CollectionCase)
    if status:
        base_query = base_query.where(CollectionCase.status == status)
        count_query = count_query.where(CollectionCase.status == status)
    if aging_bucket:
        base_query = base_query.where(CollectionCase.aging_bucket == aging_bucket)
        count_query = count_query.where(CollectionCase.aging_bucket == aging_bucket)
    if client_id:
        base_query = base_query.where(CollectionCase.client_id == client_id)
        count_query = count_query.where(CollectionCase.client_id == client_id)

    total = int(db.scalar(count_query) or 0)
    records = db.scalars(
        base_query.order_by(CollectionCase.updated_at.desc()).offset((page - 1) * size).limit(size),
    ).all()
    return list(records), total


def get_collection_case(db: Session, case_id: str) -> CollectionCase:
    case = db.get(CollectionCase, case_id)
    if case is None:
        raise ApiException(
            status_code=404,
            code="collection_case_not_found",
            message="Collection case was not found",
        )
    return case


def update_collection_case_status(
    db: Session,
    *,
    case_id: str,
    payload: CollectionCaseStatusUpdate,
    actor_id: str,
) -> CollectionCase:
    case = get_collection_case(db, case_id)
    previous_status = case.status
    case.status = payload.status
    if payload.status in {"resolved", "closed"}:
        case.closed_at = _now_utc()
    elif payload.status in {"open", "in_progress"}:
        case.closed_at = None
    db.add(case)
    db.flush()
    _append_case_action(
        db,
        collection_case=case,
        action_type="status_updated",
        actor_id=actor_id,
        note=payload.note,
        payload={"from_status": previous_status, "to_status": payload.status},
    )
    db.commit()
    db.refresh(case)
    return case


def create_collection_case_action(
    db: Session,
    *,
    case_id: str,
    payload: CollectionCaseActionCreate,
    actor_id: str,
) -> CollectionCaseAction:
    case = get_collection_case(db, case_id)
    if payload.action_type in {"reminder_sent", "warning_sent"} and case.status == "open":
        case.status = "in_progress"
        db.add(case)
        db.flush()

    action = _append_case_action(
        db,
        collection_case=case,
        action_type=payload.action_type,
        actor_id=actor_id,
        note=payload.note,
        payload={"case_id": case.id, "invoice_id": case.invoice_id},
    )
    db.commit()
    db.refresh(action)

    if payload.action_type in {"reminder_sent", "warning_sent"}:
        logger.info(
            "collections.event_hook action=%s case_id=%s invoice_id=%s",
            payload.action_type,
            case.id,
            case.invoice_id,
        )
    return action


def list_collection_case_actions(db: Session, *, case_id: str) -> list[CollectionCaseAction]:
    get_collection_case(db, case_id)
    return list(
        db.scalars(
            select(CollectionCaseAction)
            .where(CollectionCaseAction.case_id == case_id)
            .order_by(CollectionCaseAction.created_at.desc()),
        ).all(),
    )


def build_collections_overview(db: Session) -> CollectionOverviewRead:
    _sync_all_overdue_states(db)
    cases = list(db.scalars(select(CollectionCase)).all())

    bucket_totals: dict[AgingBucket, Decimal] = {
        "current": Decimal("0.00"),
        "1_30": Decimal("0.00"),
        "31_60": Decimal("0.00"),
        "61_90": Decimal("0.00"),
        "90_plus": Decimal("0.00"),
    }
    open_cases = 0
    in_progress_cases = 0
    overdue_invoices = 0
    total_outstanding = Decimal("0.00")

    for case in cases:
        if case.status == "open":
            open_cases += 1
        if case.status == "in_progress":
            in_progress_cases += 1
        if case.status in {"open", "in_progress"}:
            overdue_invoices += 1
            outstanding = _money(Decimal(str(case.outstanding_amount)))
            total_outstanding += outstanding
            bucket = (
                cast(AgingBucket, case.aging_bucket)
                if case.aging_bucket in bucket_totals
                else "90_plus"
            )
            bucket_totals[bucket] = _money(bucket_totals[bucket] + outstanding)

    return CollectionOverviewRead(
        open_cases=open_cases,
        in_progress_cases=in_progress_cases,
        overdue_invoices=overdue_invoices,
        total_outstanding_amount=_money(total_outstanding),
        bucket_totals={key: _money(value) for key, value in bucket_totals.items()},
    )
