import re
from typing import Any

from pydantic import BaseModel, EmailStr, validator, Field


class UserCreate(BaseModel):
    email_id: EmailStr
    phone_no: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

    @validator("phone_no")
    @classmethod
    def validate_sku_id(cls, v: Any) -> str:
        rgx = re.compile("^\\s*(?:\\+?(\\d{1,3}))?[-. (]*(\\d{3})[-. )]" "*(\\d{3})[-. ]*(\\d{4})(?: *x(\\d+))?\\s*$")
        if re.match(rgx, v) is None:
            raise ValueError(f"Phone Number is invalid")

        return v
