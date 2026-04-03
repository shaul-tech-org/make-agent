import base64
import re
from urllib.parse import urlparse

import frontmatter
import httpx

from app.modules.github.exceptions import (
    GitHubApiException,
    InvalidGitHubUrlException,
    NoProjectLoadedException,
)
from app.modules.github.schemas.responses import (
    AgentResponse,
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
        self._token = token
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

    def _ensure_loaded(self) -> None:
        if not self._owner or not self._repo:
            raise NoProjectLoadedException()


github_service = GitHubService()
