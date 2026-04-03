from pydantic import BaseModel


class AgentProposeRequest(BaseModel):
    name: str
    description: str
    model: str
    skills: list[str]


class AgentRejectRequest(BaseModel):
    reason: str
