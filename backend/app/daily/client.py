from __future__ import annotations
import time
import httpx
from app.config import settings

DAILY_API_BASE = "https://api.daily.co/v1"


class DailyClient:
    def __init__(self):
        self._headers = {
            "Authorization": f"Bearer {settings.daily_api_key}",
            "Content-Type": "application/json",
        }

    async def create_room(self, session_id: str, expiry_minutes: int = 60) -> dict:
        """
        Creates a short-lived Daily room, one per conversation session.
        Room name is namespaced with the session id so rooms are easy
        to trace back to a session in the Daily dashboard.
        """
        exp = int(time.time()) + expiry_minutes * 60
        payload = {
            "name": f"zippy-{session_id}",
            "properties": {
                "exp": exp,
                "enable_chat": False,
                "enable_screenshare": False,
                "start_video_off": True,
                "start_audio_off": False,
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DAILY_API_BASE}/rooms", json=payload, headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()   # includes "url", "name"

    async def create_meeting_token(
        self, room_name: str, is_owner: bool = False, expiry_minutes: int = 60
    ) -> str:
        """
        Meeting tokens let a participant (user browser, or the bot) join
        a specific room. `is_owner=True` is used for the bot so it has
        elevated permissions (e.g. recording, if ever needed).
        """
        exp = int(time.time()) + expiry_minutes * 60
        payload = {
            "properties": {
                "room_name": room_name,
                "exp": exp,
                "is_owner": is_owner,
            }
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DAILY_API_BASE}/meeting-tokens", json=payload, headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()["token"]

    async def delete_room(self, room_name: str) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{DAILY_API_BASE}/rooms/{room_name}", headers=self._headers
            )
            # 404 is fine — room may already be gone (expired via `exp`)
            if resp.status_code not in (200, 404):
                resp.raise_for_status()


daily_client = DailyClient()