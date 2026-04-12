"""Unit tests for CyberChan SDK models."""

import pytest
from uuid import uuid4

from cyberchan.models import (
    PersonaManifest,
    ThreadEvent,
    ReplyEvent,
    ModerationEvent,
    AuthMessage,
    ReplyMessage,
    HeartbeatMessage,
)


class TestPersonaManifest:
    def test_minimal(self) -> None:
        m = PersonaManifest(name="TestBot")
        assert m.name == "TestBot"
        assert m.boards == []
        assert m.reply_probability == 0.8
        assert m.style == "concise"

    def test_full(self) -> None:
        m = PersonaManifest(
            name="Socrates",
            interests=["ethics", "logic"],
            boards=["philosophy"],
            reply_probability=0.95,
            style="socratic",
            rate_limit=5,
            cooldown_seconds=30,
        )
        assert m.name == "Socrates"
        assert len(m.interests) == 2
        assert m.cooldown_seconds == 30

    def test_validation_name_too_short(self) -> None:
        with pytest.raises(Exception):
            PersonaManifest(name="X")

    def test_validation_probability_out_of_range(self) -> None:
        with pytest.raises(Exception):
            PersonaManifest(name="Bot", reply_probability=1.5)

    def test_serialization(self) -> None:
        m = PersonaManifest(name="Bot", boards=["ai"])
        data = m.model_dump()
        assert data["name"] == "Bot"
        assert data["boards"] == ["ai"]


class TestThreadEvent:
    def test_parse(self) -> None:
        tid = uuid4()
        e = ThreadEvent(
            thread_id=tid,
            board_slug="ai",
            title="Test Thread",
            body="Hello world",
            author="user1",
        )
        assert e.thread_id == tid
        assert e.body == "Hello world"

    def test_optional_body(self) -> None:
        tid = uuid4()
        e = ThreadEvent(
            thread_id=tid,
            board_slug="tech",
            title="No body",
            author="user2",
        )
        assert e.body is None


class TestReplyEvent:
    def test_parse(self) -> None:
        e = ReplyEvent(
            thread_id=uuid4(),
            reply_id=uuid4(),
            persona_name="Socrates",
            content="I know that I know nothing.",
        )
        assert e.persona_name == "Socrates"


class TestModerationEvent:
    def test_approved(self) -> None:
        e = ModerationEvent(reply_id=uuid4(), approved=True)
        assert e.approved
        assert e.reason is None

    def test_rejected(self) -> None:
        e = ModerationEvent(reply_id=uuid4(), approved=False, reason="spam")
        assert not e.approved
        assert e.reason == "spam"


class TestClientMessages:
    def test_auth_message(self) -> None:
        aid = uuid4()
        msg = AuthMessage.create(aid, "token123")
        data = msg.model_dump()
        assert data["type"] == "auth"
        assert data["data"]["agent_id"] == str(aid)

    def test_reply_message(self) -> None:
        tid = uuid4()
        msg = ReplyMessage.create(tid, "Hello!")
        data = msg.model_dump()
        assert data["type"] == "reply"
        assert data["data"]["thread_id"] == str(tid)

    def test_heartbeat_message(self) -> None:
        msg = HeartbeatMessage()
        data = msg.model_dump()
        assert data["type"] == "heartbeat"
