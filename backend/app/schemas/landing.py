from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.catalog import OfferServiceCategory, OfferServiceType
from app.schemas.contract import ContractRead, ProvisioningMode

LandingFlowType = Literal[
    "subscribe_new_service",
    "upgrade_or_downgrade_existing_service",
    "check_billing_and_download_invoices",
]
LandingDraftStatus = Literal["in_progress", "submitted", "cancelled"]
MobileNumberMode = Literal["use_existing", "assign_new"]


class LandingOfferSummary(BaseModel):
    id: str
    name: str
    service_category: OfferServiceCategory
    service_type: OfferServiceType
    monthly_fee: Decimal
    activation_fee: Decimal
    status: str
    valid_from: date
    valid_to: date | None


class LandingOfferCategory(BaseModel):
    service_category: OfferServiceCategory
    offers: list[LandingOfferSummary]


class LandingBootstrapResponse(BaseModel):
    flow_options: list[LandingFlowType]
    services: list[OfferServiceCategory]
    offer_categories: list[LandingOfferCategory]


class LandingDraftCreate(BaseModel):
    flow_type: LandingFlowType
    step: str = Field(min_length=2, max_length=64)
    cin: str | None = Field(default=None, min_length=4, max_length=40)
    payload: dict[str, Any] = Field(default_factory=dict)
    status: LandingDraftStatus = "in_progress"

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class LandingDraftUpdate(BaseModel):
    step: str | None = Field(default=None, min_length=2, max_length=64)
    cin: str | None = Field(default=None, min_length=4, max_length=40)
    payload: dict[str, Any] | None = None
    status: LandingDraftStatus | None = None

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class LandingDraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    flow_type: LandingFlowType
    step: str
    cin: str | None
    payload: dict[str, Any]
    status: LandingDraftStatus
    created_at: datetime
    updated_at: datetime


class LandingNewSubscriptionSubmitRequest(BaseModel):
    service_category: OfferServiceCategory
    offer_id: str
    cin: str = Field(min_length=4, max_length=40)
    full_name: str = Field(min_length=2, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=40)
    contract_start_date: date
    commitment_months: int | None = Field(default=None, ge=1, le=60)
    mobile_number_mode: MobileNumberMode | None = None
    existing_mobile_local_number: str | None = Field(default=None, max_length=40)
    requested_mobile_local_number: str | None = Field(default=None, max_length=40)
    home_landline_local_number: str | None = Field(default=None, max_length=40)

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized

    @field_validator("existing_mobile_local_number")
    @classmethod
    def normalize_mobile_local_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("requested_mobile_local_number")
    @classmethod
    def normalize_requested_mobile_local_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("home_landline_local_number")
    @classmethod
    def normalize_home_landline_local_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_mobile_rules(self) -> "LandingNewSubscriptionSubmitRequest":
        if self.service_category == "mobile":
            if self.mobile_number_mode is None:
                raise ValueError("mobile_number_mode is required for mobile service")
            if self.mobile_number_mode == "use_existing":
                if not self.existing_mobile_local_number:
                    raise ValueError(
                        "existing_mobile_local_number is required "
                        "when mobile_number_mode=use_existing",
                    )
                if self.requested_mobile_local_number is not None:
                    raise ValueError(
                        "requested_mobile_local_number is not allowed "
                        "when mobile_number_mode=use_existing",
                    )
            if self.mobile_number_mode == "assign_new" and self.existing_mobile_local_number:
                raise ValueError(
                    "existing_mobile_local_number is not allowed "
                    "when mobile_number_mode=assign_new",
                )
            if self.home_landline_local_number is not None:
                raise ValueError("home_landline_local_number is only allowed for internet/landline")
            return self

        if (
            self.mobile_number_mode is not None
            or self.existing_mobile_local_number is not None
            or self.requested_mobile_local_number is not None
        ):
            raise ValueError(
                "mobile number selection fields are only allowed for mobile service",
            )
        if not self.home_landline_local_number:
            raise ValueError(
                "home_landline_local_number is required for internet and landline services",
            )
        return self


class LandingPlanChangeSubmitRequest(BaseModel):
    cin: str = Field(min_length=4, max_length=40)
    source_contract_id: str
    target_offer_id: str
    contract_start_date: date
    commitment_months: int | None = Field(default=None, ge=1, le=60)

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class LandingCinLookupRequest(BaseModel):
    cin: str = Field(min_length=4, max_length=40)

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class LandingLookupVerificationResponse(BaseModel):
    cin: str
    masked_contact: str
    lookup_token: str
    expires_at: datetime


class LandingContractDocumentLinkRequest(BaseModel):
    cin: str = Field(min_length=4, max_length=40)

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class LandingContractDocumentLinkResponse(BaseModel):
    contract_id: str
    document_download_url: str


class LandingSubmitResult(BaseModel):
    contract: ContractRead
    client_id: str
    client_cin: str
    service_identifier: str
    created_client: bool
    created_subscriber: bool
    provisioning_mode: ProvisioningMode
    idempotency_replayed: bool = False
    document_download_url: str | None = None


class LandingClientSummary(BaseModel):
    id: str
    cin: str
    full_name: str
    email: str | None
    address: str | None
    phone: str | None


class LandingCurrentSubscriptionRead(BaseModel):
    contract_id: str
    subscriber_id: str
    service_identifier: str
    service_category: OfferServiceCategory
    service_type: OfferServiceType
    current_offer: LandingOfferSummary
    eligible_offers: list[LandingOfferSummary]


class LandingClientLookupResponse(BaseModel):
    client: LandingClientSummary
    subscriptions: list[LandingCurrentSubscriptionRead]


class LandingInvoiceSummary(BaseModel):
    invoice_id: str
    period_start: date
    period_end: date
    due_date: date
    issued_at: datetime
    status: str
    currency: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    document_download_url: str


class LandingInvoiceLookupResponse(BaseModel):
    client: LandingClientSummary
    invoices: list[LandingInvoiceSummary]
