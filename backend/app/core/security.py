from fastapi import FastAPI, Request, Response


def register_security_headers(app: FastAPI) -> None:
    """보안 헤더 미들웨어."""

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"

        return response
