"""SCAG-31: 기본 보안 체계 테스트."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestSecurityHeaders:
    """보안 헤더가 모든 응답에 포함되는지 검증."""

    def test_x_content_type_options(self):
        response = client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self):
        response = client.get("/health")
        assert response.headers.get("x-frame-options") == "DENY"

    def test_x_xss_protection(self):
        response = client.get("/health")
        assert response.headers.get("x-xss-protection") == "1; mode=block"

    def test_security_headers_on_error_response(self):
        response = client.get("/nonexistent-path")
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"

    def test_cache_control_on_api(self):
        response = client.get("/api/v1/metrics")
        assert "no-store" in response.headers.get("cache-control", "")


class TestApiKeyAuth:
    """인증 면제 엔드포인트 테스트."""

    def test_health_endpoint_requires_no_auth(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_docs_endpoint_requires_no_auth(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_metrics_endpoint_requires_no_auth(self):
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200


class TestInputValidation:
    """입력 검증 — 모듈 존재 시에만 테스트."""

    @pytest.fixture(autouse=True)
    def _require_coordinator(self):
        pytest.importorskip("app.modules.coordinator.router")

    def test_oversized_request_body_rejected(self):
        response = client.post("/api/v1/coordinator/route", json={
            "request": "A" * 10001,
        })
        assert response.status_code == 422

    def test_normal_request_body_accepted(self):
        response = client.post("/api/v1/coordinator/route", json={
            "request": "API 만들어줘",
        })
        assert response.status_code == 200
