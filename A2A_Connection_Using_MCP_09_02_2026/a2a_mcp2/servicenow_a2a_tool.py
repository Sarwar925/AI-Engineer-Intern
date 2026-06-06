# #=========================
# #          Tool 
# #=========================

# import requests
# from google.adk.tools import Tool
# from google.adk.tools.base_tool import BaseTool

# class ServiceNowA2ATool(BaseTool):
#     name = "servicenow_a2a_tool"
#     description = "Tool to communicate with ServiceNow A2A API"

#     def __init__(self):
#         self.url = "https://dev188406.service-now.com/api/x_agent/a2a_agent/agent"
#         self.username = "admin"
#         self.password = "786Shoaib0#"

#     def run(self, action: str, sys_id: str = "", short_description: str = "Tool to communicate with ServiceNow A2A API"):
#         payload = {"agent":"a2a_agent","action":"create_incident","sys_id":sys_id,"short_description":short_description}
#         try:
#             response = requests.post(self.url, json=payload, auth=(self.username,self.password), headers={"Content-Type":"application/json"}, timeout=10)
#             return response.json()
#         except Exception as e:
#             return {"status":"error","message":str(e)}


from google.adk.tools.base_tool import BaseTool
import requests
from google.adk.tools import Tool
class ServiceNowA2ATool(BaseTool):
    name = "servicenow_a2a_tool"
    description = "Tool to communicate with ServiceNow A2A API"

    def __init__(self):
        self.url = "https://dev188406.service-now.com/api/x_agent/a2a_agent/agent"
        self.username = "admin"
        self.password = "786Shoaib0#"

    def run(self, action: str, sys_id: str = "", short_description: str = ""):
        payload = {
            "agent": "a2a_agent",
            "action": action,
            "sys_id": sys_id,
            "short_description": short_description
        }
        try:
            response = requests.post(
                self.url,
                json=payload,
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
