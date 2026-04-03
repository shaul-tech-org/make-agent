import pytest


# === 분류 로직 단위 테스트 ===

class TestClassifier:
    """Coordinator 분류 로직 단위 테스트"""

    @pytest.mark.asyncio
    async def test_classify_simple_backend(self, client):
        """단순 백엔드 요청 → be-developer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "로그인 API 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "be-developer"

    @pytest.mark.asyncio
    async def test_classify_simple_frontend(self, client):
        """단순 프론트 요청 → fe-developer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "버튼 색상 빨간색으로 바꿔줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "fe-developer"

    @pytest.mark.asyncio
    async def test_classify_simple_researcher(self, client):
        """단순 리서치 요청 → researcher"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "Redis vs Memcached 비교 분석해줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "researcher"

    @pytest.mark.asyncio
    async def test_classify_simple_qa(self, client):
        """단순 테스트 요청 → qa-engineer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "회원가입 기능 검증 테스트 작성해줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "qa-engineer"

    @pytest.mark.asyncio
    async def test_classify_simple_infra(self, client):
        """단순 인프라 요청 → infra-engineer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "Docker Compose 설정 추가해줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "infra-engineer"

    @pytest.mark.asyncio
    async def test_classify_simple_cto(self, client):
        """단순 기술 결정 요청 → cto"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "이 프로젝트에 어떤 DB가 적합한지 아키텍처 리뷰해줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "cto"


# === 동점/경합 테스트 (개선 1: 가중치) ===

class TestTieBreaking:
    """키워드 경합 시 가중치로 올바른 에이전트 선택"""

    @pytest.mark.asyncio
    async def test_api_test_goes_to_qa(self, client):
        """'API 테스트' → 테스트 키워드가 우선 → qa-engineer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "로그인 API 테스트 작성해줘",
        })
        data = response.json()
        assert data["agent"] == "qa-engineer"

    @pytest.mark.asyncio
    async def test_api_deploy_goes_to_infra(self, client):
        """'API 배포' → 배포 키워드가 우선 → infra-engineer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "API 서버 배포해줘",
        })
        data = response.json()
        assert data["agent"] == "infra-engineer"

    @pytest.mark.asyncio
    async def test_frontend_test_goes_to_qa(self, client):
        """'UI 테스트' → 테스트가 우선 → qa-engineer"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "UI 컴포넌트 테스트 검증해줘",
        })
        data = response.json()
        assert data["agent"] == "qa-engineer"


# === 2단계 분류 테스트 (개선 2) ===

class TestTwoStepClassification:
    """category → complexity → agent 2단계 분류"""

    @pytest.mark.asyncio
    async def test_category_is_implementation(self, client):
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "로그인 API 만들어줘",
        })
        data = response.json()
        assert data["category"] == "implementation"

    @pytest.mark.asyncio
    async def test_category_is_research(self, client):
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "Redis vs Memcached 비교 분석해줘",
        })
        data = response.json()
        assert data["category"] == "research"

    @pytest.mark.asyncio
    async def test_category_is_tech_decision(self, client):
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "아키텍처 리뷰해줘",
        })
        data = response.json()
        assert data["category"] == "tech-decision"

    @pytest.mark.asyncio
    async def test_category_is_test(self, client):
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "회원가입 기능 검증 테스트 작성해줘",
        })
        data = response.json()
        assert data["category"] == "test"

    @pytest.mark.asyncio
    async def test_complex_category(self, client):
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        assert data["category"] == "complex"
        assert data["complexity"] == "complex"


# === 복합 요청 테스트 ===

class TestComplexRouting:
    """복합 요청 → CEO 위임 테스트"""

    @pytest.mark.asyncio
    async def test_classify_complex_multi_domain(self, client):
        """복합 요청 (여러 영역) → CEO"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "complex"
        assert data["agent"] == "ceo"

    @pytest.mark.asyncio
    async def test_classify_complex_full_feature(self, client):
        """복합 요청 (전체 기능) → CEO"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "게시판 만들어줘. DB 설계부터 UI까지 전부",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "complex"
        assert data["agent"] == "ceo"


# === 단순 질문 테스트 ===

class TestQuestionRouting:
    """단순 질문 → 직접 응답 테스트"""

    @pytest.mark.asyncio
    async def test_classify_question_explain(self, client):
        """설명 질문 → direct"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "이 에러가 뭐야?",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "question"
        assert data["agent"] == "direct"

    @pytest.mark.asyncio
    async def test_classify_question_status(self, client):
        """상태 질문 → direct"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "현재 진행 상황 알려줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "question"
        assert data["agent"] == "direct"


# === 라우팅 응답 형식 테스트 ===

class TestRouteResponse:
    """라우팅 응답 형식 검증"""

    @pytest.mark.asyncio
    async def test_response_has_required_fields(self, client):
        """응답에 필수 필드가 있는가"""
        response = await client.post("/api/v1/coordinator/route", json={
            "request": "API 만들어줘",
        })
        data = response.json()
        assert "request" in data
        assert "category" in data
        assert "complexity" in data
        assert "agent" in data

    @pytest.mark.asyncio
    async def test_empty_request_validation(self, client):
        """빈 요청 → 422"""
        response = await client.post("/api/v1/coordinator/route", json={})
        assert response.status_code == 422
