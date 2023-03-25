from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Customer(BaseModel):
    name: Optional[str]
    email_id: EmailStr
    phone_no: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
