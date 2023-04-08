import enum

from sqlalchemy import Column, BIGINT, INT, TEXT, Enum, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import true, false, text

from app.models import BaseModel


class ExperienceMode(str, enum.Enum):
    physical = "physical"
    virtual = "virtual"


class ExperienceStatus(str, enum.Enum):
    approval_pending = "approval_pending"
    approved = "approved"
    rejected = "rejected"


class ExperienceImage(BaseModel):
    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    experience_id = Column(INT, ForeignKey("experience.id"), nullable=False)
    url = Column(String(255), nullable=False)
    is_active = Column(Boolean(), server_default=true(), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)


class ExperienceSlot(BaseModel):
    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    experience_id = Column(INT, ForeignKey("experience.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_booked = Column(Boolean(), server_default=false(), nullable=False)
    is_active = Column(Boolean(), server_default=true(), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)


class Experience(BaseModel):
    id = Column(INT, primary_key=True, autoincrement=True, nullable=False)
    host_id = Column(INT, ForeignKey("supplier.id"), nullable=False)
    category_id = Column(INT, ForeignKey("category.id"), nullable=False)
    host_declaration = Column(TEXT, nullable=False)
    title = Column(String(50), nullable=False)
    description = Column(TEXT)
    activities = Column(TEXT)
    mode = Column(Enum(ExperienceMode), nullable=False)
    min_age = Column(INT, nullable=False)
    guest_limit = Column(INT, nullable=False)
    price_per_guest = Column(INT, nullable=False)
    venue_address = Column(TEXT)
    venue_city = Column(String(50))
    venue_state = Column(String(50))
    venue_country = Column(String(50))
    status = Column(Enum(ExperienceStatus), server_default=ExperienceStatus.approval_pending, nullable=False)
    # discount_code = Column()
    # cancellation_policy = Column()

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)

    images = relationship(
        "ExperienceImage", order_by=ExperienceImage.id, lazy="select",
        primaryjoin="and_(Experience.id == ExperienceImage.experience_id, "
                    "ExperienceImage.is_active == 'true')"
    )

    category = relationship(
        "Category", lazy="select",
        primaryjoin="and_(Category.id == Experience.category_id, "
                    "Category.is_active == 'true')",
        uselist=False
    )

    slots = relationship(
        "ExperienceSlot", order_by=ExperienceSlot.start_time, lazy="select",
        primaryjoin="and_(Experience.id == ExperienceSlot.experience_id, "
                    "ExperienceSlot.is_active == 'true', "
                    "ExperienceSlot.start_time >= func.now())",
    )
