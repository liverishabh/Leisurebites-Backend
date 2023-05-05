import enum

from sqlalchemy import Column, BIGINT, NUMERIC, String, Enum, DateTime, ForeignKey
from sqlalchemy.sql.expression import text

from app.models import BaseModel


class PaymentMethod(str, enum.Enum):
    cod = "cod"
    pg = "pg"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Payment(BaseModel):
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    booking_id = Column(BIGINT, ForeignKey('booking.id'), nullable=False)
    amount = Column(NUMERIC(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    transaction_code = Column(String(50), unique=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    pg_order_id = Column(String(50))

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
