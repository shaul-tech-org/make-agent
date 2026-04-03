from app.core.exceptions import ConflictException, NotFoundException


class AgentNotFoundException(NotFoundException):
    def __init__(self, agent_id: int):
        super().__init__(resource="Agent", resource_id=agent_id)


class AgentAlreadyExistsException(ConflictException):
    def __init__(self, name: str):
        super().__init__(message=f"Agent '{name}' already exists")
