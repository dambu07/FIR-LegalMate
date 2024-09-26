import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import threading
import queue
import re

def capture_audio(language='en-IN', result_queue=None, stop_event=None):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now.")
        while not stop_event.is_set():
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio, language=language)
                result_queue.put(text)
                st.write(f"Recognized: {text}")
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                st.write("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                st.write(f"Could not request results from speech recognition service; {e}")

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

def start_listening(language='en-IN', result_queue=None, stop_event=None):
    thread = threading.Thread(target=capture_audio, args=(language, result_queue, stop_event))
    thread.start()
    return thread

def stop_listening(thread):
    if thread:
        thread.join()
