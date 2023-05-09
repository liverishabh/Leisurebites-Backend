from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.testclient import TestClient

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id

from app.config import config
from app.controller.api_v1.api import api_router
from app.dependencies.logger import ApplicationLogger

logger = ApplicationLogger.get_logger(__name__)

app = FastAPI(title=config.PROJECT_NAME, docs_url=f"{config.API_V1_PREFIX}/docs")
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=config.MINIMUM_SIZE_FOR_COMPRESSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception occurred, Message: {str(exc.detail)}, Status Code: {exc.status_code}")
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.detail), "successful": False})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger.error(f"Invalid Request Payload, Errors: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"message": "Input payload validation failed", "errors": exc.errors(), "successful": False},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Some Internal Error occurred: %s", exc)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "successful": False},
                        headers={
                            'X-Request-ID': correlation_id.get() or "",
                            'Access-Control-Expose-Headers': 'X-Request-ID'
                        })

app.include_router(api_router, prefix=config.API_V1_PREFIX)

# test_client = TestClient(app)
