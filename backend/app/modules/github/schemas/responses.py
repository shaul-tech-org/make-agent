from pydantic import BaseModel


class GitHubLoadResponse(BaseModel):
    owner: str
    repo: str
    branch: str | None = None
    claude_dir_exists: bool


class FileTreeItem(BaseModel):
    path: str
    type: str  # "file" | "dir"
    size: int | None = None


class FileTreeResponse(BaseModel):
    files: list[FileTreeItem]


class FileContentResponse(BaseModel):
    path: str
    content: str
    size: int


class AgentResponse(BaseModel):
    name: str
    description: str
    model: str
    memory: str | None = None
    body: str
    file_path: str


class SkillResponse(BaseModel):
    name: str
    description: str
    user_invocable: bool = False
    argument_hint: str | None = None
    body: str
    references: list[str] = []
    file_path: str


class RuleResponse(BaseModel):
    name: str
    category: str
    paths: list[str] = []
    body: str
    file_path: str
    always_loaded: bool


class DiagramNode(BaseModel):
    id: str
    type: str  # "agent", "skill", "rule"
    name: str
    label: str
    metadata: dict = {}


class DiagramEdge(BaseModel):
    source: str
    target: str
    type: str  # "hierarchy", "uses_skill", "rule_scope", "skill_dep"
    label: str = ""


class DiagramResponse(BaseModel):
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]
    mermaid: str
    logs: list[str]
