import asyncio
from audio_handler import record_audio, transcribe_audio
from spotify_api import search_track, create_playlist
from genius_api import search_lyrics
from lastfm_api import get_similar_artists


async def main():
    #
    duration = 5
    filename, audio_data = record_audio(duration=duration)


    language = input("Select language for transcription (en-US for English, ru-RU for Russian): ")


    transcribed_text = transcribe_audio(audio_data, 44100, language=language)
    print(f"Transcribed text: {transcribed_text}")


    song_info = search_lyrics(transcribed_text)
    if song_info:
        print(f"Found song: {song_info['title']} by {song_info['artist']}")


        track_id = search_track(song_info['title'], song_info['artist'])

        if track_id:

            similar_artists = get_similar_artists(song_info['artist'])


            playlist_tracks = [track_id]
            for artist in similar_artists[:5]:
                artist_track = search_track(None, artist)
                if artist_track:
                    playlist_tracks.append(artist_track)

            playlist_id = create_playlist("My Generated Playlist", playlist_tracks)
            print(f"Created playlist with ID: {playlist_id}")
        else:
            print("Couldn't find the track on Spotify")
    else:
        print("Couldn't find lyrics")


if __name__ == "__main__":
    asyncio.run(main())
