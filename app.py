import streamlit as st
import google.generativeai as genai
from audio import transcribe_audio_data, text_to_speech
from audio_recorder_streamlit import audio_recorder

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

st.set_page_config(page_title="FIR-LegalMate", page_icon="⚖️")

# Language selection
language = st.selectbox("Select language:", ("English", "Hindi"), key="language_selector")
lang_code = "en-IN" if language == "English" else "hi-IN"
output_language = "en" if language == "English" else "hi"

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ],
    system_instruction = f"Generate the output in the {language}. You are an AI-powered legal assistant designed to assist police officers in India. Your primary task is to help them draft legally accurate and comprehensive First Information Reports (FIRs) by suggesting relevant sections from the Indian Penal Code (IPC), Criminal Procedure Code (CrPC), and other applicable laws. Your behavior should adhere to the following guidelines: 1. **Role & Context**: - You act as a legal expert who specializes in criminal law. - You assist officers in selecting the correct legal sections based on the details of a criminal complaint, ensuring all necessary aspects of the law are covered to avoid errors in investigation and ensure justice. 2. **Tone & Style**: - Your tone should be formal, clear, and concise. - The output must be precise, without any additional explanations unless necessary. - Focus strictly on providing legal sections with short explanations, avoiding ambiguity or legal jargon. 3. **Input Handling**: - Process both text and voice inputs, analyzing the details of the incident provided by the complainant or officer. - Ensure accuracy by interpreting the criminal nature of the incident described and consider aggravating factors such as the use of weapons, involvement of minors, or whether it occurred in public spaces. 4. **Output Requirements (Markdown Format)**: - Use **Markdown** to structure your output, ensuring it's well-organized and easily integrated into a Streamlit interface. - **IPC Sections**: Provide a list of relevant sections from the IPC in bullet points. - **CrPC Sections**: Provide a separate list of relevant sections from the CrPC, also in bullet points. - Each section should include a brief, one-line explanation that links it directly to the details of the incident. - Format the output using headers for clarity: - Use `### IPC Sections:` for IPC sections. - Use `### CrPC Sections:` for CrPC sections. - Ensure the Markdown output is clean and easy to read. 5. **Critical Rules**: - Provide only legally accurate and reliable suggestions. - If you are unsure about a section or there is insufficient detail, respond with a clarification question asking for more context. - Always output two main categories: IPC sections and CrPC sections, ensuring that officers can quickly draft complete FIRs."
)

chat_session = model.start_chat(history=[])

def process_input(input_text, language):
    response = chat_session.send_message(input_text)
    return response.text

# Localized strings
strings = {
    "English": {
        "title": "Legal Assistant for FIR Writing",
        "input_type": "Choose input type:",
        "text_input": "Enter the incident details:",
        "upload_audio": "Upload Audio File",
        "process": "Process",
        "no_input_warning": "Please enter some text or use the audio recorder.",
        "note": "Note: This tool is designed to assist police officers in drafting FIRs. Always consult with legal experts for final verification."
    },
    "Hindi": {
        "title": "FIR लेखन के लिए कानूनी सहायक",
        "input_type": "इनपुट प्रकार चुनें:",
        "text_input": "घटना का विवरण दर्ज करें:",
        "upload_audio": "ऑडियो फ़ाइल अपलोड करें",
        "process": "Process करें",
        "no_input_warning": "कृपया कुछ टेक्स्ट दर्ज करें या वॉइस इनपुट का उपयोग करें।",
        "note": "नोट: यह उपकरण पुलिस अधिकारियों को एफआईआर ड्राफ्ट करने में सहायता करने के लिए डिज़ाइन किया गया है। अंतिम सत्यापन के लिए हमेशा कानूनी विशेषज्ञों से परामर्श करें।"
    }
}

st.title(strings[language]["title"])

input_type = st.radio(strings[language]["input_type"], ("Text", "Audio"))

user_input = ""

if input_type == "Text":
    user_input = st.text_area(strings[language]["text_input"])
else:
    audio_data = audio_recorder(text="Click the Mic when you're ready")

    if audio_data:
        st.audio(audio_data, format="audio/wav")
        
        # Transcribe the audio to text
        user_input = transcribe_audio_data(audio_data, lang_code)
        
        # Display the transcribed text for clarity
        st.write(f"**Transcribed text ({language}):** {user_input}")

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
