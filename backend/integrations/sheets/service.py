from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = settings.GOOGLE_CREDENTIALS_PATH
SPREADSHEET_ID = settings.GOOGLE_SPREADSHEET_ID

RANGE_NAME_MEETINGS = 'meetings!A1'
RANGE_NAME_COMPANIES = 'companies!A1'

def update_sheet_companies(data):
    print(f"Updating sheet with {len(data)} records...") 
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    # Clear existing content
    sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME_COMPANIES
    ).execute()

    # Prepare new values
    values = [["Name", "Domain", "Object ID"]]
    for item in data:
        values.append([
            item.get("name", ""),
            item.get("domain", ""),
            item.get("hs_object_id", "")
        ])

    body = {"values": values}
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME_COMPANIES,
        valueInputOption="RAW",
        body=body
    ).execute()

def update_sheet_meetings(data):
    print(f"Updating meetings sheet with {len(data)} records...") 
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME_MEETINGS
    ).execute()

    values = [["Created By (User ID)", "Owner ID", "Engagement Type", "Text Summary", "Timestamp"]]
    for item in data:
        values.append([
            item.get("created_by", ""),
            item.get("owner_id", ""),
            item.get("type", ""),
            item.get("body_preview", ""),
            item.get("timestamp", "")
        ])


    body = {"values": values}
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME_MEETINGS,
        valueInputOption="RAW",
        body=body
    ).execute()