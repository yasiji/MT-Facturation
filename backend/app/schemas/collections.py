from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AgingBucket = Literal["current", "1_30", "31_60", "61_90", "90_plus"]
CollectionCaseStatus = Literal["open", "in_progress", "resolved", "closed"]
CollectionActionType = Literal[
    "case_opened",
    "case_reopened",
    "payment_recorded",
    "status_updated",
    "reminder_sent",
    "warning_sent",
    "note",
    "case_resolved",
    "case_closed",
]
PaymentStatus = Literal["posted", "reversed"]
PaymentMethod = Literal["cash", "card", "bank_transfer", "wallet", "other"]
InvoiceStatus = Literal["issued", "paid", "overdue", "void"]
AllocationState = Literal["partial", "full"]


class PaymentCreate(BaseModel):
    invoice_id: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    payment_date: date
    method: PaymentMethod = "other"
    reference: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=1200)


class InvoicePaymentApprovalRequest(BaseModel):
    payment_date: date | None = None
    method: PaymentMethod = "other"
    reference: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=1200)


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    client_id: str
    amount: Decimal
    currency: str
    payment_date: date
    method: PaymentMethod
    reference: str | None
    note: str | None
    status: PaymentStatus
    created_at: datetime


class PaymentAllocationResult(BaseModel):
    payment: PaymentRead
    invoice_status: InvoiceStatus
    outstanding_amount: Decimal
    allocation_state: AllocationState
    collection_case_status: CollectionCaseStatus | None
    idempotency_replayed: bool = False


class CollectionCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    client_id: str
    status: CollectionCaseStatus
    reason: str
    days_past_due: int
    aging_bucket: AgingBucket
    outstanding_amount: Decimal
    opened_at: datetime
    last_action_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CollectionCaseStatusUpdate(BaseModel):
    status: CollectionCaseStatus
    note: str | None = Field(default=None, max_length=1200)


class CollectionCaseActionCreate(BaseModel):
    action_type: CollectionActionType
    note: str | None = Field(default=None, max_length=1200)

    @model_validator(mode="after")
    def validate_action_note(self) -> "CollectionCaseActionCreate":
        if self.action_type == "note" and not (self.note and self.note.strip()):
            raise ValueError("note action requires note text")
        return self


class CollectionCaseActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    action_type: CollectionActionType
    actor_id: str | None
    note: str | None
    payload: str
    created_at: datetime


class CollectionOverviewRead(BaseModel):
    open_cases: int
    in_progress_cases: int
    overdue_invoices: int
    total_outstanding_amount: Decimal
    bucket_totals: dict[AgingBucket, Decimal]
