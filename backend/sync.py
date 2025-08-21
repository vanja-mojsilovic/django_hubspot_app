# backend/sync.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from decouple import config
from integrations.sheets.service import update_sheet
from hubspot_oauth.views import fetch_companies  # 👈 Reuse the logic

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
    companies = fetch_companies(access_token)  # 👈 Uses the shared logic
    update_sheet(companies)
    print(f"✅ Synced {len(companies)} companies to Google Sheets.")

if __name__ == "__main__":
    main()
