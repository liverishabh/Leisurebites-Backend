from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.booking import BookingType
from app.models.payment import PaymentMethod


class CheckoutDetails(BaseModel):
    sub_total: float
    service_tax: float
    promo_discount: Optional[float]
    payable_amount: float
    promo_code_id: Optional[int]
    promo_error_message: Optional[str]


class Venue(BaseModel):
    address: str
    city: str
    state: str
    country: str


class BookingCreate(BaseModel):
    booking_type: BookingType
    payment_method: PaymentMethod
    slot_id: int
    no_of_guests: int
    promo_code: Optional[str]
    venue: Optional[Venue]


class CheckoutRequest(BaseModel):
    booking_type: BookingType
    slot_id: int
    no_of_guests: int
    promo_code: Optional[str]
    venue: Optional[Venue]


class CheckoutResponse(CheckoutDetails):
    title: str
    slot_id: int
    slot_start_time: datetime
    slot_end_time: datetime
    no_of_guests: int
    venue: Optional[Venue]
