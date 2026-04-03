import base64
import re
from urllib.parse import urlparse

import frontmatter
import httpx

from app.config import settings
from app.modules.github.exceptions import (
    GitHubApiException,
    InvalidGitHubUrlException,
    NoProjectLoadedException,
)
from app.modules.github.schemas.responses import (
    AgentResponse,
    DiagramEdge,
    DiagramNode,
    DiagramResponse,
    FileContentResponse,
    FileTreeItem,
    FileTreeResponse,
    GitHubLoadResponse,
    RuleResponse,
    SkillResponse,
)

GITHUB_API = "https://api.github.com"


class GitHubService:
    def __init__(self):
        self._owner: str | None = None
        self._repo: str | None = None
        self._branch: str | None = None
        self._token: str | None = None
        self._tree_cache: list[dict] | None = None

    def _headers(self) -> dict:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def parse_url(self, url: str) -> tuple[str, str, str | None]:
        parsed = urlparse(url)
        if parsed.hostname not in ("github.com", "www.github.com"):
            raise InvalidGitHubUrlException(url)

        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) < 2:
            raise InvalidGitHubUrlException(url)

        owner, repo = parts[0], parts[1]
        branch = None
        if len(parts) >= 4 and parts[2] == "tree":
            branch = parts[3]

        return owner, repo, branch

    async def load(self, url: str, token: str | None = None) -> GitHubLoadResponse:
        owner, repo, branch = self.parse_url(url)
        self._owner = owner
        self._repo = repo
        self._branch = branch
        self._token = token or settings.github_token or None
        self._tree_cache = None

        # .claude 디렉토리 존재 여부 확인
        claude_exists = await self._check_claude_dir()

        return GitHubLoadResponse(
            owner=owner,
            repo=repo,
            branch=branch,
            claude_dir_exists=claude_exists,
        )

    async def _check_claude_dir(self) -> bool:
        try:
            await self._get_contents(".claude")
            return True
        except GitHubApiException:
            return False

    async def _get_contents(self, path: str) -> list[dict]:
        self._ensure_loaded()
        url = f"{GITHUB_API}/repos/{self._owner}/{self._repo}/contents/{path}"
        params = {}
        if self._branch:
            params["ref"] = self._branch

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            if resp.status_code == 404:
                raise GitHubApiException(f"Path not found: {path}", status_code=404)
            if resp.status_code != 200:
                raise GitHubApiException(f"GitHub API error: {resp.status_code}")
            return resp.json()

    async def _get_file_content(self, path: str) -> str:
        self._ensure_loaded()
        url = f"{GITHUB_API}/repos/{self._owner}/{self._repo}/contents/{path}"
        params = {}
        if self._branch:
            params["ref"] = self._branch

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            if resp.status_code != 200:
                raise GitHubApiException(f"Failed to read file: {path}")
            data = resp.json()
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
            return content

    async def get_tree(self) -> FileTreeResponse:
        self._ensure_loaded()
        items = await self._get_tree_recursive(".claude")
        return FileTreeResponse(files=items)

    async def _get_tree_recursive(self, path: str) -> list[FileTreeItem]:
        try:
            contents = await self._get_contents(path)
        except GitHubApiException:
            return []

        if isinstance(contents, dict):
            # single file
            return [FileTreeItem(path=contents["path"], type="file", size=contents.get("size"))]

        items: list[FileTreeItem] = []
        for item in contents:
            items.append(FileTreeItem(
                path=item["path"],
                type=item["type"],
                size=item.get("size"),
            ))
            if item["type"] == "dir":
                sub = await self._get_tree_recursive(item["path"])
                items.extend(sub)
        return items

    async def get_file(self, path: str) -> FileContentResponse:
        content = await self._get_file_content(path)
        return FileContentResponse(path=path, content=content, size=len(content))

    async def get_agents(self) -> list[AgentResponse]:
        self._ensure_loaded()
        agents: list[AgentResponse] = []
        try:
            contents = await self._get_contents(".claude/agents")
        except GitHubApiException:
            return []

        for item in contents:
            if item["type"] != "file" or not item["name"].endswith(".md"):
                continue
            try:
                raw = await self._get_file_content(item["path"])
                post = frontmatter.loads(raw)
                agents.append(AgentResponse(
                    name=post.metadata.get("name", item["name"].replace(".md", "")),
                    description=post.metadata.get("description", ""),
                    model=post.metadata.get("model", ""),
                    memory=post.metadata.get("memory"),
                    body=post.content,
                    file_path=item["path"],
                ))
            except Exception:
                continue
        return agents

    async def get_skills(self) -> list[SkillResponse]:
        self._ensure_loaded()
        skills: list[SkillResponse] = []
        try:
            contents = await self._get_contents(".claude/skills")
        except GitHubApiException:
            return []

        for item in contents:
            if item["type"] != "dir":
                continue
            try:
                raw = await self._get_file_content(f"{item['path']}/SKILL.md")
                post = frontmatter.loads(raw)

                # reference 파일 목록
                refs: list[str] = []
                try:
                    ref_contents = await self._get_contents(f"{item['path']}/reference")
                    refs = [r["name"] for r in ref_contents if r["type"] == "file"]
                except GitHubApiException:
                    pass

                skills.append(SkillResponse(
                    name=post.metadata.get("name", item["name"]),
                    description=post.metadata.get("description", ""),
                    user_invocable=post.metadata.get("user-invocable", False),
                    argument_hint=post.metadata.get("argument-hint"),
                    body=post.content,
                    references=refs,
                    file_path=f"{item['path']}/SKILL.md",
                ))
            except Exception:
                continue
        return skills

    async def get_rules(self) -> list[RuleResponse]:
        self._ensure_loaded()
        rules: list[RuleResponse] = []
        await self._scan_rules(".claude/rules", "", rules)
        return rules

    async def _scan_rules(self, path: str, category: str, rules: list[RuleResponse]) -> None:
        try:
            contents = await self._get_contents(path)
        except GitHubApiException:
            return

        for item in contents:
            if item["type"] == "dir":
                sub_cat = f"{category}/{item['name']}" if category else item["name"]
                await self._scan_rules(item["path"], sub_cat, rules)
            elif item["type"] == "file" and item["name"].endswith(".md"):
                try:
                    raw = await self._get_file_content(item["path"])
                    post = frontmatter.loads(raw)
                    paths = post.metadata.get("paths", [])
                    rules.append(RuleResponse(
                        name=item["name"].replace(".md", ""),
                        category=category,
                        paths=paths if isinstance(paths, list) else [],
                        body=post.content,
                        file_path=item["path"],
                        always_loaded=len(paths) == 0 if isinstance(paths, list) else True,
                    ))
                except Exception:
                    continue

    async def get_diagram(self) -> DiagramResponse:
        self._ensure_loaded()
        logs: list[str] = []

        logs.append("[1/5] 에이전트, 스킬, 규칙 데이터 수집 시작")
        agents = await self.get_agents()
        logs.append(f"  → 에이전트 {len(agents)}개 로드 완료")
        skills = await self.get_skills()
        logs.append(f"  → 스킬 {len(skills)}개 로드 완료")
        rules = await self.get_rules()
        logs.append(f"  → 규칙 {len(rules)}개 로드 완료")

        nodes: list[DiagramNode] = []
        edges: list[DiagramEdge] = []
        agent_names = {a.name for a in agents}
        skill_names = {s.name for s in skills}

        # --- 노드 생성 ---
        logs.append("[2/5] 노드 생성 중")
        for a in agents:
            nodes.append(DiagramNode(
                id=f"agent_{a.name}", type="agent", name=a.name,
                label=f"{a.name}\\n({a.model})",
                metadata={"model": a.model, "description": a.description},
            ))
        for s in skills:
            nodes.append(DiagramNode(
                id=f"skill_{s.name}", type="skill", name=s.name,
                label=s.name,
                metadata={"user_invocable": s.user_invocable, "description": s.description},
            ))
        for r in rules:
            nodes.append(DiagramNode(
                id=f"rule_{r.name}", type="rule", name=r.name,
                label=f"{r.name}\\n[{r.category}]",
                metadata={"category": r.category, "always_loaded": r.always_loaded},
            ))
        logs.append(f"  → 총 {len(nodes)}개 노드 생성")

        # --- 관계 분석 ---
        logs.append("[3/5] 에이전트 간 계층 관계 분석 중")
        for a in agents:
            body_lower = a.body.lower()
            for other in agent_names:
                if other != a.name and other in body_lower:
                    edges.append(DiagramEdge(
                        source=f"agent_{a.name}", target=f"agent_{other}",
                        type="hierarchy", label="delegates",
                    ))
                    logs.append(f"  → {a.name} --delegates--> {other}")

        logs.append("[4/5] 스킬 참조 관계 분석 중")
        for s in skills:
            body_lower = s.body.lower()
            # 스킬 → 에이전트 참조
            for aname in agent_names:
                if aname in body_lower:
                    edges.append(DiagramEdge(
                        source=f"skill_{s.name}", target=f"agent_{aname}",
                        type="uses_agent", label="used by",
                    ))
                    logs.append(f"  → 스킬 '{s.name}' → 에이전트 '{aname}'")
            # 스킬 → 스킬 의존성 (/skill-name 패턴)
            for other in skill_names:
                if other != s.name and f"/{other}" in s.body:
                    edges.append(DiagramEdge(
                        source=f"skill_{s.name}", target=f"skill_{other}",
                        type="skill_dep", label="depends",
                    ))
                    logs.append(f"  → 스킬 '{s.name}' --depends--> '{other}'")

        logs.append("[5/5] 규칙 적용 범위 분석 중")
        for r in rules:
            if r.always_loaded:
                logs.append(f"  → 규칙 '{r.name}' (항상 로드)")
            else:
                for p in r.paths:
                    if "*.py" in p:
                        # Python 규칙 → 백엔드 에이전트 연결
                        for aname in agent_names:
                            if "be" in aname or "backend" in aname:
                                edges.append(DiagramEdge(
                                    source=f"rule_{r.name}", target=f"agent_{aname}",
                                    type="rule_scope", label=p,
                                ))
                    elif "*.ts" in p:
                        for aname in agent_names:
                            if "fe" in aname or "frontend" in aname:
                                edges.append(DiagramEdge(
                                    source=f"rule_{r.name}", target=f"agent_{aname}",
                                    type="rule_scope", label=p,
                                ))
                logs.append(f"  → 규칙 '{r.name}' paths={r.paths}")

        # --- Mermaid 생성 ---
        mermaid = self._build_mermaid(agents, skills, rules, edges)
        logs.append(f"[완료] Mermaid 다이어그램 생성 — 노드 {len(nodes)}, 엣지 {len(edges)}")

        return DiagramResponse(nodes=nodes, edges=edges, mermaid=mermaid, logs=logs)

    def _build_mermaid(
        self,
        agents: list[AgentResponse],
        skills: list[SkillResponse],
        rules: list[RuleResponse],
        edges: list[DiagramEdge],
    ) -> str:
        lines = ["graph TD"]

        # 스타일 클래스
        lines.append("    classDef agent fill:#3b82f6,stroke:#1d4ed8,color:#fff")
        lines.append("    classDef skill fill:#10b981,stroke:#047857,color:#fff")
        lines.append("    classDef rule fill:#f59e0b,stroke:#b45309,color:#fff")

        # 에이전트 노드
        for a in agents:
            safe = a.name.replace("-", "_")
            lines.append(f'    agent_{safe}["{a.name}<br/><small>{a.model}</small>"]:::agent')

        # 스킬 노드
        for s in skills:
            safe = s.name.replace("-", "_")
            inv = "⚡" if s.user_invocable else ""
            lines.append(f'    skill_{safe}(["{inv}{s.name}"]):::skill')

        # 규칙 노드
        for r in rules:
            safe = r.name.replace("-", "_")
            scope = "🌐" if r.always_loaded else "📁"
            lines.append(f'    rule_{safe}{{{{"{scope}{r.name}"}}}}):::rule')

        # 엣지
        for e in edges:
            src = e.source.replace("-", "_")
            tgt = e.target.replace("-", "_")
            if e.label:
                lines.append(f"    {src} -->|{e.label}| {tgt}")
            else:
                lines.append(f"    {src} --> {tgt}")

        return "\n".join(lines)

    def _ensure_loaded(self) -> None:
        if not self._owner or not self._repo:
            raise NoProjectLoadedException()


github_service = GitHubService()
