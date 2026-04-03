import logging

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.metrics import error_metrics

logger = structlog.get_logger("scag.error")


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = _get_request_id(request)
        error_metrics.record(exc.status_code, request.url.path, type(exc).__name__)
        logger.warning(
            "app_error",
            method=request.method,
            path=request.url.path,
            status_code=exc.status_code,
            error=exc.message,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _get_request_id(request)
        error_metrics.record(500, request.url.path, type(exc).__name__)
        logger.error(
            "unhandled_error",
            method=request.method,
            path=request.url.path,
            exception_type=type(exc).__name__,
            error=str(exc),
            request_id=request_id,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if logging.getLogger().isEnabledFor(logging.DEBUG) else "An unexpected error occurred",
                "status_code": 500,
                "request_id": request_id,
            },
        )
