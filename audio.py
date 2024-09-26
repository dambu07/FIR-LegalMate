import speech_recognition as sr
import io
from gtts import gTTS
import tempfile
import re

def transcribe_audio_data(audio_data, language):
    r = sr.Recognizer()
    try:
        # Convert Streamlit's audio recorder data to bytes and then into a file-like object
        audio_bytes = io.BytesIO(audio_data)
        
        # Recognize the audio
        with sr.AudioFile(audio_bytes) as source:
            audio = r.record(source)
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
