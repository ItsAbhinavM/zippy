from __future__ import annotations
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

    # send current full state on connect, so the frontend isn't blank
    # until the next mutation happens
    await websocket.send_json({"type": "snapshot", "data": session.store.state.model_dump(mode="json")})

    def on_diff(diff: dict):
        import asyncio
        asyncio.create_task(websocket.send_json({"type": "diff", "data": diff}))

    session.store.subscribe(on_diff)

    try:
        while True:
            await websocket.receive_text()  # keep-alive; frontend doesn't need to send anything meaningful
    except WebSocketDisconnect:
        pass