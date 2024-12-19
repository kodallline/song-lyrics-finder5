import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


SPOTIPY_CLIENT_ID = "eaa53a3f6d3c488fad9f56b9a0505d9c"
SPOTIPY_CLIENT_SECRET = "b8c613ded81a486cb6e7b3653b2845fc"
SPOTIPY_REDIRECT_URI = "http://localhost:8000"
SCOPE = "playlist-modify-public playlist-modify-private user-library-read"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))


def create_spotify_playlist(tracks_uris):

    user_id = sp.current_user()['id']


    playlist = sp.user_playlist_create(user_id, "My Generated Playlist", public=False,
                                       description="Generated playlist with similar tracks")


    sp.playlist_add_items(playlist['id'], tracks_uris)
    return playlist['id']


def search_track_on_spotify(title, artist):
    results = sp.search(q=f"track:{title} artist:{artist}", type="track", limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    return None