"""HTTP client for the API-Football v3 REST API, with an in-memory response cache.

Plans are metered per request (the free plan allows 100 a day), so every response is cached for a
caller-chosen time, and an expired copy is served rather than failing when the provider is down or the
quota is used up.
"""

import logging
import time
from collections.abc import Callable

import httpx

from app.services import ProviderError

BASE_URL = "https://v3.football.api-sports.io"
TIMEOUT_SECONDS = 10

logger = logging.getLogger(__name__)

Params = dict[str, str | int]


class ApiFootballClient:
    def __init__(
        self,
        api_key: str,
        *,
        transport: httpx.BaseTransport | None = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._http = httpx.Client(
            base_url=BASE_URL, headers={"x-apisports-key": api_key}, timeout=TIMEOUT_SECONDS, transport=transport
        )
        self._clock = clock
        self._cache: dict[tuple, tuple[float, list[dict]]] = {}

    def get(self, path: str, params: Params, ttl: float) -> list[dict]:
        """The `response` items for a request, across all pages. Cached for `ttl` seconds."""
        key = (path, tuple(sorted(params.items())))
        cached = self._cache.get(key)
        if cached and cached[0] > self._clock():
            return cached[1]
        try:
            items = self._fetch_all_pages(path, params)
        except ProviderError:
            if cached:
                logger.warning("Serving expired API-Football data for %s %s", path, params)
                return cached[1]
            raise
        self._cache[key] = (self._clock() + ttl, items)
        return items

    def _fetch_all_pages(self, path: str, params: Params) -> list[dict]:
        body = self._fetch(path, params)
        items = list(body.get("response") or [])
        total_pages = (body.get("paging") or {}).get("total", 1)
        for page in range(2, total_pages + 1):
            items += self._fetch(path, params | {"page": page}).get("response") or []
        return items

    def _fetch(self, path: str, params: Params) -> dict:
        try:
            response = self._http.get(path, params=params)
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("API-Football request %s %s failed: %s", path, params, exc)
            raise ProviderError("Sports data provider is unavailable") from exc
        if not isinstance(body, dict):
            body = {}

        # Failures such as a bad key (HTTP 403) or an exhausted quota (HTTP 200) carry a non-empty `errors`.
        if errors := body.get("errors"):
            # A dict maps a field to its message, plus an internal `error` code that isn't worth showing.
            messages = [m for key, m in errors.items() if key != "error"] if isinstance(errors, dict) else errors
            message = "; ".join(str(m) for m in messages) or "unknown error"
            logger.warning("API-Football request %s %s returned errors: %s", path, params, message)
            raise ProviderError(f"Sports data provider error: {message}")
        if response.is_error:
            logger.warning("API-Football request %s %s failed with HTTP %s", path, params, response.status_code)
            raise ProviderError("Sports data provider is unavailable")
        return body
