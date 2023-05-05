import enum

from sqlalchemy import Column, BIGINT, NUMERIC, String, Text, Boolean, Enum, DateTime
from sqlalchemy.sql.expression import text

from app.models import BaseModel


class PromoCodeStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class PromoCodeType(str, enum.Enum):
    discount_flat = "discount_flat"
    discount_percent = "discount_percent"


class PromoCode(BaseModel):
    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    code = Column(String(100), nullable=False, index=True)
    promo_code_type = Column(Enum(PromoCodeType), nullable=False)
    description = Column(Text())
    min_purchase_amount = Column(NUMERIC(10, 2), nullable=False)
    max_discount_amount = Column(NUMERIC(10, 2), nullable=False)
    flat_discount_amount = Column(NUMERIC(10, 2), nullable=False)
    discount_percent = Column(NUMERIC(10, 2), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    visible = Column(Boolean(), nullable=False)
    status = Column(Enum(PromoCodeStatus), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
