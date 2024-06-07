from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import re


def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = 'cal.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    return credentials


def get_events(calendar):
    calendar_id = calendar

    # Create a datetime object for today's date.
    today = datetime.today()

    credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())

    # Create a Google Calendar API service object.
    service = build('calendar', 'v3', credentials=credentials)

    # Set the time zone to UTC.
    timezone = 'UTC'
    try:
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId=calendar_id, timeMin=datetime.utcnow().isoformat() + 'Z',
                                              maxResults=5, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        most_recent_event = events[0]

        if not events:
            print('No upcoming events found.')
        else:
            print(f'Upcoming event: {most_recent_event["summary"]} at {most_recent_event["start"]["dateTime"]}')
            summary = most_recent_event["summary"]
            start_time = most_recent_event["start"]["dateTime"]
            end_time = most_recent_event["end"]["dateTime"]
            visibility = most_recent_event.get("visibility", "public")
            
            description = most_recent_event.get("description")
            if description:
                soup = BeautifulSoup(description, 'html.parser')
                cleaned_desc = soup.get_text(separator='\n')
            else:
                cleaned_desc = "City of Knowledge"

            return summary, cleaned_desc, start_time, end_time, most_recent_event, visibility
    except TimeoutError:
        print("The request timed out. Please try again later.")
        pass
    except IndexError:
        print('No upcoming events found.')
    except KeyError as e:
        print(f'{e} had an error.')
        pass


def download_attachment(full_event):
    try:
        attachments = full_event.get('attachments', [])
        if attachments[0]['fileId']:
            file_id = attachments[0]['fileId']
            url = f"https://drive.google.com/uc?id={file_id}"
            attachment_response = requests.get(url)

            if attachment_response.status_code == 200:
                filename = attachments[0]['title']
                with open(filename, "wb") as f:
                    for chunk in attachment_response.iter_content(32768):
                        f.write(chunk)
                print(f"File downloaded successfully to '{filename}'.")
                return filename
            else:
                print("Failed to download file.")
    except IndexError:
        print("No attachment present.")
        pass


if __name__ == "__main__":
    get_events()
