import enum

from sqlalchemy import Column, INT, String, Enum, DateTime
from sqlalchemy.sql.expression import text

from app.models import BaseModel
from app.models.user import UserMixin


class AdminRoles(str, enum.Enum):
    KEY_ACCOUNT_MANAGEMENT = "key_account_management"


class Admin(BaseModel, UserMixin):
    id = Column(INT, primary_key=True, autoincrement=True, nullable=False)
    role = Column(Enum(AdminRoles))

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
