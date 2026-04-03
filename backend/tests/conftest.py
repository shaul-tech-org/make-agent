import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_session
from app.core.metrics import error_metrics
from app.main import app as fastapi_app

# DB 모델 자동 등록 — modules/ 아래 models.py가 있는 모듈을 동적 import
import importlib
import pkgutil
import app.modules as _modules_pkg

for _importer, _name, _ispkg in pkgutil.iter_modules(_modules_pkg.__path__):
    try:
        importlib.import_module(f"app.modules.{_name}.models")
    except (ImportError, ModuleNotFoundError):
        pass

# 테스트용 SQLite (in-memory, StaticPool로 공유)
test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_session():
    async with test_session_factory() as session:
        yield session


fastapi_app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
async def setup_db():
    """매 테스트마다 DB 테이블 생성 → 테스트 → 삭제."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def reset_in_memory_stores():
    """인메모리 저장소 초기화 + 메트릭 리셋."""
    # 동적으로 존재하는 인메모리 repository만 리셋
    _try_clear("app.modules.agent.repository", "agent_repository")
    _try_clear("app.modules.communication.repository", "communication_repository")
    _try_clear("app.modules.memory.repository", "memory_repository")
    error_metrics.reset()


def _try_clear(module_path: str, attr_name: str) -> None:
    try:
        mod = importlib.import_module(module_path)
        repo = getattr(mod, attr_name, None)
        if repo and hasattr(repo, "clear"):
            repo.clear()
    except (ImportError, ModuleNotFoundError):
        pass


@pytest.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
