import logging
import sys
import time
import uuid

import structlog
from fastapi import FastAPI, Request, Response

from app.config import settings


def setup_logging() -> None:
    """structlog 기반 로깅 설정.

    개발 모드: 컬러 콘솔 출력
    프로덕션 모드: JSON 구조화 출력
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.debug:
        # 개발 모드: 컬러 콘솔
        renderer = structlog.dev.ConsoleRenderer()
    else:
        # 프로덕션: JSON
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # scag 네임스페이스
    scag_logger = logging.getLogger("scag")
    scag_logger.setLevel(log_level)
    scag_logger.propagate = True

    # uvicorn 로그 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def register_request_logging(app: FastAPI) -> None:
    logger = structlog.get_logger("scag.request")

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=round(duration_ms, 1),
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        if request.url.path not in ("/health", "/docs", "/redoc", "/openapi.json"):
            logger.info(
                "request_handled",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 1),
            )

        response.headers["X-Request-Id"] = request_id
        return response
