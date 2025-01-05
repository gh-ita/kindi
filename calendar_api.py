import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

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
    """initializes the service instance for the first time"""
    if os.path.exists("token.json"):
      cls._creds = Credentials.from_authorized_user_file("token.json", SCOPES)
      # If no valid credentials, start the authorization flow
      if not cls._creds or not cls._creds.valid:
          if cls._creds and cls._creds.expired and cls._creds.refresh_token:
              cls._creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
              cls._creds = flow.run_local_server(port=0)

          # Save credentials for next use
          with open("token.json", "w") as token_file:
              token_file.write(cls._creds.to_json())

      # Build the service instance
      cls._service = build("calendar", "v3", credentials=cls._creds)

def check_time_availability(min_time, max_time):
  service = GoogleCalendarService.get_service()
  body = {
        "timeMin": min_time,
        "timeMax": max_time,
        "items": [{"id": "primary"}]
    }
  result = (
    service.freebusy()
    .query(body = body) 
    .execute()
  )
  busy_list = result["calendars"]["primary"]["busy"]
  if not busy_list :
    return True
  return False
  
def add_event(event):
  service = GoogleCalendarService.get_service()
  body = {
    }
  result = (
    service.events()
    .insert(body = body) 
    .execute()
  )

def main():
  try:
    min = datetime.datetime.utcnow().isoformat() + "Z"
    max = (datetime.datetime.utcnow()+ datetime.timedelta(hours=6)).isoformat() + "Z"
    #False the time slot isn't free, True it is free
    status = check_time_availability(min, max)
  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()