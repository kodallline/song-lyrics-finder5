import sounddevice as sd
import wave
import numpy as np
import speech_recognition as sr

def record_audio(duration=5, sample_rate=44100, filename="recorded_audio.wav"):
    """Record audio for a specified duration."""
    print("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording finished")

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    return filename, audio_data

def transcribe_audio(audio_data, sample_rate, language='en-US'):
    """Transcribe audio data to text."""
    recognizer = sr.Recognizer()
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    audio = sr.AudioData(audio_np.tobytes(), sample_rate, 2)

    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"