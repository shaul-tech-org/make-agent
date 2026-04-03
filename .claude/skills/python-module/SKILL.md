---
name: python-module
description: "새 FastAPI 모듈 scaffold 생성. DB 모델 + async CRUD + 커스텀 예외 + TDD 테스트까지 자동 생성."
user-invocable: true
argument-hint: "[모듈명 (영어 소문자, 단수형)]"
---

# /python-module — 모듈 Scaffold 생성

새 FastAPI 모듈의 전체 파일 구조를 자동으로 생성한다.
DB 모델, async repository, 커스텀 예외, TDD 테스트를 포함한다.

## 필수 전제조건

/project-context를 참조하라 — 공통 원칙, 레이어 분리 규칙 포함.

## 입력

모듈명 (영어 소문자, 단수형). 예: `todo`, `user`, `notification`

## 생성 구조

```
app/modules/{module}/
├── __init__.py
├── models.py              ← SQLAlchemy 모델
├── router.py              ← Controller (Depends 주입)
├── service.py             ← Service (async)
├── repository.py          ← Repository (async, session 주입)
├── exceptions.py          ← 모듈 커스텀 예외
└── schemas/
    ├── __init__.py
    ├── requests.py        ← CreateRequest, UpdateRequest (Field 검증)
    └── responses.py       ← Response

tests/test_{module}.py     ← TDD 테스트
```

## 생성 템플릿

### `models.py`
```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel


class {Module}(BaseModel):
    __tablename__ = "{module}s"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
```

### `exceptions.py`
```python
from app.core.exceptions import NotFoundException


class {Module}NotFoundException(NotFoundException):
    def __init__(self, {module}_id: int):
        super().__init__(resource="{Module}", resource_id={module}_id)
```

### `schemas/requests.py`
```python
from pydantic import BaseModel, Field


class {Module}CreateRequest(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None


class {Module}UpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
```

### `schemas/responses.py`
```python
from pydantic import BaseModel


class {Module}Response(BaseModel):
    id: int
    name: str
    description: str | None
```

### `repository.py`
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.{module}.models import {Module}
from app.modules.{module}.schemas.responses import {Module}Response


class {Module}Repository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, name: str, description: str | None) -> {Module}Response:
        item = {Module}(name=name, description=description)
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return self._to_response(item)

    async def find_all(self) -> list[{Module}Response]:
        result = await self._session.execute(select({Module}).order_by({Module}.id))
        return [self._to_response(i) for i in result.scalars().all()]

    async def find_by_id(self, item_id: int) -> {Module}Response | None:
        item = await self._session.get({Module}, item_id)
        return self._to_response(item) if item else None

    async def update(self, item_id: int, **fields) -> {Module}Response | None:
        item = await self._session.get({Module}, item_id)
        if not item:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(item, key, value)
        await self._session.commit()
        await self._session.refresh(item)
        return self._to_response(item)

    async def delete(self, item_id: int) -> bool:
        item = await self._session.get({Module}, item_id)
        if not item:
            return False
        await self._session.delete(item)
        await self._session.commit()
        return True

    @staticmethod
    def _to_response(item: {Module}) -> {Module}Response:
        return {Module}Response(id=item.id, name=item.name, description=item.description)
```

### `service.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.{module}.repository import {Module}Repository
from app.modules.{module}.schemas.requests import {Module}CreateRequest, {Module}UpdateRequest
from app.modules.{module}.schemas.responses import {Module}Response


class {Module}Service:
    def __init__(self, session: AsyncSession):
        self._repo = {Module}Repository(session)

    async def create(self, data: {Module}CreateRequest) -> {Module}Response:
        return await self._repo.create(name=data.name, description=data.description)

    async def list_all(self) -> list[{Module}Response]:
        return await self._repo.find_all()

    async def get(self, item_id: int) -> {Module}Response | None:
        return await self._repo.find_by_id(item_id)

    async def update(self, item_id: int, data: {Module}UpdateRequest) -> {Module}Response | None:
        fields = data.model_dump(exclude_none=True)
        if not fields:
            return await self._repo.find_by_id(item_id)
        return await self._repo.update(item_id, **fields)

    async def delete(self, item_id: int) -> bool:
        return await self._repo.delete(item_id)
```

### `router.py`
```python
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.{module}.exceptions import {Module}NotFoundException
from app.modules.{module}.schemas.requests import {Module}CreateRequest, {Module}UpdateRequest
from app.modules.{module}.schemas.responses import {Module}Response
from app.modules.{module}.service import {Module}Service

router = APIRouter(prefix="/api/v1/{module}s", tags=["{module}s"])


def _service(session: AsyncSession = Depends(get_session)) -> {Module}Service:
    return {Module}Service(session)


@router.post("", status_code=201, response_model={Module}Response)
async def create_{module}(data: {Module}CreateRequest, svc: {Module}Service = Depends(_service)):
    return await svc.create(data)


@router.get("", response_model=list[{Module}Response])
async def list_{module}s(svc: {Module}Service = Depends(_service)):
    return await svc.list_all()


@router.get("/{{item_id}}", response_model={Module}Response)
async def get_{module}(item_id: int, svc: {Module}Service = Depends(_service)):
    item = await svc.get(item_id)
    if not item:
        raise {Module}NotFoundException(item_id)
    return item


@router.put("/{{item_id}}", response_model={Module}Response)
async def update_{module}(item_id: int, data: {Module}UpdateRequest, svc: {Module}Service = Depends(_service)):
    item = await svc.update(item_id, data)
    if not item:
        raise {Module}NotFoundException(item_id)
    return item


@router.delete("/{{item_id}}", status_code=204)
async def delete_{module}(item_id: int, svc: {Module}Service = Depends(_service)):
    if not await svc.delete(item_id):
        raise {Module}NotFoundException(item_id)
    return Response(status_code=204)
```

### `tests/test_{module}.py`
```python
import pytest

pytest.importorskip("app.modules.{module}.router")


@pytest.mark.asyncio
async def test_create_{module}(client):
    response = await client.post("/api/v1/{module}s", json={
        "name": "테스트",
        "description": "설명",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "테스트"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_{module}s(client):
    await client.post("/api/v1/{module}s", json={"name": "항목1"})
    await client.post("/api/v1/{module}s", json={"name": "항목2"})
    response = await client.get("/api/v1/{module}s")
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_get_{module}(client):
    create = await client.post("/api/v1/{module}s", json={"name": "조회 대상"})
    item_id = create.json()["id"]
    response = await client.get(f"/api/v1/{module}s/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "조회 대상"


@pytest.mark.asyncio
async def test_get_{module}_not_found(client):
    response = await client.get("/api/v1/{module}s/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_{module}(client):
    create = await client.post("/api/v1/{module}s", json={"name": "수정 전"})
    item_id = create.json()["id"]
    response = await client.put(f"/api/v1/{module}s/{item_id}", json={"name": "수정 후"})
    assert response.status_code == 200
    assert response.json()["name"] == "수정 후"


@pytest.mark.asyncio
async def test_delete_{module}(client):
    create = await client.post("/api/v1/{module}s", json={"name": "삭제 대상"})
    item_id = create.json()["id"]
    response = await client.delete(f"/api/v1/{module}s/{item_id}")
    assert response.status_code == 204
    assert (await client.get(f"/api/v1/{module}s/{item_id}")).status_code == 404
```

## 생성 후 안내

1. **라우터 자동 등록**: main.py의 `_auto_discover_routers()`가 자동으로 발견하므로 별도 등록 불필요
2. **Alembic 마이그레이션 생성**:
   ```bash
   cd backend
   .venv/bin/alembic revision --autogenerate -m "create_{module}s_table"
   .venv/bin/alembic upgrade head
   ```
3. **테스트 실행**: `.venv/bin/python -m pytest tests/test_{module}.py -v`

## 변수 치환 규칙

- `{module}`: 입력된 모듈명 (소문자, 예: `todo`)
- `{Module}`: PascalCase (예: `Todo`)
- `{module}s`: 복수형 (예: `todos`)
