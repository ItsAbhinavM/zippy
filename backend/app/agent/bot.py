from __future__ import annotations
import logging

from pipecat.pipeline.runner import WorkerRunner
from app.agent.pipeline import build_pipeline
from app.state.store import StateStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 


async def run_bot(room_name: str, token: str, store: StateStore) -> None:
    logger.info("run_bot starting for session %s (room=%s)", store.state.session_id, room_name)
    try:
        pipeline, task = build_pipeline(room_name, token, store)
        runner = WorkerRunner()
        await runner.run(task)
    except Exception:
        logger.exception("Bot pipeline crashed for session %s", store.state.session_id)
    finally:
        logger.info("Bot pipeline ended for session %s", store.state.session_id)