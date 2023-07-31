from typing import Optional, Any

from pydantic import BaseModel, validator

from app.utility.cloud_storage import cs_utils


class Category(BaseModel):
    id: int
    name: str
    tag_line: Optional[str]
    main_image_url: Optional[str]
    thumbnail_image_url: Optional[str]

    @validator("main_image_url", "thumbnail_image_url")
    @classmethod
    def add_base_url(cls, v: Any) -> str:
        if v:
            return cs_utils.get_full_image_url(v)
        return v
