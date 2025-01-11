from dotenv import load_dotenv
from os import getenv
import requests
from g_calendar_api.calendar_api import GoogleCalendarService, GoogleDriveService
from task_setter_agent.task_setter_prompt import task_setter_system_prompt
from agent_builder import AgentBuilder
from project_planner_agent.project_planner_prompt import project_planner_prompt
from datetime import datetime, timedelta
from smolagents import ManagedAgent
from pydantic import BaseModel

load_dotenv()
#HUGGINGFACEHUB_API_TOKEN
HUGGINGFACEHUB_API_TOKEN = getenv('HUGGINGFACEHUB_API_TOKEN')
#Google client ID
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")
agent_builder = AgentBuilder()
task_setter_agent_instance = None 
drive_service_instance = None
project_planning_agent_instance = None
google_calendar_service = None 
google_drive_service = None

#Method to get the user's token, to access the apis
def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    # Your client ID, client secret, and redirect URI
    payload = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)
    response_data = response.json()

    if 'access_token' in response_data and 'refresh_token' in response_data:
        # Calculate expiry time from 'expires_in' and current time
        expiry_time = datetime.utcnow() + timedelta(seconds=response_data['expires_in'])
        formatted_expiry = expiry_time.isoformat() + 'Z'  # Format expiry as ISO8601

        # Structure the token in the desired format
        token = {
            "token": response_data['access_token'],
            "refresh_token": response_data['refresh_token'],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scopes": response_data["scope"],
            "universe_domain": "googleapis.com",
            "account": "",
            "expiry": formatted_expiry 
        }
        return token
    else:
        raise Exception("Error exchanging code for token: " + response_data.get('error', 'Unknown error'))

def initialize_google_calendar(token):
    global google_calendar_service
    if google_calendar_service is None :
        google_calendar_service = GoogleCalendarService(token)
    return google_calendar_service

#Method to initiliaze the task setter agent 
def initialize_task_agent(token):
    global task_setter_agent_instance, google_calendar_service, project_planning_agent_instance, google_drive_service
 
    if task_setter_agent_instance is None:
        if google_calendar_service is None :
            google_calendar_service = GoogleCalendarService(token)
        task_setter_agent_instance = (agent_builder
                    .set_openai_key(getenv('OPEN_AI_KEY'))
                    .set_model_id('openai/gpt-4o')
                    .add_tool([google_calendar_service])
                    .set_system_prompt(task_setter_system_prompt)
                    .set_add_base_tools(True)
                    .set_model() 
                    .build())
    return task_setter_agent_instance
    

#Method to initialize the projet planning agent
def initialize_project_agent(token):
    global project_planning_agent_instance
 
    if task_setter_agent_instance is None:
        initialize_task_agent(token)
    managed_task_setting_agent = ManagedAgent(agent=task_setter_agent_instance,
                                          name="task_setting",
                                          description="Checks the availability of the specified time slot for you.\
                                               If the time slot is available, it proceeds to add the task to Google Calendar; \
                                                   otherwise, notifies the user that the time slot is unavailable. \
                                                       When inserting a task into a specific time slot, \
                                                           give it the relevant query as an argument.")
    if project_planning_agent_instance is None :
        project_planning_agent_instance = ((agent_builder
                        .set_openai_key(getenv('OPEN_AI_KEY'))
                        .set_model_id('openai/gpt-4o')
                        .add_tool([])
                        .set_system_prompt(project_planner_prompt)
                        .set_add_base_tools(True)
                        .set_model() 
                        .set_managed_agents([managed_task_setting_agent])
                        .build()))  
    return project_planning_agent_instance


#Method to initialize the google drive service 
def initialize_google_drive(token):
    global google_drive_service
    if google_drive_service is None :
        google_drive_service= GoogleDriveService(token)
    return google_drive_service

def create_calendar(service, calendar_name: str):
    calendar = {
        'summary': calendar_name,
        'timeZone': 'UTC',
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar

def add_collaborators(service, calendar_id: str, emails: list):

    for email in emails:
        rule = {
            'scope': {
                'type': 'user',
                'value': email,
            },
            'role': 'writer',
        }
        service.acl().insert(calendarId=calendar_id, body=rule).execute()
class CreateOrganizationRequest(BaseModel):
    organization_name: str
    collaborators: list[str]