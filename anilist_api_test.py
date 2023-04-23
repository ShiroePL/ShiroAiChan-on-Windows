import requests
import webbrowser
from api_keys import client_id, client_secret
# Replace these with your own values
redirect_uri = 'https://anilist.co/api/v2/oauth/pin'

# Step 1: Obtain the authorization URL
auth_url = f'https://anilist.co/api/v2/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}'
webbrowser.open(auth_url)

# Step 2: Get the authorization code from the user
auth_code = input('Enter the authorization code from the AniList authorization page: ')

# Step 3: Exchange the authorization code for an access token
token_url = 'https://anilist.co/api/v2/oauth/token'
token_data = {
    'grant_type': 'authorization_code',
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'code': auth_code
}

response = requests.post(token_url, data=token_data)
response.raise_for_status()
token_json = response.json()
access_token = token_json['access_token']
print(f'Access Token: {access_token}')

# Now you can use this access_token to make authenticated requests to AniList API
