import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import frontmatter

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
    OrgChartNode,
    OrgChartResponse,
    RuleResponse,
    SkillResponse,
)

CLONE_BASE = Path(tempfile.gettempdir()) / "make-agent-clones"


class GitHubService:
    def __init__(self):
        self._owner: str | None = None
        self._repo: str | None = None
        self._branch: str | None = None
        self._clone_dir: Path | None = None
        self._claude_dir: Path | None = None

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

        # sparse clone .claude directory
        await self._sparse_clone(token)

        claude_exists = self._claude_dir is not None and self._claude_dir.is_dir()

        return GitHubLoadResponse(
            owner=owner,
            repo=repo,
            branch=branch,
            claude_dir_exists=claude_exists,
        )

    async def _sparse_clone(self, token: str | None = None) -> None:
        """Sparse checkout으로 .claude 디렉토리만 clone."""
        effective_token = token or settings.github_token or None
        repo_url = f"https://github.com/{self._owner}/{self._repo}.git"
        if effective_token:
            repo_url = f"https://x-access-token:{effective_token}@github.com/{self._owner}/{self._repo}.git"

        # 클론 디렉토리 (owner/repo 기준으로 캐시)
        clone_dir = CLONE_BASE / f"{self._owner}_{self._repo}"

        if clone_dir.exists():
            # 기존 클론이 있으면 pull
            try:
                await self._run_git(["git", "pull", "--depth", "1"], cwd=clone_dir)
                self._clone_dir = clone_dir
                self._claude_dir = clone_dir / ".claude"
                return
            except GitHubApiException:
                # pull 실패 시 재클론
                shutil.rmtree(clone_dir, ignore_errors=True)

        clone_dir.mkdir(parents=True, exist_ok=True)

        # git clone --depth 1 --filter=blob:none --sparse
        await self._run_git([
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            repo_url, str(clone_dir),
        ])

        # sparse-checkout set .claude
        await self._run_git(
            ["git", "sparse-checkout", "set", ".claude"],
            cwd=clone_dir,
        )

        # branch 지정 시 checkout
        if self._branch:
            await self._run_git(
                ["git", "checkout", self._branch],
                cwd=clone_dir,
            )

        self._clone_dir = clone_dir
        self._claude_dir = clone_dir / ".claude"

    async def _run_git(self, cmd: list[str], cwd: Path | None = None) -> str:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            err = stderr.decode().strip()
            raise GitHubApiException(f"Git error: {err}", status_code=502)
        return stdout.decode().strip()

    def _ensure_loaded(self) -> None:
        if not self._owner or not self._repo or not self._claude_dir:
            raise NoProjectLoadedException()

    def _read_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    async def get_tree(self) -> FileTreeResponse:
        self._ensure_loaded()
        items: list[FileTreeItem] = []
        claude_dir = self._claude_dir
        assert claude_dir is not None
        for p in sorted(claude_dir.rglob("*")):
            rel = str(p.relative_to(self._clone_dir))  # type: ignore
            items.append(FileTreeItem(
                path=rel,
                type="dir" if p.is_dir() else "file",
                size=p.stat().st_size if p.is_file() else None,
            ))
        return FileTreeResponse(files=items)

    async def get_file(self, path: str) -> FileContentResponse:
        self._ensure_loaded()
        assert self._clone_dir is not None
        file_path = self._clone_dir / path
        if not file_path.is_file():
            raise GitHubApiException(f"File not found: {path}", status_code=404)
        content = self._read_file(file_path)
        return FileContentResponse(path=path, content=content, size=len(content))

    async def get_agents(self) -> list[AgentResponse]:
        self._ensure_loaded()
        assert self._claude_dir is not None
        agents_dir = self._claude_dir / "agents"
        if not agents_dir.is_dir():
            return []

        agents: list[AgentResponse] = []
        for f in sorted(agents_dir.glob("*.md")):
            try:
                raw = self._read_file(f)
                post = frontmatter.loads(raw)
                agents.append(AgentResponse(
                    name=post.metadata.get("name", f.stem),
                    description=post.metadata.get("description", ""),
                    model=post.metadata.get("model", ""),
                    memory=post.metadata.get("memory"),
                    body=post.content,
                    file_path=str(f.relative_to(self._clone_dir)),  # type: ignore
                ))
            except Exception:
                continue
        return agents

    async def get_skills(self) -> list[SkillResponse]:
        self._ensure_loaded()
        assert self._claude_dir is not None
        skills_dir = self._claude_dir / "skills"
        if not skills_dir.is_dir():
            return []

        skills: list[SkillResponse] = []
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.is_file():
                continue
            try:
                raw = self._read_file(skill_md)
                post = frontmatter.loads(raw)

                refs: list[str] = []
                ref_dir = d / "reference"
                if ref_dir.is_dir():
                    refs = [r.name for r in sorted(ref_dir.iterdir()) if r.is_file()]

                skills.append(SkillResponse(
                    name=post.metadata.get("name", d.name),
                    description=post.metadata.get("description", ""),
                    user_invocable=post.metadata.get("user-invocable", False),
                    argument_hint=post.metadata.get("argument-hint"),
                    body=post.content,
                    references=refs,
                    file_path=str(skill_md.relative_to(self._clone_dir)),  # type: ignore
                ))
            except Exception:
                continue
        return skills

    async def get_rules(self) -> list[RuleResponse]:
        self._ensure_loaded()
        assert self._claude_dir is not None
        rules_dir = self._claude_dir / "rules"
        if not rules_dir.is_dir():
            return []

        rules: list[RuleResponse] = []
        self._scan_rules_local(rules_dir, "", rules)
        return rules

    def _scan_rules_local(self, path: Path, category: str, rules: list[RuleResponse]) -> None:
        if not path.is_dir():
            return
        for item in sorted(path.iterdir()):
            if item.is_dir():
                sub_cat = f"{category}/{item.name}" if category else item.name
                self._scan_rules_local(item, sub_cat, rules)
            elif item.is_file() and item.suffix == ".md":
                try:
                    raw = self._read_file(item)
                    post = frontmatter.loads(raw)
                    paths = post.metadata.get("paths", [])
                    rules.append(RuleResponse(
                        name=item.stem,
                        category=category,
                        paths=paths if isinstance(paths, list) else [],
                        body=post.content,
                        file_path=str(item.relative_to(self._clone_dir)),  # type: ignore
                        always_loaded=len(paths) == 0 if isinstance(paths, list) else True,
                    ))
                except Exception:
                    continue

    async def get_org_chart(self) -> OrgChartResponse:
        """rules/governance/org-chart.md의 보고 라인 테이블을 파싱하여 조직도 생성."""
        self._ensure_loaded()
        agents = await self.get_agents()
        agent_map = {a.name: a for a in agents}

        # org-chart rule 찾기
        rules = await self.get_rules()
        org_rule = next((r for r in rules if r.name == "org-chart"), None)

        # 보고 라인 파싱
        reports_to: dict[str, str] = {}  # child → parent
        roles: dict[str, str] = {}
        if org_rule:
            for line in org_rule.body.split("\n"):
                line = line.strip()
                if line.startswith("|") and not line.startswith("|-") and "에이전트" not in line and "---" not in line:
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cols) >= 3:
                        agent_name, parent, role = cols[0], cols[1], cols[2]
                        if agent_name in agent_map or agent_name == "coordinator":
                            reports_to[agent_name] = parent
                            roles[agent_name] = role

        # 트리 빌드
        def build_node(name: str) -> OrgChartNode:
            agent = agent_map.get(name)
            model = agent.model if agent else ""
            role = roles.get(name, agent.description if agent else "")
            children_names = [k for k, v in reports_to.items() if v == name]
            children = [build_node(c) for c in children_names]
            return OrgChartNode(name=name, model=model, role=role, children=children)

        # 루트: 사용자 (coordinator의 상급자)
        root = OrgChartNode(
            name="사용자",
            model="board",
            role="프로젝트 오너",
            children=[build_node(k) for k, v in reports_to.items() if v == "사용자"],
        )

        # Mermaid 생성
        mermaid = self._build_org_mermaid(root)

        return OrgChartResponse(tree=root, mermaid=mermaid)

    def _build_org_mermaid(self, root: OrgChartNode) -> str:
        lines = ["graph TD"]
        lines.append("    classDef board fill:#f59e0b,stroke:#b45309,color:#fff,font-weight:bold")
        lines.append("    classDef opus fill:#6366f1,stroke:#4338ca,color:#fff,font-weight:bold")
        lines.append("    classDef sonnet fill:#3b82f6,stroke:#1d4ed8,color:#fff")

        def add_node(node: OrgChartNode) -> None:
            safe = node.name.replace("-", "_").replace(" ", "_")
            role_short = node.role[:20] + "..." if len(node.role) > 20 else node.role
            label = f"{node.name}<br/><small>{role_short}</small>"
            if node.model == "board":
                lines.append(f'    {safe}["{label}"]:::board')
            elif "opus" in node.model:
                lines.append(f'    {safe}["{label}"]:::opus')
            else:
                lines.append(f'    {safe}(["{label}"]):::sonnet')

            for child in node.children:
                child_safe = child.name.replace("-", "_").replace(" ", "_")
                add_node(child)
                lines.append(f"    {safe} --> {child_safe}")

        add_node(root)
        return "\n".join(lines)

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
            for aname in agent_names:
                if aname in body_lower:
                    edges.append(DiagramEdge(
                        source=f"skill_{s.name}", target=f"agent_{aname}",
                        type="uses_agent", label="used by",
                    ))
                    logs.append(f"  → 스킬 '{s.name}' → 에이전트 '{aname}'")
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
        lines.append("    classDef agent fill:#3b82f6,stroke:#1d4ed8,color:#fff")
        lines.append("    classDef skill fill:#10b981,stroke:#047857,color:#fff")
        lines.append("    classDef rule fill:#f59e0b,stroke:#b45309,color:#fff")

        for a in agents:
            safe = a.name.replace("-", "_")
            lines.append(f'    agent_{safe}["{a.name}<br/><small>{a.model}</small>"]:::agent')
        for s in skills:
            safe = s.name.replace("-", "_")
            inv = "⚡" if s.user_invocable else ""
            lines.append(f'    skill_{safe}(["{inv}{s.name}"]):::skill')
        for r in rules:
            safe = r.name.replace("-", "_")
            scope = "🌐" if r.always_loaded else "📁"
            lines.append(f'    rule_{safe}{{{{"{scope}{r.name}"}}}}):::rule')
        for e in edges:
            src = e.source.replace("-", "_")
            tgt = e.target.replace("-", "_")
            if e.label:
                lines.append(f"    {src} -->|{e.label}| {tgt}")
            else:
                lines.append(f"    {src} --> {tgt}")

        return "\n".join(lines)


github_service = GitHubService()
