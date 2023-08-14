from sqlalchemy import Column, BIGINT, DateTime
from sqlalchemy.sql.expression import text

from app.models import BaseModel
from app.models.user import UserMixin


class Customer(BaseModel, UserMixin):

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
