from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.controller.api_v1.security.schema import UserType, LoginType
from app.controller.api_v1.security.utils import verify_password, get_token
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)
logger = ApplicationLogger.get_logger(__name__)


@router.post("/login/access-token", response_class=CustomJSONResponse)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_type: UserType = Query(...),
    login_type: LoginType = Query(...)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    :param db: sqlalchemy Session object
    :param form_data: username, password sent in form
    :param user_type: one of customer, supplier, admin
     :param login_type: one of email_id, phone_no
    :return: jwt token
    """
    user = verify_password(
        username=form_data.username,
        plain_password=form_data.password,
        user_type=user_type,
        login_type=login_type,
        db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account is inactive. Please contact support team"
        )

    claims = {
        "username": form_data.username,
        "email_id": user.email_id,
        "phone_no": user.phone_no,
        "user_type": user_type.value
    }
    token = get_token(claims)
    token["token_type"] = "bearer"

    return token


# @router.post("/login/swap-token")
# def login_swap_token(
#
# )

