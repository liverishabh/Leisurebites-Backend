from sqlalchemy import Column, INT, NUMERIC, TEXT, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import true, false, text

from app.models import BaseModel


class ArtistSlot(BaseModel):
    id = Column(INT, primary_key=True, autoincrement=True, nullable=False)
    artist_id = Column(INT, ForeignKey("supplier.id"), nullable=False)
    price = Column(NUMERIC(10, 2), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    venue_address = Column(TEXT)
    venue_city = Column(String(50))
    venue_state = Column(String(50))
    venue_country = Column(String(50))
    is_booked = Column(Boolean(), server_default=false(), nullable=False)
    is_active = Column(Boolean(), server_default=true(), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)

    artist = relationship(
        "Supplier", lazy="select", uselist=False
    )
