# FastAPI 고급 패턴

## 의존성 주입 패턴

```python
# dependencies.py
from fastapi import Depends
from app.modules.todo.service import TodoService, todo_service

def get_todo_service() -> TodoService:
    return todo_service
```

```python
# router.py
@router.post("", status_code=201)
async def create(data: CreateRequest, svc: TodoService = Depends(get_todo_service)):
    return svc.create(data)
```

## 예외 처리 패턴

```python
# exceptions.py
class TodoNotFoundException(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        self.message = f"Todo {todo_id} not found"
```

```python
# router.py — HTTPException 변환은 router에서만
from app.modules.todo.exceptions import TodoNotFoundException

@router.get("/{item_id}")
async def get(item_id: int):
    try:
        return svc.get(item_id)
    except TodoNotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
```

## 응답 모델 패턴

```python
# 단일 응답
response_model=TodoResponse

# 목록 응답
response_model=list[TodoResponse]

# 페이지네이션 응답
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
```

## 복잡도 확장 기준

| 기준 | 추가 파일 |
|------|----------|
| 엔드포인트 5개+ | exceptions.py, dependencies.py |
| 모듈 2개+ | app/core/ (공통 레이어) |
| DB 연동 | models.py, alembic/ |
| 테스트 15개+ | tests/unit/, tests/integration/ |
