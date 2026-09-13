from __future__ import annotations
import asyncio
from fastapi import APIRouter, HTTPException

from app.sessions.manager import session_manager
from app.livekit_room.client import livekit_client
from app.config import settings
from app.agent.bot import run_bot

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start")
async def start_session():
    session, user_token = await session_manager.start_session()

    # bot joins the same room as its own participant, with an
    # owner-level token (needed for certain Daily features later)
    bot_token = livekit_client.create_access_token(
        session.room_name,identity=f"bot-{session.session_id}" ,is_bot=True
    )

    session.bot_task = asyncio.create_task(
        run_bot(room_name=session.room_name, token=bot_token, store=session.store)
    )

    def _log_task_exception(task: asyncio.Task):
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            import logging
            logging.getLogger(__name__).exception(
                "Unhandled exception in bot task", exc_info=exc
            )

    session.bot_task.add_done_callback(_log_task_exception)

    return {
        "session_id": session.session_id,
        "room_url": settings.livekit_url,
        "user_token": user_token,
    }


@router.post("/{session_id}/end")
async def end_session(session_id: str):
    session = session_manager.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    await session_manager.end_session(session_id)
    return {"status": "ended"}