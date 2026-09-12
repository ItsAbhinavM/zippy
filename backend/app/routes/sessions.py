from __future__ import annotations
import asyncio
from fastapi import APIRouter, HTTPException

from app.sessions.manager import session_manager
from app.daily.client import daily_client
from app.agent.bot import run_bot

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start")
async def start_session():
    session, user_token = await session_manager.start_session()

    # bot joins the same room as its own participant, with an
    # owner-level token (needed for certain Daily features later)
    bot_token = await daily_client.create_meeting_token(
        session.room_name, is_owner=True
    )

    session.bot_task = asyncio.create_task(
        run_bot(
            room_url=session.room_url,
            token=bot_token,
            store=session.store,
        )
    )

    return {
        "session_id": session.session_id,
        "room_url": session.room_url,
        "user_token": user_token,
    }


@router.post("/{session_id}/end")
async def end_session(session_id: str):
    session = session_manager.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    await session_manager.end_session(session_id)
    return {"status": "ended"}