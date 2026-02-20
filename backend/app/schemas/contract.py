from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.customer import ClientType, SubscriberServiceType

ContractStatus = Literal["draft", "active", "suspended", "terminated"]
ProvisioningIntent = Literal["auto", "upgrade", "new_line"]
ProvisioningMode = Literal["upgrade_existing_contract", "new_contract"]


class ProvisionClientInput(BaseModel):
    cin: str | None = Field(default=None, min_length=4, max_length=40)
    client_type: ClientType
    full_name: str = Field(min_length=2, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)


class ProvisionSubscriberInput(BaseModel):
    service_identifier: str | None = Field(default=None, min_length=3, max_length=100)
    service_type: SubscriberServiceType | None = None


class ContractProvisionRequest(BaseModel):
    offer_id: str
    contract_start_date: date
    commitment_months: int | None = Field(default=None, ge=1, le=60)
    end_date: date | None = None
    auto_activate: bool = True
    client_id: str | None = None
    client: ProvisionClientInput | None = None
    subscriber_id: str | None = None
    subscriber: ProvisionSubscriberInput | None = None
    provisioning_intent: ProvisioningIntent = "auto"
    target_contract_id: str | None = None

    @model_validator(mode="after")
    def validate_inputs(self) -> "ContractProvisionRequest":
        if not self.client_id and self.client is None:
            raise ValueError("Either client_id or client payload must be provided")
        if self.client_id and self.client is not None:
            raise ValueError("Provide either client_id or client payload, not both")
        if self.subscriber_id and self.subscriber is not None:
            raise ValueError("Provide either subscriber_id or subscriber payload, not both")
        if self.provisioning_intent == "new_line" and self.target_contract_id is not None:
            raise ValueError("target_contract_id is only valid for upgrade provisioning intent")
        if self.provisioning_intent == "new_line" and self.subscriber_id is not None:
            raise ValueError("new_line provisioning does not allow subscriber_id reuse")
        if self.provisioning_intent == "upgrade" and self.client is not None:
            raise ValueError("Upgrade provisioning requires an existing client_id")
        if self.provisioning_intent == "upgrade" and self.client_id is None:
            raise ValueError("Upgrade provisioning requires client_id")
        if self.provisioning_intent == "upgrade" and (
            self.subscriber_id is not None or self.subscriber is not None
        ):
            raise ValueError(
                "Upgrade provisioning does not accept subscriber creation/reuse payload",
            )
        if self.end_date and self.end_date < self.contract_start_date:
            raise ValueError("end_date cannot be earlier than contract_start_date")
        return self


class ContractCreate(BaseModel):
    client_id: str
    subscriber_id: str
    offer_id: str
    contract_start_date: date
    commitment_months: int | None = Field(default=None, ge=1, le=60)
    end_date: date | None = None
    status: ContractStatus = "draft"

    @model_validator(mode="after")
    def validate_dates(self) -> "ContractCreate":
        if self.end_date and self.end_date < self.contract_start_date:
            raise ValueError("end_date cannot be earlier than contract_start_date")
        return self


class ContractStatusUpdate(BaseModel):
    status: ContractStatus


class ContractOfferUpdate(BaseModel):
    offer_id: str


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    subscriber_id: str
    offer_id: str
    status: ContractStatus
    start_date: date
    end_date: date | None
    commitment_months: int | None
    activated_at: datetime | None
    terminated_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ContractAuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_id: str
    event_type: str
    actor_id: str | None
    details: str
    created_at: datetime


class ContractProvisionResult(BaseModel):
    contract: ContractRead
    created_client: bool
    created_subscriber: bool
    provisioning_mode: ProvisioningMode
