import os
import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import google.generativeai as genai

# Initialize Google AI for FIR legal assistance
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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
    system_instruction="""You are an AI-powered legal assistant designed to assist police officers in India. 
Your primary task is to help them draft legally accurate FIRs by suggesting relevant sections from the IPC, CrPC, etc."""
)

# Function to transcribe speech to text
def recognize_speech(lang="en-IN"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... please speak now.")
        audio = recognizer.listen(source)
    try:
        st.info("Recognizing...")
        text = recognizer.recognize_google(audio, language=lang)
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I did not understand the audio.")
    except sr.RequestError:
        st.error("Error in accessing Google API.")
    return None

# Translate text to the appropriate language
def translate_text(text, target_lang):
    translator = Translator()
    result = translator.translate(text, dest=target_lang)
    return result.text

# Streamlit App UI
st.title("FIR LegalMate - AI-Powered FIR Assistance")
st.write("This tool helps police officers in India by providing legal sections for FIRs based on the description of the incident.")

# Language selection
language_option = st.selectbox("Choose Input Language", ("English", "Hindi"))

# Choose input mode
input_mode = st.radio("Select Input Mode", ('Text', 'Voice'))

if input_mode == 'Text':
    if language_option == 'English':
        user_input = st.text_area("Describe the incident (in English):")
    else:
        user_input = st.text_area("Describe the incident (in Hindi):")
        if user_input:
            user_input = translate_text(user_input, "en")
else:
    st.info("Click the button and start speaking when prompted.")
    if st.button("Record Voice"):
        if language_option == 'English':
            user_input = recognize_speech("en-IN")
        else:
            user_input = recognize_speech("hi-IN")
            if user_input:
                user_input = translate_text(user_input, "en")

# Process input using Google Gemini AI if input is provided
if user_input:
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    response = chat_session.send_message("Please suggest relevant legal sections.")
    st.write("### AI Response")
    st.markdown(response.text)

