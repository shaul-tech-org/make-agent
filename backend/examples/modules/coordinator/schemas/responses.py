from pydantic import BaseModel


class RouteResponse(BaseModel):
    request: str
    category: str
    complexity: str
    agent: str
