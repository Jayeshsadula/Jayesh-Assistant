"""
JAYESH Assistant — FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.config import get_settings
from app.database import close_mongo_connection, connect_to_mongo
from app.utils.exceptions import AppError
from app.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app.starting", app_name=settings.app_name, env=settings.app_env)
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    logger.info("app.shutdown_complete")


app = FastAPI(
    title=settings.app_name,
    description="A fully private, self-hosted AI assistant powered by local LLMs.",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.app_debug,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "request.app_error",
        path=str(request.url.path),
        error_code=exc.error_code,
        message=exc.message,
    )
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("request.unhandled_error", path=str(request.url.path), error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred. Please try again.",
                "details": {},
            }
        },
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"message": f"{settings.app_name} API is running.", "docs": "/docs"}
