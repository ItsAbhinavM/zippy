from __future__ import annotations
import asyncio
import uuid
from dataclasses import dataclass, field

from app.state.store import StateStore
from app.daily.client import daily_client


@dataclass
class Session:
    session_id: str
    room_url: str
    room_name: str
    store: StateStore
    bot_task: asyncio.Task | None = None
    ws_listeners: list = field(default_factory=list)


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    async def start_session(self) -> tuple[Session, str]:
        """
        Creates a fresh session: a StateStore, a Daily room, and a
        meeting token for the browser to join with. Returns the Session
        and the browser's join token (the bot gets its own token
        separately, inside the bot task).
        """
        session_id = uuid.uuid4().hex[:12]
        store = StateStore(session_id=session_id)

        room = await daily_client.create_room(session_id)
        room_url, room_name = room["url"], room["name"]

        session = Session(
            session_id=session_id,
            room_url=room_url,
            room_name=room_name,
            store=store,
        )
        self._sessions[session_id] = session

        user_token = await daily_client.create_meeting_token(room_name, is_owner=False)

        # bot is launched by the route handler after this returns, so it
        # can attach the task onto the session object
        return session, user_token

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def end_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session is None:
            return
        if session.bot_task is not None:
            session.bot_task.cancel()
        await daily_client.delete_room(session.room_name)


session_manager = SessionManager()