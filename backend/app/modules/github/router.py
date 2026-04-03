from fastapi import APIRouter

from app.modules.github.schemas.requests import GitHubLoadRequest
from app.modules.github.schemas.responses import (
    AgentResponse,
    FileContentResponse,
    FileTreeResponse,
    GitHubLoadResponse,
    RuleResponse,
    SkillResponse,
)
from app.modules.github.service import github_service

router = APIRouter(prefix="/api/v1/github", tags=["github"])


@router.post("/load", response_model=GitHubLoadResponse)
async def load_project(data: GitHubLoadRequest):
    return await github_service.load(data.url, data.token)


@router.get("/tree", response_model=FileTreeResponse)
async def get_tree():
    return await github_service.get_tree()


@router.get("/file", response_model=FileContentResponse)
async def get_file(path: str):
    return await github_service.get_file(path)


@router.get("/agents", response_model=list[AgentResponse])
async def get_agents():
    return await github_service.get_agents()


@router.get("/skills", response_model=list[SkillResponse])
async def get_skills():
    return await github_service.get_skills()


@router.get("/rules", response_model=list[RuleResponse])
async def get_rules():
    return await github_service.get_rules()
