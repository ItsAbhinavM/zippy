from __future__ import annotations

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineWorker
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregator,
    LLMUserAggregatorParams
)
from pipecat.processors.frame_processor import FrameProcessor

from app.config import settings
from app.agent.tools import TOOL_DEFINITION
from app.agent.prompts import GATHER_PROMPT
from app.state.store import StateStore


def build_pipeline(
    room_url: str,
    token: str,
    store: StateStore,
    state_bridge: FrameProcessor,
) -> tuple[Pipeline, PipelineWorker]:
    """
    state_bridge is a FrameProcessor (defined in tool_handlers.py, Phase 5)
    that intercepts LLM tool-call frames and applies them to `store`.
    Phase 4 wires it in as a no-op passthrough; Phase 5 gives it real logic.
    """
    transport = DailyTransport(
        room_url,
        token,
        "Zippy Assistant",
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            transcription_enabled=False,
        ),
    )

    stt = DeepgramSTTService(api_key=settings.deepgram_api_key)
    tts = CartesiaTTSService(
        api_key=settings.cartesia_api_key,
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # placeholder — pick a real Cartesia voice id
    )

    llm = GoogleLLMService(
        api_key=settings.gemini_api_key,
        model="gemini-2.0-flash",   # confirm current model name/availability
        tools=TOOL_DEFINITIONS,
        system_instruction=GATHERING_PROMPT,
    )

    user_aggregator = LLMContextAggregator()
    assistant_aggregator = LLMUserAggregatorParams()

    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        state_bridge,         
        assistant_aggregator,
        tts,
        transport.output(),
    ])

    task = PipelineWorker(pipeline, params=PipelineParams(allow_interruptions=True))
    return pipeline, task