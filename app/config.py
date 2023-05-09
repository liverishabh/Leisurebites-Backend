from typing import Optional, Dict, Any, List

from pydantic import BaseSettings, AnyUrl, validator, PostgresDsn, AnyHttpUrl


class AppConfig(BaseSettings):
    PROJECT_NAME: str = "LeisureBites Backend"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    SECRET_KEY: str

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_READ_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None
    SQLALCHEMY_READ_DATABASE_URI: Optional[AnyUrl] = None
    SQLALCHEMY_ECHO: bool = False

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v and isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("SQLALCHEMY_READ_DATABASE_URI", pre=True)
    @classmethod
    def assemble_read_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v and isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_READ_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    MINIMUM_SIZE_FOR_COMPRESSION: int = 1000

    CLOUD_STORAGE_PROVIDER: str = "aws"

    GCS_URI_BASE: str = ""
    GCS_BUCKET_NAME: str = ""
    GCS_BUCKET_URL: str = ""

    @validator("GCS_BUCKET_URL", pre=True)
    @classmethod
    def set_gcs_bucket_url(cls, v: Optional[str], values: dict) -> Any:
        return f"{values['GCS_URI_BASE']}/{values['GCS_BUCKET_NAME']}"

    S3_URI_BASE: str
    S3_BUCKET_NAME: str
    S3_BUCKET_URL: str = ""

    @validator("S3_BUCKET_URL", pre=True)
    @classmethod
    def set_s3_bucket_url(cls, v: Optional[str], values: dict) -> Any:
        return f"{values['S3_URI_BASE']}/{values['S3_BUCKET_NAME']}"

    class Config:
        case_sensitive = True
        env_file = ".env"

    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str = ""
    EMAIL_SERVICE_PROVIDER: str = "ses"

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 15


config = AppConfig()
