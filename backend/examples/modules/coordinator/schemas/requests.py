from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    request: str = Field(max_length=10000)
