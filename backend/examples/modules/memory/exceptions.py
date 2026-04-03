from app.core.exceptions import NotFoundException


class MemoryNotFoundException(NotFoundException):
    def __init__(self, agent: str, key: str):
        super().__init__(resource="Memory", resource_id=f"{agent}/{key}")
