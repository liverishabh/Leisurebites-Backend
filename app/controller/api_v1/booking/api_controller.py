from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controller.api_v1.booking.schema import (
    BookingCreate,
    CheckoutDetails,
    CheckoutRequest,
    CheckoutResponse,
    Venue
)
from app.controller.api_v1.booking.utils import (
    validate_experience_booking,
    initiate_experience_booking,
    validate_artist_booking,
    initiate_artist_booking,
    update_artist_slot_address,
    handle_booking_confirmation,
    handle_artist_booking_approval,
    handle_artist_booking_payment_initiation, get_checkout_details
)
from app.dependencies.db import get_db
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.utility.auth import get_current_customer, get_current_supplier
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)


@router.post("/checkout", response_class=CustomJSONResponse)
def checkout_booking(
    checkout_request: CheckoutRequest,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
) -> Any:
    resp = None
    if checkout_request.booking_type == BookingType.experience:
        experience_slot = validate_experience_booking(
            slot_id=checkout_request.slot_id,
            no_of_guests=checkout_request.no_of_guests,
            db=db
        )
        experience = experience_slot.experience
        checkout_details: CheckoutDetails = get_checkout_details(
            total_order_amount=float(experience.price_per_guest) * checkout_request.no_of_guests,
            promo_code=checkout_request.promo_code,
            db=db,
        )
        resp = CheckoutResponse(
            **checkout_details.dict(),
            title=experience.title,
            slot_id=checkout_request.slot_id,
            slot_start_time=experience_slot.start_time,
            slot_end_time=experience_slot.end_time,
            no_of_guests=checkout_request.no_of_guests,
            venue=Venue(
                address=experience.venue_address,
                city=experience.venue_city,
                state=experience.venue_state,
                country=experience.venue_country,
            )
        )

    elif checkout_request.booking_type == BookingType.artist:
        artist_slot = validate_artist_booking(
            slot_id=checkout_request.slot_id,
            db=db
        )
        checkout_details: CheckoutDetails = get_checkout_details(
            total_order_amount=float(artist_slot.price),
            promo_code=checkout_request.promo_code,
            db=db,
        )
        resp = CheckoutResponse(
            **checkout_details.dict(),
            title=artist_slot.artist.name,
            slot_id=checkout_request.slot_id,
            slot_start_time=artist_slot.start_time,
            slot_end_time=artist_slot.end_time,
            no_of_guests=checkout_request.no_of_guests,
            venue=checkout_request.venue
        )

    return resp


@router.post("/initiate", response_class=CustomJSONResponse)
def initiate_booking(
    create_booking_request: BookingCreate,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
) -> Any:
    """ Initiate booking """
    booking, pg_order_id = None, None
    if create_booking_request.booking_type == BookingType.experience:
        experience_slot = validate_experience_booking(
            slot_id=create_booking_request.slot_id,
            no_of_guests=create_booking_request.no_of_guests,
            db=db
        )
        booking, pg_order_id = initiate_experience_booking(
            experience=experience_slot.experience,
            customer_id=customer.id,
            payment_method=create_booking_request.payment_method,
            slot_id=create_booking_request.slot_id,
            no_of_guests=create_booking_request.no_of_guests,
            promo_code=create_booking_request.promo_code,
            db=db
        )

    elif create_booking_request.booking_type == BookingType.artist:
        artist_slot = validate_artist_booking(
            slot_id=create_booking_request.slot_id,
            db=db
        )
        update_artist_slot_address(
            artist_slot=artist_slot,
            venue=create_booking_request.venue,
        )
        booking = initiate_artist_booking(
            artist_slot=artist_slot,
            customer_id=customer.id,
            payment_method=create_booking_request.payment_method,
            no_of_guests=create_booking_request.no_of_guests,
            promo_code=create_booking_request.promo_code,
            db=db
        )

    return {
        "booking_id": booking.id,
        "booking_uuid": booking.booking_uuid,
        "pg_order_id": pg_order_id
    }


@router.post("/artist/approve/{booking_id}", response_class=CustomJSONResponse)
def approve_artist_booking(
    booking_id: int,
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db)
) -> Any:
    """ Approve Artist booking """
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.booking_type == BookingType.artist,
        Booking.status == BookingStatus.pending_with_artist,
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking not found"
        )
    if booking.supplier_id != supplier.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking does not belong to the supplier"
        )

    handle_artist_booking_approval(
        booking=booking,
        supplier=supplier,
        db=db
    )

    return "Booking Approved"


@router.post("/artist/initiate-payment/{booking_id}", response_class=CustomJSONResponse)
def approve_artist_booking(
    booking_id: int,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
) -> Any:
    """ Approve Artist booking """
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.booking_type == BookingType.artist,
        Booking.status == BookingStatus.pending,
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking not found"
        )
    if booking.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking does not belong to the customer"
        )

    pg_order_id = handle_artist_booking_payment_initiation(
        booking=booking,
        db=db
    )

    return {
        "booking_id": booking.id,
        "booking_uuid": booking.booking_uuid,
        "pg_order_id": pg_order_id
    }


@router.post("/confirm/{booking_id}", response_class=CustomJSONResponse)
def confirm_booking(
    booking_id: int,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
) -> Any:
    """ Confirm booking """
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.status == BookingStatus.pending,
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking already approved or not found"
        )
    if booking.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking does not belong to the customer"
        )

    handle_booking_confirmation(
        booking=booking,
        db=db
    )

    return {
        "booking_amount": booking.payable_amount,
        "message": "Booking Confirmed"
    }
