import enum

from sqlalchemy import Column, INT, String, TEXT, DateTime, Enum
from sqlalchemy.sql.expression import text

from app.models import BaseModel
from app.models.user import UserMixin


class SupplierType(str, enum.Enum):
    host = "host"
    artist = "artist"


class SupplierStatus(str, enum.Enum):
    created = "created"
    approval_pending = "approval_pending"
    approved = "approved"
    rejected = "rejected"


class SupplierGender(str, enum.Enum):
    male = "male"
    female = "female"
    others = "others"


class Supplier(BaseModel, UserMixin):
    type = Column(Enum(SupplierType), nullable=False)
    description = Column(TEXT)
    alternate_phone_no = Column(String(20))
    gender = Column(Enum(SupplierGender))
    address = Column(TEXT)
    language = Column(String(255))
    aadhar_number = Column(String(20))
    profile_image = Column(String(255))
    primary_category = Column(String(50))
    starting_price = Column(INT)
    status = Column(Enum(SupplierStatus), server_default=SupplierStatus.created, nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
