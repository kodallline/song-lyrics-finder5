import requests
from config import GENIUS_ACCESS_TOKEN

def search_lyrics(lyrics):
    """Search for song lyrics on Genius."""
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = f"{base_url}/search"
    params = {'q': lyrics}
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if data['response']['hits']:
        song = data['response']['hits'][0]['result']
        return {
            'title': song['title'],
            'artist': song['primary_artist']['name']
        }
    return None