from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = settings.GOOGLE_CREDENTIALS_PATH
SPREADSHEET_ID = settings.GOOGLE_SPREADSHEET_ID
RANGE_NAME = 'result!A1'

def update_sheet(data):
    print(f"Updating sheet with {len(data)} records...") 
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    # Clear existing content
    sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
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
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
