import os
import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import google.generativeai as genai
import tempfile

genai.configure(api_key=st.secrets("GEMINI_API_KEY"))

# Function to record audio using sounddevice
def record_audio(duration=5, fs=16000):
    st.write("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    return recording, fs

# Save the recorded audio to a temporary file
def save_wav_file(filename, recording, fs):
    scipy.io.wavfile.write(filename, fs, recording)

# Create the model
generation_config = {
    "temperature": 1,
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
    system_instruction="You are an AI-powered legal assistant designed to assist police officers in India in drafting legally accurate and comprehensive FIRs...",
)

# Streamlit interface
st.title("AI-Powered FIR Assistance Tool")
input_method = st.radio("Choose Input Method", ["Text", "Voice"])

if input_method == "Text":
    user_input = st.text_area("Enter the incident details in text:")
    if st.button("Submit"):
        if user_input:
            response = model.generate_content([user_input])
            st.markdown(response.text)
        else:
            st.warning("Please enter some text.")

elif input_method == "Voice":
    if st.button("Record Voice"):
        duration = st.slider("Select recording duration (seconds)", 5, 60, 5)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            recording, fs = record_audio(duration=duration)
            save_wav_file(temp_audio_file.name, recording, fs)
            
            # Upload the audio file to Gemini
            audio_file = genai.upload_file(temp_audio_file.name, mime_type="audio/wav")
            st.write("Processing the audio...")
            response = model.generate_content([audio_file, "Provide legal sections based on this audio"])
            st.markdown(response.text)
