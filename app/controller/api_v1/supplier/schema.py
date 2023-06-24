import re
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, validator

from app.config import config
from app.models.supplier import SupplierStatus, SupplierGender


class Supplier(BaseModel):
    name: Optional[str]
    email_id: EmailStr
    # phone_no: str
    # alternate_phone_no: Optional[str]
    description: Optional[str]
    gender: Optional[SupplierGender]
    address: Optional[str]
    status: SupplierStatus
    profile_image: Optional[str]

    @validator("profile_image")
    @classmethod
    def add_base_url(cls, v: Any) -> str:
        return f"{config.S3_BUCKET_URL}/{v}"


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    alternate_phone_no: Optional[str] = Field(None, min_length=1)
    gender: Optional[SupplierGender]
    address: Optional[str] = Field(None, min_length=1)
    aadhar_number: str = Field(..., min_length=1)
    primary_category: Optional[str] = Field(None, min_length=1)
    starting_price: Optional[int] = Field(None, gt=0)

    @validator("alternate_phone_no")
    @classmethod
    def validate_alternate_phone_no(cls, v: Any) -> str:
        rgx = re.compile("^\\s*(?:\\+?(\\d{1,3}))?[-. (]*(\\d{3})[-. )]" "*(\\d{3})[-. ]*(\\d{4})(?: *x(\\d+))?\\s*$")
        if re.match(rgx, v) is None:
            raise ValueError("Alternate Phone Number is invalid")

        return v


class Artist(Supplier):
    category: Optional[str]
    starting_price: Optional[int]
