import streamlit as st
import requests
import speech_recognition as sr

# Genius API credentials
GENIUS_API_KEY = "your_genius_api_key"

# LastFM credentials
LASTFM_API_KEY = "8231360901812a5d9eec29189086474c"

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

language = st.selectbox("Select language for transcription:", ["English (en-US)", "Russian (ru-RU)"])
language_code = "en-US" if "English" in language else "ru-RU"

def transcribe_audio(filename='uploaded_audio.wav', language='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return None

def get_song_details_from_genius(text):
    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = f"{base_url}/search"
    params = {"q": text}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        hits = data['response']['hits']
        if hits:
            song_title = hits[0]['result']['title']
            song_url = hits[0]['result']['url']
            artist_name = hits[0]['result']['primary_artist']['name']
            return song_title, artist_name, song_url
    return None, None, None

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

uploaded_file = st.file_uploader("Upload a .wav file", type=["wav"])

if uploaded_file is not None:
    with open("uploaded_audio.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File uploaded successfully! Transcribing audio...")

    transcribed_text = transcribe_audio('uploaded_audio.wav', language=language_code)

    if transcribed_text:
        st.write(f"Transcribed Text: {transcribed_text}")

        song_title, artist_name, song_url = get_song_details_from_genius(transcribed_text)
        if song_title:
            st.write(f"Song found: {song_title} by {artist_name}")
            st.write(f"Song URL: [Click here]({song_url})")

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
            st.write("No song found matching the transcribed text.")
    else:
        st.error("Failed to transcribe audio.")
