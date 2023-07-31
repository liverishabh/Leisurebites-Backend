from sqlalchemy import Column, INT, String, DateTime, Boolean
from sqlalchemy.sql.expression import true, text

from app.models import BaseModel


class Category(BaseModel):
    id = Column(INT, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(50), nullable=False)
    tag_line = Column(String(255))
    main_image_url = Column(String(255))
    thumbnail_image_url = Column(String(255))
    is_active = Column(Boolean(), server_default=true(), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
