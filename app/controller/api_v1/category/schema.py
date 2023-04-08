from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    name: str
    icon_image: Optional[str]
