"""SCAG-40: 에러 메트릭 수집 테스트."""

import pytest
from fastapi.testclient import TestClient

from app.core.metrics import error_metrics
from app.main import app

client = TestClient(app)


class TestMetricsEndpoint:
    """GET /api/v1/metrics 엔드포인트 테스트."""

    def test_metrics_endpoint_exists(self):
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200

    def test_metrics_returns_structure(self):
        response = client.get("/api/v1/metrics")
        body = response.json()
        assert "total_errors" in body
        assert "by_status_code" in body
        assert "by_path" in body
        assert "by_exception_type" in body

    def test_metrics_initial_state_is_zero(self):
        error_metrics.reset()
        response = client.get("/api/v1/metrics")
        body = response.json()
        assert body["total_errors"] == 0
        assert body["by_status_code"] == {}
        assert body["by_path"] == {}


class TestMetricsRecording:
    """error_metrics.record() 직접 테스트 (모듈 무관)."""

    def test_record_increments_total(self):
        error_metrics.reset()
        error_metrics.record(404, "/test", "TestException")
        snap = error_metrics.snapshot()
        assert snap["total_errors"] == 1

    def test_record_tracks_status_code(self):
        error_metrics.reset()
        error_metrics.record(422, "/test", "ValidationError")
        snap = error_metrics.snapshot()
        assert "422" in snap["by_status_code"]

    def test_record_tracks_path(self):
        error_metrics.reset()
        error_metrics.record(500, "/api/v1/test", "RuntimeError")
        snap = error_metrics.snapshot()
        assert "/api/v1/test" in snap["by_path"]

    def test_record_tracks_exception_type(self):
        error_metrics.reset()
        error_metrics.record(404, "/test", "NotFoundException")
        snap = error_metrics.snapshot()
        assert "NotFoundException" in snap["by_exception_type"]

    def test_multiple_records_accumulate(self):
        error_metrics.reset()
        error_metrics.record(404, "/a", "E1")
        error_metrics.record(422, "/b", "E2")
        error_metrics.record(500, "/c", "E3")
        snap = error_metrics.snapshot()
        assert snap["total_errors"] == 3


class TestMetricsIntegration:
    """모듈 존재 시 통합 테스트 — 모듈 없으면 skip."""

    @pytest.fixture(autouse=True)
    def _require_todo_module(self):
        pytest.importorskip("app.modules.todo.router")

    def test_404_error_increments_counter(self):
        error_metrics.reset()
        client.get("/api/v1/todos/999")
        response = client.get("/api/v1/metrics")
        body = response.json()
        assert body["total_errors"] >= 1
        assert "404" in body["by_status_code"]
