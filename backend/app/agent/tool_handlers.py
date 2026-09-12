from pipecat.processors.frame_processor import FrameProcessor
from app.state.store import StateStore

def make_state_bridge(store: StateStore)-> FrameProcessor:
    return FrameProcessor()

TOOL_HANDLERS: dict[str,callable]={}