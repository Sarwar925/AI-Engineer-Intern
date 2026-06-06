# from google.adk.agents import Agent

# root_agent = Agent(
#     name="VoiceTextAssistant",
#     model="gemini-2.5-flash-native-audio-preview-12-2025",
#     instruction="""
#     You are a helpful assistant that can handle both voice and text.

#     - If the user is speaking via microphone (voice mode): 
#     Be extremely brief, natural, and conversational. Talk like a real human. 
#     Never use markdown, lists, or tables. Keep answers short.

#     - If the user is typing text (normal chat): 
#     You may use markdown, tables, bold text, and longer detailed answers for clarity.
#     """
# )


# from google.adk.agents import Agent

# # === Voice Agent (for audio/chat in ADK Web UI) ===
# voice_agent = Agent(
#     name="VoiceAssistant",
#     model="gemini-2.5-flash-native-audio-preview-12-2025",   # Best current native audio model for Live API
#     instruction="You are a helpful, friendly voice assistant. Keep responses short, natural, and conversational — like spoken language. Avoid long explanations unless asked."
# )

# # === Text Agent (for detailed writing/markdown) ===
# text_agent = Agent(
#     name="TextAssistant",
#     model="gemini-2.5-flash",          # Stable & widely supported for text
#     # Alternative if you want newer preview: "gemini-2.5-flash-preview" (test it)
#     instruction="You are a detailed text assistant. Provide clear, well-structured markdown responses with headings, lists, and code blocks when helpful."
# )

# # === Root Orchestrator (required by ADK Web) ===
# root_agent = Agent(
#     name="Orchestrator",
#     model="gemini-2.5-flash",          # Give root a real model (important for routing)
#     sub_agents=[voice_agent, text_agent],
#     instruction="""You are an intelligent router.
# - If the user is speaking via voice/audio or wants a quick conversational reply → route to VoiceAssistant.
# - If the user asks for detailed writing, explanations, code, or long-form content → route to TextAssistant.
# - Default to VoiceAssistant for general chat.
# Always delegate clearly and do not respond directly yourself."""
# )

# # This is the agent ADK Web looks for by default
# # You can also export it explicitly if needed: __all__ = ["root_agent"]




# from google.adk.agents import Agent

# # 1. Voice Specialist
# voice_agent = Agent(
#     name="VoiceAssistant",
#     model="gemini-2.5-flash-live", 
#     instruction="Voice mode active. Keep it short and human-like."
# )

# # 2. Text Specialist
# text_agent = Agent(
#     name="TextAssistant",
#     model="gemini-3-flash-preview",
#     instruction="Text mode active. Use detailed Markdown."
# )

# # 3. Routing Function (Yahan hum check karenge)
# def orchestrator_logic(user_input, context=None):
#     # Method 1: Check if input has audio data
#     # ADK voice streams mein input ke pass 'audio' attribute hota hai
#     is_voice = hasattr(user_input, 'audio') or hasattr(user_input, 'duration')
    
#     # Method 2: Check context metadata (Web UI specific)
#     if not is_voice and context:
#         is_voice = context.metadata.get("modality") == "audio"

#     # If/Else Condition
#     if is_voice:
#         print("--- Routing to VOICE Agent ---")
#         return voice_agent
#     else:
#         print("--- Routing to TEXT Agent ---")
#         return text_agent

# # 4. Main Root Agent
# root_agent = Agent(
#     name="MainOrchestrator",
#     model="gemini-3-flash-preview",
#     router=orchestrator_logic,
#     sub_agents=[voice_agent, text_agent]
# )




from google.adk.agents import Agent
from google.adk.tools import google_search
root_agent = Agent(
   name="google_search_agent",
   model="gemini-2.0-flash-exp",
   description="Agent to answer questions using Google Search.",
   instruction="Answer the question using the Google Search tool.",
   tools=[google_search], # Easily add tools like Google Search
)