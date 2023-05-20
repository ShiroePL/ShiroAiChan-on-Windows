import requests
from api_keys import access_token
import json




def change_anime_status(ANIME_ID: int, NEW_STATUS: str):
  """Update the status of an anime"""
  headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

  # Replace 'ANIME_ID' with the ID of the anime you want to update, and 'NEW_STATUS' with the desired status
      # for testing
#   ANIME_ID = 6164  # Replace this with the actual anime ID
#   NEW_STATUS = 'PAUSED'  # Replace this with the desired status (e.g., 'CURRENT', 'PLANNING', 'COMPLETED', 'DROPPED', 'PAUSED')

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




def change_episodes_watched(ANIME_ID: int, EPISODES_WATCHED: int):
  """Update the number of episodes watched for an anime"""
  headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

  # Replace 'ANIME_ID' with the ID of the anime you want to update, and 'NEW_STATUS' with the desired status
      # for testing
#   ANIME_ID = 6164  # Replace this with the actual anime ID
#   EPISODES_WATCHED = 6  # Replace this with the desired episodes watched

  query = '''
  mutation ($id: Int, $episodes: Int) {
    SaveMediaListEntry (mediaId: $id, progress: $episodes) {
      id
      progress
    }
  }
  '''

  variables = {'id': ANIME_ID, 'episodes': EPISODES_WATCHED}

  response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}, headers=headers)
  if response.status_code != 200:
      print(response.content)

  response.raise_for_status()
  data = response.json()

  if 'errors' in data:
      print(f"An error occurred: {data['errors']}")
  else:
      print("Anime status updated successfully!")




def get_10_newest_anime():
  """Get the 10 newest anime formatted for prompt"""
  
  variables_in_api = {
    'page' : 1
    }
  
  formatted_10_list = ""

  api_request = '''
    query ($page: Int) {
    Page(page: $page, perPage: 10) {
    pageInfo {
    perPage
    }
    mediaList(userId: 444059, type: ANIME, sort: UPDATED_TIME_DESC) {
    mediaId
    status
    progress
    updatedAt
    media {
        title {
        romaji
        english
        }
        
        
        
        episodes
        
    }
    
    }
    }
    }
    '''
  url = 'https://graphql.anilist.co'

  response = requests.post(url, json={'query': api_request, 'variables': variables_in_api})

  response.raise_for_status()

  parsed_json = json.loads(response.text)

  newest_10_anime = []
  
  j = 0
  for j in range(len(parsed_json["data"]["Page"]["mediaList"])):

    media_list = parsed_json["data"]["Page"]["mediaList"][j]
    media = media_list["media"]
    title = media["title"]

    anime_dict = {
        'on_list_status': media_list["status"],
        'mediaId': media_list["mediaId"],
        'progress': media_list["progress"],
        'updatedAt': media_list["updatedAt"],
        'episodes': media["episodes"] or 0,
        #'description': media["description"].replace("<br><br>", '<br>').replace("'", '"'),
        'english': (title["english"].replace("'", '"') if title["english"] is not None else "no english title"),
        'romaji': title["romaji"].replace("'", '"')
      }

    newest_10_anime.append(anime_dict)
   # print("anime_dict: ", anime_dict)
    #format for less tokens for prompt
  for anime in newest_10_anime:
    title = anime['romaji'].replace('’', "'")
    title = anime['romaji'].replace('"', "'")
    formatted_10_list += f"\nromaji_title:{title}, id:{anime['mediaId']}, watched_episodes:{anime['progress']}/{anime['episodes']} "

    

  return formatted_10_list, newest_10_anime


def find_anime_by_id(anime_list, anime_id):
    for anime in anime_list:
        if anime['mediaId'] == anime_id:
            return anime
    return None





if __name__ == "__main__":
    
    # change_episodes_watched(6164, 6)
    # change_anime_status(6164, 'PAUSED')
    formatted_list, raw_list = get_10_newest_anime()
    search_id = 127550
    found_anime = find_anime_by_id(raw_list, search_id)
    print ("formatted list: ", formatted_list)
    if found_anime:
        print(f"Found anime with ID {search_id}:")
        print(found_anime)
    else:
        print(f"Anime with ID {search_id} not found in the list.")
    
    

    # print(result)
    pass
