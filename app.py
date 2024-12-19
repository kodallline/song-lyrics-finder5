import streamlit as st
import numpy as np
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time

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

# Function to transcribe audio to text
def transcribe_audio(filename='uploaded_audio.wav', language='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)  # Read the entire file
    try:
        text = recognizer.recognize_google(audio_data, language=language)  # Using Google API for recognition
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return None

# Function to search lyrics on Genius API
def search_lyrics(lyrics):
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = f"{base_url}/search"
    params = {'q': lyrics}
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        if data['response']['hits']:
            song = data['response']['hits'][0]['result']
            return {
                'title': song['title'],
                'artist': song['primary_artist']['name'],
                'url': song['url']
            }
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error while fetching song lyrics: {e}")
        return None

# Function to search track on Spotify by title and artist
def search_track(title, artist):
    try:
        results = sp.search(q=f"track:{title} artist:{artist}", type="track", limit=1)
        if results['tracks']['items']:
            return results['tracks']['items'][0]['uri']
        return None
    except Exception as e:
        st.error(f"Error while searching for track on Spotify: {e}")
        return None

# Function to get similar artists from LastFM
def get_similar_artists(artist_name, limit=5):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        'method': 'artist.getsimilar',
        'artist': artist_name,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'limit': limit
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        similar_artists = []
        if 'similarartists' in data and 'artist' in data['similarartists']:
            for artist in data['similarartists']['artist']:
                similar_artists.append(artist['name'])
        return similar_artists
    except requests.exceptions.RequestException as e:
        st.error(f"Error while fetching similar artists: {e}")
        return []

# Function to get tracks from similar artists
def get_tracks_from_similar_artists(similar_artists):
    similar_tracks = []
    for artist in similar_artists:
        try:
            results = sp.search(q=f"artist:{artist}", type="track", limit=1)
            if results['tracks']['items']:
                similar_tracks.append(results['tracks']['items'][0]['uri'])
        except Exception as e:
            st.error(f"Error while fetching tracks from artist {artist}: {e}")
    return similar_tracks

# Function to create playlist on Spotify
def create_playlist(name, track_uris):
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, name, public=False,
                                           description="Generated playlist with similar tracks")
        sp.playlist_add_items(playlist['id'], track_uris)
        return playlist['id']
    except Exception as e:
        st.error(f"Error while creating playlist: {e}")
        return None

# Upload file option
uploaded_file = st.file_uploader("Upload a .wav file", type=["wav"])

if uploaded_file is not None:
    # Save uploaded file
    with open("uploaded_audio.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File uploaded successfully! Transcribing audio...")

    # Transcribe the audio from the uploaded file
    transcribed_text = transcribe_audio('uploaded_audio.wav', language=language_code)

    if transcribed_text:
        st.write(f"Transcribed Text: {transcribed_text}")

        # Search for song lyrics using the transcribed text
        song_info = search_lyrics(transcribed_text)
        if song_info:
            st.write(f"Found song: {song_info['title']} by {song_info['artist']}")
            st.markdown(f"[Link to lyrics]({song_info['url']})")

            # Search for track on Spotify
            track_id = search_track(song_info['title'], song_info['artist'])
            if track_id:
                st.write("Track found on Spotify!")

                # Get similar artists
                similar_artists = get_similar_artists(song_info['artist'])
                if similar_artists:
                    st.write("Similar artists found:")
                    for artist in similar_artists:
                        st.write(f"- {artist}")
                else:
                    st.write("No similar artists found.")

                # Get tracks from similar artists
                similar_tracks = get_tracks_from_similar_artists(similar_artists)
                if similar_tracks:
                    st.write("Tracks from similar artists:")
                    for track in similar_tracks:
                        st.markdown(f"- [Listen to track](https://open.spotify.com/track/{track})")
                else:
                    st.write("No tracks found from similar artists.")

                # Create the playlist
                playlist_tracks = [track_id] + similar_tracks
                playlist_id = create_playlist("My Generated Playlist", playlist_tracks)

                if playlist_id:
                    st.write(f"Playlist created with ID: {playlist_id}")
                    st.markdown(f"[Open your playlist on Spotify](https://open.spotify.com/playlist/{playlist_id})")
                else:
                    st.error("Failed to create a playlist.")
            else:
                st.error("Could not find the track on Spotify.")
        else:
            st.error("Couldn't find lyrics.")
    else:
        st.error("Failed to transcribe audio.")
