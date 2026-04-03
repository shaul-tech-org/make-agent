from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.todo.repository import TodoRepository
from app.modules.todo.schemas.requests import TodoCreateRequest, TodoUpdateRequest
from app.modules.todo.schemas.responses import TodoResponse


class TodoService:
    def __init__(self, session: AsyncSession):
        self._repo = TodoRepository(session)

    async def create(self, data: TodoCreateRequest) -> TodoResponse:
        return await self._repo.create(
            title=data.title,
            description=data.description,
        )

    async def list_all(self) -> list[TodoResponse]:
        return await self._repo.find_all()

    async def get(self, todo_id: int) -> TodoResponse | None:
        return await self._repo.find_by_id(todo_id)

    async def update(self, todo_id: int, data: TodoUpdateRequest) -> TodoResponse | None:
        fields = data.model_dump(exclude_none=True)
        if not fields:
            return await self._repo.find_by_id(todo_id)
        return await self._repo.update(todo_id, **fields)

    async def delete(self, todo_id: int) -> bool:
        return await self._repo.delete(todo_id)
