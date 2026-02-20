from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

OfferServiceCategory = Literal["mobile", "internet", "landline"]
OfferServiceType = Literal["mobile", "fiber", "adsl", "landline"]
InternetAccessType = Literal["fiber", "adsl"]
OfferStatus = Literal["active", "retired"]


class OfferCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    service_category: OfferServiceCategory
    version: int = Field(default=1, ge=1)
    monthly_fee: Decimal = Field(gt=Decimal("0"))
    activation_fee: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    status: OfferStatus = "active"
    valid_from: date
    valid_to: date | None = None
    mobile_data_gb: int | None = Field(default=None, ge=1)
    mobile_calls_hours: int | None = Field(default=None, ge=1)
    internet_access_type: InternetAccessType | None = None
    internet_fiber_speed_mbps: int | None = Field(default=None, ge=1)
    internet_adsl_speed_mbps: int | None = Field(default=None, ge=1)
    internet_landline_included: bool = False
    internet_tv_included: bool = False
    landline_national_included: bool = False
    landline_international_hours: int | None = Field(default=None, ge=1)
    landline_phone_hours: int | None = Field(default=None, ge=1)
    service_type: OfferServiceType | None = None

    @model_validator(mode="after")
    def validate_offer_components(self) -> "OfferCreate":
        self.name = self.name.strip()
        if len(self.name) < 2:
            raise ValueError("name must have at least 2 non-space characters")
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be earlier than valid_from")

        if self.service_category == "mobile":
            if self.mobile_data_gb is None and self.mobile_calls_hours is None:
                raise ValueError("Mobile offers require at least one component: data or calls")
            self.internet_access_type = None
            self.internet_fiber_speed_mbps = None
            self.internet_adsl_speed_mbps = None
            self.internet_landline_included = False
            self.internet_tv_included = False
            self.landline_national_included = False
            self.landline_international_hours = None
            self.landline_phone_hours = None
            self.service_type = "mobile"
            return self

        if self.service_category == "internet":
            if self.internet_access_type is None:
                raise ValueError("Internet offers require internet_access_type (fiber or adsl)")
            if self.internet_access_type == "fiber":
                if self.internet_fiber_speed_mbps is None:
                    raise ValueError("Fiber internet offers require internet_fiber_speed_mbps")
                if self.internet_adsl_speed_mbps is not None:
                    raise ValueError("Internet offers must choose either fiber or adsl, not both")
                self.service_type = "fiber"
            else:
                if self.internet_adsl_speed_mbps is None:
                    raise ValueError("ADSL internet offers require internet_adsl_speed_mbps")
                if self.internet_fiber_speed_mbps is not None:
                    raise ValueError("Internet offers must choose either fiber or adsl, not both")
                self.service_type = "adsl"

            self.mobile_data_gb = None
            self.mobile_calls_hours = None
            self.internet_landline_included = True
            self.landline_national_included = False
            self.landline_international_hours = None
            self.landline_phone_hours = None
            return self

        if (
            not self.landline_national_included
            and self.landline_international_hours is None
            and self.landline_phone_hours is None
        ):
            raise ValueError(
                "Landline offers require at least one component: national, international, or phone",
            )
        self.mobile_data_gb = None
        self.mobile_calls_hours = None
        self.internet_access_type = None
        self.internet_fiber_speed_mbps = None
        self.internet_adsl_speed_mbps = None
        self.internet_landline_included = False
        self.internet_tv_included = False
        self.service_type = "landline"
        return self


class OfferUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    service_category: OfferServiceCategory | None = None
    version: int | None = Field(default=None, ge=1)
    monthly_fee: Decimal | None = Field(default=None, gt=Decimal("0"))
    activation_fee: Decimal | None = Field(default=None, ge=Decimal("0"))
    status: OfferStatus | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    mobile_data_gb: int | None = Field(default=None, ge=1)
    mobile_calls_hours: int | None = Field(default=None, ge=1)
    internet_access_type: InternetAccessType | None = None
    internet_fiber_speed_mbps: int | None = Field(default=None, ge=1)
    internet_adsl_speed_mbps: int | None = Field(default=None, ge=1)
    internet_landline_included: bool | None = None
    internet_tv_included: bool | None = None
    landline_national_included: bool | None = None
    landline_international_hours: int | None = Field(default=None, ge=1)
    landline_phone_hours: int | None = Field(default=None, ge=1)


class OfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    service_category: OfferServiceCategory
    service_type: OfferServiceType
    version: int
    monthly_fee: Decimal
    activation_fee: Decimal
    status: OfferStatus
    valid_from: date
    valid_to: date | None
    mobile_data_gb: int | None
    mobile_calls_hours: int | None
    internet_access_type: InternetAccessType | None
    internet_fiber_speed_mbps: int | None
    internet_adsl_speed_mbps: int | None
    internet_landline_included: bool
    internet_tv_included: bool
    landline_national_included: bool
    landline_international_hours: int | None
    landline_phone_hours: int | None
    created_at: datetime
    updated_at: datetime


class OfferCategoryRead(BaseModel):
    service_category: OfferServiceCategory
    offers: list[OfferRead]
