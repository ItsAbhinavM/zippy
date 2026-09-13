from __future__ import annotations
import asyncio
import uuid
from dataclasses import dataclass, field

from app.state.store import StateStore
from app.livekit_room.client import livekit_client


@dataclass
class Session:
    session_id: str
    room_name: str
    store: StateStore
    bot_task: asyncio.Task | None = None
    ws_listeners: list = field(default_factory=list)


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    async def start_session(self) -> tuple[Session, str]:
        session_id = uuid.uuid4().hex[:12]
        store = StateStore(session_id=session_id)

        room_name = await livekit_client.create_room(session_id)

        session = Session(
            session_id=session_id,
            room_name=room_name,
            store=store,
        )
        self._sessions[session_id] = session

        user_token = livekit_client.create_access_token(
            room_name, identity=f"user-{session_id}"
        )

        return session, user_token

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def end_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session is None:
            return
        if session.bot_task is not None:
            session.bot_task.cancel()
        await livekit_client.delete_room(session.room_name)


session_manager = SessionManager()