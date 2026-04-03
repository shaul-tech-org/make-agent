from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.todo.models import Todo
from app.modules.todo.schemas.responses import TodoResponse


class TodoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, title: str, description: str | None) -> TodoResponse:
        todo = Todo(title=title, description=description)
        self._session.add(todo)
        await self._session.commit()
        await self._session.refresh(todo)
        return self._to_response(todo)

    async def find_all(self) -> list[TodoResponse]:
        result = await self._session.execute(select(Todo).order_by(Todo.id))
        return [self._to_response(t) for t in result.scalars().all()]

    async def find_by_id(self, todo_id: int) -> TodoResponse | None:
        todo = await self._session.get(Todo, todo_id)
        return self._to_response(todo) if todo else None

    async def update(self, todo_id: int, **fields) -> TodoResponse | None:
        todo = await self._session.get(Todo, todo_id)
        if not todo:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(todo, key, value)
        await self._session.commit()
        await self._session.refresh(todo)
        return self._to_response(todo)

    async def delete(self, todo_id: int) -> bool:
        todo = await self._session.get(Todo, todo_id)
        if not todo:
            return False
        await self._session.delete(todo)
        await self._session.commit()
        return True

    @staticmethod
    def _to_response(todo: Todo) -> TodoResponse:
        return TodoResponse(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
        )
