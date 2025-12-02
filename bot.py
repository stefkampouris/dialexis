#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Pipecat Quickstart Example.

The example runs a simple voice AI bot that you can connect to using your
browser and speak with it. You can also deploy this bot to Pipecat Cloud.

Required AI services:
- Soniox (Speech-to-Text)
- Azure OpenAI (LLM)
- ElevenLabs (Text-to-Speech)

Run the bot using::

    uv run bot.py
"""

import os
import yaml
import time
from pathlib import Path
from typing import Optional
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.observers.loggers.user_bot_latency_log_observer import UserBotLatencyLogObserver
from pipecat.observers.loggers.llm_log_observer import LLMLogObserver


from dotenv import load_dotenv
from loguru import logger
import sys
import re

# Configure loguru with custom formatting for metrics
logger.remove()  # Remove default handler

# Custom format function to highlight metrics
def format_metrics(record):
    """Add emoji highlights to performance metrics."""
    message = record["message"]
    
    # Highlight TTFB metrics
    if "TTFB:" in message:
        try:
            ttfb_value = float(re.search(r"TTFB: ([\d.]+)", message).group(1))
            service = re.search(r"(\w+Service)#\d+", message).group(1)
            record["message"] = f"📊 {service} TTFB: {ttfb_value*1000:.2f}ms"
        except:
            pass
    
    # Highlight token/character usage
    elif "usage" in message.lower():
        if "tokens" in message:
            record["message"] = f"💰 {message}"
        elif "characters" in message:
            record["message"] = f"💰 {message}"
    
    # Highlight processing time
    elif "processing time:" in message:
        try:
            proc_time = float(re.search(r"processing time: ([\d.]+)", message).group(1))
            service = message.split(":")[0].strip()
            record["message"] = f"⏱️  {service}: {proc_time*1000:.2f}ms"
        except:
            pass
    
    return record

# Main logger with metrics formatting
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> - <level>{message}</level>",
    level="INFO",  # Set to INFO by default to reduce noise
    colorize=True,
    filter=lambda record: format_metrics(record) or True,
)

print("🚀 Starting Pipecat bot...")
print("⏳ Loading models and imports (20 seconds, first run only)\n")

logger.info("Loading Local Smart Turn Analyzer V3...")
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

logger.info("✅ Local Smart Turn Analyzer V3 loaded")
logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")

from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame, TTSSpeakFrame

logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.soniox.stt import SonioxSTTService, SonioxInputParams
from pipecat.transcriptions.language import Language
# from pipecat.services.azure.llm import AzureLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
# Note: Daily transport is not available on Windows
# from pipecat.transports.daily.transport import DailyParams

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)

# Import user identification service
from src.database.redis_client import redis_client
from src.users.identification import user_identification_service
from src.config import config

# Import calendar functions (for dental agent)
from src.calendar.calendar_functions import create_calendar_tools, register_calendar_functions


def load_prompt(prompt_file: str = "prompts/dental-secretary-condensed.yaml") -> str:
    """Load system prompt from YAML file."""
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        logger.warning(f"Prompt file {prompt_file} not found, using default prompt")
        return "You are a friendly AI assistant. Respond naturally and keep your answers conversational."
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)
            return prompt_data.get("instructions", "You are a friendly AI assistant.")
    except Exception as e:
        logger.error(f"Error loading prompt file: {e}")
        return "You are a friendly AI assistant. Respond naturally and keep your answers conversational."


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info(f"Starting bot with agent type: {config.AGENT_TYPE}")
    
    # Initialize Redis connection
    try:
        await redis_client.initialize()
        logger.info("✓ Redis client initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Redis: {e}")
        logger.warning("Bot will continue without user identification")

    # Load appropriate prompt based on agent type
    if config.AGENT_TYPE == "hotel":
        prompt_file = "prompts/hotel-receptionist.yaml"
        logger.info("Loading hotel receptionist configuration...")
        
        # Import and initialize hotel components
        from src.hotel.hotel_knowledge import initialize_knowledge_base
        from src.hotel.hotel_functions import create_hotel_tools, register_hotel_functions
        
        # Initialize hotel knowledge base
        try:
            initialize_knowledge_base(config.HOTEL_CONFIG_PATH)
            logger.info(f"✓ Hotel knowledge base initialized from {config.HOTEL_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize hotel knowledge base: {e}")
            raise
    else:
        # Default to dental agent
        prompt_file = "prompts/dental-secretary-condensed.yaml"
        logger.info("Loading dental secretary configuration...")
    
    system_prompt = load_prompt(prompt_file)
    
    # Add current date/time to system prompt
    from datetime import datetime
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %H:%M")
    
    # Format date/time message based on agent type
    if config.AGENT_TYPE == "hotel":
        system_prompt = f"{system_prompt}\n\n---\nIMPORTANT: The current date and time is {current_datetime}. Use this to calculate 'tomorrow', 'next week', etc."
    else:
        system_prompt = f"{system_prompt}\n\n---\nΣΗΜΑΝΤΙΚΟ: Η σημερινή ημερομηνία και ώρα είναι {current_datetime}. Χρησιμοποίησε αυτή την ημερομηνία για να υπολογίσεις 'αύριο', 'τη Δευτέρα', κλπ."
    
    logger.info(f"Loaded {config.AGENT_TYPE} agent prompt ({len(system_prompt)} chars)")

    stt = SonioxSTTService(api_key=os.getenv("SONIOX_API_KEY"), params=SonioxInputParams(language_hints=[Language.EN, Language.EL], model="stt-rt-v3"))

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVEN_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        model=os.getenv("ELEVENLABS_MODEL"),
        sample_rate=16000,
        params=ElevenLabsTTSService.InputParams(speed=1.1, optimize_streaming_latency=4, use_speaker_boost=True, style=1.0)
    )

    # llm = AzureLLMService(
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    #     model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    #     api_version=os.getenv("OPENAI_API_VERSION", "2024-12-01-preview"),
    # )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

    # Register appropriate function handlers based on agent type
    if config.AGENT_TYPE == "hotel":
        # Register hotel function handlers
        register_hotel_functions(llm)
        logger.info("✓ Hotel functions registered with LLM")
        
        # Create hotel tools schema
        hotel_tools = create_hotel_tools()
        tools = hotel_tools
    else:
        # Register calendar function handlers (dental agent)
        register_calendar_functions(llm)
        logger.info("✓ Calendar functions registered with LLM")
        
        # Create calendar tools schema
        calendar_tools = create_calendar_tools()
        tools = calendar_tools

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]

    # Create context with appropriate tools
    context = LLMContext(messages, tools=tools)
    context_aggregator = LLMContextAggregatorPair(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi), UserBotLatencyLogObserver(), LLMLogObserver()],
    )

    # Add event handler to provide immediate voice feedback when function calls start
    # This must be registered AFTER task is created so we can queue frames to it
    @llm.event_handler("on_function_calls_started")
    async def on_function_calls_started(service, function_calls):
        """Provide immediate voice feedback when a function call is triggered."""
        if not function_calls:
            return
        
        # Get the first function call to determine what kind of feedback to give
        function_name = function_calls[0].get("function", {}).get("name", "")
        
        # Map function names to natural responses based on agent type
        if config.AGENT_TYPE == "hotel":
            feedback_messages = {
                "get_hotel_information": "Let me get that information for you...",
                "get_checkin_checkout_info": "One moment, let me check that...",
                "get_room_information": "Let me pull up our room details...",
                "get_facility_information": "Let me see what we have available...",
            }
        else:
            # Greek messages for dental agent
            feedback_messages = {
                "check_doctor_availability": "Ας δω... ελέγχω τη διαθεσιμότητα...",
                "get_next_available_slots": "Μια στιγμή, ψάχνω τα επόμενα διαθέσιμα ραντεβού...",
                "create_appointment": "Εντάξει, κλείνω το ραντεβού...",
                "update_appointment": "Εντάξει, αλλάζω το ραντεβού...",
                "cancel_appointment": "Εντάξει, ακυρώνω το ραντεβού..."
            }
        
        # Get appropriate message or use default
        default_msg = "One moment..." if config.AGENT_TYPE == "hotel" else "Μια στιγμή..."
        message = feedback_messages.get(function_name, default_msg)
        
        logger.info(f"🔊 Function call started: {function_name} - Speaking: '{message}'")
        
        # Queue the TTSSpeakFrame to the pipeline - it will flow through to TTS service
        # This allows the agent to speak immediately while the function call executes in parallel
        await task.queue_frames([TTSSpeakFrame(message)])


    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        
        # Try to identify user by phone number (if available in client metadata)
        user_profile = None
        user_context = ""
        
        # In a real Twilio integration, the phone number would come from:
        # phone_number = client.get("caller_phone_number") or client.get("From")
        # For now, we'll use a test phone number from environment or metadata
        test_phone = os.getenv("TEST_PHONE_NUMBER", None)
        
        if test_phone:
            logger.info(f"Identifying user with phone: {test_phone}")
            user_profile, is_new_user = await user_identification_service.identify_user(test_phone)
            
            if user_profile:
                logger.info(f"✓ User identified: {user_profile.name}")
                # Generate user context for LLM
                user_context = await user_identification_service.generate_user_context(user_profile)
                
                # Add user context to system prompt
                messages.append({
                    "role": "system",
                    "content": f"ΠΛΗΡΟΦΟΡΙΕΣ ΧΡΗΣΤΗ:\n{user_context}\n\nGreet {user_profile.preferred_name} warmly in Greek using their preferred greeting if available."
                })
            elif is_new_user:
                logger.info(f"✗ New user - no profile found")
                # For new users, we could initiate a registration flow
                messages.append({
                    "role": "system",
                    "content": "This is a new user. Introduce yourself as Niniko and ask for their name in Greek."
                })
        else:
            # No phone number available - use default greeting
            logger.info("No phone number for identification - using default greeting")
            messages.append({
                "role": "system", 
                "content": "Greet the user warmly in Greek as Niniko would. Start with a simple 'Καλημέρα' and ask how they are today."
            })
        
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        # Note: Daily transport is not available on Windows
        # "daily": lambda: DailyParams(
        #     audio_in_enabled=True,
        #     audio_out_enabled=True,
        #     vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
        #     turn_analyzer=LocalSmartTurnAnalyzerV3(),
        # ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
