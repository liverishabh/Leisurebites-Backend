from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.booking import BookingStatus


class Customer(BaseModel):
    name: Optional[str]
    email_id: EmailStr
    phone_no: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)


class CustomerBooking(BaseModel):
    title: str
    booking_uuid: str
    booking_type: str
    venue: str
    no_of_guests: int
    status: BookingStatus
    slot_start_time: datetime
    slot_end_time: datetime
    sub_total: float
    service_tax: float
    promo_discount: float
    payable_amount: float
    booking_time: Optional[datetime]
