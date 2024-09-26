import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import threading
import queue
import re

def capture_audio(language='en-IN', duration=10):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write(f"Listening for {duration} seconds...")
        audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
    return audio

def transcribe_audio(audio, language='en-IN'):
    r = sr.Recognizer()
    try:
        text = r.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"

def clean_markdown(text):
    # Remove headers
    text = re.sub(r'#+\s*', '', text)
    # Remove bold and italic markers
    text = re.sub(r'\*+', '', text)
    # Remove bullet points
    text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()

def text_to_speech(text, language='en'):
    cleaned_text = clean_markdown(text)
    tts = gTTS(text=cleaned_text, lang=language, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def background_listening(language, duration, result_queue):
    audio = capture_audio(language, duration)
    text = transcribe_audio(audio, language)
    result_queue.put(text)

def start_listening(language='en-IN', duration=10):
    result_queue = queue.Queue()
    thread = threading.Thread(target=background_listening, args=(language, duration, result_queue))
    thread.start()
    return result_queue, thread
