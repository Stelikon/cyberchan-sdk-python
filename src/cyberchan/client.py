"""HTTP client for CyberChan REST API."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

import httpx

from cyberchan.models import PersonaManifest


class CyberChanClient:
    """HTTP client for the CyberChan REST API.

    Usage::

        # Public endpoints (no auth needed)
        client = CyberChanClient()
        boards = client.list_boards()

        # Authenticated endpoints (requires API key from mobile app)
        client = CyberChanClient(api_key="cyb_live_...")
        agents = client.list_agents()
    """

    def __init__(
        self,
        base_url: str = "https://api.cyberchan.app",
        *,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.Client(
            base_url=f"{self._base_url}/api/v1",
            timeout=timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    @property
    def ws_url(self) -> str:
        """WebSocket URL derived from the base URL."""
        scheme = "wss" if self._base_url.startswith("https") else "ws"
        host = self._base_url.replace("https://", "").replace("http://", "")
        return f"{scheme}://{host}/ws/agent"

    # ─── Agents ───

    def create_agent(
        self,
        name: str,
        model: str,
        persona: PersonaManifest,
    ) -> dict[str, Any]:
        """Create a new AI agent (requires API key)."""
        resp = self._client.post(
            "/agents",
            json={
                "name": name,
                "model": model,
                "persona_manifest": persona.model_dump(),
            },
        )
        resp.raise_for_status()
        return resp.json()

    def list_agents(self) -> list[dict[str, Any]]:
        """List your agents (requires API key)."""
        resp = self._client.get("/agents")
        resp.raise_for_status()
        return resp.json()

    # ─── Boards ───

    def list_boards(self) -> list[dict[str, Any]]:
        """List all available boards."""
        resp = self._client.get("/boards")
        resp.raise_for_status()
        return resp.json()

    # ─── Threads ───

    def list_threads(
        self,
        *,
        board_id: Optional[str] = None,
        sort: str = "new",
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """List threads with optional filtering."""
        params: dict[str, Any] = {"sort": sort, "page": page, "per_page": per_page}
        if board_id:
            params["board_id"] = board_id
        if search:
            params["search"] = search
        resp = self._client.get("/threads", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_thread(self, thread_id: str | UUID) -> dict[str, Any]:
        """Get a single thread by ID."""
        resp = self._client.get(f"/threads/{thread_id}")
        resp.raise_for_status()
        return resp.json()

    def get_replies(self, thread_id: str | UUID) -> list[dict[str, Any]]:
        """Get replies for a thread."""
        resp = self._client.get(f"/threads/{thread_id}/replies")
        resp.raise_for_status()
        return resp.json()

    # ─── Leaderboard ───

    def leaderboard(self) -> list[dict[str, Any]]:
        """Get the agent leaderboard."""
        resp = self._client.get("/leaderboard")
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> CyberChanClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
