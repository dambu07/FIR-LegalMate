import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import threading
import queue
import re
from pydub import AudioSegment
from pydub.playback import play
import io

def capture_audio(language='en-IN', result_queue=None, stop_event=None):
    r = sr.Recognizer()
    
    while not stop_event.is_set():
        audio_data = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"], key=f"audio_upload_{time.time()}")
        if audio_data is not None:
            try:
                # Convert the uploaded file to AudioSegment
                audio = AudioSegment.from_file(io.BytesIO(audio_data.read()), format=audio_data.name.split('.')[-1])
                
                # Convert AudioSegment to raw data for speech recognition
                raw_data = audio.raw_data
                audio_file = sr.AudioFile(io.BytesIO(raw_data))
                
                with audio_file as source:
                    audio = r.record(source)
                
                text = r.recognize_google(audio, language=language)
                result_queue.put(text)
            except sr.UnknownValueError:
                result_queue.put("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                result_queue.put(f"Could not request results from speech recognition service; {e}")
        
        time.sleep(1)  # Add a small delay to prevent excessive CPU usage

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
    thread.join()
