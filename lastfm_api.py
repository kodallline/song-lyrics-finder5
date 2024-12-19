import requests

LASTFM_API_KEY = "4d8374703980a8ebec4a0aabdc6b2dd5"

def get_similar_tracks_from_lastfm(artist_name, limit=5):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        'method': 'artist.getsimilar',
        'artist': artist_name,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'limit': limit
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    similar_tracks = []

    if 'similarartists' in data:
        for artist in data['similarartists']['artist']:
            similar_tracks.append({
                'artist': artist['name'],
                'track': artist['toptracks']['track'][0]['name']
            })
    return similar_tracks