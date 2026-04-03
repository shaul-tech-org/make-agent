from pydantic import BaseModel, Field


class DelegationRequest(BaseModel):
    request: str = Field(max_length=10000)
