import streamlit as st
from streamlit_audio_recorder import st_audiorec
import numpy as np
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

# Spotify API credentials
SPOTIPY_CLIENT_ID = "3bohttarqt3ukj6gq7sq5m3u0"
SPOTIPY_CLIENT_SECRET = "b8c613ded81a486cb6e7b3653b2845fc"
SPOTIPY_REDIRECT_URI = "http://localhost:8000"
SCOPE = "playlist-modify-public playlist-modify-private user-library-read"

# Genius and LastFM credentials
GENIUS_ACCESS_TOKEN = "ozpgRhgVKsnIH60SjvAnkPYaNgXffNvOO4f9o2ZEBRHCpp9kdN85RYCenrOHetIy"
LASTFM_API_KEY = "8231360901812a5d9eec29189086474c"

# Spotipy client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

# Configure the page
st.set_page_config(layout="wide", page_title="Voice to Playlist")
st.markdown("""
<style>
    .stApp {
        background-color: #FFF0F5;
    }
    .stButton>button {
        background-color: #FF69B4;
        color: white;
    }
    .stProgress>div>div>div {
        background-color: #FF1493;
    }
    h1, h2, h3 {
        color: #C71585;
    }
</style>
""", unsafe_allow_html=True)

st.title("Voice to Playlist Generator")
st.image("mimimimi.png", width=50)

# Language selection for transcription
language = st.selectbox("Select language for transcription:", ["English (en-US)", "Russian (ru-RU)"])
language_code = "en-US" if "English" in language else "ru-RU"

def transcribe_audio(audio_data, sample_rate, language='en-US'):
    recognizer = sr.Recognizer()
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    audio = sr.AudioData(audio_np.tobytes(), sample_rate, 2)

    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def search_lyrics(lyrics):
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

def search_track(title, artist):
    results = sp.search(q=f"track:{title} artist:{artist}", type="track", limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    return None

def get_similar_artists(artist_name, limit=5):
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
    
    similar_artists = []

    if 'similarartists' in data and 'artist' in data['similarartists']:
        for artist in data['similarartists']['artist']:
            similar_artists.append(artist['name'])

    return similar_artists

def get_tracks_from_similar_artists(similar_artists):
    similar_tracks = []

    for artist in similar_artists:
        results = sp.search(q=f"artist:{artist}", type="track", limit=1)
        if results['tracks']['items']:
            similar_tracks.append(results['tracks']['items'][0]['uri'])

    return similar_tracks

def create_playlist(name, track_uris):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name, public=False,
                                       description="Generated playlist with similar tracks")
    sp.playlist_add_items(playlist['id'], track_uris)
    return playlist['id']

# Button to start recording
audio_data = st_audiorec(duration=10, key="audio")  # Allow user to record for 10 seconds

if audio_data is not None:
    st.write("Recording finished. Transcribing...")

    transcribed_text = transcribe_audio(audio_data, 44100, language=language_code)

    if transcribed_text:
        st.write(f"Transcribed text: {transcribed_text}")

        song_info = search_lyrics(transcribed_text)

        if song_info:
            st.write(f"Found song: {song_info['title']} by {song_info['artist']}")

            track_id = search_track(song_info['title'], song_info['artist'])

            if track_id:
                st.write("Track found on Spotify!")

                # Get similar artists
                similar_artists = get_similar_artists(song_info['artist'])
                st.write("Similar artists found:", similar_artists)

                # Get tracks from the similar artists
                similar_tracks = get_tracks_from_similar_artists(similar_artists)
                st.write("Tracks from similar artists found:", similar_tracks)

                # Create the playlist
                playlist_tracks = [track_id] + similar_tracks
                playlist_id = create_playlist("My Generated Playlist", playlist_tracks)

                if playlist_id:
                    st.write(f"Playlist created with ID: {playlist_id}")
                else:
                    st.error("Failed to create a playlist.")
            else:
                st.error("Could not find the track on Spotify.")
        else:
            st.error("Couldn't find lyrics.")
    else:
        st.error("Failed to transcribe audio.")
