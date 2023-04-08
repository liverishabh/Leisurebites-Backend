from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controller.api_v1.category.schema import Category as CategoryResponse
from app.dependencies.db import get_db
from app.models.category import Category
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)


@router.get("/categories")
def get_categories(
    db: Session = Depends(get_db),
) -> Any:
    categories = db.query(Category).filter(
        Category.is_active.is_(True)
    ).all()

    resp = []
    for category in categories:
        resp.append(CategoryResponse(**category.__dict__))

    return resp
