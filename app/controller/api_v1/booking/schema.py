from typing import Optional

from pydantic import BaseModel

from app.models.booking import BookingType


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
    slot_id: int
    no_of_guests: int
    promo_code: Optional[str]
    venue: Optional[Venue]
