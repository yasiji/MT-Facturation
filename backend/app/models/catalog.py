import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "service_category",
            "version",
            name="uq_offers_name_category_version",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    service_category: Mapped[str] = mapped_column(String(32), nullable=False)
    service_type: Mapped[str] = mapped_column(String(32), nullable=False)
    mobile_data_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mobile_calls_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    internet_access_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    internet_fiber_speed_mbps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    internet_adsl_speed_mbps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    internet_landline_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    internet_tv_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    landline_national_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    landline_international_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    landline_phone_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    monthly_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    activation_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
