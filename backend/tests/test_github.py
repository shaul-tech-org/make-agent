"""GitHub .claude 조회 API 테스트."""

import pytest

from app.modules.github.service import github_service


@pytest.fixture(autouse=True)
def reset_github_service():
    """각 테스트마다 GitHub 서비스 상태 리셋."""
    github_service._owner = None
    github_service._repo = None
    github_service._branch = None
    github_service._token = None
    github_service._tree_cache = None


@pytest.mark.asyncio
async def test_parse_github_url_owner_repo(client):
    """GitHub URL에서 owner/repo를 파싱한다."""
    response = await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["owner"] == "shaul-it-org"
    assert body["repo"] == "make-agent"


@pytest.mark.asyncio
async def test_parse_github_url_with_tree(client):
    """tree/branch 포함 URL도 파싱한다."""
    response = await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent/tree/master",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["owner"] == "shaul-it-org"
    assert body["repo"] == "make-agent"
    assert body["branch"] == "master"


@pytest.mark.asyncio
async def test_invalid_github_url(client):
    """잘못된 URL은 422를 반환한다."""
    response = await client.post("/api/v1/github/load", json={
        "url": "https://example.com/not-github",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_claude_tree(client):
    """로딩된 프로젝트의 .claude 트리를 조회한다."""
    # load first
    await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })

    response = await client.get("/api/v1/github/tree")
    assert response.status_code == 200
    body = response.json()
    assert "files" in body


@pytest.mark.asyncio
async def test_get_file_content(client):
    """특정 파일의 내용을 조회한다."""
    await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })

    response = await client.get("/api/v1/github/file", params={
        "path": ".claude/CLAUDE.md",
    })
    # .claude/CLAUDE.md가 GitHub에 존재하면 200, 없으면 skip
    if response.status_code == 200:
        body = response.json()
        assert "content" in body
        assert "path" in body
    else:
        pytest.skip("CLAUDE.md not found on GitHub")


@pytest.mark.asyncio
async def test_get_agents(client):
    """에이전트 목록을 조회한다."""
    await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })

    response = await client.get("/api/v1/github/agents")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    if len(body) > 0:
        agent = body[0]
        assert "name" in agent
        assert "description" in agent
        assert "model" in agent


@pytest.mark.asyncio
async def test_get_skills(client):
    """스킬 목록을 조회한다."""
    await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })

    response = await client.get("/api/v1/github/skills")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_get_rules(client):
    """규칙 목록을 조회한다."""
    await client.post("/api/v1/github/load", json={
        "url": "https://github.com/shaul-it-org/make-agent",
    })

    response = await client.get("/api/v1/github/rules")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_no_project_loaded(client):
    """프로젝트 미로딩 상태에서 조회 시 404."""
    response = await client.get("/api/v1/github/tree")
    assert response.status_code == 404
