import enum

from sqlalchemy import Column, BIGINT, INT, NUMERIC, String, Enum, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.models import BaseModel


class BookingType(str, enum.Enum):
    experience = "experience"
    artist = "artist"


class BookingStatus(str, enum.Enum):
    pending_with_artist = "pending_with_artist"  # only for artist booking
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    failed = "failed"


class BookingCancelledBy(str, enum.Enum):
    customer = "customer"
    supplier = "supplier"


class Booking(BaseModel):
    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    booking_uuid = Column(String(30), unique=True, nullable=False)
    booking_type = Column(Enum(BookingType), nullable=False)
    customer_id = Column(BIGINT, ForeignKey("customer.id"), nullable=False)
    supplier_id = Column(INT, ForeignKey("supplier.id"), nullable=False)
    experience_slot_id = Column(BIGINT, ForeignKey("experience_slot.id"))
    artist_slot_id = Column(BIGINT, ForeignKey("artist_slot.id"))
    no_of_guests = Column(INT, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False)

    sub_total = Column(NUMERIC(10, 2), nullable=False)
    service_tax = Column(NUMERIC(10, 2), nullable=False)
    promo_discount = Column(NUMERIC(10, 2))
    payable_amount = Column(NUMERIC(10, 2), nullable=False)
    promo_code_id = Column(BIGINT, ForeignKey("promo_code.id"))

    cancellation_time = Column(DateTime(timezone=True))
    cancelled_by = Column(Enum(BookingCancelledBy))
    cancellation_reason = Column(Text())

    confirmation_time = Column(DateTime(timezone=True))

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)

    experience_slot = relationship(
        "ExperienceSlot", lazy="select", uselist=False
    )
    artist_slot = relationship(
        "ArtistSlot", lazy="select", uselist=False
    )
