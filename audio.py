import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

def transcribe_audio(audio_file, language='en-IN'):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        if language == 'en-IN':
            text = r.recognize_google(audio, language='en-IN')
        elif language == 'hi-IN':
            text = r.recognize_google(audio, language='hi-IN')
        else:
            raise ValueError("Unsupported language")
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"

def text_to_speech(text, language='en'):
    tts = gTTS(text=text, lang=language, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def get_audio_input():
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    if audio_file is not None:
        return audio_file
    return None
