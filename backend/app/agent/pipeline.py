from __future__ import annotations

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineWorker
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair

from app.config import settings
from app.agent.tools import TOOLS_SCHEMA
from app.agent.tool_handlers import register_all_tools
from app.agent.prompts import GATHERING_PROMPT
from app.state.store import StateStore


def build_pipeline(room_name: str, token: str, store: StateStore) -> tuple[Pipeline, PipelineWorker]:
    transport = LiveKitTransport(
        settings.livekit_url,
        token,
        room_name,
        LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
        ),
    )

    stt = DeepgramSTTService(api_key=settings.deepgram_api_key)

    tts = CartesiaTTSService(
        api_key=settings.cartesia_api_key,
        settings=CartesiaTTSService.Settings(
            # voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # confirm this is a REAL voice id from your account
            voice="db6b0ed5-d5d3-463d-ae85-518a07d3c2b4",
        ),
    )

    llm = GoogleLLMService(
        api_key=settings.gemini_api_key,
        settings=GoogleLLMService.Settings(model="gemini-3.6-flash"),
        system_instruction=GATHERING_PROMPT,
    )
    register_all_tools(llm, store)

    context = LLMContext(
        messages=[],
        tools=TOOLS_SCHEMA,
    )

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)
    @user_aggregator.event_handler("on_user_turn_stopped")
    async def _on_user_turn_stopped(aggregator, *args):
        message = args[-1] if args else None
        if message is not None and getattr(message, "content", None):
            store.push_transcript("user", message.content)

    @assistant_aggregator.event_handler("on_assistant_turn_stopped")
    async def _on_assistant_turn_stopped(aggregator, *args):
        message = args[-1] if args else None
        if message is not None and getattr(message, "content", None):
            store.push_transcript("assistant", message.content)

    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,                    
        transport.output(),
        assistant_aggregator,
    ])

    task = PipelineWorker(pipeline, params=PipelineParams(allow_interruptions=True))
    return pipeline, task