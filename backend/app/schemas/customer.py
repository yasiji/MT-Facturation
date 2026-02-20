from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ClientType = Literal["individual", "business"]
ClientStatus = Literal["active", "suspended", "terminated"]
SubscriberServiceType = Literal["mobile", "fiber", "adsl", "tv", "addon", "landline"]
SubscriberStatus = Literal["active", "suspended", "terminated"]


class ClientCreate(BaseModel):
    cin: str | None = Field(default=None, min_length=4, max_length=40)
    client_type: ClientType
    full_name: str = Field(min_length=2, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    status: ClientStatus = "active"

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class ClientUpdate(BaseModel):
    cin: str | None = Field(default=None, min_length=4, max_length=40)
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    status: ClientStatus | None = None

    @field_validator("cin")
    @classmethod
    def normalize_cin(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) < 4:
            raise ValueError("CIN must have at least 4 non-space characters")
        return normalized


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cin: str | None
    client_type: ClientType
    full_name: str
    address: str | None
    email: str | None
    phone: str | None
    is_delinquent: bool
    delinquent_since: datetime | None
    status: ClientStatus
    created_at: datetime
    updated_at: datetime


class SubscriberCreate(BaseModel):
    service_type: SubscriberServiceType
    service_identifier: str = Field(min_length=3, max_length=100)
    status: SubscriberStatus = "active"

    @field_validator("service_identifier")
    @classmethod
    def normalize_service_identifier(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 3:
            raise ValueError("Service identifier must have at least 3 non-space characters")
        return normalized


class SubscriberUpdate(BaseModel):
    status: SubscriberStatus | None = None


class SubscriberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    service_type: SubscriberServiceType
    service_identifier: str
    status: SubscriberStatus
    created_at: datetime
    updated_at: datetime
