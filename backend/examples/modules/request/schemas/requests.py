from pydantic import BaseModel, Field


class UnifiedRequest(BaseModel):
    request: str = Field(max_length=10000)
