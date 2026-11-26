import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import logger


class PerformanceTelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures execution latency, injects X-Process-Time and X-Request-ID headers,
    and logs slow requests (> 500ms) for performance tracking.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        response: Response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        response.headers["X-Request-ID"] = request_id

        # Production HTTP Security Headers
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        if process_time_ms > 500 and not request.url.path.startswith("/chat"):
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time_ms:.2f}ms (status {response.status_code})"
            )

        return response
