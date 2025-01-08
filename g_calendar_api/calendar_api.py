import datetime
import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from transformers import tool
from dotenv import load_dotenv
from googleapiclient.http import MediaInMemoryUpload
import os 

load_dotenv
# If modifying these scopes, delete the file token.json.
#SCOPES = os.getenv('SCOPES')
SCOPES = ["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/calendar.events"]
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
          flow = InstalledAppFlow.from_client_secrets_file("g_calendar_api\\credentials.json", SCOPES)
          cls._creds = flow.run_local_server(port=0)

          # Save credentials for the next run
          with open("token.json", "w") as token_file:
              token_file.write(cls._creds.to_json())

      # If the credentials are not valid, refresh or prompt the user for login
      if not cls._creds or not cls._creds.valid:
          if cls._creds and cls._creds.expired and cls._creds.refresh_token:
              cls._creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file("g_calendar_api\\credentials.json", SCOPES)
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

@tool
def create_doc_for_notes(doc_title: str, notes: str)->str:
  """"
  This tool allows users to create a file in google drive, given the title of the file doc_file and 
  its content notes. 
  It is called when the notes have been generated.
  It returns the link of the google drive file.
  
  Args:
      doc_title: The title of the google drive.
      notes: The content of the google drive.
  """
  SCOPES = ["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/calendar.events"]
  token={"token": "ya29.a0ARW5m76uc0Kbu8YH19kTOXUdon_p1rbsYZeP7st0GUn1E0HRDVDsSSSuEYWEJuyIUzqZO3tcPXOlWGNFt_AW2QzaLIF-bCXYFXTuxs6jhzlXaAeSunG8TAsqGgb0Nz_9yDGSzDLIctDbLQ8SJsRQqKqNrLr9xu_CUvjYZr99aCgYKATcSARISFQHGX2Mi71GrL8fMITEwvsj3FuKP6w0175", "refresh_token": "1//0327GQ77EkF5bCgYIARAAGAMSNwF-L9IrtEBj8htG7qv-zosh9-IBZek9a5gu0wtDlVs2hO_E2Tr-oqNBx6F0VHJQbIAbc5PNGmo", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "67080987154-e5jl5oj52p77eejgtd3bbpa611otp74f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/calendar.events"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-01-07T22:31:50.808478Z"}
  creds = Credentials.from_authorized_user_info(token, SCOPES)
  service = build("drive", "v2", credentials=creds)
  try:
      body = {
          "title": doc_title,  
          "mimeType": "text/plain", 
      }
      media = MediaInMemoryUpload(notes.encode("utf-8"), mimetype="text/plain")
      result = (
          service.files()
          .insert(body=body, media_body=media, fields="id, title, alternateLink")
          .execute()
      )
      return result['alternateLink']
  except Exception as e:
      print(f"An error occurred: {e}")

@tool
def insert_notes_url(file_url: str, event_title: str, date: str, start_time: str,end_time:str) -> str:
  """
  This tool allows users to append a file_url to the attachments of a Google Calendar event.
  Given the URL of the file file_url, the event_title which the title of the google calendar event
  , the date which is the day of the event, 
  the start_time which is the starting hour, 
  and the end_time of the event which is the ending hour,
  this function retrieves the event ID and updates the event by appending the file_url to its attachments attribute.
  It returns whether the file URL has been successfully appended or not.

  Args:
      file_url: The URL of the Google Drive file.
      event_title: The title of the Google Calendar event.
      date: The day of the event in the format "%Y-%m-%d".
      start_time: The starting time of the event in the format "%H:%M:%S".
      end_time: The ending time of the event in the format "%H:%M:%S".
  """

  SCOPES = ["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/calendar.events"]
  token={"token": "ya29.a0ARW5m76uc0Kbu8YH19kTOXUdon_p1rbsYZeP7st0GUn1E0HRDVDsSSSuEYWEJuyIUzqZO3tcPXOlWGNFt_AW2QzaLIF-bCXYFXTuxs6jhzlXaAeSunG8TAsqGgb0Nz_9yDGSzDLIctDbLQ8SJsRQqKqNrLr9xu_CUvjYZr99aCgYKATcSARISFQHGX2Mi71GrL8fMITEwvsj3FuKP6w0175", "refresh_token": "1//0327GQ77EkF5bCgYIARAAGAMSNwF-L9IrtEBj8htG7qv-zosh9-IBZek9a5gu0wtDlVs2hO_E2Tr-oqNBx6F0VHJQbIAbc5PNGmo", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "67080987154-e5jl5oj52p77eejgtd3bbpa611otp74f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/calendar.events"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-01-07T22:31:50.808478Z"}
  creds = Credentials.from_authorized_user_info(token, SCOPES)
  service = build("calendar", "v3", credentials=creds)
  timezone_offset="+01:00"
  try:
      start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
      time_min = start_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")
      end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")
      time_max= end_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")
      page_token = None
      event_id = None
      while True:
          events = service.events().list(
              calendarId='primary',
              timeMin=time_min,
              timeMax=time_max,
          ).execute()
          for event in events['items']:
              if event["summary"] == event_title:  
                  event_id = event["id"] 
                  break
          if event_id:
              break 

          page_token = events.get('nextPageToken')
          if not page_token:
              break
      if not event_id:
          raise ValueError(f"No event found with title '{event_title}' between {time_min} and {time_max}.")
      event = service.events().get(calendarId="primary", eventId=event_id).execute()
      if "attachments" not in event:
          event["attachments"] = []
      event["attachments"].append({"fileUrl": file_url, "title": "Notes"})
      result = (
          service.events()
          .update(calendarId="primary", eventId=event_id, supportsAttachments=True, body=event)
          .execute()
      )
      return f"The notes were successfully attached to the event. Updated event ID: {result['id']}"  
  except Exception as e:
      print(f"An error occurred: {e}")
      return "Failed to update the event."

  
def main():
  try:
    file = create_doc_for_notes("nighit doc","jveiojijfepf")
    res = insert_notes_url(file, "last event","2025-01-06","22:00:00","23:00:00")
    print(res)
  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
