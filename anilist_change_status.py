import requests
from api_keys import access_token

# Replace 'YOUR_ACCESS_TOKEN' with the access token you got from the previous script
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

# Replace 'ANIME_ID' with the ID of the anime you want to update, and 'NEW_STATUS' with the desired status
ANIME_ID = 6164  # Replace this with the actual anime ID
NEW_STATUS = 'PAUSED'  # Replace this with the desired status (e.g., 'CURRENT', 'PLANNING', 'COMPLETED', 'DROPPED', 'PAUSED')

query = '''
mutation ($id: Int, $status: MediaListStatus) {
  SaveMediaListEntry (mediaId: $id, status: $status) {
    id
    status
  }
}
'''

variables = {'id': ANIME_ID, 'status': NEW_STATUS}

response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}, headers=headers)
if response.status_code != 200:
    print(response.content)

response.raise_for_status()
data = response.json()

if 'errors' in data:
    print(f"An error occurred: {data['errors']}")
else:
    print("Anime status updated successfully!")
