import requests
import urllib.parse
from decouple import config
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from integrations.sheets.service import update_sheet

def oauth_home(request):
    return HttpResponse("Welcome to the OAuth module.")

def oauth_login(request):
    params = {
        'client_id': config('HUBSPOT_CLIENT_ID'),
        'redirect_uri': config('HUBSPOT_REDIRECT_URI'),
        'scope': 'crm.objects.companies.read',
        'response_type': 'code'
    }

    auth_url = f"https://app.hubspot.com/oauth/authorize?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

def hubspot_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("No code provided.", status=400)

    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": config("HUBSPOT_CLIENT_ID"),
        "client_secret": config("HUBSPOT_CLIENT_SECRET"),
        "redirect_uri": config("HUBSPOT_REDIRECT_URI"),
        "code": code,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return HttpResponse(f"Token exchange failed: {response.text}", status=500)

    token_data = response.json()
    access_token = token_data.get("access_token")

    # Display token and link to fetch companies
    html = f"""
    <h2>OAuth Successful</h2>
    <p>Access Token:</p>
    <pre>{access_token}</pre>
    <p><a href="/oauth/companies/?access_token={access_token}">View Companies</a></p>
    """

    print("Token response:", token_data)

    return HttpResponse(html)

def get_contacts(request):
    return HttpResponse("Contacts endpoint.")  # Placeholder

def get_companies(request):
    access_token = request.GET.get("access_token")
    if not access_token:
        return JsonResponse({"error": "Missing access token"}, status=400)

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    params = {
        "limit": 100  # Max per page
    }

    all_companies = []
    after = None

    while len(all_companies) < 1000:
        if after:
            params["after"] = after
        else:
            params.pop("after", None)  # Clean up if not set

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return JsonResponse({"error": response.text}, status=500)

        data = response.json()
        for company in data.get("results", []):
            props = company.get("properties", {})
            all_companies.append({
                "name": props.get("name", ""),
                "domain": props.get("domain", ""),
                "hs_object_id": company.get("id", "")
            })

            if len(all_companies) >= 1000:
                break  # Stop early if we've hit the target

        paging = data.get("paging", {}).get("next", {})
        after = paging.get("after")
        if not after:
            break  # No more pages

    try:
        update_sheet(all_companies)
    except Exception as e:
        return JsonResponse({"error": f"Sheet update failed: {str(e)}"}, status=500)

    return JsonResponse(all_companies, safe=False)


def oauth_backend_redirect(request):
    refresh_token = config("HUBSPOT_REFRESH_TOKEN")
    print("DEBUG: Refresh token loaded:", repr(refresh_token))
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": config("HUBSPOT_CLIENT_ID"),
        "client_secret": config("HUBSPOT_CLIENT_SECRET"),
        "refresh_token": config("HUBSPOT_REFRESH_TOKEN")
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return HttpResponse(f"Token refresh failed: {response.text}", status=500)

    access_token = response.json().get("access_token")
    if not access_token:
        return HttpResponse("No access token returned.", status=500)

    print("Loaded refresh token:", repr(config("HUBSPOT_REFRESH_TOKEN")))
    return redirect(f"/oauth/companies/?access_token={access_token}")

# hubspot_oauth/views.py

def fetch_companies(access_token, max_records=1000, page_size=100):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": page_size}

    all_companies = []
    after = None

    while len(all_companies) < max_records:
        if after:
            params["after"] = after
        else:
            params.pop("after", None)

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"HubSpot API error: {response.text}")

        data = response.json()
        for company in data.get("results", []):
            props = company.get("properties", {})
            all_companies.append({
                "name": props.get("name", ""),
                "domain": props.get("domain", ""),
                "hs_object_id": company.get("id", "")
            })

            if len(all_companies) >= max_records:
                break

        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break

    return all_companies

def fetch_meetings(access_token, max_records=10, page_size=50):
    engagements_url = "https://api.hubapi.com/engagements/v1/engagements/paged"
    users_url = "https://api.hubapi.com/settings/v3/users"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: Fetch users to map owner IDs to names
    user_response = requests.get(users_url, headers=headers)
    user_response.raise_for_status()
    users = user_response.json().get("results", [])
    user_map = {str(u["id"]): u["email"] for u in users}

    # Step 2: Fetch meetings
    all_meetings = []
    offset = 0

    while len(all_meetings) < max_records:
        params = {"limit": page_size, "offset": offset}
        response = requests.get(engagements_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for item in data.get("results", []):
            engagement = item.get("engagement", {})
            if engagement.get("type") != "MEETING":
                continue

            owner_id = str(engagement.get("createdBy"))
            meeting = {
                "owner": user_map.get(owner_id, f"User {owner_id}"),
                "timestamp": engagement.get("timestamp"),
                "id": engagement.get("id")
            }
            all_meetings.append(meeting)

            if len(all_meetings) >= max_records:
                break

        if not data.get("hasMore"):
            break
        offset = data.get("offset")

    return all_meetings



