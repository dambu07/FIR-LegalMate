import streamlit as st
import google.generativeai as genai
from audio import capture_audio, text_to_speech, transcribe_realtime_audio
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import numpy as np
import time

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ],
    system_instruction="..."  # Keep the instruction as it is.
)

chat_session = model.start_chat(history=[])

# Define real-time audio processing class
class AudioProcessor(AudioProcessorBase):
    def __init__(self, lang_code="en-IN"):
        self.lang_code = lang_code
        self.transcription = ""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio = audio.mean(axis=1).astype(np.float32)  # Convert to mono
        self.transcription = transcribe_realtime_audio(audio, self.lang_code)
        return frame

# Process input
def process_input(input_text, language):
    response = chat_session.send_message(input_text)
    return response.text

# App Configuration
st.set_page_config(page_title="FIR-LegalMate", page_icon="⚖️")

# Language selection at the start
language = st.selectbox("Select language:", ("English", "Hindi"), key="language_selector")
lang_code = "en-IN" if language == "English" else "hi-IN"
output_language = "en" if language == "English" else "hi"

# Localized strings
strings = {
    "English": {
        "title": "Legal Assistant for FIR Writing",
        "input_type": "Choose input type:",
        "text_input": "Enter the incident details:",
        "upload_audio": "Upload Audio File",
        "process": "Process",
        "realtime_voice": "Real-Time Voice Input",
        "no_input_warning": "Please enter some text, upload an audio file, or use real-time voice input.",
        "note": "Note: This tool is designed to assist police officers in drafting FIRs. Always consult with legal experts for final verification."
    },
    "Hindi": {
        "title": "एफआईआर लेखन के लिए कानूनी सहायक",
        "input_type": "इनपुट प्रकार चुनें:",
        "text_input": "घटना का विवरण दर्ज करें:",
        "upload_audio": "ऑडियो फ़ाइल अपलोड करें",
        "process": "प्रक्रिया करें",
        "realtime_voice": "रियल-टाइम वॉयस इनपुट",
        "no_input_warning": "कृपया कुछ टेक्स्ट दर्ज करें, ऑडियो फ़ाइल अपलोड करें, या रियल-टाइम वॉयस इनपुट का उपयोग करें।",
        "note": "नोट: यह उपकरण पुलिस अधिकारियों को एफआईआर ड्राफ्ट करने में सहायता करने के लिए डिज़ाइन किया गया है। अंतिम सत्यापन के लिए हमेशा कानूनी विशेषज्ञों से परामर्श करें।"
    }
}

st.title(strings[language]["title"])

# Input type selection
input_type = st.radio(strings[language]["input_type"], ("Text", "Audio", strings[language]["realtime_voice"]))

user_input = ""

if input_type == "Text":
    user_input = st.text_area(strings[language]["text_input"])
elif input_type == "Audio":
    audio_file = st.file_uploader(strings[language]["upload_audio"], type=["wav", "mp3", "ogg"])
    if audio_file is not None:
        user_input = capture_audio(audio_file, lang_code)
        st.write(f"Transcribed text ({language}):", user_input)
elif input_type == strings[language]["realtime_voice"]:
    # Real-time voice input using WebRTC
    ctx = webrtc_streamer(
        key="real-time-voice",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=lambda: AudioProcessor(lang_code=lang_code),
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )
    if ctx.audio_processor:
        user_input = ctx.audio_processor.transcription
        st.write(f"Transcribed text ({language}):", user_input)

# Process input on button click
if st.button(strings[language]["process"]):
    if user_input:
        result = process_input(user_input, language)
        st.markdown(result)

        # Generate audio output
        audio_output = text_to_speech(result, output_language)
        st.audio(audio_output, format="audio/mp3")
    else:
        st.warning(strings[language]["no_input_warning"])

st.markdown("---")
st.write(strings[language]["note"])
