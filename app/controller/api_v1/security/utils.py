import time
from datetime import timedelta
from typing import Optional, Dict, Any

from jose import jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import config
from app.controller.api_v1.security.schema import UserType, LoginType
from app.dependencies.redis import redis_client
from app.models.admin import Admin
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.user import UserMixin
from app.utility.auth import get_token_key
from app.utility.constants import AUTH_EXPIRY_TIME_SECONDS, JWT_ENCODE_ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    username: str,
    plain_password: str,
    user_type: UserType,
    login_type: LoginType,
    db: Session
) -> Optional[UserMixin]:
    """ Verify plain password with hashed password """

    user: Optional[UserMixin] = None
    user_model = None
    if user_type == UserType.customer:
        user_model = Customer
    elif user_type == UserType.supplier:
        user_model = Supplier
    elif user_type == UserType.admin:
        user_model = Admin

    if login_type == LoginType.email_id:
        user = db.query(user_model).filter(func.lower(user_model.email_id) == username.lower()).first()
    elif login_type == LoginType.phone_no:
        user = db.query(user_model).filter(user_model.phone_no == username).first()

    if not user:
        return None

    if not pwd_context.verify(plain_password, user.hashed_password):
        return None

    return user


def get_token(claims: Dict[Any, Any]) -> Dict[str, str]:
    """ create token, save in Redis and return """

    access_token_expire_delta = timedelta(seconds=AUTH_EXPIRY_TIME_SECONDS)
    expiry_time = time.time() + access_token_expire_delta.total_seconds()
    claims["exp"] = expiry_time
    encoded_jwt = jwt.encode(claims, config.SECRET_KEY, algorithm=JWT_ENCODE_ALGORITHM)
    redis_client.set(get_token_key(encoded_jwt, claims["username"]), "", ex=access_token_expire_delta)
    redis_client.set(get_token_key(encoded_jwt, add_username_prefix=False), "", ex=access_token_expire_delta)

    token: Dict[Any, Any] = {
        "access_token": encoded_jwt,
        "access_token_expiry": expiry_time,
    }
    return token
