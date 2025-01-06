import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from transformers import tool
from dotenv import load_dotenv
import os 

load_dotenv
# If modifying these scopes, delete the file token.json.
SCOPES = os.getenv('SCOPES')

class GoogleCalendarService : 
  _service = None
  _creds = None 
  
  @classmethod
  def get_service(cls):
    """returns the service instance"""
    if not cls._service :
      cls._initialize_service()
    return cls._service
  
  @classmethod
  def _initialize_service(cls):
      """Initializes the service instance for the first time."""
      if os.path.exists("token.json"):
          # If token.json exists, load the credentials
          cls._creds = Credentials.from_authorized_user_file("token.json", SCOPES)
      else:
          # If token.json doesn't exist, start the authorization flow
          flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
          cls._creds = flow.run_local_server(port=0)

          # Save credentials for the next run
          with open("token.json", "w") as token_file:
              token_file.write(cls._creds.to_json())

      # If the credentials are not valid, refresh or prompt the user for login
      if not cls._creds or not cls._creds.valid:
          if cls._creds and cls._creds.expired and cls._creds.refresh_token:
              cls._creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
              cls._creds = flow.run_local_server(port=0)
              with open("token.json", "w") as token_file:
                  token_file.write(cls._creds.to_json())

      # Build the service instance
      cls._service = build("calendar", "v3", credentials=cls._creds)

  
@tool
def check_time_availability(start_date:str, end_date:str)-> str:
  """
    Check if the specified time slot is available in the user's Google Calendar.

    This function verifies whether the time slot defined by start_date and end_date
    is free or occupied. It returns a sentence informing whether the time slot is free or not.

    Args:
        start_date: The start time of the time slot, formatted as an ISO 8601 string (e.g., "2023-01-01T10:00:00Z").
        end_date: The end time of the time slot, formatted as an ISO 8601 string (e.g., "2023-01-01T11:00:00Z").

    """
    
  #service = GoogleCalendarService.get_service()
  SCOPES = ["https://www.googleapis.com/auth/calendar"]
  token = {"token": "ya29.a0ARW5m74TSEM9Q8w_HqiUJlRVnyrPZNFM1Y-lpO520M1TEr6ER6PfrPCKspuykl8gEBQy6tyxb2mLJNajLg-hFAU_DiuYPGVm_wchEvLZNPw61wIODxfxX0b7uWj0wCI7stoHP2lCuUeFDnOiFs1YV_kZ1hYITdFySzxucB5eaCgYKAXQSARISFQHGX2MiB5YP8jwTxFBeU167wBpwgg0175", "refresh_token": "1//03kYHPa9filyxCgYIARAAGAMSNwF-L9IrWw-omHgQEpd5ndo2dwH0QnpNbJF4ool1JPe_rx60fmz1B7Mqjo_vxfm_wrncys-uN28", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "67080987154-e5jl5oj52p77eejgtd3bbpa611otp74f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-01-05T09:59:37.840425Z"}
  creds = Credentials.from_authorized_user_info(token, SCOPES)
  service = build("calendar", "v3", credentials=creds)
  body = {
        "timeMin": start_date,
        "timeMax": end_date,
        "items": [{"id": "primary"}]
    }
  try :
    result = (
      service.freebusy().query(body=body).execute()
    )
    busy_list = result["calendars"]["primary"]["busy"]
    if not busy_list :
      return f"the time slot {start_date} to {end_date} is free you can insert the task in it"
    else :
      return f"the time slot {start_date} to {end_date} is not free you can't insert the task in it"
  except Exception as e:
    print(f"An error occured {e}")

@tool
def add_task(start_date:str, end_date:str, desc:str)->str:
  """
  This tool allows users to add a task. with a defined start_date and end_date, 
  along with a description, to their Google Calendar. 
  It is called after checking that the time slot is available using the check_time_availability method.
  It returns a sentence .
  
  Args:
      start_date: The start time of the task, formatted as an ISO 8601 string (e.g., "2023-01-01T10:00:00Z").
      end_date: The end time of the task, formatted as an ISO 8601 string (e.g., "2023-01-01T11:00:00Z").
      desc: A brief description of the task to be added to the calendar.

  """
  #service = GoogleCalendarService.get_service()
  SCOPES = ["https://www.googleapis.com/auth/calendar"]
  token = {"token": "ya29.a0ARW5m74TSEM9Q8w_HqiUJlRVnyrPZNFM1Y-lpO520M1TEr6ER6PfrPCKspuykl8gEBQy6tyxb2mLJNajLg-hFAU_DiuYPGVm_wchEvLZNPw61wIODxfxX0b7uWj0wCI7stoHP2lCuUeFDnOiFs1YV_kZ1hYITdFySzxucB5eaCgYKAXQSARISFQHGX2MiB5YP8jwTxFBeU167wBpwgg0175", "refresh_token": "1//03kYHPa9filyxCgYIARAAGAMSNwF-L9IrWw-omHgQEpd5ndo2dwH0QnpNbJF4ool1JPe_rx60fmz1B7Mqjo_vxfm_wrncys-uN28", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "67080987154-e5jl5oj52p77eejgtd3bbpa611otp74f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-01-05T09:59:37.840425Z"}
  creds = Credentials.from_authorized_user_info(token, SCOPES)
  service = build("calendar", "v3", credentials=creds)
  body = {
      "start": {"dateTime":start_date},
      "end":{"dateTime" :end_date},
      "description": desc
      }
  try:
    result = (
      service.events()
      .insert(calendarId = "primary", body = body) 
      .execute()
    )
    print(result)
    return f"The task {desc} starting at {start_date} to {end_date} has been added to the google calendar"
  except Exception as e:
    print(f"An error occured: {e}")

def main():
  try:
    start = (datetime.datetime.utcnow()+ datetime.timedelta(hours=6)).isoformat() + "Z"
    end = (datetime.datetime.utcnow()+ datetime.timedelta(hours=8)).isoformat() + "Z"
    desc = "first event created while building the kindi app"
    #False the time slot isn't free, True it is free
    status = check_time_availability(start, end)
    if status :
      res = add_task(start, end, desc)
      print("event added")
      return res
    print('time slot full')
    return status
    

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
  
