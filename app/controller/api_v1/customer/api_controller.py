from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.controller.api_v1.customer.schema import Customer as CustomerResponse, CustomerUpdate, CustomerBooking
from app.controller.api_v1.security.utils import get_password_hash
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.models.booking import Booking, BookingType
from app.models.customer import Customer
from app.utility.auth import get_current_customer
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute
from app.utility.schema import UserCreate

router = APIRouter(route_class=RequestResponseLoggingRoute)
logger = ApplicationLogger.get_logger(__name__)


@router.post("/register", response_class=CustomJSONResponse)
def register_customer(
    create_user_request: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """ Register Customer """
    user = db.query(Customer).filter(
        or_(
            Customer.email_id == create_user_request.email_id,
            Customer.phone_no == create_user_request.phone_no
        )
    ).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email id or phone no already exist"
        )

    customer = Customer()
    customer.email_id = create_user_request.email_id
    customer.phone_no = create_user_request.phone_no
    customer.hashed_password = get_password_hash(create_user_request.password)

    db.add(customer)
    db.commit()

    return "Customer registered successfully"


@router.get("/profile", response_class=CustomJSONResponse)
def get_customer_profile(
    customer: Customer = Depends(get_current_customer)
) -> Any:
    """ Get Customer Profile """
    return CustomerResponse(**customer.__dict__)


@router.post("/profile", response_class=CustomJSONResponse)
def update_customer_profile(
    update_customer_request: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Any:
    """ Update Customer Profile """
    customer_dict = update_customer_request.dict(exclude_unset=True)
    customer_db_dict = jsonable_encoder(customer)

    for field in customer_db_dict:
        if field in customer_dict:
            setattr(customer, field, customer_dict[field])

    db.commit()
    return "Customer Profile updated successfully"


@router.get("/bookings", response_class=CustomJSONResponse)
def get_customer_bookings(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Any:
    """ Get Customer Bookings """
    bookings: List[Booking] = db.query(Booking).filter(
        Booking.customer_id == customer.id
    ).all()

    bookings_resp = []
    for booking in bookings:
        if booking.booking_type == BookingType.artist:
            slot = booking.artist_slot
            title = slot.artist.name
            venue = slot.venue_address
        else:
            slot = booking.experience_slot
            experience = slot.experience
            title = experience.title
            venue = experience.venue_address
        bookings_resp.append(
            CustomerBooking(
                **booking.__dict__,
                title=title,
                venue=venue,
                slot_start_time=slot.start_time,
                slot_end_time=slot.end_time,
                booking_time=booking.confirmation_time
            )
        )

    return bookings_resp
