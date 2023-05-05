from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Query
from sqlalchemy.orm import Session

from app.config import config
from app.controller.api_v1.experience.schema import ExperienceCreate, Experience as ExperienceResponse, \
    ExperienceSlotAdd
from app.controller.api_v1.experience.utils import validate_new_slot
from app.dependencies.db import get_db
from app.models.supplier import Supplier
from app.models.category import Category
from app.models.experience import Experience, ExperienceImage, ExperienceStatus, ExperienceSlot
from app.utility.auth import get_current_supplier
from app.utility.cloud_storage import cs_utils, get_cloud_file_path
from app.utility.constants import EXPERIENCE_IMAGE_DIR
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)


@router.get("/popular", response_class=CustomJSONResponse)
def get_popular_experiences(
    db: Session = Depends(get_db),
) -> Any:
    """ Get Popular Experiences """
    pass


@router.get("/similar", response_class=CustomJSONResponse)
def get_similar_experiences(
    experience_id: int = Query(...),
    db: Session = Depends(get_db),
) -> Any:
    """ Get Similar Experiences """
    pass


@router.get("", response_class=CustomJSONResponse)
def get_experience_by_id(
    experience_id: int = Query(...),
    db: Session = Depends(get_db),
) -> Any:
    """ Get Experience by Id """
    experience: Experience = db.query(Experience).filter(
        Experience.id == experience_id,
        Experience.status == ExperienceStatus.approved
    ).first()

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No experience found with id {experience_id}"
        )

    image_urls = []
    for image in experience.images:
        image_urls.append(f"{config.S3_BUCKET_URL}/{image.url}")

    return ExperienceResponse(
        **experience.__dict__,
        experience_id=experience.id,
        image_urls=image_urls,
        category=experience.category.name,
        slots=experience.slots
    )


@router.post("/category/all", response_class=CustomJSONResponse)
def get_experiences_by_category(

    category_id: int = Query(...),
    db: Session = Depends(get_db),
) -> Any:
    """ Get all Experiences of a category """
    experiences: List[Experience] = db.query(Experience).filter(
        Experience.category_id == category_id,
        Experience.status == ExperienceStatus.approved
    ).all()

    resp = []
    for experience in experiences:
        main_image_url = experience.images[0].url
        resp.append(ExperienceResponse(
            **experience.__dict__,
            experience_id=experience.id,
            image_urls=[f"{config.S3_BUCKET_URL}/{main_image_url}"]
        ))

    return resp


@router.get("/host/all", response_class=CustomJSONResponse)
def get_all_experiences_of_host(
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    """ Get all experiences of a host """
    experiences: List[Experience] = db.query(Experience).filter(
        Experience.host_id == supplier.id
    ).all()

    resp = []
    for experience in experiences:
        main_image_url = experience.images[0].url
        resp.append(ExperienceResponse(
            **experience.__dict__,
            experience_id=experience.id,
            image_urls=[f"{config.S3_BUCKET_URL}/{main_image_url}"],
            category=experience.category.name
        ))

    return resp


@router.post("/create", response_class=CustomJSONResponse)
def create_experience(
    create_experience_request: ExperienceCreate,
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    """ Create an Experience """
    category = db.query(Category).filter(
        Category.id == create_experience_request.category_id,
        Category.is_active.is_(True)
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_experience_request.category_id} does not exist"
        )
    experience_dict = create_experience_request.dict(exclude_unset=True)
    experience = Experience()

    for key, value in experience_dict.items():
        setattr(experience, key, value)

    experience.host_id = supplier.id
    db.add(experience)
    db.commit()
    db.refresh(experience)

    return {"experience_id": experience.id}


@router.post("/upload-image", response_class=CustomJSONResponse)
def upload_image(
    images: List[UploadFile],
    experience_id: int = Query(...),
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    """ Upload image for an experience (max 4 images allowed) """
    experience = db.query(Experience).filter(
        Experience.host_id == supplier.id,
        Experience.id == experience_id
    ).first()
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experience with id {experience_id} does not exist"
        )

    images_db = []
    for image in images:
        cloud_file_path = get_cloud_file_path(image.filename, EXPERIENCE_IMAGE_DIR)
        image_uploaded, image_url = cs_utils.upload_file(image, cloud_file_path)

        if not image_uploaded:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Image Upload Failed"
            )

        experience_image = ExperienceImage()
        experience_image.experience_id = experience_id
        experience_image.url = cloud_file_path
        images_db.append(experience_image)

    if images_db:
        db.bulk_save_objects(images_db)
        db.commit()

    return "Images uploaded successfully"


@router.post("/add-slot", response_class=CustomJSONResponse)
def add_slot(
    add_slot_request: ExperienceSlotAdd,
    experience_id: int = Query(...),
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db)
) -> Any:
    """ Add slot for an experience """
    experience: Experience = db.query(Experience).filter(
        Experience.host_id == supplier.id,
        Experience.id == experience_id
    ).first()
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experience with id {experience_id} does not exist"
        )

    if not validate_new_slot(
        start_time=add_slot_request.start_time,
        end_time=add_slot_request.end_time,
        existing_slots=experience.slots
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slot start or end time"
        )

    slot = ExperienceSlot()
    slot.experience_id = experience_id
    slot.start_time = add_slot_request.start_time
    slot.end_time = add_slot_request.end_time

    db.add(slot)
    db.commit()

    return "Slot added successfully"
