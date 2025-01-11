import datetime
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from transformers import tool
from dotenv import load_dotenv
from googleapiclient.http import MediaInMemoryUpload
from smolagents import Tool

load_dotenv
SCOPES = ["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/calendar.events"]


class GoogleCalendarService(Tool):
    name = "google_calendar_service"
    description = "Allows checking the availability of time slots in a Google Calendar and setting tasks and URLs."
    inputs = {
        "start_date": {
            "type": 'string',
            "description": "The start time of the time slot, formatted as an ISO 8601 string (e.g., '2023-01-01T10:00:00Z')."
        },
        "end_date": {
            "type": 'string',
            "description": "The end time of the time slot, formatted as an ISO 8601 string (e.g., '2023-01-01T11:00:00Z')."
        },
        "desc": {
            "type": 'string',
            "description": "Description of the task to be added to the calendar (only required for adding tasks).",
            "nullable": "True"
        },
        
        "file_url": {
            "type": 'string',
            "description": "URL of the file to be added as an attachment to a Google Calendar event (only required for adding notes).",
            "nullable": "True"
        },
        "event_title": {
            "type": 'string',
            "description": "Title of the event to which notes are to be attached (only required for adding notes).",
            "nullable": "True"
        },
        "date": {
            "type": 'string',
            "description": "The date of the event (only required for adding notes).",
            "nullable": "True"
        },
        "start_time": {
            "type": 'string',
            "description": "Start time of the event (only required for adding notes).",
            "nullable": "True"
        },
        "end_time": {
            "type": 'string',
            "description": "End time of the event (only required for adding notes).",
            "nullable": "True"
        }
    }
    output_type = "string"

    _service = None
    _creds = None
    def __init__(self, token: dict):
        """
        Initialize the GoogleCalendarService.

        Args:
            token (dict): The token dictionary returned from the OAuth process.
        """
        super().__init__()
        self._creds = Credentials.from_authorized_user_info(token, SCOPES)
        self._service = build("calendar", "v3", credentials=self._creds)


    
    def forward(self, start_date: str, end_date: str, desc: str = None, file_url: str = None, event_title: str = None, date: str = None, start_time: str = None, end_time: str = None) -> str:
        """
        Handle the logic for checking time availability, adding tasks, or inserting file URL to events.
        """
        if desc:
            return self.add_task(start_date, end_date, desc)
        elif file_url and event_title and date and start_time and end_time:
            return self.insert_notes_url(file_url, event_title, date, start_time, end_time)
        else:
            return self.check_time_availability(start_date, end_date)
        

    def check_time_availability(self, start_date: str, end_date: str) -> str:
        """
        Check if the specified time slot is available in the user's Google Calendar.

        This function verifies whether the time slot defined by start_date and end_date
        is free or occupied. It returns a sentence informing whether the time slot is free or not.

        Args:
            start_date: The start time of the time slot, formatted as an ISO 8601 string
                        (e.g., "2023-01-01T10:00:00Z").
            end_date: The end time of the time slot, formatted as an ISO 8601 string
                      (e.g., "2023-01-01T11:00:00Z").
        """
        if not self._service:
            raise Exception("Service not initialized. Call 'initialize_service' with a token first.")

        body = {
            "timeMin": start_date,
            "timeMax": end_date,
            "items": [{"id": "primary"}]
        }
        try:
            result = self._service.freebusy().query(body=body).execute()
            busy_list = result["calendars"]["primary"]["busy"]
            if not busy_list:
                return f"The time slot {start_date} to {end_date} is free. You can insert the task in it."
            else:
                return f"The time slot {start_date} to {end_date} is not free. You can't insert the task in it."
        except Exception as e:
            return f"An error occurred: {e}"

    def add_task(self, start_date: str, end_date: str, desc: str) -> str:
        """
        Add a task to the Google Calendar with a defined start_date, end_date, and description.

        Args:
            start_date: The start time of the task, formatted as an ISO 8601 string
                        (e.g., "2023-01-01T10:00:00Z").
            end_date: The end time of the task, formatted as an ISO 8601 string
                      (e.g., "2023-01-01T11:00:00Z").
            desc: A brief description of the task to be added to the calendar.
        """
        if not self._service:
            raise Exception("Service not initialized. Call 'initialize_service' with a token first.")

        body = {
            "start": {"dateTime": start_date},
            "end": {"dateTime": end_date},
            "description": desc
        }
        try:
            result = self._service.events().insert(calendarId="primary", body=body).execute()
            return f"The task {desc} starting at {start_date} to {end_date} has been added to the Google Calendar"
        except Exception as e:
            return f"An error occurred: {e}"

    @classmethod
    def insert_notes_url(self, file_url: str, event_title: str, date: str, start_time: str, end_time: str) -> str:
        """
        Append a file URL to the attachments of a Google Calendar event.

        Args:
            file_url: The URL of the Google Drive file.
            event_title: The title of the Google Calendar event.
            date: The day of the event in the format "%Y-%m-%d".
            start_time: The starting time of the event in the format "%H:%M:%S".
            end_time: The ending time of the event in the format "%H:%M:%S".
        """
        if not self._service:
            raise Exception("Service not initialized. Call 'initialize_service' with a token first.")
        
        timezone_offset = "+01:00"
        try:
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
            time_min = start_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")
            time_max = end_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")

            page_token = None
            event_id = None
            while True:
                events = self._service.events().list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                ).execute()
                for event in events["items"]:
                    if event["summary"] == event_title:
                        event_id = event["id"]
                        break
                if event_id:
                    break

                page_token = events.get("nextPageToken")
                if not page_token:
                    break

            if not event_id:
                raise ValueError(f"No event found with title '{event_title}' between {time_min} and {time_max}.")
            
            event = self._service.events().get(calendarId="primary", eventId=event_id).execute()
            if "attachments" not in event:
                event["attachments"] = []
            event["attachments"].append({"fileUrl": file_url, "title": "Notes"})

            result = self._service.events().update(
                calendarId="primary", eventId=event_id, supportsAttachments=True, body=event
            ).execute()

            return f"The notes were successfully attached to the event. Updated event ID: {result['id']}"

        except Exception as e:
            return f"An error occurred: {e}"


class GoogleDriveService(Tool):
    name = "google_drive_service"
    description = "Allows creating a Google Drive document for storing notes. The document is created with a specified title and content, and a link to access the document is returned."
    inputs = {
        "doc_title": {
            "type": "string",
            "description": "The title of the Google Drive document to be created."
        },
        "notes": {
            "type": "string",
            "description": "The content of the document to be created in Google Drive."
        }
    }
    output_type = "string"
    
    _service = None
    _creds = None
    def __init__(self, token: dict):
        """
        Initialize the GoogleDriveService.

        Args:
            token (dict): The token dictionary returned from the OAuth process.
        """
        super().__init__()
        self._creds = Credentials.from_authorized_user_info(token, SCOPES)
        self._service = build("drive", "v2", credentials=self._creds)


    def forward(self, doc_title: str, notes: str) -> str:
        if notes and doc_title:
            return self.create_doc_for_notes(doc_title, notes)


    def create_doc_for_notes(self, doc_title: str, notes: str) -> str:
        """
        Create a file in Google Drive with the given title and notes content.

        Args:
            doc_title: The title of the Google Drive document.
            notes: The content of the document to be created in Google Drive.
        """
        if not self._service:
            raise Exception("Service not initialized. Call 'initialize_service' with a token first.")

        try:
            body = {
                "title": doc_title,  
                "mimeType": "text/plain", 
            }
            media = MediaInMemoryUpload(notes.encode("utf-8"), mimetype="text/plain")
            result = (
                self._service.files()
                .insert(body=body, media_body=media, fields="id, title, alternateLink")
                .execute()
            )
            return result['alternateLink']
        except Exception as e:
            return f"An error occurred: {e}"
"""
@tool
def check_time_availability(start_date:str, end_date:str,google_calendar_service:any)-> str:
  \"""
    Check if the specified time slot is available in the user's Google Calendar.

    This function verifies whether the time slot defined by start_date and end_date
    is free or occupied. It returns a sentence informing whether the time slot is free or not.

    Args:
        start_date: The start time of the time slot, formatted as an ISO 8601 string (e.g., "2023-01-01T10:00:00Z").
        end_date: The end time of the time slot, formatted as an ISO 8601 string (e.g., "2023-01-01T11:00:00Z").
        google_calendar_service: The Google Calendar service instance used to interact with the Google Calendar API.
    \""" 
  body = {
        "timeMin": start_date,
        "timeMax": end_date,
        "items": [{"id": "primary"}]
    }
  try :
    result = (
      google_calendar_service.freebusy().query(body=body).execute()
    )
    busy_list = result["calendars"]["primary"]["busy"]
    if not busy_list :
      return f"the time slot {start_date} to {end_date} is free you can insert the task in it"
    else :
      return f"the time slot {start_date} to {end_date} is not free you can't insert the task in it"
  except Exception as e:
    print(f"An error occured {e}")

@tool
def add_task(start_date:str, end_date:str, desc:str, google_calendar_service: any)->str:
  \"""
  This tool allows users to add a task with a defined start_date and end_date, 
  along with a description, to their Google Calendar. 
  It is called after checking that the time slot is available using the check_time_availability method.
  It returns a sentence.

  Args:
      start_date: The start time of the task, formatted as an ISO 8601 string (e.g., "2023-01-01T10:00:00Z").
      end_date: The end time of the task, formatted as an ISO 8601 string (e.g., "2023-01-01T11:00:00Z").
      desc: A brief description of the task to be added to the calendar.
      google_calendar_service: The Google Calendar service instance used to interact with the Google Calendar API.
  \"""
  body = {
      "start": {"dateTime":start_date},
      "end":{"dateTime" :end_date},
      "description": desc
      }
  try:
    result = (
      google_calendar_service.events()
      .insert(calendarId = "primary", body = body) 
      .execute()
    )
    print(result)
    return f"The task {desc} starting at {start_date} to {end_date} has been added to the google calendar"
  except Exception as e:
    print(f"An error occured: {e}")

@tool
def create_doc_for_notes(doc_title: str, notes: str, google_drive_service:any)->str:
  
  This tool allows users to create a file in google drive, given the title of the file doc_file and 
  its content notes. 
  It is called when the notes have been generated.
  It returns the link of the google drive file.
  
  Args:
      doc_title: The title of the google drive.
      notes: The content of the google drive.
      google_drive_service: The Google Drive service instance used to interact with the Google Drive API.
  
  try:
      body = {
          "title": doc_title,  
          "mimeType": "text/plain", 
      }
      media = MediaInMemoryUpload(notes.encode("utf-8"), mimetype="text/plain")
      result = (
          google_drive_service.files()
          .insert(body=body, media_body=media, fields="id, title, alternateLink")
          .execute()
      )
      return result['alternateLink']
  except Exception as e:
      print(f"An error occurred: {e}")

@tool
def insert_notes_url(file_url: str, event_title: str, date: str, start_time: str,end_time:str, google_calendar_service:any) -> str:
  \"""
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
      google_calendar_service: The Google Calendar service instance used to interact with the Google Calendar API.
  \"""
  timezone_offset="+01:00"
  try:
      start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
      time_min = start_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")
      end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")
      time_max= end_datetime.strftime(f"%Y-%m-%dT%H:%M:%S{timezone_offset}")
      page_token = None
      event_id = None
      while True:
          events = google_calendar_service.events().list(
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
      event = google_calendar_service.events().get(calendarId="primary", eventId=event_id).execute()
      if "attachments" not in event:
          event["attachments"] = []
      event["attachments"].append({"fileUrl": file_url, "title": "Notes"})
      result = (
          google_calendar_service.events()
          .update(calendarId="primary", eventId=event_id, supportsAttachments=True, body=event)
          .execute()
      )
      return f"The notes were successfully attached to the event. Updated event ID: {result['id']}"  
  except Exception as e:
      print(f"An error occurred: {e}")
      return "Failed to update the event."

  
def main():
  GoogleCalendarService()

if __name__ == "__main__":
  main()
"""