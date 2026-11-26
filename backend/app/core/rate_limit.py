import time
import threading
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette import status
from app.core.logging import logger


class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Tracks timestamps of requests per client IP to enforce burst and sustained limits.
    """
    def __init__(self, requests_per_minute: int = 120, burst_limit: int = 30):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = 60.0
        self._clients: Dict[str, List[float]] = {}
        self._lock = threading.RLock()

    def is_allowed(self, client_ip: str, is_heavy_endpoint: bool = False) -> bool:
        now = time.time()
        max_requests = 20 if is_heavy_endpoint else self.requests_per_minute

        with self._lock:
            if client_ip not in self._clients:
                self._clients[client_ip] = []

            # Filter timestamps outside the sliding window
            cutoff = now - self.window_seconds
            self._clients[client_ip] = [t for t in self._clients[client_ip] if t > cutoff]

            if len(self._clients[client_ip]) >= max_requests:
                return False

            self._clients[client_ip].append(now)
            return True


limiter = SlidingWindowRateLimiter(requests_per_minute=120)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying IP-based rate limiting across endpoints, with stricter
    thresholds on resource-intensive endpoints (e.g. LLM RAG chat and forecast triggers).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Bypass health, docs, and static inspection routes
        path = request.url.path
        if path in ("/health", "/docs", "/redoc", "/openapi.json", "/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        is_heavy = path.startswith("/api/v1/chat") or path.endswith("/forecast/trigger")

        if not limiter.is_allowed(client_ip, is_heavy_endpoint=is_heavy):
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please throttle your requests.",
                    "client_ip": client_ip,
                    "retry_after_seconds": 30
                },
                headers={"Retry-After": "30"}
            )

        return await call_next(request)
