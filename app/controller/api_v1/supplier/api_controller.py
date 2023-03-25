from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.controller.api_v1.security.utils import get_password_hash
from app.controller.api_v1.supplier.schema import Supplier as SupplierResponse, SupplierUpdate
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.models.supplier import Supplier, SupplierType, SupplierStatus
from app.utility.auth import get_current_supplier
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
    supplier: Supplier = Depends(get_current_supplier)
) -> Any:
    """ Get Supplier Profile """
    return SupplierResponse(**supplier.__dict__)


@router.post("/profile", response_class=CustomJSONResponse)
def update_customer_profile(
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
