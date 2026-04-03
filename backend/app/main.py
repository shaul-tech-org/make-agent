import importlib
import pkgutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.error_handler import register_error_handlers
from app.core.logging import register_request_logging, setup_logging
from app.core.metrics import error_metrics
from app.core.security import register_security_headers

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_request_logging(app)
register_security_headers(app)


def _auto_discover_routers() -> None:
    """app/modules/ 하위의 모든 모듈에서 router를 자동 발견하여 등록."""
    import app.modules as modules_pkg

    for _importer, module_name, _ispkg in pkgutil.iter_modules(modules_pkg.__path__):
        try:
            router_module = importlib.import_module(f"app.modules.{module_name}.router")
            if hasattr(router_module, "router"):
                app.include_router(router_module.router)
        except (ImportError, ModuleNotFoundError):
            pass


_auto_discover_routers()


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}


@app.get("/api/v1/metrics")
async def get_metrics():
    return error_metrics.snapshot()


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
