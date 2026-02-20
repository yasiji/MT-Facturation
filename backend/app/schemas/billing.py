from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

InvoiceStatus = Literal["issued", "paid", "overdue", "void"]
InvoiceLineType = Literal["recurring", "activation"]


class BillingRunRequest(BaseModel):
    period_start: date
    period_end: date
    due_days: int = Field(default=15, ge=1, le=90)
    tax_rate: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), le=Decimal("1.00"))

    @model_validator(mode="after")
    def validate_dates(self) -> "BillingRunRequest":
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot be earlier than period_start")
        return self


class BillingRunResult(BaseModel):
    billing_run_id: str
    period_start: date
    period_end: date
    invoice_count: int
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    invoice_ids: list[str]
    idempotency_replayed: bool = False


class InvoiceLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    contract_id: str
    line_type: InvoiceLineType
    description: str
    quantity: int
    unit_amount: Decimal
    line_total: Decimal
    created_at: datetime


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    billing_run_id: str
    client_id: str
    period_start: date
    period_end: date
    due_date: date
    status: InvoiceStatus
    currency: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    issued_at: datetime
    pdf_file_name: str | None
    created_at: datetime
    updated_at: datetime


class InvoiceDetailRead(InvoiceRead):
    lines: list[InvoiceLineRead]
