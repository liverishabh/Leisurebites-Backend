from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    tag_line: Optional[str]
    main_image_url: Optional[str]
    thumbnail_image_url: Optional[str]
