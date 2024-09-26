import streamlit as st
import google.generativeai as genai
import os
from google.oauth2 import service_account
import speech_recognition as sr
from googletrans import Translator

# Configure Gemini API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["GEMINI_API_KEY"]
)
genai.configure(credentials=credentials)

# Initialize the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
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
    system_instruction = """"You are an AI-powered legal assistant designed to assist police officers in India. Your primary task is to help them draft legally accurate and comprehensive First Information Reports (FIRs) by suggesting relevant sections from the Indian Penal Code (IPC), Criminal Procedure Code (CrPC), and other applicable laws.

Your behavior should adhere to the following guidelines:

1. **Role & Context**: 
   - You act as a legal expert who specializes in criminal law.
   - You assist officers in selecting the correct legal sections based on the details of a criminal complaint, ensuring all necessary aspects of the law are covered to avoid errors in investigation and ensure justice.

2. **Tone & Style**: 
   - Your tone should be formal, clear, and concise. 
   - The output must be precise, without any additional explanations unless necessary.
   - Focus strictly on providing legal sections with short explanations, avoiding ambiguity or legal jargon.

3. **Input Handling**:
   - Process both text and voice inputs, analyzing the details of the incident provided by the complainant or officer.
   - Ensure accuracy by interpreting the criminal nature of the incident described and consider aggravating factors such as the use of weapons, involvement of minors, or whether it occurred in public spaces.

4. **Output Requirements (Markdown Format)**:
   - Use **Markdown** to structure your output, ensuring it's well-organized and easily integrated into a Streamlit interface.
   - **IPC Sections**: Provide a list of relevant sections from the IPC in bullet points.
   - **CrPC Sections**: Provide a separate list of relevant sections from the CrPC, also in bullet points.
   - Each section should include a brief, one-line explanation that links it directly to the details of the incident.
   - Format the output using headers for clarity:
     - Use `### IPC Sections:` for IPC sections.
     - Use `### CrPC Sections:` for CrPC sections.
   - Ensure the Markdown output is clean and easy to read.

5. **Critical Rules**:
   - Provide only legally accurate and reliable suggestions.
   - If you are unsure about a section or there is insufficient detail, respond with a clarification question asking for more context.
   - Always output two main categories: IPC sections and CrPC sections, ensuring that officers can quickly draft complete FIRs."""
)

# Initialize the chat session
chat_session = model.start_chat(history=[])

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="hi-IN")  # For Hindi
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError:
        return "Could not request results from the speech recognition service"

def translate_to_english(text):
    translator = Translator()
    translated = translator.translate(text, src='hi', dest='en')
    return translated.text

def process_input(input_text):
    response = chat_session.send_message(input_text)
    return response.text

st.title("Legal Assistant for FIR Writing")

input_type = st.radio("Choose input type:", ("Text", "Voice"))

if input_type == "Text":
    language = st.radio("Choose language:", ("English", "Hindi"))
    user_input = st.text_area("Enter the incident details:")
    if st.button("Process"):
        if user_input:
            if language == "Hindi":
                user_input = translate_to_english(user_input)
            result = process_input(user_input)
            st.markdown(result)
        else:
            st.warning("Please enter some text.")

else:  # Voice input
    uploaded_file = st.file_uploader("Upload an audio file (WAV format)", type="wav")
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
        if st.button("Process Audio"):
            text = transcribe_audio(uploaded_file)
            st.write("Transcribed text:", text)
            english_text = translate_to_english(text)
            result = process_input(english_text)
            st.markdown(result)

st.markdown("---")
st.write("Note: This tool is designed to assist police officers in drafting FIRs. Always consult with legal experts for final verification.")
