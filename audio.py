import speech_recognition as sr
from gtts import gTTS
import tempfile
import io

# Function to capture audio from a file (used in file uploader)
def capture_audio(audio_data, language='en-IN'):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_data.read())) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"

# Function to transcribe real-time audio (WebRTC)
def transcribe_realtime_audio(audio, language='en-IN'):
    r = sr.Recognizer()
    audio_data = sr.AudioData(audio, sample_rate=16000, sample_width=2)
    try:
        text = r.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"

# Function to generate speech from text
def text_to_speech(text, language='en'):
    tts = gTTS(text=text, lang=language, slow=False)

    # Create a temporary file and save the speech as mp3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
    
    # Open the temporary file to return it as a buffer
    with open(fp.name, "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    return io.BytesIO(audio_bytes)
