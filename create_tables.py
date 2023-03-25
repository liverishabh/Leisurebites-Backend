from app.dependencies.db import db_engine
from app.models import BaseModel

if __name__ == "__main__":
    BaseModel.metadata.create_all(db_engine)
