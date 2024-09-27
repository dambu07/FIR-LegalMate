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
language = st.selectbox("Select language:", (
    "English", "Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", 
    "Kannada", "Odia", "Malayalam", "Punjabi", "Assamese", "Urdu", "Maithili", 
    "Santali", "Konkani", "Sindhi", "Kashmiri", "Dogri", "Bodo", "Manipuri (Meitei)"
))

# Mapping language to language codes
language_map = {
    "English": ("en-IN", "en"),
    "Hindi": ("hi-IN", "hi"),
    "Bengali": ("bn-IN", "bn"),
    "Telugu": ("te-IN", "te"),
    "Marathi": ("mr-IN", "mr"),
    "Tamil": ("ta-IN", "ta"),
    "Gujarati": ("gu-IN", "gu"),
    "Kannada": ("kn-IN", "kn"),
    "Odia": ("or-IN", "or"),
    "Malayalam": ("ml-IN", "ml"),
    "Punjabi": ("pa-IN", "pa"),
    "Assamese": ("as-IN", "as"),
    "Urdu": ("ur-IN", "ur"),
    "Maithili": ("mai-IN", "mai"),
    "Santali": ("sat-IN", "sat"),
    "Konkani": ("kok-IN", "kok"),
    "Sindhi": ("sd-IN", "sd"),
    "Kashmiri": ("ks-IN", "ks"),
    "Dogri": ("doi-IN", "doi"),
    "Bodo": ("brx-IN", "brx"),
    "Manipuri (Meitei)": ("mni-IN", "mni")
}

# Set the language code and output language based on selection
lang_code, output_language = language_map[language]

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
        "process": "प्रोसेस करें",
        "no_input_warning": "कृपया कुछ टेक्स्ट दर्ज करें या वॉइस इनपुट का उपयोग करें।",
        "note": "नोट: यह उपकरण पुलिस अधिकारियों को एफआईआर ड्राफ्ट करने में सहायता करने के लिए डिज़ाइन किया गया है। अंतिम सत्यापन के लिए हमेशा कानूनी विशेषज्ञों से परामर्श करें।"
    },
    "Bengali": {
        "title": "এফআইআর লেখার জন্য আইনি সহায়তা",
        "input_type": "ইনপুট প্রকার নির্বাচন করুন:",
        "text_input": "ঘটনার বিবরণ লিখুন:",
        "upload_audio": "অডিও ফাইল আপলোড করুন",
        "process": "প্রক্রিয়া করুন",
        "no_input_warning": "অনুগ্রহ করে কিছু পাঠ্য লিখুন বা অডিও রেকর্ডার ব্যবহার করুন।",
        "note": "বিঃ দ্রঃ এই সরঞ্জামটি এফআইআর খসড়া তৈরিতে সহায়তা করার জন্য ডিজাইন করা হয়েছে। চূড়ান্ত যাচাইয়ের জন্য সর্বদা আইনি বিশেষজ্ঞদের সাথে পরামর্শ করুন।"
    },
    "Telugu": {
        "title": "FIR రాయడానికి న్యాయ సహాయకుడు",
        "input_type": "ఇన్‌పుట్ రకాన్ని ఎంచుకోండి:",
        "text_input": "సంఘటన వివరాలు నమోదు చేయండి:",
        "upload_audio": "ఆడియో ఫైల్‌ని అప్‌లోడ్ చేయండి",
        "process": "ప్రాసెస్ చేయండి",
        "no_input_warning": "దయచేసి కొన్ని పాఠ్యాన్ని నమోదు చేయండి లేదా వాయిస్ ఇన్‌పుట్ ఉపయోగించండి.",
        "note": "గమనిక: ఈ సాధనం FIRలు తయారు చేయడంలో పోలీసు అధికారులకు సహాయం చేయడానికి రూపొందించబడింది. తుది నిర్ధారణ కోసం ఎల్లప్పుడూ న్యాయ నిపుణులతో సంప్రదించండి."
    },
    "Marathi": {
        "title": "FIR लिहिण्यासाठी कायदेशीर सहाय्यक",
        "input_type": "इनपुट प्रकार निवडा:",
        "text_input": "घटनेचा तपशील प्रविष्ट करा:",
        "upload_audio": "ऑडिओ फाइल अपलोड करा",
        "process": "प्रक्रिया करा",
        "no_input_warning": "कृपया काही मजकूर प्रविष्ट करा किंवा ऑडिओ इनपुट वापरा.",
        "note": "सूचना: हे साधन एफआयआर तयार करण्यात पोलिस अधिकाऱ्यांना मदत करण्यासाठी डिझाइन केले आहे. अंतिम पडताळणीसाठी नेहमी कायदेशीर तज्ञांचा सल्ला घ्या."
    },
    "Tamil": {
        "title": "FIR எழுதுவதற்கான சட்ட உதவியாளர்",
        "input_type": "உள்ளீட்டு வகையைத் தேர்ந்தெடுக்கவும்:",
        "text_input": "நிகழ்வின் விவரங்களை உள்ளிடுங்கள்:",
        "upload_audio": "ஆடியோ கோப்பைப் பதிவேற்றவும்",
        "process": "செயலாக்கவும்",
        "no_input_warning": "சில உரையை உள்ளிடவும் அல்லது ஒலி உள்ளீட்டை பயன்படுத்தவும்.",
        "note": "குறிப்பு: இந்த கருவி FIRகளை உருவாக்க காவல் அதிகாரிகளுக்கு உதவுவதற்காக வடிவமைக்கப்பட்டது. இறுதி சரிபார்ப்பிற்கு எப்போதும் சட்ட நிபுணர்களுடன் கலந்தாலோசிக்கவும்."
    },
    "Gujarati": {
        "title": "FIR લખવા માટે કાનૂની સહાયક",
        "input_type": "ઇનપુટ પ્રકાર પસંદ કરો:",
        "text_input": "ઘટનાની વિગતો દાખલ કરો:",
        "upload_audio": "ઓડિયો ફાઈલ અપલોડ કરો",
        "process": "પ્રક્રિયા કરો",
        "no_input_warning": "કૃપા કરીને કાંઈક લખો અથવા ઓડિયો ઇનપુટનો ઉપયોગ કરો.",
        "note": "નોંધ: આ ટૂલ એફઆઇઆર ડ્રાફ્ટ કરવા માટે પોલીસ અધિકારીઓને સહાય કરવા માટે રચાયેલ છે. અંતિમ ચકાસણી માટે હંમેશા કાનૂની નિષ્ણાતોની સલાહ લો."
    },
    "Kannada": {
        "title": "FIR ಬರೆಯಲು ಕಾನೂನು ಸಹಾಯಕ",
        "input_type": "ಇನ್ಪುಟ್ ಪ್ರಕಾರ ಆಯ್ಕೆಮಾಡಿ:",
        "text_input": "ಘಟನೆಯ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ:",
        "upload_audio": "ಆಡಿಯೋ ಫೈಲ್ ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "process": "ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ",
        "no_input_warning": "ದಯವಿಟ್ಟು ಕೆಲವು ಪಠ್ಯವನ್ನು ನಮೂದಿಸಿ ಅಥವಾ ವಾಯ್ಸ್ ಇನ್‌ಪುಟ್ ಬಳಸಿರಿ.",
        "note": "ಸೂಚನೆ: ಈ ಸಾಧನವು FIRಗಳನ್ನು ಕರಡು ಮಾಡಲು ಪೊಲೀಸ್ ಅಧಿಕಾರಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾಗಿದೆ. ಅಂತಿಮ ದೃಢೀಕರಣಕ್ಕಾಗಿ ಕಾನೂನು ತಜ್ಞರೊಂದಿಗೆ ಸದಾ ಪರಾಮರ್ಶಿಸಿ."
    },
    "Odia": {
        "title": "FIR ଲେଖିବା ପାଇଁ କାନୁନ ସହାୟକ",
        "input_type": "ଇନପୁଟ ପ୍ରକାର ଚୟନ କରନ୍ତୁ:",
        "text_input": "ଘଟଣା ବିବରଣୀ ଦାଖଲ କରନ୍ତୁ:",
        "upload_audio": "ଅଡିଓ ଫାଇଲ ଅପଲୋଡ୍ କରନ୍ତୁ",
        "process": "ପ୍ରକ୍ରିୟା କରନ୍ତୁ",
        "no_input_warning": "ଦୟାକରି କିଛି ଟେକ୍ସଟ୍ ଦାଖଲ କରନ୍ତୁ କିମ୍ବା ଭଓଇସ୍ ଇନପୁଟ୍ ବ୍ୟବହାର କରନ୍ତୁ।",
        "note": "ଟିପ୍ପଣୀ: ଏହି ସାଧନଟି FIR ତିଆରି କରିବାରେ ପୋଲିସ୍ ଅଧିକାରୀଙ୍କୁ ସହାୟତା କରିବା ପାଇଁ ଉଦ୍ଦିଷ୍ଟ ହୋଇଛି। ଶେଷ ଯାଞ୍ଚ ପାଇଁ ସଦା ବିଶେଷଜ୍ଞଙ୍କ ସହ ମତାମତ କରନ୍ତୁ।"
    },
    "Malayalam": {
        "title": "FIR എഴുതുന്നതിനുള്ള നിയമ സഹായി",
        "input_type": "ഇൻപുട്ട് തരം തിരഞ്ഞെടുക്കുക:",
        "text_input": "സംഭവത്തിന്റെ വിശദാംശങ്ങൾ നൽകുക:",
        "upload_audio": "ഓഡിയോ ഫയൽ അപ്‌ലോഡ് ചെയ്യുക",
        "process": "പ്രക്രിയ ചെയ്യുക",
        "no_input_warning": "ദയവായി കുറച്ച് ടെക്സ്റ്റ് നൽകുക അല്ലെങ്കിൽ ശബ്ദ ഇൻപുട്ട് ഉപയോഗിക്കുക.",
        "note": "ശ്രദ്ധിക്കുക: ഈ ഉപകരണം FIRകൾ തയ്യാറാക്കുന്നതിൽ പോലീസ് ഉദ്യോഗസ്ഥരെ സഹായിക്കാൻ രൂപകൽപ്പന ചെയ്തതാണ്. അന്തിമ പരിശോധനയ്ക്കായി നിയമ വിദഗ്ധരുമായി എപ്പോഴും കരുതൽ സ്വീകരിക്കുക."
    },
    "Punjabi": {
        "title": "FIR ਲਿਖਣ ਲਈ ਕਾਨੂੰਨੀ ਸਹਾਇਕ",
        "input_type": "ਇਨਪੁਟ ਤਰੱਕ ਚੁਣੋ:",
        "text_input": "ਘਟਨਾ ਦੇ ਵੇਰਵੇ ਦਾਖਲ ਕਰੋ:",
        "upload_audio": "ਆਡੀਓ ਫਾਇਲ ਅਪਲੋਡ ਕਰੋ",
        "process": "ਪ੍ਰਕਿਰਿਆ ਕਰੋ",
        "no_input_warning": "ਕਿਰਪਾ ਕਰਕੇ ਕੁਝ ਟੈਕਸਟ ਦਾਖਲ ਕਰੋ ਜਾਂ ਆਡੀਓ ਇਨਪੁਟ ਵਰਤੋ।",
        "note": "ਨੋਟ: ਇਹ ਟੂਲ FIR ਲਿਖਣ ਵਿਚ ਪੁਲਿਸ ਅਧਿਕਾਰੀਆਂ ਦੀ ਮਦਦ ਕਰਨ ਲਈ ਡਿਜ਼ਾਇਨ ਕੀਤਾ ਗਿਆ ਹੈ। ਅੰਤਮ ਸਤਿਆਪਨ ਲਈ ਹਮੇਸ਼ਾਂ ਕਾਨੂੰਨੀ ਮਾਹਰਾਂ ਨਾਲ ਸਲਾਹ ਕਰੋ।"
    },
    "Assamese": {
        "title": "FIR লিখিবলৈ আইনী সহায়ক",
        "input_type": "ইনপুট প্ৰকাৰ বাচক:",
        "text_input": "ঘটনাৰ বিৱৰণ লিখক:",
        "upload_audio": "অডিঅ' ফাইল আপলোড কৰক",
        "process": "প্ৰক্ৰিয়া কৰক",
        "no_input_warning": "অনুগ্ৰহ কৰি কিছুমান লিখক বা ভয়েচ্‌ ইনপুট ব্যৱহাৰ কৰক।",
        "note": "টোকা: এই টুলটো FIR খচৰা কৰিবলৈ আৰক্ষী বিষয়াসকলক সহায় কৰিবৰ বাবে ডিজাইন কৰা হৈছে। চূড়ান্ত পৰীক্ষাৰ বাবে সদায় আইনী বিশেষজ্ঞসকলৰ লগত পৰামৰ্শ কৰক।"
    },
    "Urdu": {
        "title": "ایف آئی آر لکھنے کے لئے قانونی مددگار",
        "input_type": "انپٹ قسم کا انتخاب کریں:",
        "text_input": "واقعہ کی تفصیلات درج کریں:",
        "upload_audio": "آڈیو فائل اپ لوڈ کریں",
        "process": "پروسیس کریں",
        "no_input_warning": "براہ کرم کچھ متن درج کریں یا آڈیو انپٹ استعمال کریں۔",
        "note": "نوٹ: یہ ٹول ایف آئی آر کا مسودہ تیار کرنے میں پولیس افسران کی مدد کرنے کے لئے ڈیزائن کیا گیا ہے۔ حتمی تصدیق کے لئے ہمیشہ قانونی ماہرین سے مشورہ کریں۔"
    },
    "Maithili": {
        "title": "FIR लिखबा लेल कानूनी सहयोगी",
        "input_type": "इनपुट प्रकार चुनू:",
        "text_input": "घटना के विवरण दर्ज करू:",
        "upload_audio": "ऑडियो फाइल अपलोड करू",
        "process": "प्रोसेस करू",
        "no_input_warning": "कृपया किछु पाठ दर्ज करू या आवाज इनपुट उपयोग करू।",
        "note": "नोट: ई टूल पुलिस अधिकारी के FIR ड्राफ्ट करे में मदद करे खातिर डिजाइन कएल गेल अछि। अंतिम सत्यापन लेल हमेशा कानूनी विशेषज्ञ के संग सलाह करू।"
    },
    "Santali": {
        "title": "FIR लिखाए आरक कानुनी सहयोगी",
        "input_type": "इनपुट प्रकार चनाओ:",
        "text_input": "घटना अक विवरण दाखिल करा:",
        "upload_audio": "ऑडियो फाइल अपलोड करा",
        "process": "प्रोसेस करा",
        "no_input_warning": "कृपया किछु पाठ दाखिल करा या आवाज इनपुट प्रयोग करा।",
        "note": "नोट: ई टूल पुलिस अधिकारी के FIR ड्राफ्ट करे में सहायता करबअ लेल डिजाइन कायल गयल अछि। अंतिम सत्यापन लेल हमेशा कानुनी विशेषज्ञ सखत सलाह करा।"
    },
    "Konkani": {
        "title": "FIR लिहण्यासाठी कायद्याचो सहाय्यक",
        "input_type": "इनपुट प्रकार निवडा:",
        "text_input": "घटनेचे तपशील भरा:",
        "upload_audio": "ऑडिओ फाइल अपलोड करा",
        "process": "प्रक्रिया करा",
        "no_input_warning": "कृपया थोडं टेक्स्ट भरा वा ऑडिओ इनपुट वापरा.",
        "note": "सूचना: हे टूल पोलिस अधिकाऱ्यांना FIR ड्राफ्ट करपाच्या मदतीसाठी डिझाइन केलंय. अंतिम सत्यापनाक ताजे नेहमीच कायदा तज्ञांचे सल्ला घ्या."
    },
    "Sindhi": {
        "title": "FIR لکڻ لاءِ قانوني مددگار",
        "input_type": "ان پٽ جو قسم چونڊيو:",
        "text_input": "واقعي جا تفصيل درج ڪريو:",
        "upload_audio": "آڊيو فائل اپلوڊ ڪريو",
        "process": "پروسيس ڪريو",
        "no_input_warning": "مهرباني ڪري ڪجهه ٽيڪسٽ داخل ڪريو يا آڊيو ان پٽ استعمال ڪريو.",
        "note": "نوٽ: ھي اوزار پوليس آفيسرن کي FIR مسودو ڪرڻ ۾ مدد ڏيڻ لاءِ ڊزائين ڪيو ويو آھي. حتمي تصديق لاءِ هميشه قانوني ماهرن سان صلاح ڪريو."
    },
    "Kashmiri": {
        "title": "FIR لکھنے کے لئے قانونی مددگار",
        "input_type": "انپٹ قسم کا انتخاب کریں:",
        "text_input": "واقعہ کی تفصیلات درج کریں:",
        "upload_audio": "آڈیو فائل اپ لوڈ کریں",
        "process": "پروسیس کریں",
        "no_input_warning": "براہ کرم کچھ متن درج کریں یا آڈیو انپٹ استعمال کریں۔",
        "note": "نوٹ: یہ ٹول ایف آئی آر کا مسودہ تیار کرنے میں پولیس افسران کی مدد کرنے کے لئے ڈیزائن کیا گیا ہے۔ حتمی تصدیق کے لئے ہمیشہ قانونی ماہرین سے مشورہ کریں۔"
    },
    "Dogri": {
        "title": "FIR लिखण खा़तिर क़ानूनी सहायक",
        "input_type": "इनपुट प्रकार चुनौ:",
        "text_input": "घटना दा विवरण लिखो:",
        "upload_audio": "ऑडियो फाइल अपलोड करो",
        "process": "प्रक्रिया करो",
        "no_input_warning": "कृपया किछु पाठ लिखौ जा आवाज इनपुट इस्तेमाल करो।",
        "note": "नोट: ई टूल पुलिस अधिकारी खा़तिर FIR लिखण में सहायता करन खातिर डिजाइन कायल गया अछि। अंतिम सत्यापन वास्ते हमेशा कानूनी विशेषज्ञ संग सलाह करो।"
    },
    "Bodo": {
        "title": "FIR लेखनाय र कोनुन साहाय",
        "input_type": "इनपुट प्रकार सानोलाय:",
        "text_input": "घटनार विवरण सानोलाय:",
        "upload_audio": "ऑडिओ फाइल अपलोड कराय",
        "process": "प्रकृया कराय",
        "no_input_warning": "दयाकरी किछु पाठ सानोलाय ना वॉयस इनपुट उपयोग कराय.",
        "note": "नोट: ई टूल पुलिस अधिकारीर FIR ड्राफ्ट करायमदाय साहाय करनाक लागि डिजाइन कायलगायअ अछि. अंतिम सत्यापन र लागि हमेशा कोनुन विशेषज्ञ संग सलाह गरयअ."
    },
    "Manipuri (Meitei)": {
        "title": "FIR লিকহাকপা নিংথৌ মশঙ",
        "input_type": "ইনপুটপ্রকার অয়েনখ্রী:",
        "text_input": "ঘটনার কেবতউং লিখবিরাক",
        "upload_audio": "অডিওফাইল আপলোড তবিরাক",
        "process": "প্রক্রিয়া করাক",
        "no_input_warning": "দয়া করিকিং কিছুমান লিখওয়ৈবা, ভয়েস ইনপুট শোমজালগিবখ্রী।",
        "note": "নোট: ঐন তুবতুলিটুলদা পুলিশ কর্মকর্তা FIR খসড়া তৈরিতুমাশঙঙ। চূড়ান্তপরীক্ষাস্য়্য়উদাম্রিককথাটৈ ইমাইবচুগ্ন্স খাইশৈ।"
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
