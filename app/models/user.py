from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.expression import true


class UserMixin:
    name = Column(String(100))
    email_id = Column(String, unique=True, index=True, nullable=False)
    phone_no = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean(), server_default=true(), nullable=False)
