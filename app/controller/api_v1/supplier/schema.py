import re
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, validator

from app.models.supplier import SupplierStatus, SupplierGender


class Supplier(BaseModel):
    name: Optional[str]
    email_id: EmailStr
    phone_no: str
    alternate_phone_no: Optional[str]
    description: Optional[str]
    gender: Optional[SupplierGender]
    address: Optional[str]
    status: SupplierStatus


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    alternate_phone_no: Optional[str] = Field(None, min_length=1)
    gender: Optional[SupplierGender]
    address: Optional[str] = Field(None, min_length=1)
    aadhar_number: str = Field(..., min_length=1)

    @validator("alternate_phone_no")
    @classmethod
    def validate_alternate_phone_no(cls, v: Any) -> str:
        rgx = re.compile("^\\s*(?:\\+?(\\d{1,3}))?[-. (]*(\\d{3})[-. )]" "*(\\d{3})[-. ]*(\\d{4})(?: *x(\\d+))?\\s*$")
        if re.match(rgx, v) is None:
            raise ValueError("Alternate Phone Number is invalid")

        return v
