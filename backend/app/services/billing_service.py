import hashlib
import json
import logging
import os
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from pathlib import Path
from typing import Any

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
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.errors import ApiException
from app.core.settings import get_settings
from app.models.billing import BillingRun, Invoice, InvoiceLine
from app.models.catalog import Offer
from app.models.contract import Contract
from app.models.customer import Client
from app.schemas.billing import BillingRunRequest, BillingRunResult

logger = logging.getLogger("mt_facturation.billing")
MONEY_QUANT = Decimal("0.01")


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _request_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _invoice_documents_root() -> Path:
    configured = get_settings().invoice_documents_dir.strip()
    base = Path(configured)
    if base.is_absolute():
        return base
    return Path(os.getcwd()) / base


def _is_contract_billable(contract: Contract, *, period_start: date, period_end: date) -> bool:
    if contract.status != "active":
        return False
    if contract.start_date > period_end:
        return False
    if contract.end_date and contract.end_date < period_start:
        return False
    return True


def _build_invoice_pdf(*, invoice: Invoice, client: Client, lines: list[InvoiceLine]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=f"Invoice {invoice.id}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=19,
        textColor=colors.HexColor("#10344E"),
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "InvoiceSection",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#0A5B63"),
        spaceAfter=6,
        spaceBefore=8,
    )
    text_style = ParagraphStyle(
        "InvoiceBody",
        parent=styles["BodyText"],
        fontSize=9.7,
        leading=13,
        textColor=colors.HexColor("#1D2E3E"),
    )
    muted = ParagraphStyle(
        "InvoiceMuted",
        parent=text_style,
        fontSize=9,
        textColor=colors.HexColor("#4D6071"),
    )

    story: list[Any] = []
    story.append(Paragraph("MT FACTURATION", muted))
    story.append(Paragraph("Monthly Invoice", title_style))
    invoice_meta_block = (
        f"<b>Invoice ID:</b> {invoice.id}<br/>"
        f"<b>Issue Date:</b> {invoice.issued_at.date().isoformat()}<br/>"
        f"<b>Due Date:</b> {invoice.due_date.isoformat()}<br/>"
        f"<b>Billing Period:</b> {invoice.period_start.isoformat()} "
        f"to {invoice.period_end.isoformat()}"
    )
    story.append(
        Paragraph(
            invoice_meta_block,
            text_style,
        ),
    )
    story.append(Spacer(1, 8))

    client_table = Table(
        [
            ["Billed To", client.full_name],
            ["CIN", client.cin or "-"],
            ["Email", client.email or "-"],
            ["Phone", client.phone or "-"],
            ["Address", client.address or "-"],
        ],
        colWidths=[40 * mm, 126 * mm],
    )
    client_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4F7")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1D3043")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BFD1DA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ],
        ),
    )
    story.append(client_table)

    story.append(Paragraph("Invoice Lines", section_style))
    line_rows: list[list[str]] = [["Description", "Type", "Qty", "Unit (MAD)", "Total (MAD)"]]
    for line in lines:
        line_rows.append(
            [
                line.description,
                line.line_type,
                str(line.quantity),
                f"{line.unit_amount:.2f}",
                f"{line.line_total:.2f}",
            ],
        )
    lines_table = Table(
        line_rows,
        colWidths=[82 * mm, 26 * mm, 14 * mm, 24 * mm, 24 * mm],
    )
    lines_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D7EDF1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F3448")),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BDD0DA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FCFD")]),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
        ),
    )
    story.append(lines_table)

    story.append(Spacer(1, 8))
    totals_table = Table(
        [
            ["Subtotal", f"{invoice.subtotal_amount:.2f} {invoice.currency}"],
            ["Tax", f"{invoice.tax_amount:.2f} {invoice.currency}"],
            ["Total", f"{invoice.total_amount:.2f} {invoice.currency}"],
        ],
        colWidths=[40 * mm, 36 * mm],
        hAlign="RIGHT",
    )
    totals_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF6F8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BFD1DA")),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ],
        ),
    )
    story.append(totals_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("This invoice is system-generated and immutable once issued.", muted))

    def draw_frame(canvas_obj: Any, _doc: Any) -> None:
        width, height = A4
        canvas_obj.saveState()
        canvas_obj.setStrokeColor(colors.HexColor("#A2C9D8"))
        canvas_obj.setLineWidth(1.0)
        canvas_obj.roundRect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm, 6 * mm, 1, 0)
        canvas_obj.setFillColor(colors.HexColor("#0D5C63"))
        canvas_obj.rect(12 * mm, height - 24 * mm, width - 24 * mm, 8 * mm, stroke=0, fill=1)
        canvas_obj.restoreState()

    document.build(story, onFirstPage=draw_frame, onLaterPages=draw_frame)
    return buffer.getvalue()


def _write_invoice_pdf(db: Session, invoice: Invoice, lines: list[InvoiceLine]) -> None:
    client = db.get(Client, invoice.client_id)
    if client is None:
        raise ApiException(
            status_code=409,
            code="invoice_client_missing",
            message="Invoice client record is missing",
        )

    pdf_bytes = _build_invoice_pdf(invoice=invoice, client=client, lines=lines)
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    root = _invoice_documents_root()
    root.mkdir(parents=True, exist_ok=True)
    file_name = f"invoice-{invoice.id}.pdf"
    file_path = root / file_name
    file_path.write_bytes(pdf_bytes)

    invoice.pdf_file_name = file_name
    invoice.pdf_file_path = str(file_path)
    invoice.pdf_sha256 = digest
    db.add(invoice)
    db.flush()


def _build_line_description(offer: Offer, *, line_type: str) -> str:
    if line_type == "activation":
        return f"{offer.name} activation fee"
    return f"{offer.name} monthly recurring fee"


def _build_run_result(run: BillingRun) -> BillingRunResult:
    try:
        summary_payload = json.loads(run.summary_payload)
    except json.JSONDecodeError:
        summary_payload = {}
    invoice_ids = summary_payload.get("invoice_ids", [])
    if not isinstance(invoice_ids, list):
        invoice_ids = []
    return BillingRunResult(
        billing_run_id=run.id,
        period_start=run.period_start,
        period_end=run.period_end,
        invoice_count=run.invoice_count,
        subtotal_amount=run.subtotal_amount,
        tax_amount=run.tax_amount,
        total_amount=run.total_amount,
        invoice_ids=[str(item) for item in invoice_ids],
    )


def run_billing_cycle(
    db: Session,
    *,
    payload: BillingRunRequest,
    idempotency_key: str,
) -> BillingRunResult:
    normalized_key = idempotency_key.strip()
    if len(normalized_key) < 8:
        raise ApiException(
            status_code=400,
            code="idempotency_key_invalid",
            message="Idempotency-Key header must contain at least 8 characters",
        )

    request_payload = payload.model_dump(mode="json")
    payload_hash = _request_hash(request_payload)
    existing = db.scalar(select(BillingRun).where(BillingRun.idempotency_key == normalized_key))
    if existing:
        if existing.request_hash != payload_hash:
            raise ApiException(
                status_code=409,
                code="idempotency_key_payload_conflict",
                message="Idempotency-Key was already used with a different payload",
            )
        return _build_run_result(existing).model_copy(update={"idempotency_replayed": True})

    contracts = list(
        db.scalars(
            select(Contract).where(
                Contract.status == "active",
                Contract.start_date <= payload.period_end,
                (Contract.end_date.is_(None) | (Contract.end_date >= payload.period_start)),
            ),
        ).all(),
    )
    offer_ids = {contract.offer_id for contract in contracts}
    offers = {
        offer.id: offer
        for offer in db.scalars(select(Offer).where(Offer.id.in_(offer_ids))).all()
    } if offer_ids else {}

    run = BillingRun(
        period_start=payload.period_start,
        period_end=payload.period_end,
        status="completed",
        idempotency_key=normalized_key,
        request_hash=payload_hash,
        summary_payload="{}",
    )
    db.add(run)
    db.flush()

    grouped_contracts: dict[str, list[Contract]] = {}
    for contract in contracts:
        if not _is_contract_billable(
            contract,
            period_start=payload.period_start,
            period_end=payload.period_end,
        ):
            continue
        grouped_contracts.setdefault(contract.client_id, []).append(contract)

    all_invoice_ids: list[str] = []
    run_subtotal = Decimal("0.00")
    run_tax = Decimal("0.00")
    run_total = Decimal("0.00")

    for client_id, client_contracts in grouped_contracts.items():
        due_date = payload.period_end + timedelta(days=payload.due_days)
        invoice = Invoice(
            billing_run_id=run.id,
            client_id=client_id,
            period_start=payload.period_start,
            period_end=payload.period_end,
            due_date=due_date,
            status="issued",
            currency="MAD",
            issued_at=_utc_now(),
        )
        db.add(invoice)
        db.flush()

        line_items: list[InvoiceLine] = []
        for contract in client_contracts:
            offer = offers.get(contract.offer_id)
            if offer is None:
                continue

            recurring_amount = _money(Decimal(str(offer.monthly_fee)))
            recurring_line = InvoiceLine(
                invoice_id=invoice.id,
                contract_id=contract.id,
                line_type="recurring",
                description=_build_line_description(offer, line_type="recurring"),
                quantity=1,
                unit_amount=recurring_amount,
                line_total=recurring_amount,
            )
            db.add(recurring_line)
            line_items.append(recurring_line)

            activation_amount = _money(Decimal(str(offer.activation_fee)))
            if (
                activation_amount > Decimal("0.00")
                and payload.period_start <= contract.start_date <= payload.period_end
            ):
                activation_line = InvoiceLine(
                    invoice_id=invoice.id,
                    contract_id=contract.id,
                    line_type="activation",
                    description=_build_line_description(offer, line_type="activation"),
                    quantity=1,
                    unit_amount=activation_amount,
                    line_total=activation_amount,
                )
                db.add(activation_line)
                line_items.append(activation_line)

        if not line_items:
            db.delete(invoice)
            continue

        subtotal = _money(sum((line.line_total for line in line_items), Decimal("0.00")))
        tax_amount = _money(subtotal * payload.tax_rate)
        total = _money(subtotal + tax_amount)
        invoice.subtotal_amount = subtotal
        invoice.tax_amount = tax_amount
        invoice.total_amount = total
        db.add(invoice)
        db.flush()
        _write_invoice_pdf(db, invoice, line_items)

        all_invoice_ids.append(invoice.id)
        run_subtotal += subtotal
        run_tax += tax_amount
        run_total += total

    run.invoice_count = len(all_invoice_ids)
    run.subtotal_amount = _money(run_subtotal)
    run.tax_amount = _money(run_tax)
    run.total_amount = _money(run_total)
    run.summary_payload = json.dumps(
        {
            "invoice_ids": all_invoice_ids,
            "invoice_count": run.invoice_count,
        },
        sort_keys=True,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    logger.info(
        "billing.run_completed run_id=%s period=%s..%s invoice_count=%s",
        run.id,
        run.period_start.isoformat(),
        run.period_end.isoformat(),
        run.invoice_count,
    )
    return _build_run_result(run)


def list_invoices(
    db: Session,
    *,
    page: int,
    size: int,
    client_id: str | None = None,
    service_category: str | None = None,
    offer_id: str | None = None,
) -> tuple[list[Invoice], int]:
    base_query = select(Invoice)
    if client_id:
        base_query = base_query.where(Invoice.client_id == client_id)

    if service_category or offer_id:
        line_query = (
            select(InvoiceLine.invoice_id)
            .join(Contract, InvoiceLine.contract_id == Contract.id)
            .join(Offer, Contract.offer_id == Offer.id)
        )
        if service_category:
            line_query = line_query.where(Offer.service_category == service_category)
        if offer_id:
            line_query = line_query.where(Offer.id == offer_id)
        base_query = base_query.where(Invoice.id.in_(line_query))

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    records = db.scalars(
        base_query.order_by(Invoice.issued_at.desc()).offset((page - 1) * size).limit(size),
    ).all()
    return list(records), int(total)


def get_invoice(db: Session, invoice_id: str) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise ApiException(
            status_code=404,
            code="invoice_not_found",
            message="Invoice was not found",
        )
    return invoice


def get_invoice_lines(db: Session, invoice_id: str) -> list[InvoiceLine]:
    get_invoice(db, invoice_id)
    return list(
        db.scalars(
            select(InvoiceLine)
            .where(InvoiceLine.invoice_id == invoice_id)
            .order_by(InvoiceLine.created_at.asc()),
        ).all(),
    )


def get_invoice_for_download(db: Session, invoice_id: str) -> Invoice:
    invoice = get_invoice(db, invoice_id)
    if invoice.pdf_file_path and Path(invoice.pdf_file_path).exists():
        return invoice

    lines = get_invoice_lines(db, invoice_id)
    if not lines:
        raise ApiException(
            status_code=409,
            code="invoice_lines_missing",
            message="Invoice has no lines and cannot generate PDF",
        )
    _write_invoice_pdf(db, invoice, lines)
    db.commit()
    db.refresh(invoice)
    return invoice
