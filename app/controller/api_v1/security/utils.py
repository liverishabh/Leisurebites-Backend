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
from app.utility.constants import (
    AUTH_EXPIRY_TIME_SECONDS,
    JWT_ENCODE_ALGORITHM,
    PSWD_RESET_PREFIX,
    EMAIL_TEMPLATES_DIR
)
from app.utility.email_sender import email_sender

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_model(user_type: UserType):
    if user_type == UserType.customer:
        return Customer
    elif user_type == UserType.supplier:
        return Supplier
    elif user_type == UserType.admin:
        return Admin


def verify_password(
    username: str,
    plain_password: str,
    user_type: UserType,
    login_type: LoginType,
    db: Session
) -> Optional[UserMixin]:
    """ Verify plain password with hashed password """

    user: Optional[UserMixin] = None
    user_model = get_user_model(user_type)

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


def get_password_reset_token(email_id: str) -> str:
    """ create password reset token """

    reset_token_expire_delta = timedelta(minutes=config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)
    expiry_time = time.time() + reset_token_expire_delta.total_seconds()
    encoded_jwt = jwt.encode(
        claims={"exp": expiry_time, "sub": email_id},
        key=config.SECRET_KEY,
        algorithm=JWT_ENCODE_ALGORITHM,
    )
    return encoded_jwt


def get_password_reset_redis_key(email_id: str) -> str:
    return PSWD_RESET_PREFIX + email_id


def get_password_reset_token_from_redis(email_id: str) -> Optional[str]:
    redis_key = get_password_reset_redis_key(email_id)
    return redis_client.get(redis_key)


def set_password_reset_token_in_redis(email_id: str, token: str) -> None:
    redis_key = get_password_reset_redis_key(email_id)
    redis_client.set(redis_key, token, ex=config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES * 60)


def delete_password_reset_token_from_redis(email_id: str) -> None:
    redis_key = get_password_reset_redis_key(email_id)
    redis_client.delete(redis_key)


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(
            token=token,
            key=config.SECRET_KEY,
            algorithms=JWT_ENCODE_ALGORITHM
        )
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def delete_login_tokens_from_redis(pattern: str) -> None:
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key.partition(':')[2])
        redis_client.delete(key)


def send_reset_password_email(destination_email: str, user_name: str, token: str, redirect_url: str) -> None:
    subject = "Password Reset requested"
    with open(EMAIL_TEMPLATES_DIR + "/reset_password.html") as f:
        template_str = f.read()
    reset_link = f"{redirect_url}?token={token}"

    email_sender.send_email(
        destination_emails=[destination_email],
        email_subject=subject,
        email_body=template_str,
        environment={
            "user_name": user_name,
            "valid_time": config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
            "reset_link": reset_link
        }
    )


def logout_user(token: str) -> bool:
    if not redis_client.exists(get_token_key(token, add_username_prefix=False)):
        return False

    redis_client.delete(get_token_key(token))
    redis_client.delete(get_token_key(token, add_username_prefix=False))

    return True
