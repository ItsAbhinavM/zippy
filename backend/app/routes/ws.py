from __future__ import annotations
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.sessions.manager import session_manager

router = APIRouter()


@router.websocket("/session/{session_id}/state")
async def state_socket(websocket: WebSocket, session_id: str):
    session = session_manager.get(session_id)
    if session is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    await websocket.send_json({
        "type": "snapshot",
        "data": session.store.state.model_dump(mode="json"),
    })

    def on_message(envelope: dict):
        asyncio.create_task(websocket.send_json(envelope))

    session.store.subscribe(on_message)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass