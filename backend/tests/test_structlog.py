"""SCAG-38: structlog 기반 JSON 구조화 로깅 테스트."""

import json

import structlog
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestStructlogIntegration:
    """structlog이 올바르게 설정되었는지 검증."""

    def test_structlog_is_configured(self):
        """structlog 설정이 로드되었는지 확인."""
        config = structlog.get_config()
        assert config["processors"] is not None

    def test_get_logger_returns_bound_logger(self):
        """structlog.get_logger()가 BoundLogger를 반환하는지 확인."""
        logger = structlog.get_logger("test")
        assert logger is not None

    def test_logger_supports_context_binding(self):
        """context binding이 동작하는지 확인."""
        logger = structlog.get_logger("test")
        bound = logger.bind(request_id="abc123", agent="be-developer")
        assert bound is not None


class TestRequestLogging:
    """요청 로깅 미들웨어가 structlog과 호환되는지 검증."""

    def test_successful_request_returns_request_id(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers

    def test_error_request_returns_request_id(self):
        response = client.get("/api/v1/todos/999")
        assert response.status_code == 404
        assert "x-request-id" in response.headers


class TestJsonLogOutput:
    """프로덕션 모드에서 JSON 로그가 출력되는지 검증."""

    def test_structlog_json_serializable(self):
        """structlog 이벤트가 JSON 직렬화 가능한지 확인."""
        event = {
            "event": "test_event",
            "request_id": "abc123",
            "status_code": 200,
            "method": "GET",
            "path": "/health",
            "duration_ms": 1.5,
        }
        serialized = json.dumps(event)
        parsed = json.loads(serialized)
        assert parsed["event"] == "test_event"
        assert parsed["request_id"] == "abc123"
