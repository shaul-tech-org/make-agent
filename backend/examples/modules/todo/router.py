from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.todo.exceptions import TodoNotFoundException
from app.modules.todo.schemas.requests import TodoCreateRequest, TodoUpdateRequest
from app.modules.todo.schemas.responses import TodoResponse
from app.modules.todo.service import TodoService

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


def _service(session: AsyncSession = Depends(get_session)) -> TodoService:
    return TodoService(session)


@router.post("", status_code=201, response_model=TodoResponse)
async def create_todo(data: TodoCreateRequest, svc: TodoService = Depends(_service)):
    return await svc.create(data)


@router.get("", response_model=list[TodoResponse])
async def list_todos(svc: TodoService = Depends(_service)):
    return await svc.list_all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, svc: TodoService = Depends(_service)):
    todo = await svc.get(todo_id)
    if not todo:
        raise TodoNotFoundException(todo_id)
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, data: TodoUpdateRequest, svc: TodoService = Depends(_service)):
    todo = await svc.update(todo_id, data)
    if not todo:
        raise TodoNotFoundException(todo_id)
    return todo


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, svc: TodoService = Depends(_service)):
    if not await svc.delete(todo_id):
        raise TodoNotFoundException(todo_id)
    return Response(status_code=204)
