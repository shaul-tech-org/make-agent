from collections import defaultdict
from threading import Lock


class ErrorMetrics:
    """In-memory 에러 카운터 (Counter 패턴)."""

    def __init__(self):
        self._lock = Lock()
        self._total = 0
        self._by_status: dict[int, int] = defaultdict(int)
        self._by_path: dict[str, int] = defaultdict(int)
        self._by_exception: dict[str, int] = defaultdict(int)

    def record(self, status_code: int, path: str, exception_type: str) -> None:
        with self._lock:
            self._total += 1
            self._by_status[status_code] += 1
            self._by_path[path] += 1
            self._by_exception[exception_type] += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "total_errors": self._total,
                "by_status_code": {str(k): v for k, v in sorted(self._by_status.items())},
                "by_path": dict(sorted(self._by_path.items(), key=lambda x: -x[1])),
                "by_exception_type": dict(sorted(self._by_exception.items(), key=lambda x: -x[1])),
            }

    def reset(self) -> None:
        with self._lock:
            self._total = 0
            self._by_status.clear()
            self._by_path.clear()
            self._by_exception.clear()


error_metrics = ErrorMetrics()
