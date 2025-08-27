# backend/sync.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from decouple import config
from integrations.sheets.service import update_sheet_companies,update_sheet_meetings
from hubspot_oauth.views import fetch_companies, fetch_meetings 
import requests

def get_access_token():
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": config("HUBSPOT_CLIENT_ID"),
        "client_secret": config("HUBSPOT_CLIENT_SECRET"),
        "refresh_token": config("HUBSPOT_REFRESH_TOKEN")
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json().get("access_token")

def main():
    print("🔄 Starting HubSpot → Google Sheets sync...")
    access_token = get_access_token()

    companies = fetch_companies(access_token)
    print(f"✅ Fetched {len(companies)} companies.")

    meetings = fetch_meetings(access_token, max_records=10)
    print(f"✅ Fetched {len(meetings)} meetings.")

    # Option 1: Combine both into one sheet
    update_sheet_companies(companies)
    update_sheet_meetings(meetings)

    # I want to Push separately 
    

    print("✅ Synced data to Google Sheets.")

if __name__ == "__main__":
    main()
