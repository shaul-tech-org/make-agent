from app.core.exceptions import NotFoundException


class TodoNotFoundException(NotFoundException):
    def __init__(self, todo_id: int):
        super().__init__(resource="Todo", resource_id=todo_id)
