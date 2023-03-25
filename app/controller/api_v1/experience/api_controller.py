from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.config import config
from app.controller.api_v1.experience.schema import ExperienceCreate, Experience as ExperienceResponse
from app.dependencies.db import get_db
from app.models.supplier import Supplier
from app.models.category import Category
from app.models.experience import Experience, ExperienceImage
from app.utility.auth import get_current_supplier
from app.utility.cloud_storage import cs_utils, get_cloud_file_path
from app.utility.constants import EXPERIENCE_IMAGE_DIR
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)


@router.get("", response_class=CustomJSONResponse)
def get_experience(
    supplier: Supplier = Depends(get_current_supplier),
    db: Session = Depends(get_db),
) -> Any:
    experiences: List[Experience] = db.query(Experience).filter(
        Experience.host_id == supplier.id
    ).all()

    resp = []
    for experience in experiences:
        image_urls = []
        for image in experience.images:
            image_urls.append(f"{config.S3_BUCKET_URL}/{image.url}")
        resp.append(ExperienceResponse(
            **experience.__dict__,
            experience_id=experience.id,
            image_urls=image_urls,
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
