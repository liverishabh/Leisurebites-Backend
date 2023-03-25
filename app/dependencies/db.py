from typing import Generator

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import sessionmaker, Session

from app.config import config

ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_size": 10,
    "pool_recycle": 300,
    "max_overflow": 20,
    "pool_timeout": 30,
}

READ_DB_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_size": 20,
    "pool_recycle": 300,
    "max_overflow": 50,
    "pool_timeout": 30,
}

db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI, **ENGINE_OPTIONS, echo=config.SQLALCHEMY_ECHO)
read_db_engine = create_engine(config.SQLALCHEMY_READ_DATABASE_URI, **READ_DB_ENGINE_OPTIONS, echo=config.SQLALCHEMY_ECHO)

SessionLocal = sessionmaker(
    bind=db_engine,
    autocommit=False,
    autoflush=False,
)
ReadSessionLocal = sessionmaker(
    bind=read_db_engine
)


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_read_db() -> Generator[Session, None, None]:
    try:
        db = ReadSessionLocal()
        yield db
    finally:
        db.close()
