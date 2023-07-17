from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.controller.api_v1.security.utils import get_password_hash
from app.controller.api_v1.supplier.schema import (
    Supplier as SupplierResponse,
    SupplierUpdate,
    Artist as ArtistResponse
)
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.models.artist_slot import ArtistSlot
from app.models.booking import Booking
from app.models.experience import Experience, ExperienceSlot, ExperienceStatus
from app.models.supplier import Supplier, SupplierType, SupplierStatus
from app.utility.auth import get_current_supplier
from app.utility.cloud_storage import cs_utils, get_cloud_file_path
from app.utility.constants import PROFILE_IMAGE_DIR
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute
from app.utility.schema import UserCreate

router = APIRouter(route_class=RequestResponseLoggingRoute)
logger = ApplicationLogger.get_logger(__name__)


@router.post("/register", response_class=CustomJSONResponse)
def register_supplier(
    create_user_request: UserCreate,
    supplier_type: SupplierType = Query(...),
    db: Session = Depends(get_db),
) -> Any:
    """ Register Supplier """
    user = db.query(Supplier).filter(
        or_(
            Supplier.email_id == create_user_request.email_id,
            Supplier.phone_no == create_user_request.phone_no
        )
    ).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email id or phone no already exist"
        )

    supplier = Supplier()
    supplier.email_id = create_user_request.email_id
    supplier.phone_no = create_user_request.phone_no
    supplier.hashed_password = get_password_hash(create_user_request.password)
    supplier.type = supplier_type

    db.add(supplier)
    db.commit()

    return "Supplier registered successfully"


@router.get("/profile", response_class=CustomJSONResponse)
def get_supplier_profile(
    supplier_id: int = Query(...),
    db: Session = Depends(get_db),
) -> Any:
    """ Get Supplier Profile """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No supplier found"
        )
    if not supplier.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return SupplierResponse(**supplier.__dict__)


@router.post("/profile", response_class=CustomJSONResponse)
def update_supplier_profile(
    update_supplier_request: SupplierUpdate,
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    """ Update Supplier Profile """
    supplier_dict = update_supplier_request.dict(exclude_unset=True)
    supplier_db_dict = jsonable_encoder(supplier)

    for field in supplier_db_dict:
        if field in supplier_dict:
            setattr(supplier, field, supplier_dict[field])

    if supplier.status == SupplierStatus.created:
        supplier.status = SupplierStatus.approval_pending

    db.commit()
    return "Supplier Profile updated successfully"


@router.post("/upload-profile-image", response_class=CustomJSONResponse)
def update_supplier_profile_image(
    image: UploadFile,
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    """ Update Supplier Profile Image """
    cloud_file_path = get_cloud_file_path(image.filename, PROFILE_IMAGE_DIR)
    image_uploaded, image_url = cs_utils.upload_file(image, cloud_file_path)

    if not image_uploaded:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f"Image Upload Failed"
        )

    supplier.profile_image = cloud_file_path
    db.commit()

    return "Image uploaded successfully"


@router.get("/all_artists", response_class=CustomJSONResponse)
def get_all_artists(
    db: Session = Depends(get_db),
) -> Any:
    """ Get All Artists """
    artists: List[Supplier] = db.query(Supplier).filter(
        Supplier.type == SupplierType.artist,
        Supplier.status == SupplierStatus.approved
    ).all()

    resp = []
    for artist in artists:
        resp.append(ArtistResponse(
            **artist.__dict__,
            category=artist.primary_category
        ))

    return resp

# @router.get("/bookings", response_class=CustomJSONResponse)
# def get_supplier_bookings(
#     supplier: Supplier = Depends(get_current_supplier),
#     db: Session = Depends(get_db),
# ) -> Any:
#     """ Get Supplier Bookings """
#     if supplier.type == SupplierType.artist:
#         slots = db.query(ArtistSlot).filter(
#             ArtistSlot.artist_id == supplier.id,
#             ArtistSlot.is_active.is_(True),
#             ArtistSlot.start_time >= func.now()
#         ).all()
#     else:
#         experiences = db.query(Experience).filter(
#             Experience.host_id == supplier.id,
#             Experience.status == ExperienceStatus.approved
#         ).all()
#         slots = db.query(ExperienceSlot).filter(
#             ExperienceSlot.experience_id.in_([exp.id for exp in experiences]),
#             ExperienceSlot.is_active.is_(True),
#             ExperienceSlot.start_time >= func.now()
#         ).all()
#     bookings: List[Booking] = db.query(Booking).filter(
#         Booking.supplier_id == supplier.id
#     ).all()
#
#     bookings_resp = []
#     for booking in bookings:
#         if booking.booking_type == BookingType.artist:
#             slot = booking.artist_slot
#             title = slot.artist.name
#             venue = slot.venue_address
#         else:
#             slot = booking.experience_slot
#             experience = slot.experience
#             title = experience.title
#             venue = experience.venue_address
#         bookings_resp.append(
#             CustomerBooking(
#                 **booking.__dict__,
#                 title=title,
#                 venue=venue,
#                 slot_start_time=slot.start_time,
#                 slot_end_time=slot.end_time,
#                 booking_time=booking.confirmation_time
#             )
#         )
#
#     return bookings_resp
