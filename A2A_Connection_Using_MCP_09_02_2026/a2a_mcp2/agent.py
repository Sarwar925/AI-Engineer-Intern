# def create_incident_servicenow(short_description: str) -> dict:
#     """
#     Creates an incident in ServiceNow using Table REST API.
#     No Scripted REST API required.
#     """

#     url = "https://dev188406.service-now.com/api/now/table/incident"
#     your_password = os.environ.get("SERVICENOW_PASSWORD")
#     admin = os.environ.get("SERVICENOW_USERNAME")
#     payload = {
#         "short_description": short_description,
#         "urgency": "2",
#         "impact": "2"
#     }

#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json"
#     }

#     try:
#         response = requests.post(
#             url,
#             auth=HTTPBasicAuth(admin, your_password),  # <-- CHANGE
#             json=payload,
#             headers=headers,
#             timeout=15
#         )

#         data = response.json()

#         if "result" in data:
#             sys_id = data["result"]["sys_id"]
#             number = data["result"]["number"]

#             ticket_url = f"https://dev188406.service-now.com/nav_to.do?uri=incident.do?sys_id={sys_id}"

#             return {
#                 "status": "success",
#                 "incident_number": number,
#                 "sys_id": sys_id,
#                 "url": ticket_url
#             }

#         return data

#     except Exception as e:
#         return {"status": "error", "message": str(e)}



# # =========================
# #        IMPORTS
# # =========================
# import requests
# from requests.auth import HTTPBasicAuth

# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.adk.tools.function_tool import FunctionTool
# from google.adk.models import LiteLlm
# from google.genai import types

# import os
# import dotenv
# dotenv.load_dotenv()


# # =========================
# #   ServiceNow Function
# # =========================


# def create_incident_servicenow(short_description: str):

#     url = "https://dev188406.service-now.com/api/now/table/incident"
#     admin = os.environ.get("SERVICENOW_USERNAME")
#     your_password = os.environ.get("SERVICENOW_PASSWORD")
#     payload = {
#         "short_description": short_description
#     }

#     response = requests.post(
#         url,
#         auth=HTTPBasicAuth(admin, your_password),
#         json=payload
#     )

#     return response.json()




# # =========================
# #        ADK AGENT
# # =========================
# APP_NAME = "servicenow_table_api_agent"
# USER_ID = "user1"
# SESSION_ID = "session1"

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# model = LiteLlm(
#     model="openai/gpt-4o",
#     api_key=OPENAI_API_KEY
# )

# root_agent = LlmAgent(
#     name="servicenow_agent",
#     model=model,
#     description=(
#         "You are a ServiceNow assistant. "
#         "When user asks to create ticket/incident, use the tool to create incident in ServiceNow."
#     ),
#     tools=[create_incident_servicenow]
# )





import os
import dotenv
import requests
from requests.auth import HTTPBasicAuth

# IMPORTANT: Ensure you have run 'pip install "google-adk[a2a]"'
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import AgentTool  # To link agents
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models import LiteLlm
from google.adk.apps import App 

# Load environment variables
dotenv.load_dotenv()

# =========================
#     ENV VARIABLES
# =========================
SERVICENOW_INSTANCE = os.environ.get("SERVICENOW_INSTANCE")
SERVICENOW_USERNAME = os.environ.get("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.environ.get("SERVICENOW_PASSWORD")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# =========================
#    ServiceNow Tool
# =========================
def create_incident_servicenow(short_description: str):
    """Creates an incident in ServiceNow when a user reports a problem."""
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    payload = {"short_description": short_description}

    response = requests.post(
        url,
        auth=HTTPBasicAuth(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
        json=payload
    )

    if response.status_code in [200, 201]:
        return {"status": "success", "incident_details": response.json().get('result')}
    else:
        return {"status": "error", "message": response.text}

# =========================
#         MODELS
# =========================
# Using GPT-4o via LiteLlm as the engine
model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_API_KEY)

# =========================
#     AGENT DEFINITIONS
# =========================

# 1. The Worker Agent: Handles ServiceNow tasks directly
servicenow_agent = LlmAgent(
    name="servicenow_agent",
    model=model,
    description="I am a ServiceNow specialist. I use my tools to create incidents.",
    tools=[create_incident_servicenow]
)

# 2. The User Agent: Orchestrates the request
# We use AgentTool to wrap the servicenow_agent so the user_agent can "call" it.
user_agent = LlmAgent(
    name="user_agent",
    model=model,
    description="I am a customer service agent. I delegate technical tickets to the servicenow_agent.",
    tools=[AgentTool(agent=servicenow_agent)] 
)

# =========================
#     APP & RUNNER
# =========================
# The App container only needs the root (entry) agent.
my_a2a_app = App(
    name="servicenow_a2a_app",
    root_agent=user_agent
)

session_service = InMemorySessionService()
runner = Runner(session_service=session_service)

# =========================
#        EXECUTION
# =========================
def run_a2a_demo(user_input: str):
    print(f"--- Starting A2A Task: {user_input} ---")
    
    # Running via the App context enables the a2a_mcp2 modules
    result = runner.run(
        agent=user_agent,
        prompt=user_input,
        app=my_a2a_app
    )
    
    print("\nFinal Response from System:")
    print(result.text if hasattr(result, 'text') else result)

if __name__ == "__main__":
    prompt = "I need to create a ticket because the office Wi-Fi is down on the 5th floor."
    run_a2a_demo(prompt)