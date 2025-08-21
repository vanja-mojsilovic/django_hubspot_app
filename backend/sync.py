# backend/sync.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
import requests
from decouple import config
from integrations.sheets.service import update_sheet



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

def fetch_companies(access_token):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    companies = response.json()

    return [
        {
            "name": c["properties"].get("name", ""),
            "domain": c["properties"].get("domain", ""),
            "hs_object_id": c.get("id", "")
        }
        for c in companies.get("results", [])
    ]

def main():
    print("🔄 Starting HubSpot → Google Sheets sync...")
    access_token = get_access_token()
    companies = fetch_companies(access_token)
    update_sheet(companies)
    print(f"✅ Synced {len(companies)} companies to Google Sheets.")

if __name__ == "__main__":
    main()
