import asyncio
from typing import Any

import httpx
from core.config import settings


async def safe_get(client: httpx.AsyncClient, url: str) -> dict | None:
    """
    Perform a GET request and return parsed JSON or None on any failure.
    Never raises — caller decides how to handle a None result.
    """
    try:
        response = await client.get(url, timeout=settings.HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPStatusError, httpx.RequestError, asyncio.TimeoutError):
        return None


async def safe_proxy(
    method: str,
    url: str,
    headers: dict | None = None,
    body: bytes | None = None,
) -> tuple[int, Any]:
    """
    Forward an arbitrary request to an upstream service.
    Returns (status_code, json_body).
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                timeout=settings.HTTP_TIMEOUT,
            )
            try:
                data = resp.json()
            except Exception:  # noqa: BLE001
                data = {"detail": resp.text}
            return resp.status_code, data
        except httpx.RequestError as exc:
            return 503, {"detail": f"Upstream unavailable: {exc}"}