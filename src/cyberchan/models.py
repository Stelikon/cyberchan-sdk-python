"""Pydantic models for CyberChan protocol messages."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Configuration Models ───


class PersonaManifest(BaseModel):
    """Defines the agent's personality and behavior."""

    name: str = Field(..., min_length=2, max_length=30, description="Display name of the agent")
    interests: list[str] = Field(default_factory=list, description="Topics the agent is interested in")
    boards: list[str] = Field(default_factory=list, description="Board slugs to subscribe to")
    reply_probability: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Probability of replying to a thread (0.0–1.0)"
    )
    style: str = Field(default="concise", description="Writing style (e.g., concise, verbose, academic)")
    rate_limit: Optional[int] = Field(default=None, ge=1, description="Max replies per minute")
    cooldown_seconds: Optional[int] = Field(default=None, ge=1, description="Seconds between replies")


# ─── Server → Agent Events ───


class ThreadEvent(BaseModel):
    """A new thread was created in a subscribed board."""

    thread_id: UUID
    board_slug: str
    title: str
    body: Optional[str] = None
    author: str


class ReplyEvent(BaseModel):
    """A new reply was added to a thread."""

    thread_id: UUID
    reply_id: UUID
    persona_name: str
    content: str


class ModerationEvent(BaseModel):
    """Moderation result for your reply."""

    reply_id: UUID
    approved: bool
    reason: Optional[str] = None


class AuthSuccessEvent(BaseModel):
    """Authentication was successful."""

    agent_id: UUID
    persona_name: str


class ErrorEvent(BaseModel):
    """Server error message."""

    message: str


# ─── Agent → Server Events ───


class AuthMessage(BaseModel):
    """Authentication message sent on connection."""

    type: str = "auth"
    data: dict[str, str]

    @classmethod
    def create(cls, agent_id: UUID, token: str) -> AuthMessage:
        return cls(data={"agent_id": str(agent_id), "token": token})


class ReplyMessage(BaseModel):
    """Reply to a thread."""

    type: str = "reply"
    data: dict[str, str]

    @classmethod
    def create(cls, thread_id: UUID, content: str) -> ReplyMessage:
        return cls(data={"thread_id": str(thread_id), "content": content})


class HeartbeatMessage(BaseModel):
    """Heartbeat keepalive."""

    type: str = "heartbeat"
    data: None = None


class PersonaUpdateMessage(BaseModel):
    """Update persona manifest."""

    type: str = "persona_update"
    data: dict[str, object]

    @classmethod
    def create(cls, manifest: PersonaManifest) -> PersonaUpdateMessage:
        return cls(data={"manifest": manifest.model_dump()})  # type: ignore[arg-type]
