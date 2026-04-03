import pytest


@pytest.mark.asyncio
async def test_create_todo(client):
    response = await client.post("/api/v1/todos", json={
        "title": "테스트 할 일",
        "description": "설명입니다",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "테스트 할 일"
    assert data["description"] == "설명입니다"
    assert data["completed"] is False
    assert "id" in data


@pytest.mark.asyncio
async def test_create_todo_without_description(client):
    response = await client.post("/api/v1/todos", json={
        "title": "제목만",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_todo_validation_error(client):
    response = await client.post("/api/v1/todos", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_todos(client):
    await client.post("/api/v1/todos", json={"title": "첫 번째"})
    await client.post("/api/v1/todos", json={"title": "두 번째"})

    response = await client.get("/api/v1/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_todo(client):
    create = await client.post("/api/v1/todos", json={"title": "조회 대상"})
    todo_id = create.json()["id"]

    response = await client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "조회 대상"


@pytest.mark.asyncio
async def test_get_todo_not_found(client):
    response = await client.get("/api/v1/todos/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_todo(client):
    create = await client.post("/api/v1/todos", json={"title": "수정 전"})
    todo_id = create.json()["id"]

    response = await client.put(f"/api/v1/todos/{todo_id}", json={
        "title": "수정 후",
        "completed": True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "수정 후"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_update_todo_not_found(client):
    response = await client.put("/api/v1/todos/99999", json={
        "title": "없는 항목",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo(client):
    create = await client.post("/api/v1/todos", json={"title": "삭제 대상"})
    todo_id = create.json()["id"]

    response = await client.delete(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 204

    get_response = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(client):
    response = await client.delete("/api/v1/todos/99999")
    assert response.status_code == 404
