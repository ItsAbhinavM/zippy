from __future__ import annotations
from livekit import api

from app.config import settings


class LiveKitClient:
    def __init__(self):
        self._lkapi = api.LiveKitAPI(
            url=settings.livekit_url,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )

    async def create_room(self, session_id: str, empty_timeout_s: int = 900) -> str:
        """
        Explicitly creates a room (rather than relying on
        create-on-join) so we can set an empty-room timeout — LiveKit
        auto-deletes the room after it's been empty this long, which
        is our equivalent of Daily's `exp` auto-expiry.
        """
        room_name = f"zippy-{session_id}"
        await self._lkapi.room.create_room(
            api.CreateRoomRequest(name=room_name, empty_timeout=empty_timeout_s)
        )
        return room_name

    def create_access_token(
        self, room_name: str, identity: str, is_bot: bool = False
    ) -> str:
        """
        Generates a JWT the browser (or bot) uses to join the room.
        `identity` must be unique per participant in the room.
        """
        grant = api.VideoGrants(room_join=True, room=room_name)
        token = (
            api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
            .with_identity(identity)
            .with_name("Zippy Assistant" if is_bot else "User")
            .with_grants(grant)
        )
        return token.to_jwt()

    async def delete_room(self, room_name: str) -> None:
        try:
            await self._lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
        except Exception:
            pass  # room may already be gone — same tolerance as Daily's 404 handling

    async def aclose(self) -> None:
        await self._lkapi.aclose()


livekit_client = LiveKitClient()