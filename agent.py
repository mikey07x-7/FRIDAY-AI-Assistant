import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation
from tools import get_weather, search_web, send_email, create_calendar_event, list_upcoming_events, delete_calendar_event, delete_event_by_name
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

load_dotenv()

# -----------------------------
# Optimize the Realtime LLM
# -----------------------------
# Tips for faster speech:
# - Reduce latency by using streaming=True (if supported)
# - Lower the temperature slightly for faster token generation
# - Use smaller voices/models if available
llm_config = google.beta.realtime.RealtimeModel(
    voice="Aoede",      # High-quality voice
    temperature=0.6,     # Slightly lower for faster generation
    
)

# -----------------------------
# Assistant Agent
# -----------------------------
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=llm_config,
            tools=[
                 get_weather,
                 search_web,
                 send_email,
                 create_calendar_event,
                 list_upcoming_events,
                 delete_calendar_event,     # by ID
                 delete_event_by_name       # by name
           ],
        )

# -----------------------------
# Entry point for LiveKit
# -----------------------------
async def entrypoint(ctx: agents.JobContext):
    # Use the same optimized LLM for the session
    session = AgentSession(llm=llm_config)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    # Generate reply once session is active
    await session.generate_reply(instructions=SESSION_INSTRUCTION)

# -----------------------------
# CLI run
# -----------------------------
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
