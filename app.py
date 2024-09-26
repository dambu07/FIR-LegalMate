import streamlit as st
import google.generativeai as genai
from audio import capture_audio, text_to_speech, transcribe_realtime_audio
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import asyncio

# Configure Google Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192
}
model = genai.GenerativeModel("gemini-1.5-pro-002",
        generation_config=generation_config,
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ],
    system_instruction="Generate the output in the language which you received the input. You are an AI-powered legal assistant designed to assist police officers in India. Your primary task is to help them draft legally accurate and comprehensive First Information Reports (FIRs) by suggesting relevant sections from the Indian Penal Code (IPC), Criminal Procedure Code (CrPC), and other applicable laws. Your behavior should adhere to the following guidelines: 1. **Role & Context**: - You act as a legal expert who specializes in criminal law. - You assist officers in selecting the correct legal sections based on the details of a criminal complaint, ensuring all necessary aspects of the law are covered to avoid errors in investigation and ensure justice. 2. **Tone & Style**: - Your tone should be formal, clear, and concise. - The output must be precise, without any additional explanations unless necessary. - Focus strictly on providing legal sections with short explanations, avoiding ambiguity or legal jargon. 3. **Input Handling**: - Process both text and voice inputs, analyzing the details of the incident provided by the complainant or officer. - Ensure accuracy by interpreting the criminal nature of the incident described and consider aggravating factors such as the use of weapons, involvement of minors, or whether it occurred in public spaces. 4. **Output Requirements (Markdown Format)**: - Use **Markdown** to structure your output, ensuring it's well-organized and easily integrated into a Streamlit interface. - **IPC Sections**: Provide a list of relevant sections from the IPC in bullet points. - **CrPC Sections**: Provide a separate list of relevant sections from the CrPC, also in bullet points. - Each section should include a brief, one-line explanation that links it directly to the details of the incident. - Format the output using headers for clarity: - Use `### IPC Sections:` for IPC sections. - Use `### CrPC Sections:` for CrPC sections. - Ensure the Markdown output is clean and easy to read. 5. **Critical Rules**: - Provide only legally accurate and reliable suggestions. - If you are unsure about a section or there is insufficient detail, respond with a clarification question asking for more context. - Always output two main categories: IPC sections and CrPC sections, ensuring that officers can quickly draft complete FIRs."
)

def process_input(input_text):
    response = model.generate_content(input_text)
    return response[0].text

st.set_page_config(page_title="FIR-LegalMate", page_icon="⚖️")

# Language selection at the start
language = st.selectbox("Select language:", ("English", "Hindi"), key="language_selector")
lang_code = "en-IN" if language == "English" else "hi-IN"
output_language = "en" if language == "English" else "hi"

st.title("Legal Assistant for FIR Writing")

# Input type selection (Text or Speech Realtime)
input_type = st.radio("Choose input type:", ("Text", "Speech (Realtime)"))

user_input = ""

if input_type == "Text":
    user_input = st.text_area("Enter the incident details:")
elif input_type == "Speech (Realtime)":
    st.write("Please speak into the microphone:")
    
    # WebRTC-based real-time audio stream processing
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.recognizer = sr.Recognizer()
            self.text_output = ""

        def recv(self, frame):
            audio = frame.to_ndarray().tobytes()
            try:
                self.text_output = transcribe_realtime_audio(audio, lang_code)
            except Exception as e:
                self.text_output = str(e)
            return frame

    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode="sendonly",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.state.playing:
        if webrtc_ctx.audio_processor and webrtc_ctx.audio_processor.text_output:
            user_input = webrtc_ctx.audio_processor.text_output
            st.write(f"Transcribed text ({language}): {user_input}")

if st.button("Process") and user_input:
    result = process_input(user_input)
    st.markdown(result)

    # Generate audio output
    audio_output = text_to_speech(result, output_language)
    st.audio(audio_output, format="audio/mp3")

st.markdown("---")
st.write("Note: This tool is designed to assist police officers in drafting FIRs. Always consult with legal experts for final verification.")
