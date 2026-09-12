from __future__ import annotations
import logging

from pipecat.pipeline.runner import WorkerRunner
from app.agent.pipeline import build_pipeline
from app.state.store import StateStore

logger = logging.getLogger(__name__)


async def run_bot(room_url: str, token: str, store: StateStore) -> None:
    pipeline, task = build_pipeline(room_url, token, store)
    runner = WorkerRunner()
    try:
        await runner.run(task)
    except Exception:
        logger.exception("Bot pipeline crashed for session %s", store.state.session_id)
    finally:
        logger.info("Bot pipeline ended for session %s", store.state.session_id)