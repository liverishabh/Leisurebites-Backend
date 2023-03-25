from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.experience import ExperienceMode


class ExperienceSlot(BaseModel):
    start_time: datetime
    end_time = datetime
    is_booked = bool


class Experience(BaseModel):
    experience_id: int
    category: str
    host_declaration: str
    title: str
    description: Optional[str]
    activities: Optional[str]
    mode: ExperienceMode
    min_age: int
    guest_limit: int
    price_per_guest: int
    venue_address: Optional[str]
    venue_city: Optional[str]
    venue_state: Optional[str]
    venue_country: Optional[str]
    image_urls: List[str]
    slots: Optional[List[ExperienceSlot]]


class ExperienceCreate(BaseModel):
    category_id: int
    host_declaration: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    activities: Optional[str] = Field(None, min_length=1)
    mode: ExperienceMode
    min_age: int = Field(..., gt=0)
    guest_limit: int = Field(..., gt=0)
    price_per_guest: int = Field(..., gt=0)
    venue_address: Optional[str] = Field(None, min_length=1)
    venue_city: Optional[str] = Field(None, min_length=1)
    venue_state: Optional[str] = Field(None, min_length=1)
    venue_country: Optional[str] = Field(None, min_length=1)
