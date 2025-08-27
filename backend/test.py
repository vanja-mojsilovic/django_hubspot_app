from decouple import config
print(config('HUBSPOT_CLIENT_ID'))
import requests

token_url = "https://api.hubapi.com/oauth/v1/token"
data = {
    "grant_type": "authorization_code",
    "client_id": "c9bec269-534b-45d1-807d-ef9fb03ca64a",
    "client_secret": "7c8e55c7-be91-4637-9427-86345f150e9d",  # replace with your actual secret
    "redirect_uri": "https://webhook.site/9ddce9ad-d440-408b-958f-2a12e4b36188",
    "code": "na1-70a1-2d40-4913-b15a-264f0d0f03bc"
}

response = requests.post(token_url, data=data)
tokens = response.json()
print(tokens)
