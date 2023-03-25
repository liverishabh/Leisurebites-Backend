import base64
import json

from fastapi import Header, HTTPException, status, Depends
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from app.config import config
from app.controller.api_v1.security.schema import UserType
from app.dependencies.db import get_db
from app.dependencies.logger import ApplicationLogger
from app.dependencies.redis import redis_client
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.utility.constants import AUTH_TOKEN_PREFIX, JWT_ENCODE_ALGORITHM

logger = ApplicationLogger.get_logger(__name__)


def get_token_key(token: str, username: str = None, add_username_prefix: bool = True) -> str:
    if not add_username_prefix:
        return f"{AUTH_TOKEN_PREFIX}{token}"
    if not username:
        jwt_payload_token = token.split('.')[1]
        padded_token = jwt_payload_token + "==="
        username = json.loads(base64.urlsafe_b64decode(padded_token)).get("username", None)
    if not username:
        return f"{AUTH_TOKEN_PREFIX}{token}"
    return f"{username}:{AUTH_TOKEN_PREFIX}{token}"


def get_claims_from_token_and_validate_redis(token: str):
    try:
        if not redis_client.exists(get_token_key(token, add_username_prefix=False)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Auth Token"
            )
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[JWT_ENCODE_ALGORITHM])
    except JWTError as jwt_exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth Token expired"
        ) from jwt_exception
    return payload


def get_current_customer(
    token: str = Header(None, convert_underscores=False, alias="X-Auth-Token"),
    db: Session = Depends(get_db)
) -> Customer:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth Token not found"
        )
    claims = get_claims_from_token_and_validate_redis(token)
    if claims["user_type"] != UserType.customer.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for this request"
        )
    customer = db.query(Customer).filter(Customer.email_id == claims["email_id"]).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No customer found"
        )
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    logger.info("User %s authenticated successfully", claims['email_id'])
    return customer


def get_current_supplier(
    token: str = Header(None, convert_underscores=False, alias="X-Auth-Token"),
    db: Session = Depends(get_db)
) -> Supplier:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth Token not found"
        )
    claims = get_claims_from_token_and_validate_redis(token)
    if claims["user_type"] != UserType.supplier.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for this request"
        )
    supplier = db.query(Supplier).filter(Supplier.email_id == claims["email_id"]).first()
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

    logger.info("User %s authenticated successfully", claims['email_id'])
    return supplier
