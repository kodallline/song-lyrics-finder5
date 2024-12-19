import streamlit as st
import numpy as np
import speech_recognition as sr
import requests

# LastFM credentials
LASTFM_API_KEY = "8231360901812a5d9eec29189086474c"

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
            base_url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'artist.gettoptracks',
                'artist': artist,
                'api_key': LASTFM_API_KEY,
                'format': 'json',
                'limit': 1
            }
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'toptracks' in data and 'track' in data['toptracks']:
                similar_tracks.append(data['toptracks']['track'][0]['name'])
        except requests.exceptions.RequestException as e:
            st.error(f"Error while fetching tracks from artist {artist}: {e}")
    return similar_tracks

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

        # Assuming the transcribed text is the artist's name for simplicity
        artist_name = transcribed_text

        # Get similar artists and their tracks
        similar_artists = get_similar_artists(artist_name)
        if similar_artists:
            st.write("Similar artists found:")
            for artist in similar_artists:
                st.write(f"- {artist}")

            similar_tracks = get_tracks_from_similar_artists(similar_artists)
            if similar_tracks:
                st.write("Tracks from similar artists:")
                for track in similar_tracks:
                    st.write(f"- {track}")
            else:
                st.write("No tracks found from similar artists.")
        else:
            st.write("No similar artists found.")
    else:
        st.error("Failed to transcribe audio.")
