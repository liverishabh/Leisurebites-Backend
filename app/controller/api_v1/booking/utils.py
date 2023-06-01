from datetime import datetime
from typing import Any, Optional

import pytz
from shortuuid import ShortUUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.controller.api_v1.booking.schema import Venue, CheckoutDetails
from app.models.artist_slot import ArtistSlot
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.customer import Customer
from app.models.experience import Experience, ExperienceSlot
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.promo_code import PromoCode, PromoCodeStatus, PromoCodeType
from app.models.supplier import Supplier
from app.utility.constants import EMAIL_TEMPLATES_DIR
from app.utility.email_sender import email_sender
from app.utility.payment_gateway import pg_utils


def validate_experience_booking(
    slot_id: int,
    no_of_guests: int,
    db: Session
) -> Experience:
    experience_slot: ExperienceSlot = db.query(ExperienceSlot).filter(
        ExperienceSlot.id == slot_id,
        ExperienceSlot.is_active.is_(True),
        ExperienceSlot.start_time >= datetime.now(tz=pytz.utc)
    ).first()

    if not experience_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No slot is available for booking"
        )

    if no_of_guests > experience_slot.remaining_guest_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No of guests exceeds guest limit"
        )

    return experience_slot.experience


def validate_artist_booking(
    slot_id: int,
    db: Session
) -> Any:
    artist_slot: ArtistSlot = db.query(ArtistSlot).filter(
        ArtistSlot.id == slot_id,
        ArtistSlot.is_booked.is_(False),
        ArtistSlot.is_active.is_(True),
        ArtistSlot.start_time >= datetime.now(tz=pytz.utc)
    ).first()

    if not artist_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No slot is available for booking"
        )

    return artist_slot


def update_artist_slot_address(
    artist_slot: ArtistSlot,
    venue: Venue,
) -> Any:
    artist_slot.venue_address = venue.address
    artist_slot.venue_city = venue.city
    artist_slot.venue_city = venue.state
    artist_slot.venue_country = venue.country


def get_promo_discount(
    total_order_amount: float,
    promo_code: Optional[str],
    db: Session
) -> Any:
    promo_discount = 0
    promo_error_message = None
    promo_code_id = None
    if promo_code:
        promo: PromoCode = db.query(PromoCode).filter(
            PromoCode.code == promo_code,
            PromoCode.status == PromoCodeStatus.active,
            PromoCode.start_time <= datetime.now(tz=pytz.utc),
            PromoCode.end_time >= datetime.now(tz=pytz.utc),
        ).first()

        if promo:
            if promo.min_purchase_amount > total_order_amount:
                promo_error_message = f"Code applicable for purchase amount greater than {promo.min_purchase_amount}"

            if promo.promo_code_type == PromoCodeType.discount_flat:
                promo_code_id = promo.id
                promo_discount = min(promo.flat_discount_amount, promo.max_discount_amount)
            elif promo.promo_code_type == PromoCodeType.discount_percent:
                promo_code_id = promo.id
                promo_discount = min(
                    round(promo.discount_percent * total_order_amount / 100, 2),
                    promo.max_discount_amount
                )
        else:
            promo_error_message = "Invalid promo code"

    return {
        "promo_code_id": promo_code_id,
        "promo_discount": promo_discount,
        "promo_error_message": promo_error_message
    }


def get_checkout_details(
    total_order_amount: float,
    promo_code: Optional[str],
    db: Session,
) -> CheckoutDetails:
    service_tax = round(total_order_amount * 0.18, 2)
    promo_details = get_promo_discount(
        total_order_amount=total_order_amount,
        promo_code=promo_code,
        db=db
    )
    promo_discount = promo_details["promo_discount"]
    checkout_details = CheckoutDetails(
        sub_total=total_order_amount,
        service_tax=service_tax,
        promo_discount=promo_discount,
        payable_amount=round(total_order_amount + service_tax - promo_discount, 2),
        promo_code_id=promo_details["promo_code_id"],
        promo_error_message=promo_details["promo_error_message"]
    )

    return checkout_details


def generate_booking_uuid() -> str:
    return "LB" + datetime.now().strftime("%y%m%d%H%M%S") + ShortUUID(alphabet="0123456789").random(length=4)


def get_booking_row(
    checkout_details: CheckoutDetails,
    customer_id: int,
    supplier_id: int,
    no_of_guests: int,
) -> Booking:
    booking = Booking()
    booking.booking_uuid = generate_booking_uuid()
    booking.customer_id = customer_id
    booking.supplier_id = supplier_id
    booking.no_of_guests = no_of_guests
    booking.status = BookingStatus.pending

    for key, value in checkout_details.dict().items():
        setattr(booking, key, value)

    return booking


def get_payment_row(
    booking: Booking,
) -> Payment:
    payment = Payment()
    payment.booking_id = booking.id
    payment.amount = booking.payable_amount
    payment.status = PaymentStatus.pending
    payment.transaction_code = ShortUUID().random(length=24)
    payment.payment_method = PaymentMethod.pg

    return payment


def initiate_experience_booking(
    experience: Experience,
    customer_id: int,
    slot_id: int,
    no_of_guests: int,
    promo_code: Optional[str],
    db: Session,
) -> Any:
    checkout_details: CheckoutDetails = get_checkout_details(
        total_order_amount=float(experience.price_per_guest) * no_of_guests,
        promo_code=promo_code,
        db=db,
    )

    booking = get_booking_row(
        checkout_details=checkout_details,
        customer_id=customer_id,
        supplier_id=experience.host_id,
        no_of_guests=no_of_guests,
    )
    booking.booking_type = BookingType.experience
    booking.experience_slot_id = slot_id

    db.add(booking)
    db.flush()
    db.refresh(booking)

    payment = get_payment_row(booking)
    payment.pg_order_id = pg_utils.create_order()

    db.add(payment)

    db.commit()

    return booking, payment.pg_order_id


def initiate_artist_booking(
    artist_slot: ArtistSlot,
    customer_id: int,
    no_of_guests: int,
    promo_code: Optional[str],
    db: Session,
) -> Any:
    checkout_details: CheckoutDetails = get_checkout_details(
        total_order_amount=float(artist_slot.price),
        promo_code=promo_code,
        db=db,
    )

    booking = get_booking_row(
        checkout_details=checkout_details,
        customer_id=customer_id,
        supplier_id=artist_slot.artist_id,
        no_of_guests=no_of_guests,
    )
    booking.status = BookingStatus.pending_with_artist
    booking.booking_type = BookingType.artist
    booking.artist_slot_id = artist_slot.id

    db.add(booking)
    db.flush()
    db.refresh(booking)

    payment = get_payment_row(booking)

    db.add(payment)

    db.commit()

    return booking


def handle_artist_booking_approval(
    booking: Booking,
    supplier: Supplier,
    db: Session,
) -> None:
    booking.status = BookingStatus.pending
    db.commit()

    customer: Customer = db.query(Customer).filter(
        Customer.id == booking.customer_id,
    ).first()

    send_booking_approval_email(
        destination_email=customer.email_id,
        booking_uuid=booking.booking_uuid,
        customer_name=customer.name,
        artist_name=supplier.name,
    )


def handle_artist_booking_payment_initiation(
    booking: Booking,
    db: Session,
) -> Any:
    payment = db.query(Payment).filter(
        Payment.booking_id == booking.id,
        Payment.status == PaymentStatus.pending,
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not found"
        )

    payment.pg_order_id = pg_utils.create_order()
    return payment.pg_order_id


def handle_booking_confirmation(
    booking: Booking,
    db: Session,
) -> None:
    if booking.booking_type == BookingType.experience:
        experience_slot: ExperienceSlot = db.query(ExperienceSlot).filter(
            ExperienceSlot.id == booking.experience_slot_id,
            ExperienceSlot.remaining_guest_limit >= booking.no_of_guests,
            ExperienceSlot.is_active.is_(True),
        ).with_for_update().first()

        if not experience_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slot is available for booking"
            )

        experience_slot.remaining_guest_limit -= booking.no_of_guests
    elif booking.booking_type == BookingType.artist:
        artist_slot: ArtistSlot = db.query(ArtistSlot).filter(
            ArtistSlot.id == booking.artist_slot_id,
            ArtistSlot.is_booked.is_(False),
            ArtistSlot.is_active.is_(True),
        ).with_for_update().first()

        if not artist_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slot is available for booking"
            )
        artist_slot.is_booked = True

    payment = db.query(Payment).filter(
        Payment.booking_id == booking.id,
        Payment.status == PaymentStatus.pending,
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not found"
        )
    if not pg_utils.verify_payment(payment.pg_order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )

    payment.status = PaymentStatus.success
    booking.status = BookingStatus.confirmed
    booking.confirmation_time = datetime.now(tz=pytz.UTC)
    db.commit()


def send_booking_approval_email(
    destination_email: str,
    booking_uuid: str,
    customer_name: str,
    artist_name: str
) -> None:
    subject = "Payment Pending for your booking"
    with open(EMAIL_TEMPLATES_DIR + "/artist_booking.html") as f:
        template_str = f.read()

    email_sender.send_email(
        destination_emails=[destination_email],
        email_subject=subject,
        email_body=template_str,
        environment={
            "customer_name": customer_name,
            "artist_name": artist_name,
            "booking_uuid": booking_uuid
        }
    )
