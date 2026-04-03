# pytest 테스트 패턴 카탈로그

## 기본 구조

```python
# tests/conftest.py
import pytest
from app.modules.todo.repository import todo_repository

@pytest.fixture(autouse=True)
def reset_stores():
    todo_repository.clear()
    yield
```

## API 테스트 패턴

### 성공 케이스
```python
def test_create_returns_201(client):
    response = client.post("/api/v1/todos", json={"title": "Test"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test"
    assert "id" in response.json()
```

### 실패 케이스
```python
def test_get_nonexistent_returns_404(client):
    response = client.get("/api/v1/todos/999")
    assert response.status_code == 404

def test_create_invalid_returns_422(client):
    response = client.post("/api/v1/todos", json={})
    assert response.status_code == 422
```

### CRUD 전체 흐름
```python
def test_crud_flow(client):
    # Create
    res = client.post("/api/v1/todos", json={"title": "Test"})
    todo_id = res.json()["id"]

    # Read
    res = client.get(f"/api/v1/todos/{todo_id}")
    assert res.json()["title"] == "Test"

    # Update
    res = client.put(f"/api/v1/todos/{todo_id}", json={"title": "Updated"})
    assert res.json()["title"] == "Updated"

    # Delete
    res = client.delete(f"/api/v1/todos/{todo_id}")
    assert res.status_code == 204

    # Verify deleted
    res = client.get(f"/api/v1/todos/{todo_id}")
    assert res.status_code == 404
```

## 테스트 격리 원칙

**DO**: autouse fixture로 각 테스트 전 상태 초기화
**DO**: 각 테스트가 독립적으로 실행 가능
**DON'T**: 테스트 간 데이터 공유 (순서 의존)
**DON'T**: 외부 서비스에 의존하는 테스트 (mock 사용)
