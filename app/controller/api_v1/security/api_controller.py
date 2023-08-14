from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status, Body, Form, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.controller.api_v1.security.schema import UserType, LoginType
from app.controller.api_v1.security.utils import (
    verify_password,
    get_token,
    get_user_model,
    get_password_reset_token,
    set_password_reset_token_in_redis,
    send_reset_password_email,
    verify_password_reset_token,
    get_password_reset_token_from_redis,
    get_password_hash,
    delete_password_reset_token_from_redis,
    delete_login_tokens_from_redis,
    logout_user
)
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.utility.response import CustomJSONResponse
from app.utility.router import RequestResponseLoggingRoute

router = APIRouter(route_class=RequestResponseLoggingRoute)
logger = ApplicationLogger.get_logger(__name__)


@router.post("/login/access-token", response_class=CustomJSONResponse)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_type: UserType = Query(...),
    login_type: LoginType = Query(...),
    db: Session = Depends(get_db),
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
        "id": user.id,
        "username": form_data.username,
        "email_id": user.email_id,
        "phone_no": user.phone_no,
        "user_type": user_type.value
    }
    if user_type == UserType.supplier:
        claims["status"] = user.status
    token = get_token(claims)
    token["token_type"] = "bearer"

    return token


@router.post("/password-recovery", response_class=CustomJSONResponse)
def recover_password(
    email_id: EmailStr = Body(...),
    user_type: UserType = Body(...),
    redirect_url: str = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """ Send Email for Password Recovery """
    user_model = get_user_model(user_type)
    user = db.query(user_model).filter(func.lower(user_model.email_id) == email_id.lower()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user found with the given email_id",
        )

    password_reset_token = get_password_reset_token(email_id=email_id)
    set_password_reset_token_in_redis(email_id=email_id, token=password_reset_token)
    try:
        send_reset_password_email(
            destination_email=user.email_id,
            user_name=user.name,
            token=password_reset_token,
            redirect_url=redirect_url
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Failure in sending email",
        )

    return "Password recovery email sent"


@router.post("/reset-password", response_class=CustomJSONResponse)
def reset_password(
    reset_token: str = Form(...),
    new_password: str = Form(...),
    user_type: UserType = Query(...),
    db: Session = Depends(get_db)
) -> Any:
    """ Reset password """
    user_model = get_user_model(user_type)
    email_id = verify_password_reset_token(reset_token)
    if not email_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link is invalid"
        )

    reset_token_redis = get_password_reset_token_from_redis(email_id)
    if not reset_token_redis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link has been used"
        )
    if reset_token_redis != reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link has been updated"
        )

    user = db.query(user_model).filter(func.lower(user_model.email_id) == email_id.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist in system",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="User is inactive"
        )

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.commit()

    delete_password_reset_token_from_redis(email_id)
    delete_login_tokens_from_redis(pattern=f"{email_id}:*")
    delete_login_tokens_from_redis(pattern=f"{user.phone_no}:*")
    return "Password updated successfully"


@router.post("/logout", response_class=CustomJSONResponse)
def logout(
    token: str = Header(None, convert_underscores=False, alias="X-Auth-Token")
) -> Any:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth Token not found"
        )
    if not logout_user(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session expired or invalid"
        )
    return "Successfully logged out"


# @router.post("/login/swap-token")
# def login_swap_token(
#
# )

