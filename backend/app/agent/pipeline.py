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
from app.agent.prompts import  GATHER_PROMPT
from app.state.store import StateStore


def build_pipeline(room_name: str, token: str, store: StateStore) -> tuple[Pipeline, PipelineWorker]:
    transport = LiveKitTransport(
        settings.livekit_url,   # url
        token,                  # token
        room_name,              # room_name — NOT a display name
        LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
        ),
    )

    stt = DeepgramSTTService(api_key=settings.deepgram_api_key)
    tts = CartesiaTTSService(
        api_key=settings.cartesia_api_key,
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",
    )

    llm = GoogleLLMService(
        api_key=settings.gemini_api_key,
        model="gemini-3.6-flash",
    )
    register_all_tools(llm, store)

    # Universal context replaces the old service-specific
    # OpenAILLMContext/GoogleLLMContext pattern — one context object
    # works with any provider.
    context = LLMContext(
        messages=[{"role": "system", "content": GATHER_PROMPT}],
        tools=TOOLS_SCHEMA,
    )

    # LLMContextAggregatorPair is tuple-unpackable directly, per
    # pipecat's own docs/examples — this replaces the old
    # llm.create_context_aggregator(context).user()/.assistant() calls.
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        assistant_aggregator,
        tts,
        transport.output(),
    ])

    task = PipelineWorker(pipeline, params=PipelineParams(allow_interruptions=True))
    return pipeline, task