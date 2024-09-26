import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import re
from pydub import AudioSegment
import io

def capture_audio(audio_data, language='en-IN'):
    r = sr.Recognizer()

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
            return text
        except sr.UnknownValueError:
            return "Speech recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from speech recognition service; {e}"
    return ""

def transcribe_realtime_audio(audio, language='en-IN'):
    r = sr.Recognizer()
    try:
        # Create an AudioData instance for real-time processing
        audio_data = sr.AudioData(audio, sample_rate=16000, sample_width=2)
        text = r.recognize_google(audio_data, language=language)
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
