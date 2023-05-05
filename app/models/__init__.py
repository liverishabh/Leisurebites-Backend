import re

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql.schema import MetaData


@as_declarative()
class BaseModel:
    metadata: MetaData
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        """CamelCase __name__ to snake_case __tablename__"""
        return "_".join(x.lower() for x in re.findall(r"[A-Z][a-z]*", self.__name__))


from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.experience import Experience, ExperienceImage, ExperienceSlot
from app.models.category import Category
from app.models.booking import Booking
from app.models.artist_slot import ArtistSlot
from app.models.promo_code import PromoCode
from app.models.payment import Payment
